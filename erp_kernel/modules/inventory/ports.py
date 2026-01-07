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
