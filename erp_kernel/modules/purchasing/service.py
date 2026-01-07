from typing import List
from uuid import UUID
from pydantic import BaseModel

from erp_kernel.core.result import Result
from erp_kernel.core.ports import EventBus
from erp_kernel.core.value_objects import Money
from erp_kernel.modules.purchasing.domain.models import PurchaseOrder, POLine, POIssued
from erp_kernel.modules.purchasing.ports import PurchaseRepository

# --- Commands ---
class CreateDraftCommand(BaseModel):
    vendor: str
    lines: List[dict] # Simplified for command input: [{"sku": "A", "qty": 10, "price": 5.0}]
    tenant_id: str

class PurchasingService:
    def __init__(self, repository: PurchaseRepository, event_bus: EventBus):
        self.repository = repository
        self.event_bus = event_bus

    async def create_draft(self, cmd: CreateDraftCommand) -> Result[PurchaseOrder, str]:
        # Convert raw dicts to Domain Objects
        try:
            domain_lines = [
                POLine(
                    sku=line['sku'], 
                    qty=line['qty'], 
                    unit_price=Money(amount=line['price'])
                ) for line in cmd.lines
            ]
        except Exception as e:
            return Result.fail(f"Invalid line data: {str(e)}")

        po = PurchaseOrder(vendor=cmd.vendor, lines=domain_lines)
        
        await self.repository.save(po)
        return Result.ok(po)

    async def issue_po(self, po_id: UUID, tenant_id: str) -> Result[PurchaseOrder, str]:
        # 1. Load
        po = await self.repository.get_by_id(po_id)
        if not po:
            return Result.fail("PO not found")
            
        # 2. Logic
        result = po.issue_po()
        if result.is_failure():
            return result
        
        updated_po = result.value
        
        # 3. Persist
        await self.repository.save(updated_po)
        
        # 4. Publish
        event = POIssued(
            po_id=updated_po.po_id,
            vendor=updated_po.vendor,
            total_amount=updated_po.total_amount.amount,
            currency=updated_po.total_amount.currency,
            lines=[{"sku": l.sku, "qty": l.qty} for l in updated_po.lines],
            tenant_id=tenant_id
        )
        await self.event_bus.publish([event])
        
        return Result.ok(updated_po)
