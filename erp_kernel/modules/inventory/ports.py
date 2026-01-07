from abc import ABC, abstractmethod
from typing import Optional
from erp_kernel.modules.inventory.domain.models import StockItem

class StockRepository(ABC):
    """
    Port for accessing StockItem persistence.
    """
    @abstractmethod
    async def get_by_sku(self, sku: str) -> Optional[StockItem]:
        """Retrieve a StockItem by its SKU."""
        pass

    @abstractmethod
    async def save(self, item: StockItem) -> None:
        """Persist a StockItem (upsert)."""
        pass

class InboundOrderRepository(ABC):
    """
    Port for accessing Expected Inbound Orders.
    This separates the 'Read Expectation' concern from the 'Write Stock' concern.
    """
    @abstractmethod
    async def get_expectation(self, po_id: str, sku: str) -> Optional[dict]:
        """
        Returns expectation details if found. 
        Return Dict for simplicity in MVP: {'qty_ordered': int, 'qty_received': int}
        """
        pass
    
    @abstractmethod
    async def update_received(self, po_id: str, sku: str, qty: int) -> None:
        """Updates the received quantity."""
        pass
