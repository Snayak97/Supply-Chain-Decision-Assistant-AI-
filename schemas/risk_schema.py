"""
Risk analysis schemas for stockout probability and revenue at risk.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class StockoutRiskRow(BaseModel):
    """Stockout risk for a single SKU under a scenario."""
    sku_id: str
    category: str
    channel: str
    
    # Current position
    net_available_qty: float
    baseline_demand: float
    scenario_demand: float
    
    # Risk metrics
    stockout_probability: float = Field(
        ge=0, le=1,
        description="Probability of stockout under scenario (0-1)"
    )
    revenue_at_risk: float = Field(
        default=0,
        description="Expected revenue loss if stockout occurs"
    )
    units_at_risk: float = Field(
        default=0,
        description="Expected units short if stockout occurs"
    )
    
    # Risk classification
    risk_level: str = Field(
        default="LOW",
        description="Risk level: LOW, MEDIUM, HIGH, CRITICAL"
    )
    is_core: bool = False
    
    class Config:
        from_attributes = True


class StockoutRiskResult(BaseModel):
    """Result from calculate_stockout_risk tool."""
    at_risk_skus: List[StockoutRiskRow] = Field(default_factory=list)
    
    total_revenue_at_risk: float = 0
    total_units_at_risk: float = 0
    sku_count_at_risk: int = 0
    core_sku_count_at_risk: int = 0
    
    # Breakdown by risk level
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    
    # Breakdown by category
    category_breakdown: Optional[dict] = None
    
    summary: str = Field(default="", description="Natural language summary for LLM")
    
    class Config:
        from_attributes = True


class StockoutRiskResponse(BaseModel):

    category: str

    total_forecast: float

    total_available_inventory: float

    stockout_exposure: float

    risk_level: str