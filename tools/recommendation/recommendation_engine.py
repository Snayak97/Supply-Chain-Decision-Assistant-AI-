"""
Recommendation engine for actionable mitigation proposals.
Layer 4 - Recommendation Layer
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from collections import defaultdict

from core.database.models import PurchaseOrder, SKUMaster
from core.database.session import SessionLocal
from schemas.risk_schema import StockoutRiskResult
from schemas.otb_schema import OTBPositionResult
from schemas.recommendation_schema import RecommendationResult, Recommendation, ActionType


def generate_recommendations(
    stockout_risk: StockoutRiskResult,
    otb_position: OTBPositionResult,
    category: Optional[str] = None
) -> RecommendationResult:
    """
    Convert scenario delta into ranked mitigation actions.
    
    For each SKU that transitions from safe to at-risk: propose expedite, additional PO,
    or channel reallocation. For OTB overcommit: propose PO delays or cancellations.
    Presents tradeoffs with confidence caveats.
    
    Args:
        stockout_risk: Stockout risk result from calculate_stockout_risk
        otb_position: OTB position result from evaluate_otb_position
        category: Optional category filter
    
    Returns:
        RecommendationResult with ranked recommendations
    """
    recommendations = []
    total_cost = 0
    total_revenue_protected = 0
    total_cash_released = 0
    
    db: Session = SessionLocal()
    try:
        # Get open POs for expediting/cancellation recommendations
        open_pos = db.query(PurchaseOrder).filter(
            PurchaseOrder.status.in_(["OPEN", "IN_TRANSIT"])
        ).all()
        
        po_lookup = defaultdict(list)
        for po in open_pos:
            po_lookup[po.sku_id].append(po)
        
        # Generate recommendations for at-risk SKUs
        for risk_row in stockout_risk.at_risk_skus[:10]:  # Top 10 at-risk SKUs
            if risk_row.risk_level in ["CRITICAL", "HIGH"]:
                # Recommendation 1: Expedite existing POs
                if risk_row.sku_id in po_lookup:
                    for po in po_lookup[risk_row.sku_id]:
                        if po.is_cancelable and po.status == "OPEN":
                            freight_cost = po.ordered_qty * 2  # Assume $2/unit expedite cost
                            revenue_protected = risk_row.revenue_at_risk * 0.8  # 80% of revenue at risk
                            
                            rec = Recommendation(
                                action_type=ActionType.EXPEDITE,
                                sku_id=risk_row.sku_id,
                                po_number=po.po_number,
                                category=risk_row.category,
                                description=f"Expedite PO {po.po_number} for {risk_row.sku_id}",
                                rationale=f"SKU at {risk_row.risk_level} risk with ${risk_row.revenue_at_risk:,.0f} revenue at risk. Expediting reduces stockout probability.",
                                cost=freight_cost,
                                revenue_protected=revenue_protected,
                                cash_released=0,
                                priority="HIGH" if risk_row.risk_level == "CRITICAL" else "MEDIUM",
                                confidence=0.75,
                                caveats=[
                                    "This recommendation is based on forecast point estimate.",
                                    "At the lower CI-80 bound, this SKU may return to safe territory.",
                                    f"Expedite cost of ${freight_cost:,.0f} should be weighed against revenue protected."
                                ]
                            )
                            recommendations.append(rec)
                            total_cost += freight_cost
                            total_revenue_protected += revenue_protected
                
                # Recommendation 2: Additional PO for core SKUs
                if risk_row.is_core:
                    sku_info = db.query(SKUMaster).filter(SKUMaster.sku_id == risk_row.sku_id).first()
                    if sku_info:
                        additional_qty = max(sku_info.moq, int(risk_row.units_at_risk * 1.2))
                        po_cost = additional_qty * sku_info.unit_cost
                        revenue_protected = risk_row.revenue_at_risk * 0.9
                        
                        rec = Recommendation(
                            action_type=ActionType.BUY,
                            sku_id=risk_row.sku_id,
                            category=risk_row.category,
                            description=f"Raise additional PO for {additional_qty} units of {risk_row.sku_id}",
                            rationale=f"Core SKU at {risk_row.risk_level} risk. Additional buffer protects revenue and customer experience.",
                            cost=po_cost,
                            revenue_protected=revenue_protected,
                            cash_released=0,
                            priority="HIGH",
                            confidence=0.7,
                            caveats=[
                                f"Requires ${po_cost:,.0f} additional commitment.",
                                "Lead time of 2-4 weeks applies before inventory arrives.",
                                "Consider OTB availability before proceeding."
                            ]
                        )
                        recommendations.append(rec)
                        total_cost += po_cost
                        total_revenue_protected += revenue_protected
        
        # Generate recommendations for OTB overcommit
        for otb_row in otb_position.category_positions:
            if otb_row.is_overcommitted:
                # Find cancelable POs in this category
                category_pos = [po for po in open_pos if po.category == otb_row.category and po.is_cancelable]
                
                for po in category_pos[:3]:  # Top 3 cancelable POs
                    if po.total_value:
                        rec = Recommendation(
                            action_type=ActionType.CANCEL,
                            sku_id=po.sku_id,
                            po_number=po.po_number,
                            category=po.category,
                            description=f"Cancel PO {po.po_number} for {po.sku_id}",
                            rationale=f"Category {otb_row.category} is overcommitted by ${otb_row.overcommit_amount:,.0f}. Canceling this PO releases cash.",
                            cost=0,
                            revenue_protected=0,
                            cash_released=po.total_value,
                            priority="MEDIUM",
                            confidence=0.6,
                            caveats=[
                                f"Cancel penalty: {po.cancel_penalty_pct}% of PO value.",
                                "May impact future availability of this SKU.",
                                "Consider delaying instead of canceling if penalty is high."
                            ]
                        )
                        recommendations.append(rec)
                        total_cash_released += po.total_value * (1 - po.cancel_penalty_pct / 100)
        
        # Sort recommendations by priority and revenue protected
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        recommendations.sort(key=lambda x: (priority_order.get(x.priority, 3), -x.revenue_protected))
        
        # Count by priority
        high_priority_count = sum(1 for r in recommendations if r.priority == "HIGH")
        medium_priority_count = sum(1 for r in recommendations if r.priority == "MEDIUM")
        low_priority_count = sum(1 for r in recommendations if r.priority == "LOW")
        
        # Action type breakdown
        action_type_breakdown = defaultdict(int)
        for rec in recommendations:
            action_type_breakdown[rec.action_type.value] += 1
        
        summary = (
            f"Generated {len(recommendations)} recommendations. "
            f"Total cost: ${total_cost:,.0f}, Revenue protected: ${total_revenue_protected:,.0f}, "
            f"Cash released: ${total_cash_released:,.0f}. "
            f"High priority: {high_priority_count}, Medium: {medium_priority_count}, Low: {low_priority_count}."
        )
        
        return RecommendationResult(
            recommendations=recommendations,
            total_cost=total_cost,
            total_revenue_protected=total_revenue_protected,
            total_cash_released=total_cash_released,
            high_priority_count=high_priority_count,
            medium_priority_count=medium_priority_count,
            low_priority_count=low_priority_count,
            action_type_breakdown=dict(action_type_breakdown),
            summary=summary
        )
        
    finally:
        db.close()