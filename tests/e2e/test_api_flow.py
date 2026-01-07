import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from erp_kernel.infrastructure.web.main import app
from erp_kernel.infrastructure.persistence.database import Base, EventModel
from erp_kernel.infrastructure.web.routers.inventory import get_db
# We need to override the dependency to use a test DB

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestE2EAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        # Dispose engine to release lock
        engine.dispose()
        import os
        if os.path.exists("./test_api.db"):
            try:
                os.remove("./test_api.db")
            except PermissionError:
                pass # Ignore if still locked, test passed anyway

    def test_a_handshake_capabilities(self):
        """Test A (The Handshake): Verify AI discovery endpoint."""
        response = self.client.get("/system/capabilities")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("inventory", data["modules"])
        
        # Check tool def
        tool = next((t for t in data["tools"] if t["name"] == "receive_goods"), None)
        self.assertIsNotNone(tool, "receive_goods tool definition missing")

    def test_b_transaction_flow(self):
        """Test B (The Transaction): Full Write Flow."""
        payload = {
            "sku": "E2E-TEST-01", 
            "qty": 50, 
            "bin_location": "Z99",
            "tenant_id": "e2e_tester"
        }
        
        response = self.client.post("/inventory/receive", json=payload)
        
        # Assert Status
        self.assertEqual(response.status_code, 200, f"Request failed: {response.text}")
        
        # Assert Response
        json_resp = response.json()
        self.assertEqual(json_resp["status"], "success")
        self.assertEqual(json_resp["data"]["sku"], "E2E-TEST-01")
        self.assertEqual(json_resp["data"]["qty"], 50)

        # Assert Data Persistence logic (checking side effect)
        # Using a fresh db session to check state
        db = TestingSessionLocal()
        event = db.query(EventModel).filter(EventModel.tenant_id == "e2e_tester").first()
        self.assertIsNotNone(event, "Event was not persisted to DB!")
        db.close()

if __name__ == '__main__':
    unittest.main()
