from fastapi import FastAPI
from contextlib import asynccontextmanager
from erp_kernel.infrastructure.persistence.database import init_db
from erp_kernel.infrastructure.web.routers import inventory, system, purchasing
from erp_kernel.modules.inventory.handlers import handle_po_issued
from erp_kernel.modules.purchasing.domain.models import POIssued

# Minimal Event Bus Registry (In-Memory for now)
# Ideally this is in infrastructure/event_bus
HANDLERS = {
    "POIssued": [handle_po_issued]
}

# We need a way to hook this into the bus used by Purchasing Router.
# Currently Purchasing uses a fresh SimpleBus().
# We need to share the bus or make the subscription implicit via an Event Mediator.
# For this MVP phase, let's patch the persistence logic to run handlers.

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB exists
    init_db()
    
    # We can't easily injection-subscribe without a global bus.
    # But since we built the routers to instantiate their own bus, 
    # we need to make sure the bus they use (e.g. SqliteEventStore) 
    # triggers these handlers.
    
    # TEMPORARY: We will MonkeyPatch the EventBus in the routers to use a SharedBus 
    # that has this subscription.
    
    yield
    # Shutdown

app = FastAPI(
    title="AERP Kernel ('Odoo AI')",
    description="Event-Sourced ERP Kernel with AI Interface",
    version="3.0.0",
    lifespan=lifespan
)

app.include_router(inventory.router)
app.include_router(purchasing.router)
app.include_router(system.router)

@app.get("/")
def health_check():
    return {"status": "running", "kernel": "hexagonal"}
