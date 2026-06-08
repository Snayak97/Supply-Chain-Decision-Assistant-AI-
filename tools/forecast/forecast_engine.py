"""
Forecast tools for demand forecasting with confidence intervals.
Layer 3 - Tool/Capability Layer
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import numpy as np

from core.database.models import Forecast, SKUMaster
from core.database.session import SessionLocal
from schemas.forecast_schema import ForecastResult, ForecastRow, AdjustedForecastResult, AdjustedForecastRow
from schemas.perturbation_schema import Perturbation, PerturbationType


def get_demand_forecast(
    sku_ids: Optional[List[str]] = None,
    category: Optional[str] = None,
    channel: Optional[str] = None,
    date_range: Optional[str] = None,
    horizon_days: int = 90
) -> ForecastResult:
    """
    Retrieve baseline forecast for the relevant SKU set and horizon.
    
    Reads from v_forecast_with_ci (Forecast model) and returns base + campaign-adjusted
    point forecast with CI bands per SKU/channel/date.
    
    Args:
        sku_ids: Optional list of SKU IDs to filter
        category: Optional category filter
        channel: Optional channel filter
        date_range: Optional date range filter
        horizon_days: Forecast horizon in days (default 90)
    
    Returns:
        ForecastResult with forecast data and summary
    """
    db: Session = SessionLocal()
    
    try:
        # Build query
        query = db.query(Forecast, SKUMaster).join(
            SKUMaster, Forecast.sku_id == SKUMaster.sku_id
        )
        
        if sku_ids:
            query = query.filter(Forecast.sku_id.in_(sku_ids))
        if category:
            query = query.filter(Forecast.category == category)
        if channel:
            query = query.filter(Forecast.channel == channel)
        
        # Get forecast data
        results = query.all()
        
        forecast_rows = []
        total_qty = 0
        sku_set = set()
        
        for forecast, sku_master in results:
            row = ForecastRow(
                sku_id=forecast.sku_id,
                category=forecast.category,
                channel=forecast.channel,
                date=forecast.date,
                base_forecast_qty=forecast.base_forecast_qty,
                adjusted_forecast_qty=forecast.adjusted_forecast_qty,
                lower_ci_80=forecast.lower_ci_80,
                upper_ci_80=forecast.upper_ci_80,
                lower_ci_95=forecast.lower_ci_95,
                upper_ci_95=forecast.upper_ci_95,
                ci_width_80=forecast.ci_width_80
            )
            forecast_rows.append(row)
            total_qty += forecast.adjusted_forecast_qty
            sku_set.add(forecast.sku_id)
        
        # Generate summary
        summary = (
            f"Retrieved forecast for {len(sku_set)} SKUs across "
            f"{len(set(r.category for r in forecast_rows))} categories and "
            f"{len(set(r.channel for r in forecast_rows))} channels. "
            f"Total forecast quantity: {total_qty:,.0f} units."
        )
        
        return ForecastResult(
            forecast_data=forecast_rows,
            total_forecast_qty=total_qty,
            sku_count=len(sku_set),
            summary=summary
        )
        
    finally:
        db.close()
        


def apply_topline_adjustment(
    base_forecast: ForecastResult,
    perturbations: List[Perturbation],
    scope_filter: Optional[Dict[str, Any]] = None
) -> AdjustedForecastResult:
    """
    Apply perturbations to base forecast to produce adjusted forecast series.
    
    Applies scalar multiplier or override dict to base forecast. Perturbations on
    overlapping SKU sets compose correctly (e.g., apparel +30% and topline +25% on
    apparel SKUs = ×1.625, not double-applied).
    
    Does not modify CI widths - shifts point forecast only.
    
    Args:
        base_forecast: Baseline forecast result from get_demand_forecast
        perturbations: List of perturbation objects to apply
        scope_filter: Optional scope filter (channel, category, sku_ids)
    
    Returns:
        AdjustedForecastResult with adjusted forecast data
    """
    adjusted_rows = []
    original_total = 0
    adjusted_total = 0
    
    category_breakdown = {}
    channel_breakdown = {}
    
    for row in base_forecast.forecast_data:
        # Apply scope filter
        if scope_filter:
            if 'category' in scope_filter and row.category != scope_filter['category']:
                adjusted_rows.append(AdjustedForecastRow(
                    sku_id=row.sku_id,
                    category=row.category,
                    channel=row.channel,
                    date=row.date,
                    original_qty=row.adjusted_forecast_qty,
                    adjusted_qty=row.adjusted_forecast_qty,
                    lower_ci_80=row.lower_ci_80,
                    upper_ci_80=row.upper_ci_80,
                    perturbation_applied_pct=0,
                    perturbation_summary="No perturbation (out of scope)"
                ))
                original_total += row.adjusted_forecast_qty
                adjusted_total += row.adjusted_forecast_qty
                continue
        
        # Calculate total multiplier for this row
        total_multiplier = 1.0
        perturbation_summaries = []
        
        for pert in perturbations:
            multiplier = 1.0
            
            if pert.type == PerturbationType.TOPLINE:
                if pert.scope == 'all' or (pert.sku_ids and row.sku_id in pert.sku_ids):
                    multiplier = pert.multiplier
                    perturbation_summaries.append(str(pert))
            
            elif pert.type == PerturbationType.CHANNEL:
                if pert.channel and row.channel == pert.channel:
                    multiplier = pert.multiplier
                    perturbation_summaries.append(str(pert))
            
            elif pert.type == PerturbationType.CATEGORY:
                if pert.category and row.category == pert.category:
                    multiplier = pert.multiplier
                    perturbation_summaries.append(str(pert))
            
            # Compose multipliers (multiply, not add)
            total_multiplier *= multiplier
        
        # Apply multiplier
        original_qty = row.adjusted_forecast_qty
        adjusted_qty = original_qty * total_multiplier
        change_pct = (total_multiplier - 1.0) * 100
        
        # Shift CI bands (not scale in MVP)
        lower_ci = row.lower_ci_80
        upper_ci = row.upper_ci_80
        if lower_ci and upper_ci:
            ci_width = upper_ci - lower_ci
            lower_ci = adjusted_qty - (ci_width / 2)
            upper_ci = adjusted_qty + (ci_width / 2)
        
        adjusted_row = AdjustedForecastRow(
            sku_id=row.sku_id,
            category=row.category,
            channel=row.channel,
            date=row.date,
            original_qty=original_qty,
            adjusted_qty=adjusted_qty,
            lower_ci_80=lower_ci,
            upper_ci_80=upper_ci,
            perturbation_applied_pct=change_pct,
            perturbation_summary=" | ".join(perturbation_summaries) if perturbation_summaries else "No perturbation"
        )
        adjusted_rows.append(adjusted_row)
        
        original_total += original_qty
        adjusted_total += adjusted_qty
        
        # Track breakdowns
        if row.category not in category_breakdown:
            category_breakdown[row.category] = {'original': 0, 'adjusted': 0}
        category_breakdown[row.category]['original'] += original_qty
        category_breakdown[row.category]['adjusted'] += adjusted_qty
        
        if row.channel not in channel_breakdown:
            channel_breakdown[row.channel] = {'original': 0, 'adjusted': 0}
        channel_breakdown[row.channel]['original'] += original_qty
        channel_breakdown[row.channel]['adjusted'] += adjusted_qty
    
    total_change_pct = ((adjusted_total / original_total) - 1.0) * 100 if original_total > 0 else 0
    
    summary = (
        f"Applied {len(perturbations)} perturbation(s). "
        f"Total forecast changed from {original_total:,.0f} to {adjusted_total:,.0f} units "
        f"({total_change_pct:+.1f}% change)."
    )
    
    return AdjustedForecastResult(
        adjusted_data=adjusted_rows,
        original_total_qty=original_total,
        adjusted_total_qty=adjusted_total,
        total_change_pct=total_change_pct,
        category_breakdown=category_breakdown,
        channel_breakdown=channel_breakdown,
        summary=summary
    )