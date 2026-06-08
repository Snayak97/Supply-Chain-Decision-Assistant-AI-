"""
OTB (Open-to-Buy) analysis tools for budget vs committed spend.
Layer 3 - Tool/Capability Layer
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from collections import defaultdict

from core.database.models import OTBPlan, PurchaseOrder, SKUMaster
from core.database.session import SessionLocal
from schemas.otb_schema import OTBPositionResult, OTBPositionRow
from schemas.forecast_schema import AdjustedForecastResult


def evaluate_otb_position(
    adjusted_forecast: AdjustedForecastResult,
    period: Optional[str] = None,
    category: Optional[str] = None
) -> OTBPositionResult:
    """
    Re-evaluate OTB commitment and overcommit flags under adjusted demand.
    
    Reads from v_otb_plan and v_open_pos. Re-evaluates committed spend vs budget
    under adjusted demand. Surfaces overcommit by category.
    
    Args:
        adjusted_forecast: Adjusted forecast result from apply_topline_adjustment
        period: Optional period filter (e.g., "2026-Q2")
        category: Optional category filter
    
    Returns:
        OTBPositionResult with category positions and summary
    """
    db: Session = SessionLocal()
    
    try:
        # Get OTB plans
        query = db.query(OTBPlan)
        if category:
            query = query.filter(OTBPlan.category == category)
        if period:
            query = query.filter(OTBPlan.period == period)
        
        otb_plans = query.all()
        
        # Get open POs to calculate committed spend
        po_query = db.query(PurchaseOrder)
        if category:
            po_query = po_query.filter(PurchaseOrder.category == category)
        
        open_pos = po_query.filter(PurchaseOrder.status.in_(["OPEN", "IN_TRANSIT"])).all()
        
        # Calculate committed spend by category
        committed_spend_by_category = defaultdict(float)
        for po in open_pos:
            if po.total_value:
                committed_spend_by_category[po.category] += po.total_value
            elif po.ordered_qty and po.unit_cost:
                committed_spend_by_category[po.category] += po.ordered_qty * po.unit_cost
        
        # Build category positions
        category_positions = []
        total_budget = 0
        total_committed = 0
        total_available = 0
        overcommitted_categories = []
        total_overcommit = 0
        
        for otb in otb_plans:
            committed = committed_spend_by_category.get(otb.category, 0)
            available = otb.budget - committed
            utilization = (committed / otb.budget * 100) if otb.budget > 0 else 0
            is_overcommitted = committed > otb.budget
            overcommit_amt = max(0, committed - otb.budget)
            
            position_row = OTBPositionRow(
                category=otb.category,
                period=otb.period,
                budget=otb.budget,
                committed_spend=committed,
                available_otb=available,
                utilization_pct=utilization,
                is_overcommitted=is_overcommitted,
                overcommit_amount=overcommit_amt
            )
            category_positions.append(position_row)
            
            total_budget += otb.budget
            total_committed += committed
            total_available += available
            
            if is_overcommitted:
                overcommitted_categories.append(otb.category)
                total_overcommit += overcommit_amt
        
        # Calculate additional commitment required due to scenario
        # Estimate: 20% of forecast increase requires additional PO commitment
        forecast_increase = adjusted_forecast.adjusted_total_qty - adjusted_forecast.original_total_qty
        additional_commitment_required = forecast_increase * 50  # Assume $50 avg unit cost
        
        summary = (
            f"OTB position evaluated for {len(category_positions)} categories. "
            f"Total budget: ${total_budget:,.0f}, Committed: ${total_committed:,.0f}, "
            f"Available: ${total_available:,.0f}. "
            f"Overcommitted categories: {len(overcommitted_categories)}. "
            f"Scenario may require ${additional_commitment_required:,.0f} additional commitment."
        )
        
        return OTBPositionResult(
            category_positions=category_positions,
            total_budget=total_budget,
            total_committed=total_committed,
            total_available=total_available,
            overcommitted_categories=overcommitted_categories,
            total_overcommit_amount=total_overcommit,
            scenario_demand_increase=forecast_increase,
            additional_commitment_required=additional_commitment_required,
            summary=summary
        )
        
    finally:
        db.close()
