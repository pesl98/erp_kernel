# AERP Kernel (The "Odoo AI" Protocol)

**An Event-Sourced, AI-Native ERP Foundation for Capital Optimization.**

> **Status:** Gold Master (Kernel Verified)
> **Architecture:** Hexagonal (Ports & Adapters)
> **Focus:** Data Durability, Capital Safety, and AI Interoperability.

---

## 1. The Vision
Most ERPs are monolithic "CRUD" apps that simply update the current state of a database. If a record changes, history is lost.
**AERP** is built on **First Principles** to solve this:
* **Immutable Ledger:** We never "update" a record. We append an Event. The database is just a "Flight Recorder" of business history.
* **Capital Safety:** Strict "Three-Way Matching" logic prevents ghost inventory and capital leakage.
* **AI-Native:** The system exposes a `GET /system/capabilities` meta-layer, allowing external AI Agents to "learn" the ERP dynamically without hardcoded integrations.

## 2. Architecture (The "Onion")
The system strictly enforces **Hexagonal Architecture** to decouple Business Logic from Infrastructure.

```text
/erp_kernel
├── /core               # Shared Kernel (BaseEvent, Result Monad)
├── /modules            # Pure Domain Logic (Inventory, Purchasing)
│   ├── domain/         # Entities & Business Rules (No SQL, No HTTP)
│   ├── ports/          # Interfaces (Repository Protocols)
│   └── service/        # Orchestration (The "Brain")
└── /infrastructure     # Adapters (The "Body")
    ├── persistence/    # SQLite / SQLAlchemy
    ├── web/            # FastAPI Routers
    └── ui/             # Streamlit Dashboard
3. Key Capabilities
A. The "Three-Way Match" (Fraud Protection) Unlike simple inventory scripts, AERP separates Purchasing from Receiving.

Rule: You cannot receive goods without a valid, issued Purchase Order (PO).

Mechanism: The Inventory module listens to POIssued events and builds a local "Expectation" table.

Security: Receiving against a fake PO ID returns 400 Bad Request (Verified by E2E Tests).

B. Event Sourcing (The Flight Recorder) Every action is serialized as a Pydantic Event and written to the events table before side effects occur.

Auditability: Complete replay capability.

Resilience: If the server crashes, the State can be rebuilt from the Event Log.

C. The AI Socket Designed to be operated by Humans or AI Agents.

Human: Via Streamlit UI.

Agent: Via Semantic API (/system/capabilities).

4. Getting Started
Prerequisites
Python 3.10+

pip

Installation
Bash

git clone [https://github.com/your-username/erp_kernel.git](https://github.com/your-username/erp_kernel.git)
cd erp_kernel
pip install -r requirements.txt
Running the Kernel (API)
The "Brain" runs on FastAPI (Port 8000).

Bash

uvicorn infrastructure.web.main:app --reload
Running the Dashboard (UI)
The "Face" runs on Streamlit (Port 8501).

Bash

streamlit run infrastructure/ui/app.py
5. Testing & Verification
We use a Testing Pyramid strategy:

Unit Tests: Verify Domain Logic in isolation (In-Memory).

Integration Tests: Verify SQLite Adapters.

E2E Tests: Verify the full HTTP Lifecycle and Fraud Scenarios.

Bash

# Run the full suite
pytest tests/
6. Project Status
[x] Phase 1: Core Event Bus & Persistence (Completed)

[x] Phase 2: Inventory Module (Completed)

[x] Phase 3: Purchasing Module (Completed)

[x] Phase 4: The "Three-Way Match" Integration (Completed & Verified)

[ ] Phase 5: User Interface (Streamlit) - In Progress

Built with First Principles in The Netherlands.
