from datetime import datetime
from pydantic import BaseModel, Field
from erp_kernel.core.result import Result

class StockItem(BaseModel):
    """
    Domain Entity for Inventory Stock.
    Pure logic: maintains invariants (no negative stock).
    """
    sku: str
    qty: int = 0
    bin_location: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    def add_stock(self, qty: int) -> Result['StockItem', str]:
        if qty < 0:
            return Result.fail("Cannot add negative quantity")
        
        self.qty += qty
        self.last_updated = datetime.utcnow()
        return Result.ok(self)

    def remove_stock(self, qty: int) -> Result['StockItem', str]:
        if qty < 0:
            return Result.fail("Cannot remove negative quantity")
        
        if self.qty < qty:
            return Result.fail(f"Insufficient stock. Current: {self.qty}, Requested: {qty}")
        
        self.qty -= qty
        self.last_updated = datetime.utcnow()
        return Result.ok(self)
