import json
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert

from erp_kernel.core.base_event import BaseEvent
from erp_kernel.core.ports import EventStore
from erp_kernel.modules.inventory.domain.models import StockItem
from erp_kernel.modules.inventory.ports import StockRepository
from erp_kernel.infrastructure.persistence.database import EventModel, StockModel, ExpectedInboundModel, SessionLocal

# --- Event Store Adapter ---

class SqliteEventStore(EventStore):
    def __init__(self, db: Session):
        self.db = db

    async def save(self, events: List[BaseEvent]) -> None:
        """Serialize and save events to SQLite."""
        for event in events:
            db_event = EventModel(
                event_id=str(event.event_id),
                tenant_id=event.tenant_id,
                event_type=event.event_type,
                payload=event.to_json(),
                occurred_at=event.timestamp,
                version=event.version
            )
            self.db.add(db_event)
        self.db.commit()

    async def load_stream(self, stream_id: UUID) -> List[BaseEvent]:
        # Not yet strictly required for the current flow, but required by interface.
        # Implementation left simple for now.
        return []

# --- Stock Repository Adapter ---

from erp_kernel.modules.inventory.ports import InboundOrderRepository

class SqliteInboundOrderRepository(InboundOrderRepository):
    def __init__(self, db: Session):
        self.db = db
        
    async def get_expectation(self, po_id: str, sku: str) -> Optional[dict]:
        record = self.db.query(ExpectedInboundModel).filter(
            ExpectedInboundModel.po_id == po_id,
            ExpectedInboundModel.sku == sku
        ).first()
        
        if record:
            return {'qty_ordered': record.qty_ordered, 'qty_received': record.qty_received}
        return None

    async def update_received(self, po_id: str, sku: str, qty: int) -> None:
        record = self.db.query(ExpectedInboundModel).filter(
            ExpectedInboundModel.po_id == po_id,
            ExpectedInboundModel.sku == sku
        ).first()
        if record:
            record.qty_received += qty
            self.db.commit()

class SqliteStockRepository(StockRepository):
    def __init__(self, db: Session):
        self.db = db

    async def get_by_sku(self, sku: str) -> Optional[StockItem]:
        """Load SQL Persistence Model -> Map to Domain Entity."""
        stock_record = self.db.query(StockModel).filter(StockModel.sku == sku).first()
        
        if not stock_record:
            return None
            
        # Mapping: Model -> Entity
        return StockItem(
            sku=stock_record.sku,
            qty=stock_record.qty,
            bin_location=stock_record.bin_location,
            last_updated=stock_record.last_updated
        )

    async def save(self, item: StockItem) -> None:
        """Map Domain Entity -> SQL Persistence Model -> Save."""
        
        # Check if exists
        existing = self.db.query(StockModel).filter(StockModel.sku == item.sku).first()
        
        if existing:
            existing.qty = item.qty
            existing.bin_location = item.bin_location
            existing.last_updated = item.last_updated
        else:
            new_record = StockModel(
                sku=item.sku,
                qty=item.qty,
                bin_location=item.bin_location,
                last_updated=item.last_updated
            )
            self.db.add(new_record)
        
        self.db.commit()
