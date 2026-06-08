"""
Forecast schemas for demand forecasting with confidence intervals.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ForecastRow(BaseModel):
    """Single forecast row for a SKU/channel/date combination."""
    sku_id: str
    category: str
    channel: str
    date: str
    
    # Base forecast before campaign adjustments
    base_forecast_qty: float
    
    # Adjusted forecast after campaign uplift
    adjusted_forecast_qty: float
    
    # Confidence intervals
    lower_ci_80: Optional[float] = None
    upper_ci_80: Optional[float] = None
    lower_ci_95: Optional[float] = None
    upper_ci_95: Optional[float] = None
    
    # Volatility proxy
    ci_width_80: Optional[float] = None
    
    class Config:
        from_attributes = True


class ForecastResult(BaseModel):
    """Result from get_demand_forecast tool."""
    forecast_data: List[ForecastRow] = Field(default_factory=list)
    total_forecast_qty: float = 0
    total_revenue: Optional[float] = None
    sku_count: int = 0
    date_range: Optional[str] = None
    
    summary: str = Field(default="", description="Natural language summary for LLM")
    
    class Config:
        from_attributes = True


class AdjustedForecastRow(BaseModel):
    """Forecast row after applying scenario perturbations."""
    sku_id: str
    category: str
    channel: str
    date: str
    
    original_qty: float
    adjusted_qty: float
    
    # Confidence intervals (shifted, not scaled in MVP)
    lower_ci_80: Optional[float] = None
    upper_ci_80: Optional[float] = None
    
    # Perturbation tracking
    perturbation_applied_pct: float = Field(
        default=0,
        description="Total percentage change applied"
    )
    perturbation_summary: str = Field(
        default="",
        description="Human-readable summary of perturbations applied"
    )
    
    class Config:
        from_attributes = True


class AdjustedForecastResult(BaseModel):
    """Result from apply_topline_adjustment tool."""
    adjusted_data: List[AdjustedForecastRow] = Field(default_factory=list)
    
    original_total_qty: float = 0
    adjusted_total_qty: float = 0
    total_change_pct: float = 0
    
    # Breakdown by category/channel
    category_breakdown: Optional[dict] = None
    channel_breakdown: Optional[dict] = None
    
    summary: str = Field(default="", description="Natural language summary for LLM")
    
    class Config:
        from_attributes = True