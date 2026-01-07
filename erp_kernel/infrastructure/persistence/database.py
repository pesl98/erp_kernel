from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# 1. Setup SQLite Engine
DATABASE_URL = "sqlite:///./aerp.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # Needed for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 2. Define EventModel
class EventModel(Base):
    __tablename__ = "events"

    event_id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    event_type = Column(String, index=True, nullable=False)
    payload = Column(Text, nullable=False)  # JSON string
    occurred_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)

# 3. Define StockModel (Projections)
class StockModel(Base):
    __tablename__ = "stock_items"

    sku = Column(String, primary_key=True, index=True)
    qty = Column(Integer, default=0)
    bin_location = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)

class ExpectedInboundModel(Base):
    __tablename__ = "expected_inbound"

    # Composite Key ideally, but using ID for simplicity in this MVP
    id = Column(Integer, primary_key=True, autoincrement=True) 
    po_id = Column(String, index=True, nullable=False)
    sku = Column(String, index=True, nullable=False)
    qty_ordered = Column(Integer, nullable=False)
    qty_received = Column(Integer, default=0)
    tenant_id = Column(String, index=True)

def init_db():
    Base.metadata.create_all(bind=engine)
