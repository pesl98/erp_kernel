import unittest
import asyncio
from typing import List, Callable, Awaitable, Optional, Dict
from uuid import UUID

from erp_kernel.core.result import Result
from erp_kernel.core.base_event import BaseEvent
from erp_kernel.core.ports import EventBus
from erp_kernel.modules.inventory.domain.models import StockItem
from erp_kernel.modules.inventory.domain.events import StockReceived
from erp_kernel.modules.inventory.ports import StockRepository
from erp_kernel.modules.inventory.service import InventoryService, ReceiveGoodsCommand

# --- Mocks / In-Memory Adapters ---

class InMemoryStockRepository(StockRepository):
    def __init__(self):
        self._store: Dict[str, StockItem] = {}

    async def get_by_sku(self, sku: str) -> Optional[StockItem]:
        # Return a copy to simulate DB boundary
        if sku in self._store:
            return self._store[sku].model_copy()
        return None

    async def save(self, item: StockItem) -> None:
        self._store[item.sku] = item.model_copy()

class MockEventBus(EventBus):
    def __init__(self):
        self.published_events: List[BaseEvent] = []

    async def publish(self, events: List[BaseEvent]) -> None:
        self.published_events.extend(events)

    def subscribe(self, event_type: str, handler: Callable[[BaseEvent], Awaitable[None]]) -> None:
        pass

# --- Test Case ---

class TestInventoryCore(unittest.IsolatedAsyncioTestCase):
    
    async def test_receive_goods_flow(self):
        # 1. Setup
        repo = InMemoryStockRepository()
        bus = MockEventBus()
        service = InventoryService(repository=repo, event_bus=bus)
        
        command = ReceiveGoodsCommand(
            sku="TABLE_LEG_001",
            qty=10,
            bin_location="A-01-01",
            tenant_id="test_tenant"
        )

        # 2. Action
        result = await service.receive_goods(command)

        # 3. Assertions
        
        # Assert 1: Result is Success
        self.assertTrue(result.is_success(), f"Service failed: {result._value if result.is_failure() else ''}")
        self.assertEqual(result.value.qty, 10)
        
        # Assert 2: Repo contains Qty 10
        stored_item = await repo.get_by_sku("TABLE_LEG_001")
        self.assertIsNotNone(stored_item)
        self.assertEqual(stored_item.qty, 10)
        self.assertEqual(stored_item.bin_location, "A-01-01")

        # Assert 3: Event emitted
        self.assertEqual(len(bus.published_events), 1)
        event = bus.published_events[0]
        self.assertIsInstance(event, StockReceived)
        self.assertEqual(event.qty_added, 10)
        self.assertEqual(event.sku, "TABLE_LEG_001")
        self.assertEqual(event.tenant_id, "test_tenant")

if __name__ == '__main__':
    unittest.main()
