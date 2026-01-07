from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from erp_kernel.core.result import Result
from erp_kernel.core.ports import EventBus
from erp_kernel.modules.inventory.domain.models import StockItem
from erp_kernel.modules.inventory.domain.events import StockReceived
from erp_kernel.modules.inventory.ports import StockRepository, InboundOrderRepository

class ReceiveGoodsCommand(BaseModel):
    sku: str
    qty: int
    bin_location: str
    tenant_id: str
    ref_po_id: Optional[str] = None

class InventoryService:
    """
    Application Service (Orchestrator).
    Coordinates the loading of data, execution of domain logic, persistence, and event emission.
    """
    def __init__(self, repository: StockRepository, event_bus: EventBus, inbound_repo: Optional[InboundOrderRepository] = None):
        self.repository = repository
        self.event_bus = event_bus
        self.inbound_repo = inbound_repo

    async def receive_goods(self, cmd: ReceiveGoodsCommand) -> Result[StockItem, str]:
        # 0. Validate Expectation (The 3-Way Match Check)
        if cmd.ref_po_id:
            if not self.inbound_repo:
                return Result.fail("Configuration Error: Inbound validation required but no repository provided.")

            expectation = await self.inbound_repo.get_expectation(cmd.ref_po_id, cmd.sku)
            
            if not expectation:
                return Result.fail(f"Unexpected receipt: PO {cmd.ref_po_id} does not expect SKU {cmd.sku}")
            
            remaining = expectation['qty_ordered'] - expectation['qty_received']
            if cmd.qty > remaining:
                return Result.fail(f"Over-receipt: Expected {remaining}, Received {cmd.qty}")
            
            # Update Expectation
            await self.inbound_repo.update_received(cmd.ref_po_id, cmd.sku, cmd.qty)
        
        # 1. Load Aggregate
        item = await self.repository.get_by_sku(cmd.sku)
        
        if not item:
            # If item doesn't exist, create it (policy decision)
            item = StockItem(sku=cmd.sku, qty=0, bin_location=cmd.bin_location)
        
        # 2. Execute Domain Logic
        result = item.add_stock(cmd.qty)
        
        if result.is_failure():
            # If domain constraint violated, bubble up failure
            return result
        
        updated_item = result.value
        
        # 3. Persist State
        await self.repository.save(updated_item)
        
        # 4. Emit Event
        event = StockReceived(
            sku=updated_item.sku,
            qty_added=cmd.qty,
            new_quantity=updated_item.qty,
            location=updated_item.bin_location,
            tenant_id=cmd.tenant_id
        )
        await self.event_bus.publish([event])
        
        return Result.ok(updated_item)
