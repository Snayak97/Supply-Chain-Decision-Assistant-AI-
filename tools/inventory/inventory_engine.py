"""
Inventory tools for position and availability analysis.
Layer 3 - Tool/Capability Layer
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from core.database.models import Inventory, SKUMaster
from core.database.session import SessionLocal
from schemas.inventory_schema import InventoryPositionResult, InventoryRow


def get_inventory_position(
    sku_ids: Optional[List[str]] = None,
    category: Optional[str] = None,
    channel: Optional[str] = None,
    warehouse: Optional[str] = None
) -> InventoryPositionResult:
    """
    Retrieve current inventory position across warehouses and channels.
    
    Reads from v_inventory_position and returns net available-to-sell per SKU/warehouse/channel.
    Used by calculate_stockout_risk to determine buffer before scenario causes stockout.
    
    Args:
        sku_ids: Optional list of SKU IDs to filter
        category: Optional category filter
        channel: Optional channel filter
        warehouse: Optional warehouse filter
    
    Returns:
        InventoryPositionResult with inventory data and summary
    """
    db: Session = SessionLocal()
    
    try:
        # Build query
        query = db.query(Inventory, SKUMaster).join(
            SKUMaster, Inventory.sku_id == SKUMaster.sku_id
        )
        
        if sku_ids:
            query = query.filter(Inventory.sku_id.in_(sku_ids))
        # if category:
        #     # query = query.filter(Inventory.category == category)
        #     query = db.query(Inventory, SKUMaster).join(
        #         SKUMaster,
        #         Inventory.sku_id == SKUMaster.sku_id
        #     ).filter(SKUMaster.category == category)
        if category:
            query = query.filter(SKUMaster.category == category)

         

        if channel:
            query = query.filter(Inventory.channel == channel)
        if warehouse:
            query = query.filter(Inventory.warehouse == warehouse)
        
        # Get inventory data
        results = query.all()
        
        inventory_rows = []
        total_on_hand = 0
        total_in_transit = 0
        total_reserved = 0
        total_available = 0
        sku_set = set()
        
        for inventory, sku_master in results:
            # Calculate net available if not already set
            net_available = inventory.net_available_qty
            if net_available is None:
                net_available = inventory.on_hand_qty + inventory.in_transit_qty - inventory.reserved_qty
            
            row = InventoryRow(
                sku_id=inventory.sku_id,
                warehouse=inventory.warehouse,
                channel=inventory.channel,
                on_hand_qty=inventory.on_hand_qty,
                in_transit_qty=inventory.in_transit_qty,
                reserved_qty=inventory.reserved_qty,
                net_available_qty=net_available
            )
            inventory_rows.append(row)
            
            total_on_hand += inventory.on_hand_qty
            total_in_transit += inventory.in_transit_qty
            total_reserved += inventory.reserved_qty
            total_available += net_available
            sku_set.add(inventory.sku_id)
        
        # Generate summary
        summary = (
            f"Retrieved inventory for {len(sku_set)} SKUs across "
            f"{len(set(r.warehouse for r in inventory_rows))} warehouses and "
            f"{len(set(r.channel for r in inventory_rows))} channels. "
            f"Total available: {total_available:,.0f} units."
        )
        
        return InventoryPositionResult(
            inventory_data=inventory_rows,
            total_on_hand=total_on_hand,
            total_in_transit=total_in_transit,
            total_reserved=total_reserved,
            total_available=total_available,
            sku_count=len(sku_set),
            summary=summary
        )
        
    finally:
        db.close()