"""
OTB (Open-to-Buy) schemas for budget vs committed spend analysis.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class OTBPositionRow(BaseModel):
    """OTB position for a single category/period."""
    category: str
    period: str
    
    budget: float
    committed_spend: float
    available_otb: float
    
    utilization_pct: float
    is_overcommitted: bool = False
    overcommit_amount: float = 0
    
    class Config:
        from_attributes = True


class OTBPositionResult(BaseModel):
    """Result from evaluate_otb_position tool."""
    category_positions: List[OTBPositionRow] = Field(default_factory=list)
    
    total_budget: float = 0
    total_committed: float = 0
    total_available: float = 0
    
    overcommitted_categories: List[str] = Field(default_factory=list)
    total_overcommit_amount: float = 0
    
    # Scenario impact
    scenario_demand_increase: float = 0
    additional_commitment_required: float = 0
    
    summary: str = Field(default="", description="Natural language summary for LLM")
    
    class Config:
        from_attributes = True
