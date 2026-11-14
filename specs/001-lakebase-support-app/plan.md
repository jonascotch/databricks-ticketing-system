# Implementation Plan: Lakebase Support App

**Branch**: `001-lakebase-support-app` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-lakebase-support-app/spec.md`

## Summary

Build a small Flask app with Jinja templates and Lakebase PostgreSQL, following
the compact structure of the user's Databricks Lakebase reference app. The app
lets signed-in workspace users view tickets, inspect messages, create tickets,
add messages, and update ticket status. Use a Databricks App Lakebase resource
and its managed app identity for database access. Set up the two-table schema
and repeatable sample data using small SQL files.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Flask, psycopg 3, Databricks SDK, Gunicorn

**Storage**: Lakebase Autoscaling PostgreSQL; no separate operational store

**Testing**: Focused deployed-app workflow, input-validation, concurrency-failure feedback, and persistence checks

**Target Platform**: Databricks Apps in the user's Databricks workspace

**Project Type**: Server-rendered internal web application

**Performance Goals**: No quantified response-time or throughput target for
this course-scale sample app; render the complete message history without
pagination.

**Constraints**: Databricks authentication and app permissions gate access.
All signed-in users can access the same tickets; the app records the signed-in
user as creator or author. Database access uses the configured Lakebase app
resource. Do not commit credentials or expose them in logs.

**Scale/Scope**: Small course assignment; at least three seeded tickets with
at least two messages each. No separate frontend service, public API, AI
features, or production operations framework.

## Constitution Check

| Principle / constraint | Plan response | Gate |
|---|---|---|
| User Value & Ticket Clarity | Focus on the required ticket list, ticket thread, creation, messages, and status update. | PASS |
| Data Integrity & Traceability | Persist the required ticket/message fields and relationship, record signed-in actor and timestamps, validate required inputs, and seed sample records. | PASS |
| Essential Databricks Security | Use Databricks sign-in/app permissions and the supported Lakebase app resource; do not hard-code credentials, expose them in logs, or add custom identity fallbacks. | PASS |
| Focused Testing & Verification | Verify required workflows, input validation, status-update failure feedback, deployment, and persistence after refresh with concise smoke checks. | PASS |
| Course-Scale Simplicity | Use small SQL setup files, a basic Flask app, and actionable ordinary error feedback; avoid production-scale controls. | PASS |

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
lakebase.py               # Lakebase resource connection
templates/                # Server-rendered ticket list and detail/forms
static/style.css          # Small application stylesheet
db/
├── schema.sql            # Tickets and ticket_messages tables
└── seed.sql              # Repeatable demonstration records
app.yaml                  # Databricks Apps runtime and resource binding
requirements.txt
README.md
```

**Structure Decision**: Use one Flask app with Jinja templates and a small
Lakebase helper, matching the reference app's overall shape. Keep schema and
seed setup in plain SQL files that can be run in Lakebase SQL Editor. Do not
carry forward its unrelated Massive API ingestion, static-password URL, or
runtime table-creation behavior. These paths keep the application, database setup, and deployment configuration
small and directly aligned with the assignment.

## Design Decisions

- Use Lakebase Autoscaling as the operational data store and attach it through
  Databricks App resources. Connect using the documented app identity/OAuth
  flow rather than a static-password URL.
- Keep server-rendered, same-origin forms for the required workflows. Use
  straightforward form validation and redirects after successful writes. The
  assignment lists validation and helpful errors as a bonus, but this project
  selects that bonus and includes it in required implementation scope.
- Create the `tickets` and `ticket_messages` tables from `db/schema.sql`, then
  add the required sample records from `db/seed.sql`. If a separate SQL Editor
  identity creates the tables, grant the app's Lakebase database role the
  schema/table permissions needed to read and write them.
- Use the app's shared database identity for queries. Record the signed-in
  user performing the action in `tickets.created_by` or
  `ticket_messages.author`; do not accept creator/author values from form
  fields.
- Render the complete message history without pagination for this sample app.
- Allow the three example statuses (`open`, `in_progress`, and `resolved`).
  Let the database handle concurrent status updates. If a status write fails,
  re-read and render the latest ticket state with an error banner or toast.
  No status audit table, optimistic concurrency mechanism, migration runner,
  custom authentication fallback, or CSRF secret framework is required for
  this assignment.
- Never include credentials in application logs or user-facing errors.
- Keep validation focused on the required deployed workflows and confirmation
  that changes persist after refresh, including clear feedback for invalid
  input and the latest ticket state after a failed status update. Broad unit,
  integration, load, and resilience suites are not required.

## Constitution Check (Post-Design)

| Principle / constraint | Design evidence | Gate |
|---|---|---|
| User value and clear workflow | The UI covers ticket list, details/messages, creation, and status changes. | PASS |
| Data integrity and traceability | Required fields, ticket-message foreign key, signed-in actor attribution, selected input-validation bonus, and repeatable seed data. | PASS |
| Essential Databricks security | Databricks app permissions, managed Lakebase app resource, no committed credentials, and no credentials in logs or user-facing errors. | PASS |
| Focused testing and verification | Deployed workflow checks cover required operations, validation, status-update failure feedback, and refresh persistence. | PASS |
| Course-scale simplicity | Plain SQL setup and a small Flask application without production-only frameworks. | PASS |

No constitution violations remain.
