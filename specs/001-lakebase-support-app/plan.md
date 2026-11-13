# Implementation Plan: Lakebase Support App

**Branch**: `001-lakebase-support-app` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-lakebase-support-app/spec.md`

## Summary

Build a small, server-rendered Flask ticketing app backed exclusively by Lakebase
PostgreSQL. Reuse the reference app's compact Flask/templates/database-helper
structure, but replace its static-password secret-URL connection and unrelated
Massive API ingestion with a Databricks Apps Lakebase resource, app identity,
and short-lived OAuth database credentials. Versioned SQL migrations and
idempotent sample seeding establish the ticket schema; users can list tickets,
view messages, create tickets, post messages, and update status.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Flask, psycopg 3, Databricks SDK, Gunicorn,
Flask-WTF, pytest

**Storage**: Lakebase Autoscaling PostgreSQL; no separate operational store

**Testing**: pytest unit tests, Flask test-client workflow tests, and an
integration run against the configured Lakebase database

**Target Platform**: Databricks Apps in the user's Databricks workspace; local
development supported

**Project Type**: Server-rendered internal web application

**Performance Goals**: Meet the spec's under-five-minute ticket workflow;
render the ticket list and selected ticket thread within 2 seconds at p95 for
the expected small bootcamp dataset

**Constraints**: All access requires Databricks app sign-in and app permission.
All signed-in users share the same ticket access and write permissions.
Database credentials are supplied through the Lakebase app resource, not
committed or embedded in URLs. Validate browser form submissions and avoid
logging ticket contents or credentials. Store the Flask/CSRF signing key in a
Databricks secret resource.

**Scale/Scope**: Small internal bootcamp workload; at least three seeded
tickets with at least two messages each, plus user-created records. No separate
frontend service, public API, AI features, or advanced analytics in this phase.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / constraint | Plan response | Gate |
|---|---|---|
| User Value & Ticket Clarity | Keep the UI focused on ticket list, thread, creation, messages, and status. | PASS |
| Data Integrity & Traceability | Enforce relational constraints and field validation; store immutable messages and status-change audit events; use transactions and optimistic concurrency for status updates. | PASS |
| Least-Privilege Security | Require Databricks sign-in/app access, use the app's least-privilege Lakebase resource identity, derive actor identity from trusted platform headers, protect form posts against CSRF, and keep secrets out of source/logs. | PASS |
| Test-First Change Control | Add focused tests for validation, persistence, authorization identity, and stale concurrent updates before implementation changes. | PASS |
| Reliable Operations & Observability | Provide a health endpoint, safe user-facing database errors, and structured server logs without ticket contents or credentials. | PASS |

No constitution violations are required by the proposed design.

## Project Structure

### Documentation (this feature)

```text
specs/001-lakebase-support-app/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── web.md
└── tasks.md
```

### Source Code (repository root)

```text
app.py                    # Flask routes and request/response behavior
ticket_service.py         # Ticket and message operations / validation
lakebase.py               # Lakebase resource authentication and query helpers
templates/                # Server-rendered ticket list and detail/forms
static/                   # Small application stylesheet
db/
└── migrations/           # Ordered SQL schema changes
scripts/
├── migrate.py            # Serialized, versioned schema migration runner
└── seed_sample_data.py   # Idempotent sample-ticket and message seeding
tests/
├── unit/
├── integration/
└── conftest.py
app.yaml                  # Databricks Apps runtime and resource binding
requirements.txt
README.md
```

**Structure Decision**: Use one Flask app with Jinja templates, a focused ticket
service, and a separate Lakebase helper. This keeps the familiar shape of the
referenced repository while avoiding a separate SPA/API deployment. The
Massive-specific client, synchronization workflow, unrelated dependencies, and
runtime table-creation calls are not carried forward. The repository currently
contains Spec Kit metadata but no application source, so these are planned
paths, not existing files.

## Design Decisions

- Use Lakebase Autoscaling as the only operational data store and bind it as a
  Databricks App resource. Use the Databricks-supported OAuth credential flow
  for app database access; do not copy the reference's static-password URL.
- Keep server-rendered same-origin forms rather than adding a JavaScript SPA or
  a separately deployed API. Use POST/Redirect/GET for successful writes.
- Apply versioned SQL migrations outside request handlers. Seed fixed sample
  identifiers idempotently so redeploys do not duplicate demonstration data.
- The migration runner uses a database advisory lock and a migration version
  table so simultaneous app starts do not apply the same change concurrently.
- Restrict app entry through Databricks app permissions. Since the clarified
  access model gives every signed-in workspace user identical ticket access,
  database access uses the app identity; ticket/message actor attribution uses
  the trusted forwarded identity, not a submitted form value.
- Configure Flask-WTF's signing/CSRF key as an app secret resource; it is
  separate from the Lakebase connection credentials.
- Store status changes in a small audit table. Use a version value on tickets
  for optimistic concurrency; a stale update is rejected with a reload message
  instead of silently overwriting another user's change.
- Support the three example states `open`, `in_progress`, and `resolved`.
  Allow transitions among these valid states, including reopening resolved
  tickets, since no narrower workflow policy was specified.

## Constitution Check (Post-Design)

| Principle / constraint | Design evidence | Gate |
|---|---|---|
| User value and clear workflow | Minimal ticket list, details/thread, and explicit create/message/status actions. | PASS |
| Data integrity and traceability | Ticket-message foreign key, constraints, transactional status plus audit writes, actor/time fields, idempotent seed, optimistic version check. | PASS |
| Least privilege and data protection | Databricks sign-in and app permission, app-scoped database role, trusted actor identity, CSRF protection, no secrets or message contents in logs. | PASS |
| Test-first and validation | Unit and workflow tests cover invalid input, successful writes, persistence, and concurrent status conflicts. | PASS |
| Reliable operation and observability | Health endpoint, deployment checks, useful sanitized errors, structured logs. | PASS |

No constitution violations remain.
