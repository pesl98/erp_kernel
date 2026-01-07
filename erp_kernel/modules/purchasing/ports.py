from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from erp_kernel.modules.purchasing.domain.models import PurchaseOrder

class PurchaseRepository(ABC):
    @abstractmethod
    async def get_by_id(self, po_id: UUID) -> Optional[PurchaseOrder]:
        pass

    @abstractmethod
    async def save(self, po: PurchaseOrder) -> None:
        pass
