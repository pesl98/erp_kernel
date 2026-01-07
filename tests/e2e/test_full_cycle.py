import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from erp_kernel.infrastructure.web.main import app
from erp_kernel.infrastructure.persistence.database import Base
from erp_kernel.infrastructure.web.routers.inventory import get_db as get_inventory_db

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_full_cycle.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override dependency in all routers (main app uses global override mostly, but specifically routers might need it)
# app.dependency_overrides[get_db] = override_get_db # Removed as clean import failed and it's redundant if we target routers
app.dependency_overrides[get_inventory_db] = override_get_db

class TestFullCycle(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        
        # MONKEY PATCH: Ensure event handlers write to the Test DB, not Prod DB
        # 1. Patch the Source Definition
        import erp_kernel.infrastructure.persistence.database as db_module
        cls._original_session_local = db_module.SessionLocal
        db_module.SessionLocal = TestingSessionLocal
        
        # 2. Patch the Handlers Module specifically (because it might have already imported it)
        # Force import to ensure we can patch it
        import erp_kernel.modules.inventory.handlers as handlers_module
        handlers_module.SessionLocal = TestingSessionLocal

    @classmethod
    def tearDownClass(cls):
        # Restore Patch
        import erp_kernel.infrastructure.persistence.database as db_module
        db_module.SessionLocal = cls._original_session_local
        
        engine.dispose()
        import os
        if os.path.exists("./test_full_cycle.db"):
            try:
                os.remove("./test_full_cycle.db")
            except: pass

    def test_full_business_cycle(self):
        tenant_id = "cycle_tenant"

        # --- Scenario A: The Happy Path ---
        print("\n--- Running Scenario A: Happy Path ---")
        
        # 1. Create Draft PO
        payload_draft = {
            "vendor": "ACME",
            "lines": [{"sku": "WIDGET-X", "qty": 100, "price": 10.0}],
            "tenant_id": tenant_id
        }
        res_draft = self.client.post("/purchasing/orders", json=payload_draft)
        self.assertEqual(res_draft.status_code, 200)
        po_id = res_draft.json()["po_id"]
        
        # 2. Approve PO (Triggers Event -> Expectation)
        res_issue = self.client.post(f"/purchasing/orders/{po_id}/issue?tenant_id={tenant_id}")
        self.assertEqual(res_issue.status_code, 200)
        
        # 3. Receive Goods (Ref PO)
        payload_receive = {
            "sku": "WIDGET-X",
            "qty": 100,
            "bin_location": "A1",
            "tenant_id": tenant_id,
            "ref_po_id": po_id
        }
        res_recv = self.client.post("/inventory/receive", json=payload_receive)
        self.assertEqual(res_recv.status_code, 200, f"Receipt Failed: {res_recv.text}")
        self.assertEqual(res_recv.json()["data"]["qty"], 100)
        
        print("Scenario A PASSED")

        # --- Scenario B: The Fraud Attempt ---
        print("\n--- Running Scenario B: Fraud Attempt ---")
        payload_fraud = {
            "sku": "GOLD-BAR",
            "qty": 50,
            "bin_location": "X",
            "tenant_id": tenant_id,
            "ref_po_id": "FAKE-PO-999"
        }
        res_fraud = self.client.post("/inventory/receive", json=payload_fraud)
        self.assertEqual(res_fraud.status_code, 400)
        self.assertIn("Unexpected receipt", res_fraud.json()["detail"])
        print("Scenario B PASSED")

        # --- Scenario C: The Over-Delivery ---
        print("\n--- Running Scenario C: Over-Delivery ---")
        # Try to receive MORE against the original legitimate PO (already fully received)
        payload_over = {
            "sku": "WIDGET-X",
            "qty": 50,
            "bin_location": "A1",
            "tenant_id": tenant_id,
            "ref_po_id": po_id
        }
        res_over = self.client.post("/inventory/receive", json=payload_over)
        self.assertEqual(res_over.status_code, 400)
        self.assertIn("Over-receipt", res_over.json()["detail"])
        print("Scenario C PASSED")

if __name__ == '__main__':
    unittest.main()
