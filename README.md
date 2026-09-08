# Ikano Onboarding - Sample App

A production-minded sample application demonstrating a multi-country, multi-segment customer onboarding flow across Sweden, Spain, and Poland for both private individuals and businesses.

### Key Highlights
- **Deterministic Decisioning Engine**: Evaluates verification outcomes into `approved`, `manual_review`, or `rejected`.
- **Mocked External Checks**: Identity (KYC), Business Registry (KYB), PEP/Sanctions, Credit/Affordability, and Bank Account (IBAN).
- **Data-Driven Flow Engine**: Configuration-driven step transitions with zero country-specific `if/else` conditionals.
- **Unified Deployment Architecture**: Single multi-stage container serving the Astro static frontend and FastAPI backend on AWS ECS.

---

## Project Structure

```
├── compose.yaml          # Postgres + API + UI with live reload
├── Makefile              # Development, test, and deployment automation
├── backend/              # FastAPI + SQLAlchemy + PostgreSQL API
│   ├── app/
│   │   ├── domain/       # Enums and domain-specific errors
│   │   ├── flows/        # Six onboarding flows defined as data
│   │   ├── db/           # SQLAlchemy models and persistence
│   │   ├── integrations/ # Deterministic mock external check clients
│   │   ├── decisioning/  # Decision engine (approved / manual_review / rejected)
│   │   ├── schemas/      # Pydantic request/response and step models
│   │   ├── services/     # Step orchestrator, submission, and resume services
│   │   └── api/          # FastAPI routes and controllers
│   ├── tests/            # pytest + testcontainers suite
│   └── README.md         # Backend setup, tests, and details
├── frontend/             # Astro + Tailwind UI with schema-driven forms
│   └── README.md         # Frontend setup and architecture
├── terraform/            # AWS ECS + RDS + ALB infrastructure configuration
└── README.md             # Project overview and architecture guide
```

See [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md) for component-specific guides.

---

## Quick Start

### 1. Run Everything in Docker (Recommended)

**Prerequisites**: Docker with Compose v2 and GNU Make.

```bash
make up                  # Build images, start services, and wait for health checks
make logs                # Follow service logs (Ctrl-C exits log stream)
make ps                  # Inspect service status
make down                # Stop containers (database data is preserved)
```

Without Make:
- Start: `docker compose up --build --wait`
- Logs: `docker compose logs -f`
- Stop: `docker compose down`

**Service Endpoints**:
- **Web UI**: http://localhost:4321
- **Swagger Docs**: http://localhost:8000/docs
- **PostgreSQL**: `localhost:5432`

---

### 2. Run Locally

**Prerequisites**:
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Node.js 22.12+ and npm
- Docker 

```bash
make install             # Install Python (uv) and Node (npm) dependencies
make db-up               # Start local PostgreSQL container
make dev                 # Start API (:8000) and Astro UI (:4321) with reload
```

To run against an external PostgreSQL database:
```bash
export APP_DATABASE_URL='postgresql+asyncpg://postgres:postgres@localhost:5432/ikano_onboarding'
make install
make dev
```

---

### 3. Configuration & Environment Variables

- **Backend Configuration**:
  - Configured via `APP_*` environment variables or `backend/.env`.
- **Frontend Configuration**:
  - Configured via `PUBLIC_API_BASE_URL` or `frontend/.env`.

---

### 4. Convenience Make Commands

| Command | Description |
|---|---|
| `make help` | Show all available Make commands |
| `make up` / `make down` | Start or stop the complete Docker stack |
| `make logs SERVICE=backend` | Follow logs for a designated service |
| `make ps` | Display Docker service status |
| `make db-up` / `make db-down` | Start or stop the local PostgreSQL container |
| `make install` | Install dependencies from lockfiles via `uv` and `npm` |
| `make dev` | Start backend and frontend locally with reload |
| `make backend` / `make frontend` | Run services individually |
| `make frontend-logs` / `make frontend-stop` | Follow logs or stop background Astro dev server |
| `make test` | Run backend pytest suite |
| `make build` | Run frontend production build |

---

## Running Tests

Run backend tests and frontend build validation:

```bash
make test                               # Run the full backend pytest suite
make test ARGS="-q tests/test_flows.py" # Run a specific test module or pytest flags
make build                              # Validate frontend static production build
```

---

## Demo Scenarios

Every mock integration is **deterministic**, ensuring all scenarios are reproducible and testable via input suffixes.

| Mock Integration | Input Trigger | Ends with `000` | Ends with `999` | Ends with `888` | Ends with `666` | Otherwise |
|---|---|---|---|---|---|---|
| **Identity / KYC** | National ID / Rep ID | `manual_review` | `document_mismatch` | `expired_id` | N/A | `verified` |
| **KYB / Registry** | Org number / NIF / NIP | `dissolved` | `unknown_representative` | `missing_ubo` | N/A | `active_company` |
| **PEP / Sanctions** | National ID / Owner ID | `possible_hit` | N/A | N/A | `confirmed_hit` | `no_hit` |
| **Credit / Affordability** | National ID / Org ID | `low_affordability` | `poor_credit_history` | N/A | N/A | `clean` |
| **Bank Account** | IBAN (last 2 digits) | `unreachable` (`...00`) | `name_mismatch` (`...99`) | N/A | N/A | `iban_verified` |

### End-to-End Private Individual Outcomes

Use matching identifier suffixes for `personal_identity_number`, `dni_or_nie`, or `pesel`:

1. **Approved**:
   - Identifier with a clean suffix (e.g., `199001011234`).
   - Results in clean KYC, credit, and sanctions checks.
2. **Manual Review**:
   - Identifier ending in `000` (e.g., `199001011000`).
   - Identity, sanctions, and credit checks return review-level outcomes simultaneously.
3. **Rejected**:
   - Identifier ending in `999` (e.g., `199001011999`).
   - Identity check fails with `document_mismatch`.

> **Executable Documentation**: See [backend/tests/test_step_lifecycle.py](backend/tests/test_step_lifecycle.py) for complete step-by-step payloads covering all three paths.

---

## Architecture

| Module | Responsibility |
|---|---|
| `app/domain/` | Domain enums (`Country`, `CustomerType`, `ApplicationStatus`, `Decision`, `StepStatus`) and custom domain errors |
| `app/flows/` | `FlowDefinition` and `StepDefinition` dataclasses; flow registry mapping `(Country, CustomerType) -> FlowDefinition` |
| `app/db/` | SQLAlchemy models: `OnboardingApplication`, `StepState`, `IntegrationResult`, and `AuditEvent` |
| `app/integrations/` | External check clients (identity, registry, sanctions, credit, bank) behind typed `Protocol` interfaces |
| `app/decisioning/` | `DecisionEngine`: maps integration outcomes to final decisions and reason codes (pure logic, zero DB dependency) |
| `app/schemas/` | Pydantic request/response models and per-step validation schemas |
| `app/services/` | `onboarding.py` (CRUD/resume) and `step_processing.py` (orchestrator: validate, persist, trigger, advance) |
| `app/api/` | Thin FastAPI route handlers translating domain errors to HTTP responses |
| `frontend/` | Astro + Tailwind UI rendering forms dynamically from backend JSON Schemas |

### Request Lifecycle (Step Completion)

When an applicant submits data for an onboarding step:
1. **Schema Validation**: FastAPI validates the incoming payload against the schema registered for `(country, customer_type, step_id)`.
2. **Transition Validation**: `step_processing.complete_step()` verifies the transition is allowed from the current state.
3. **Answer Persistence**: Form inputs are stored in `StepState.answers`.
4. **Integration Triggering**: The service checks `STEP_INTEGRATIONS` and executes relevant mock clients.
5. **Audit Logging**: Persists `IntegrationResult` and `AuditEvent` records.
6. **Flow Progression**: Updates `current_step` using the flow definition's `next_step()`.
7. **Final Submission**: Calling `PUT .../submit` supplies all persisted `IntegrationResult` records to `DecisionEngine` to produce the final decision.

### Extending to a New Country

Adding a new country requires zero conditional branching:
1. Add the country code to the `Country` enum in `app/domain/enums.py`.
2. Define the country flow in `app/flows/<country>.py`.
3. Register the flow in `FLOW_REGISTRY`.
4. Define step input schemas in `STEP_INPUT_SCHEMAS`.
5. Map triggered external checks in `STEP_INTEGRATIONS`.

---

## Design Choices

- **Flows as Configuration**:
  - Six `FlowDefinition` instances are maintained in a lookup registry rather than branching in code.
- **Deterministic Integration Mocks**:
  - Mocks determine responses based on input suffixes, ensuring predictable demos and deterministic tests.
- **Decoupled Decision Engine**:
  - `DecisionEngine.decide()` accepts a list of `(integration, outcome)` tuples without database models, making it isolated and unit-testable.
- **String Enums over Native Postgres Enums**:
  - Stored as `VARCHAR` (`native_enum=False`) with Pydantic boundary validation to simplify schema migrations.
- **JSONB for Step Answers**:
  - Stored as JSONB per step (`StepState.answers`), avoiding table alterations when form fields change.
- **PII Protection**:
  - Sensitive values are confined to `StepState.answers`.
  - Logs, `AuditEvent`, and `IntegrationResult` record only event types, metadata, and status codes.
- **Structured Tracing & Logs**:
  - Every log entry includes a `request_id` (via `asgi-correlation-id`, preserving AWS ALB `X-Amzn-Trace-Id`) and `application_id`.
- **Opaque Resume Tokens**:
  - Resumption relies on a random token (`secrets.token_urlsafe`) stored with a 30-day expiry.
  - Stored in an `HttpOnly` cookie to prevent JavaScript access.
  - `GET /api/v1/resume` resolves the user's current step without exposing database primary keys.
  - `POST /api/v1/resume/clear` clears the cookie for demo convenience.
- **Schema-Driven UI Rendering**:
  - The Astro frontend generates form controls dynamically from backend JSON Schemas via `GET .../steps/current`.
  - `form-renderer.js` constructs inputs, validation constraints, and nested lists without per-country template branching.

---

## Assumptions

- **Spain and Poland Business Steps**: Split into verification (`..._iban` / `..._bank_validation`) and `review_sign` for clearer UI progress and audit records.
- **Representative Identity Field**: Added `representative_identifier` across authority verification steps so identity mock checks can run.
- **Bank Account Verification Scope**: Configured for Spain and Poland business flows, matching the project brief.
- **Beneficial Owner Sanctions**: Checks the first listed beneficial owner (simplified for mock purposes).
- **Regulatory Rules**: Country-specific checks and fields are demonstration models, not legal advice for Sweden, Spain, or Poland.

---

## AWS Deployment & Infrastructure

The repository provides a single-environment (`dev`) Terraform setup in [terraform/](terraform/) using AWS ECS Fargate, RDS PostgreSQL, and an Application Load Balancer.

### Architecture Overview: Unified Container Strategy

Astro builds into static assets (`HTML`, `CSS`, JavaScript), allowing **FastAPI to serve the static frontend directly**:

1. **Unified Multi-Stage Image ([prod.Dockerfile](prod.Dockerfile))**:
   - **Stage 1 (Node 22)**: Builds the Astro frontend with relative API paths (`PUBLIC_API_BASE_URL=/api/v1`) into `/app/dist`.
   - **Stage 2 (Python 3.12)**: Installs FastAPI dependencies, copies backend code, and mounts `/app/dist` at `/` using Starlette `StaticFiles`.
2. **Same-Origin Benefits**:
   - `/` serves the Astro web app.
   - `/api/v1/*` routes to backend API endpoints.
   - `/health` serves ALB health checks.
   - `/docs` serves OpenAPI documentation.
   - Cookies (`resume_token`) work natively without cross-origin or `SameSite` constraints.
   - Eliminates CORS configurations and secondary target groups.
3. **Local Dev Unchanged**:
   - Local development (`make dev` or `make up`) continues to run Astro on port `4321` with hot-module reloading and proxying to FastAPI on port `8000`.

![AWS ECS Architecture](./AWS-ECS-Fargate-Application-Architecture.png)


---

### Infrastructure Trade-offs

| Dimension | Production Standard | Take-Home Demo Pattern | Rationale |
|---|---|---|---|
| **Container Setup** | Separate ECS services for Node and Python | Unified multi-stage container | Halves compute costs; eliminates multi-target ALB routing and CORS complexity. |
| **Compute** | Multi-AZ On-Demand Fargate with auto-scaling | Single Fargate Spot task (0.25 vCPU, 512 MiB) | ~70% cost reduction; ideal for temporary review environments. |
| **Database** | Multi-AZ Aurora Serverless v2 with backups | Single-AZ RDS PostgreSQL 18 (`db.t4g.micro`, 20GB gp3) | AWS Free Tier eligible; automated password generation. |
| **Teardown** | Deletion protection enabled, final snapshots | Deletion protection disabled, snapshots skipped | Frictionless teardown via `make app-destroy` without manual unlocks. |
| **Access** | Custom domain with Route53 and ACM SSL | ALB Port 80 direct HTTP forward | Reviewers can test immediately via ALB DNS without domain configuration delays. |
| **Egress** | Dedicated NAT Gateway per AZ | Single shared NAT Gateway | Balances private subnet security with reduced NAT charges. |
| **State Storage** | S3 backend with DynamoDB locking | Local state by default (S3 bootstrap module included) | Immediate deployment without pre-existing AWS bucket prerequisites. |

> **Note on Remote State**: A production remote state module is included in `terraform/bootstrap/`. For the now, local state is default so that `make deploy` runs cleanly without manual setup.

---

### Deployment Guide

#### Prerequisites
- AWS CLI configured with active credentials (`aws configure`).
- Docker installed and running.
- Terraform v1.5+ installed.

#### Two-Stage Deployment Flow

The deployment is split into two phases to avoid ECS pull failures:
1. **ECR Repository Creation** (`terraform/global/ecr`)
2. **Container Build and Push** (`prod.Dockerfile` pushed to ECR)
3. **Application Stack Provisioning** (`terraform/live/dev`: VPC, RDS, ALB, ECS)

#### Option A: Automated One-Shot Deployment

```bash
make deploy
```
*Sequentially executes ECR creation, image build/push, and application deployment.*

#### Option B: Step-by-Step Deployment

```bash
# 1. Provision ECR repository
make ecr-init
make ecr-apply

# 2. Build and push production image
make build-push

# 3. Provision infrastructure (VPC, RDS, ALB, ECS)
make app-init
make app-apply
```

#### Accessing the Deployed App

Retrieve output endpoints:
```bash
make app-output
```

Open the `alb_url` in your browser:
```
http://ikano-dev-alb-<hash>.elb.amazonaws.com
```
- **Web UI**: Customer onboarding experience at `/`
- **Swagger Docs**: Interactive API documentation at `/docs`
- **Health Check**: ALB endpoint at `/health`

---

### Teardown & Resource Cleanup

To avoid recurring AWS charges, tear down provisioned resources:

```bash
# Tear down ECS, ALB, RDS, and VPC
make app-destroy

# Or tear down everything including the ECR repository
make destroy-all
```

---

