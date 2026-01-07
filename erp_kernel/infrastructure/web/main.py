from fastapi import FastAPI
from contextlib import asynccontextmanager
from erp_kernel.infrastructure.persistence.database import init_db
from erp_kernel.infrastructure.web.routers import inventory, system

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB exists
    init_db()
    yield
    # Shutdown

app = FastAPI(
    title="AERP Kernel ('Odoo AI')",
    description="Event-Sourced ERP Kernel with AI Interface",
    version="3.0.0",
    lifespan=lifespan
)

app.include_router(inventory.router)
app.include_router(system.router)

@app.get("/")
def health_check():
    return {"status": "running", "kernel": "hexagonal"}
