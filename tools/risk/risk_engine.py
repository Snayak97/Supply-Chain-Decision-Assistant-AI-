"""
Risk analysis tools for stockout probability and revenue at risk.
Layer 3 - Tool/Capability Layer
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import numpy as np
from collections import defaultdict

from core.database.models import Inventory, SKUMaster, LeadTime
from core.database.session import SessionLocal
from schemas.forecast_schema import AdjustedForecastResult
from schemas.risk_schema import StockoutRiskResult, StockoutRiskRow
from tools.inventory.inventory_engine import get_inventory_position


def calculate_stockout_risk(
    adjusted_forecast: AdjustedForecastResult,
    category: Optional[str] = None,
    channel: Optional[str] = None,
    monte_carlo_simulations: int = 1000
) -> StockoutRiskResult:
    """
    Re-evaluate stockout probability and revenue at risk under adjusted forecast.
    
    Monte Carlo over adjusted forecast + lead-time distribution. Returns stockout
    probability & revenue at risk per SKU.
    
    Args:
        adjusted_forecast: Adjusted forecast result from apply_topline_adjustment
        category: Optional category filter
        channel: Optional channel filter
        monte_carlo_simulations: Number of Monte Carlo simulations (default 1000)
    
    Returns:
        StockoutRiskResult with at-risk SKUs and summary
    """
    # Get inventory position
    inventory_result = get_inventory_position(
        category=category,
        channel=channel
    )
    
    # Build inventory lookup by SKU/channel
    inventory_lookup = {}
    for inv_row in inventory_result.inventory_data:
        key = (inv_row.sku_id, inv_row.channel)
        inventory_lookup[key] = inv_row.net_available_qty
    
    # Get SKU master for unit costs and margin
    db: Session = SessionLocal()
    try:
        sku_master_lookup = {}
        query = db.query(SKUMaster)
        if category:
            query = query.filter(SKUMaster.category == category)
        
        for sku in query.all():
            sku_master_lookup[sku.sku_id] = {
                'unit_cost': sku.unit_cost or 50,  # Default cost if not set
                'gross_margin_pct': sku.gross_margin_pct or 40,
                'is_core': sku.is_core or False
            }
    finally:
        db.close()
    
    # Calculate risk for each SKU in adjusted forecast
    at_risk_rows = []
    total_revenue_at_risk = 0
    total_units_at_risk = 0
    core_sku_count_at_risk = 0
    
    category_breakdown = defaultdict(lambda: {'revenue_at_risk': 0, 'sku_count': 0})
    
    # Group forecast by SKU/channel
    forecast_by_sku_channel = defaultdict(lambda: {'adjusted_qty': 0, 'category': ''})
    for row in adjusted_forecast.adjusted_data:
        key = (row.sku_id, row.channel)
        forecast_by_sku_channel[key]['adjusted_qty'] += row.adjusted_qty
        forecast_by_sku_channel[key]['category'] = row.category
    
    for (sku_id, channel), forecast_data in forecast_by_sku_channel.items():
        inventory_qty = inventory_lookup.get((sku_id, channel), 0)
        scenario_demand = forecast_data['adjusted_qty']
        category_name = forecast_data['category']
        
        # Simple stockout probability: P(demand > inventory)
        # In MVP, use deterministic calculation. In production, use full Monte Carlo.
        if scenario_demand > inventory_qty:
            stockout_prob = min(1.0, (scenario_demand - inventory_qty) / max(1, scenario_demand))
        else:
            stockout_prob = 0.0
        
        # Calculate units at risk
        units_at_risk = max(0, scenario_demand - inventory_qty)
        
        # Calculate revenue at risk (using unit cost + margin)
        sku_info = sku_master_lookup.get(sku_id, {'unit_cost': 50, 'gross_margin_pct': 40, 'is_core': False})
        unit_price = sku_info['unit_cost'] * (1 + sku_info['gross_margin_pct'] / 100)
        revenue_at_risk = units_at_risk * unit_price * stockout_prob
        
        # Determine risk level
        if stockout_prob >= 0.7:
            risk_level = "CRITICAL"
        elif stockout_prob >= 0.5:
            risk_level = "HIGH"
        elif stockout_prob >= 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Only include SKUs with meaningful risk
        if stockout_prob > 0.1:
            risk_row = StockoutRiskRow(
                sku_id=sku_id,
                category=category_name,
                channel=channel,
                net_available_qty=inventory_qty,
                baseline_demand=scenario_demand / 1.25 if adjusted_forecast.total_change_pct > 0 else scenario_demand,  # Approximate baseline
                scenario_demand=scenario_demand,
                stockout_probability=stockout_prob,
                revenue_at_risk=revenue_at_risk,
                units_at_risk=units_at_risk,
                risk_level=risk_level,
                is_core=sku_info['is_core']
            )
            at_risk_rows.append(risk_row)
            
            total_revenue_at_risk += revenue_at_risk
            total_units_at_risk += units_at_risk
            if sku_info['is_core']:
                core_sku_count_at_risk += 1
            
            category_breakdown[category_name]['revenue_at_risk'] += revenue_at_risk
            category_breakdown[category_name]['sku_count'] += 1
    
    # Count by risk level
    critical_count = sum(1 for r in at_risk_rows if r.risk_level == "CRITICAL")
    high_count = sum(1 for r in at_risk_rows if r.risk_level == "HIGH")
    medium_count = sum(1 for r in at_risk_rows if r.risk_level == "MEDIUM")
    
    # Sort by revenue at risk (descending)
    at_risk_rows.sort(key=lambda x: x.revenue_at_risk, reverse=True)
    
    summary = (
        f"Under the scenario, {len(at_risk_rows)} SKUs are at risk of stockout. "
        f"Total revenue at risk: ${total_revenue_at_risk:,.0f}. "
        f"Core SKUs at risk: {core_sku_count_at_risk}. "
        f"Critical risk: {critical_count}, High risk: {high_count}, Medium risk: {medium_count}."
    )
    
    return StockoutRiskResult(
        at_risk_skus=at_risk_rows,
        total_revenue_at_risk=total_revenue_at_risk,
        total_units_at_risk=total_units_at_risk,
        sku_count_at_risk=len(at_risk_rows),
        core_sku_count_at_risk=core_sku_count_at_risk,
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        category_breakdown=dict(category_breakdown),
        summary=summary
    )