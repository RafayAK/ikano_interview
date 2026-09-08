# backend

FastAPI + SQLAlchemy (async) + Postgres API for the Ikano onboarding sample.
See the [root README](../README.md) for the system-level architecture, demo
scenarios, and assumptions — this file covers running and testing the backend
specifically.

## Setup

Prerequisites: Python 3.12+, [uv](https://docs.astral.sh/uv/), Docker.

```bash
cd backend                # from the repository root
uv sync
docker compose -f ../compose.yaml up --wait db  # only Postgres
uv run uvicorn app.main:app --reload
```

For the full Docker stack or combined local API/UI development, use the
[root Makefile commands](../README.md#quick-start): `make up` or
`make install`, `make db-up`, and `make dev` from the repository root.

Tables are created automatically on startup — no manual migration step needed
for local dev (see [Assumptions](../README.md#assumptions) for why). Swagger
UI is at **http://localhost:8000/docs**.

## Running tests

```bash
uv run pytest
```

No manual database setup needed: [testcontainers](https://testcontainers-python.readthedocs.io/)
spins up its own disposable Postgres container automatically (session-scoped —
one container for the whole run), independent of the `docker compose` database
used for manual/local exploration. Each test runs inside a transaction that's
rolled back afterwards, so tests never see each other's data — requires Docker
running, nothing else.

## Project layout

```
app/
├── main.py         FastAPI app, middleware, lifespan (creates tables on startup)
├── config.py       pydantic-settings (database URL, CORS origins, cookie/log settings)
├── domain/         enums.py (Country, CustomerType, ApplicationStatus, Decision, StepStatus)
│                   errors.py (every domain-specific failure mode)
├── flows/          FlowDefinition/StepDefinition (frozen dataclasses)
│                   one file per country with its flows as data
│                   registry.py — (Country, CustomerType) → FlowDefinition
├── db/             SQLAlchemy models: OnboardingApplication, StepState,
│                   IntegrationResult, AuditEvent
├── integrations/   one file per mock check (identity, registry, sanctions,
│                   credit, bank_account) — typed Protocol + deterministic Mock*Client
├── decisioning/    DecisionEngine — integration outcomes → final decision.
│                   Zero DB dependency, fully unit-testable in isolation
├── schemas/        Pydantic models; steps.py's per-(country, customer_type,
│                   step_id) input-schema registry
├── services/       onboarding.py (create/get/submit/audit-events/resume)
│                   step_processing.py (the step-completion orchestrator)
└── api/            thin routes — translate domain errors to HTTP status codes

tests/
├── conftest.py     testcontainers + per-test transaction-rollback fixtures
├── test_flows.py, test_integrations.py, test_decisioning.py
└── test_api.py, test_step_lifecycle.py, test_resume.py   full HTTP-level tests
```

## Configuration

All settings are in `app/config.py` (`pydantic-settings`), overridable via
`APP_`-prefixed environment variables or a `.env` file, e.g. `APP_DATABASE_URL`,
`APP_CORS_ALLOW_ORIGINS`, `APP_LOG_LEVEL`.
