AERP v3.0: The "Odoo AI" Protocol
Vision: An AI-Native, Event-Sourced ERP Kernel for SMBs. Architecture: Hexagonal (Ports & Adapters) + Event Sourcing.

1. The Core Philosophy (First Principles)
We are not building a monolithic application. We are building a Business Operating System that is:

Immutable: The database is a log of what happened (Events), not just what is (State). This allows time-travel debugging and AI simulations.

Hexagonal: The "Business Logic" (Rules) must never know about the "Infrastructure" (Web, DB, UI). This allows us to scale from SQLite to PostgreSQL without rewriting logic.

AI-Configurable: The system exposes its own "Meta-Schema" via API, allowing an AI Agent to inspect, extend, and configure the ERP dynamically.

2. Architecture: The "Onion" Model

Shutterstock
A. The Core (The Domain)
Location: /core and /modules/*/domain

Constraint: Pure Python. Zero dependencies (No SQL, No HTTP, No UI).

Content: Pydantic Models, Business Rules, Math.

Example: calculate_moving_average(history: List[Cost]) -> Decimal

B. The Application Layer (The Orchestrator)
Location: /modules/*/service

Role: Connects the Core to the World. Handles the flow.

Content: "Receive Request" -> "Load Event History" -> "Apply Business Rule" -> "Save New Event".

C. The Infrastructure Layer (The Adapters)
Location: /infrastructure

Role: The dirty work.

Content:

Persistence: SQLite adapters (initially), upgradable to Postgres.

Web: FastAPI routers.

Bus: Event Bus implementation.

3. The "Event Sourcing" Engine
Unlike Odoo (which updates rows), AERP appends events.

The Flow:

Command: User clicks "Receive Goods".

Event: System writes StockReceived(sku='A', qty=10) to the Event Ledger.

Projection: The system updates a read-optimized table (current_stock) for fast UI queries.

Why this matters for "Odoo AI":

Audit: Infinite undo/redo.

AI Simulation: An AI can fork the Event Log, replay it with different parameters ("What if we ordered 2 days earlier?"), and find optimizations.

4. The Scalability Protocol
To ensure this works for SMBs (not just one user):

Multi-Tenancy Ready: All Events must carry a tenant_id field.

Async by Default: The API must use async/await to handle concurrent users.

API-First: The UI is just a client. If the UI is slow, the Core is fine.

5. The "Meta" Interface (For AI Agents)
To enable "AI Configuration," the system must describe itself.

Endpoint: GET /system/capabilities

Response: JSON Schema describing every installed module, its events, and its commands.

Usage: When you ask an AI to "Add a discount feature," it queries this endpoint to understand where to inject the logic.