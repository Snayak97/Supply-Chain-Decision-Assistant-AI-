"""
Inventory schemas for position and availability analysis.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class InventoryRow(BaseModel):
    """Inventory position for a single SKU/warehouse/channel."""
    sku_id: str
    warehouse: str
    channel: str
    
    on_hand_qty: float
    in_transit_qty: float = 0
    reserved_qty: float = 0
    net_available_qty: float
    
    class Config:
        from_attributes = True


class InventoryPositionResult(BaseModel):
    """Result from inventory position queries."""
    inventory_data: List[InventoryRow] = Field(default_factory=list)
    
    total_on_hand: float = 0
    total_in_transit: float = 0
    total_reserved: float = 0
    total_available: float = 0
    
    sku_count: int = 0
    
    summary: str = Field(default="", description="Natural language summary for LLM")
    
    class Config:
        from_attributes = True