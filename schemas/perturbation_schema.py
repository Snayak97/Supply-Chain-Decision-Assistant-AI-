"""
Perturbation schemas for scenario simulation.
Defines the structure for different types of demand adjustments.
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from enum import Enum


class PerturbationType(str, Enum):
    """Types of perturbations supported in scenario simulation."""
    TOPLINE = "topline"
    CHANNEL = "channel"
    CATEGORY = "category"
    SHIPMENT_DELAY = "shipment_delay"


class Perturbation(BaseModel):
    """
    A single perturbation to apply to the forecast.
    
    Examples:
    - Topline: {type: 'topline', multiplier: 1.25, scope: 'all'}
    - Channel: {type: 'channel', channel: 'DTC', multiplier: 0.85}
    - Category: {type: 'category', category: 'apparel', multiplier: 1.30}
    - Shipment Delay: {type: 'shipment_delay', delay_days: 14, scope: 'all'}
    """
    type: PerturbationType
    multiplier: Optional[float] = Field(
        None,
        description="Multiplier to apply (e.g., 1.25 for +25%, 0.85 for -15%)"
    )
    channel: Optional[str] = Field(
        None,
        description="Channel to apply perturbation to (for type='channel')"
    )
    category: Optional[str] = Field(
        None,
        description="Category to apply perturbation to (for type='category')"
    )
    delay_days: Optional[int] = Field(
        None,
        description="Days to delay shipments (for type='shipment_delay')"
    )
    scope: Optional[str] = Field(
        "all",
        description="Scope of perturbation: 'all', or specific SKU list"
    )
    sku_ids: Optional[List[str]] = Field(
        None,
        description="Specific SKU IDs to apply perturbation to"
    )
    
    def __str__(self) -> str:
        """Human-readable description of the perturbation."""
        if self.type == PerturbationType.TOPLINE:
            change_pct = (self.multiplier - 1) * 100
            direction = "+" if change_pct > 0 else ""
            return f"{direction}{change_pct:.0f}% topline"
        elif self.type == PerturbationType.CHANNEL:
            change_pct = (self.multiplier - 1) * 100
            direction = "+" if change_pct > 0 else ""
            return f"{direction}{change_pct:.0f}% {self.channel}"
        elif self.type == PerturbationType.CATEGORY:
            change_pct = (self.multiplier - 1) * 100
            direction = "+" if change_pct > 0 else ""
            return f"{direction}{change_pct:.0f}% {self.category}"
        elif self.type == PerturbationType.SHIPMENT_DELAY:
            return f"{self.delay_days}-day shipment delay"
        return f"{self.type} perturbation"


class PerturbationList(BaseModel):
    """List of perturbations to apply in sequence."""
    perturbations: List[Perturbation] = Field(default_factory=list)
    
    def get_summary(self) -> str:
        """Get a human-readable summary of all perturbations."""
        if not self.perturbations:
            return "No perturbations"
        return " | ".join(str(p) for p in self.perturbations)
