Phase 1: Architecture & Design (Status: In Progress)
✅ Completed / Decided
Core Philosophy: "ODL is the Engine, not the Product." No direct user access to ODL.

Technology Stack:

Controller: OpenDaylight Titanium (Java 21, Custom Karaf Build).

Backend: Microservices (Go/Python) handling logic, validation, and RBAC.

Frontend: Custom SPA (React/Angular) talking only to the Backend/API Gateway.

Database: PostgreSQL (Config/Inventory) + InfluxDB/Prometheus (Telemetry).

Repository Structure: Monorepo established with clear separation (docs, schemas, backend, odl).

Component Design:

Orchestrator: Defined the "Template -> Translate -> Validate -> Push" pipeline.

Southbound: Defined "Mount Point" strategy for SONiC (gNMI) and OEM (NETCONF).

Data Lifecycle:

Configuration: Defined the State Machine (DRAFT → PENDING → SYNCED).

Telemetry: Defined the "Fast Path" (Switch → ODL → Kafka → InfluxDB) to bypass MD-SAL overhead.

📝 In Draft / To-Do (Immediate)
Database Schema: Need to define the SQL tables for devices, tenants, and intent_history.

API Contracts: Need to write the OpenAPI (Swagger) spec for the communication between UI and Backend.

Southbound Decision Record (ADR): Need to formally document exactly how we handle SONiC gNMI connection parameters.

Phase 2: Implementation (Status: Not Started)
⏳ Pending Actions
Lab Setup:

Initialize Git Repository.

Set up Linux VM with Java 21 & Maven.

ODL Build:

Generate the Custom Karaf Distribution using the pom.xml we discussed.

Configure netconf and restconf ports.

Backend Skeleton:

Create the Go/Python project structure.

Connect to PostgreSQL.
