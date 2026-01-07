from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from erp_kernel.core.result import Result
from erp_kernel.core.base_event import BaseEvent
from erp_kernel.core.value_objects import Money

# --- Events ---
class POIssued(BaseEvent):
    event_type: str = "POIssued"
    po_id: UUID
    vendor: str
    total_amount: float
    currency: str
    lines: List[dict] # payload of what to expect: [{"sku": "A", "qty": 10}]

# --- Models ---
class POStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    COMPLETED = "completed"

class POLine(BaseModel):
    sku: str
    qty: int
    unit_price: Money

class PurchaseOrder(BaseModel):
    """
    Domain Aggregate for Purchase Orders.
    """
    po_id: UUID = Field(default_factory=uuid4)
    vendor: str
    lines: List[POLine]
    status: POStatus = POStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def total_amount(self) -> Money:
        total = 0.0
        currency = "USD"
        if self.lines:
            currency = self.lines[0].unit_price.currency
            for line in self.lines:
                total += line.qty * line.unit_price.amount
        return Money(amount=total, currency=currency)

    def issue_po(self) -> Result['PurchaseOrder', str]:
        if self.status != POStatus.DRAFT:
            return Result.fail(f"Cannot issue PO in state {self.status}")
        
        if not self.lines:
            return Result.fail("Cannot issue empty PO")

        self.status = POStatus.ISSUED
        return Result.ok(self)
