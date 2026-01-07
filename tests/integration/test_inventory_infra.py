import unittest
import asyncio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from erp_kernel.infrastructure.persistence.database import Base, EventModel, StockModel
from erp_kernel.infrastructure.persistence.adapters import SqliteStockRepository, SqliteEventStore
from erp_kernel.modules.inventory.service import InventoryService, ReceiveGoodsCommand
from erp_kernel.core.ports import EventBus
from erp_kernel.core.base_event import BaseEvent
from typing import List, Callable, Awaitable

# --- Mock Event Bus (Infrastructure doesn't include a real bus yet) ---
class MockEventBus(EventBus):
    def __init__(self, event_store):
        self.event_store = event_store

    async def publish(self, events: List[BaseEvent]) -> None:
        # In a real app, the bus might persist events asynchronously.
        # Here we manually ensure they hit the store for the test assertion.
        await self.event_store.save(events)

    def subscribe(self, event_type: str, handler: Callable[[BaseEvent], Awaitable[None]]) -> None:
        pass

# --- Integration Test ---
class TestInventoryInfrastructure(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        # 1. Setup Test DB (:memory: for isolation and speed)
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    async def test_full_infrastructure_flow(self):
        # 2. Arrange: Wiring the Adapter Graph
        repo = SqliteStockRepository(self.session)
        event_store = SqliteEventStore(self.session)
        
        # We hook the store into the bus mock so events are persisted
        bus = MockEventBus(event_store) 
        
        service = InventoryService(repository=repo, event_bus=bus)

        cmd = ReceiveGoodsCommand(
            sku="TEST_PRODUCT_001",
            qty=50,
            bin_location="Z-99",
            tenant_id="integration_tenant"
        )

        # 3. Act
        result = await service.receive_goods(cmd)

        # 4. Assert
        self.assertTrue(result.is_success())

        # Assert 1 (State): Query the stock table (Projection)
        stock_record = self.session.query(StockModel).filter(StockModel.sku == "TEST_PRODUCT_001").first()
        self.assertIsNotNone(stock_record)
        self.assertEqual(stock_record.qty, 50)
        self.assertEqual(stock_record.bin_location, "Z-99")

        # Assert 2 (Log): Query the events table (Source of Truth)
        event_record = self.session.query(EventModel).filter(EventModel.tenant_id == "integration_tenant").first()
        self.assertIsNotNone(event_record, "CRITICAL: No event persisted to the Ledger!")
        self.assertEqual(event_record.event_type, "StockReceived")
        
        # Verify Payload Integrity
        import json
        payload = json.loads(event_record.payload)
        self.assertEqual(payload['sku'], "TEST_PRODUCT_001")
        self.assertEqual(payload['qty_added'], 50)

if __name__ == '__main__':
    unittest.main()
