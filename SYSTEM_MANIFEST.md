SYSTEM_MANIFEST.md: The "Odoo AI" Protocol
Vision: A scalable, modular ERP kernel built on Event Sourcing. Designed for SMBs, capable of self-configuration via AI.

1. Architectural First Principles
A. The "Event Source" Truth
Most ERPs are "Current State" systems (they store Qty: 10). We are building an "Event State" system.

Rule: The database is a projection, not the source of truth.

Mechanism: Every business action (Create PO, Move Stock) is immutable. It is written to an Event Log first.

Why: This allows AI to "fork" the business state to run simulations ("What if we bought 20% more stock?") without touching production data.

B. The "Hexagonal" Core
We strictly separate the Domain Logic from the Infrastructure.

Inner Circle (Domain): Pure Python logic. No SQL, no HTTP. Just Pydantic models and math.

Outer Circle (Adapters): FastAPI (Web), SQLite (Persistence), Streamlit (UI).

Benefit: We can swap SQLite for Postgres later without rewriting a single line of business logic.

C. The "AI Interface"
The system must expose a GET /meta/capabilities endpoint.

It returns a JSON schema of all active modules and their tools.

This allows an external AI to "learn" the ERP instantly.

2. Directory Structure (The Skeleton)


/erp-kernel
├── /core               # The Nervous System (Event Bus, Base Contracts)
├── /modules            # The Organs (Independent Business Units)
│   ├── /inventory      # Logic for physical goods
│   ├── /purchasing     # Logic for acquisition
│   └── /identity       # Logic for Users/Tenants (Scalability Requirement)
├── /interfaces         # The Gateways
│   ├── /api            # FastAPI (The Brain)
│   └── /ui             # Streamlit (The Face)
└── /infrastructure     # The Plumbing (DB Drivers, File I/O)

3. The "Golden Rules" for Agents
No "God Objects": Do not create a single utils.py. Every function belongs to a specific Domain.

Type-Safety is Law: Use Pydantic V2 for everything. No raw dictionaries.

Test the Contract: Every module must have a test that proves it listens to events.

Operational Durability: Events must be persisted to disk (SQLite) before processing.

4. Phase 1 Execution Plan (The MVP Kernel)
Core: Build the EventBus with persistence.

Module A: Inventory (The Ledger).

Module B: Purchasing (The Trigger).

Integration: Prove that a PO Event triggers an Inventory Ledger entry.