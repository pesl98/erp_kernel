from uuid import UUID
from datetime import datetime
from pydantic import Field
from erp_kernel.core.base_event import BaseEvent

class StockReceived(BaseEvent):
    """Event emitted when stock is added to inventory."""
    event_type: str = "StockReceived"
    sku: str
    qty_added: int
    new_quantity: int
    location: str
