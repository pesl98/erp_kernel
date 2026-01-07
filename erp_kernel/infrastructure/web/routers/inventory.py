from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from erp_kernel.core.result import Result
from erp_kernel.infrastructure.persistence.database import SessionLocal
from erp_kernel.infrastructure.persistence.adapters import SqliteStockRepository, SqliteEventStore
from erp_kernel.modules.inventory.service import InventoryService, ReceiveGoodsCommand
from erp_kernel.core.ports import EventBus

# Note: In a real app, DI would be cleaner (e.g., using fast-depends)
# For now, we manually wire the dependencies.

router = APIRouter(prefix="/inventory", tags=["inventory"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mock Event Bus for now (until we add a real persistent bus implementation)
class SimpleEventBus(EventBus):
    async def publish(self, events): pass
    def subscribe(self, event_type, handler): pass

# Request DTO
class ReceiveGoodsRequest(BaseModel):
    sku: str
    qty: int
    bin_location: str
    tenant_id: str

@router.post("/receive")
async def receive_goods(req: ReceiveGoodsRequest, db: Session = Depends(get_db)):
    # 1. Wire Adapters
    # 1. Wire Adapters
    repo = SqliteStockRepository(db)
    
    # 2026-01-07: Use Real Event Persistence for E2E tests to pass
    # In production, this might publish to a message queue, but here we just write to DB.
    # We construct a simple adapter that uses the same DB session.
    class PersistentEventBus(EventBus):
        def __init__(self, db_session):
            self.store = SqliteEventStore(db_session)
        async def publish(self, events):
            await self.store.save(events)
        def subscribe(self, event_type, handler): pass

    bus = PersistentEventBus(db)
    service = InventoryService(repository=repo, event_bus=bus)
    
    # 2. Convert to Command
    cmd = ReceiveGoodsCommand(
        sku=req.sku,
        qty=req.qty,
        bin_location=req.bin_location,
        tenant_id=req.tenant_id
    )
    
    # 3. Execute Service
    result = await service.receive_goods(cmd)
    
    # 4. Unwrap Result
    if result.is_success():
        return {"status": "success", "data": result.value.model_dump()}
    else:
        raise HTTPException(status_code=400, detail=str(result.error))
