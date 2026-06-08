"""
Scenario schemas for end-to-end scenario simulation results.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from schemas.forecast_schema import AdjustedForecastResult
from schemas.risk_schema import StockoutRiskResult
from schemas.otb_schema import OTBPositionResult
from schemas.recommendation_schema import RecommendationResult


class ScenarioRequest(BaseModel):
    """User request for scenario simulation."""
    query: str
    session_id: Optional[str] = None
    scope: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Filters: category, channel, sku_ids, date_range"
    )


class ScenarioResult(BaseModel):
    """Complete end-to-end scenario simulation result."""
    session_id: str
    query: str
    
    # Perturbations applied
    perturbations: List[Dict[str, Any]] = Field(default_factory=list)
    perturbation_summary: str = ""
    
    # Layer 3: Tool results
    baseline_forecast: Optional[Dict[str, Any]] = None
    adjusted_forecast: Optional[Dict[str, Any]] = None
    stockout_risk: Optional[Dict[str, Any]] = None
    otb_position: Optional[Dict[str, Any]] = None
    
    # Layer 4: Recommendations
    recommendations: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: float = 0
    
    # Tool execution trace
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    
    summary: str = Field(default="", description="Natural language summary for LLM")


class ScenarioComparison(BaseModel):
    """Baseline vs scenario comparison for UI rendering."""
    category: str
    channel: str
    
    baseline_qty: float
    scenario_qty: float
    change_pct: float
    
    baseline_revenue: Optional[float] = None
    scenario_revenue: Optional[float] = None
    
    # Risk comparison
    baseline_risk_skus: int = 0
    scenario_risk_skus: int = 0
    new_risk_skus: List[str] = Field(default_factory=list)
    
    # OTB comparison
    baseline_otb_utilization: float = 0
    scenario_otb_utilization: float = 0
    otb_overcommit: bool = False