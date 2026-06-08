"""
Recommendation schemas for actionable mitigation proposals.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


class ActionType(str, Enum):
    """Types of actions the system can recommend."""
    BUY = "buy"
    HOLD = "hold"
    CANCEL = "cancel"
    DELAY = "delay"
    EXPEDITE = "expedite"
    REALLOCATE = "reallocate"


class Recommendation(BaseModel):
    """A single actionable recommendation."""
    action_type: ActionType
    sku_id: Optional[str] = None
    po_number: Optional[str] = None
    category: Optional[str] = None
    
    description: str
    rationale: str
    
    # Quantification
    cost: float = Field(default=0, description="Cost to implement (e.g., freight premium)")
    revenue_protected: float = Field(default=0, description="Revenue protected by this action")
    cash_released: float = Field(default=0, description="Cash released by this action")
    
    # Priority and confidence
    priority: str = Field(default="MEDIUM", description="Priority: LOW, MEDIUM, HIGH")
    confidence: float = Field(default=0.7, ge=0, le=1, description="Confidence in recommendation")
    
    # Tradeoff information
    is_tradeoff: bool = False
    alternative_options: Optional[List[str]] = None
    
    # Caveats
    caveats: List[str] = Field(default_factory=list)


class RecommendationResult(BaseModel):
    """Result from the Recommendation Layer."""
    recommendations: List[Recommendation] = Field(default_factory=list)
    
    total_cost: float = 0
    total_revenue_protected: float = 0
    total_cash_released: float = 0
    
    # Summary statistics
    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0
    
    # Action type breakdown
    action_type_breakdown: Optional[dict] = None
    
    summary: str = Field(default="", description="Natural language summary for LLM")
    
    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):

    category: str

    risk_level: str

    recommendation: str