# Tasks: Lakebase Support App

**Input**: Design documents from `specs/001-lakebase-support-app/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/web.md`, and `quickstart.md`

**Tests**: Tests are included because the feature explicitly requires deployment
and testing, and the project constitution requires verified behavior for
workflow and data changes. Write the focused tests before their implementation
tasks and confirm they fail for the missing behavior.

**Organization**: Tasks are grouped by user story so the read-only ticket
experience can be delivered before write workflows.

## Phase 1: Setup

**Purpose**: Establish dependencies, Databricks deployment configuration, and
project instructions.

- [ ] T001 [P] Create `requirements.txt` for Python 3.11 with Flask, `psycopg[binary]`, Databricks SDK, Gunicorn, Flask-WTF, and pytest.
- [ ] T002 [P] Create `app.yaml` with the production Gunicorn command, Lakebase database resource binding, and Flask/CSRF secret resource per `specs/001-lakebase-support-app/research.md`.
- [ ] T003 [P] Create `README.md` with repository setup, local test instructions, and a link to `specs/001-lakebase-support-app/quickstart.md`.

---

## Phase 2: Foundational

**Purpose**: Implement and verify the database, shared security setup, and
sample data that every user story depends on.

- [ ] T004 Create isolated pytest configuration and Lakebase integration fixtures in `tests/conftest.py`.
- [ ] T005 [P] Write failing migration/schema contract tests in `tests/integration/test_schema.py` for UUID primary keys, required fields, status checks, and the `ticket_messages.ticket_id` foreign key.
- [ ] T006 [P] Create `db/migrations/001_initial_schema.sql` for tickets, ticket messages, and status history; use `UUID, primary key, generated on creation` for entity IDs; enforce `title` as “Text, required, trimmed, 1–200 characters”, `status` as “Text, required, one of `open`, `in_progress`, `resolved`; defaults to `open`”, `created_by`, `author`, and `changed_by` as “Text, required”, timestamps as “Timestamp with time zone, required, server/database generated”, `version` as “Positive integer, required, starts at 1”, `ticket_messages.ticket_id` as “UUID, required foreign key to `Ticket.ticket_id`”, and status history values as “Text, required, valid ticket status”.
- [ ] T007 [P] Implement `lakebase.py` with the Databricks Apps Lakebase resource OAuth flow, parameterized query/transaction helpers, and fresh credentials for new connections; do not read a static-password Lakebase URL.
- [ ] T008 Implement `scripts/migrate.py` to take a PostgreSQL advisory lock, track applied migration versions, and apply ordered SQL migrations outside request handlers.
- [ ] T009 Write failing seed-data assertions in `tests/integration/test_sample_seed.py` for at least three tickets, at least two messages for every seeded ticket, and at least two distinct statuses.
- [ ] T010 Implement `scripts/seed_sample_data.py` with stable sample IDs and conflict-safe inserts that do not overwrite existing user changes.
- [ ] T011 [P] Write failing authentication and CSRF tests in `tests/unit/test_identity_and_csrf.py` to reject missing trusted identity and invalid CSRF tokens on writes.
- [ ] T012 Configure the Flask app, secret-backed CSRF key, trusted forwarded-user resolver, sanitized error handling, structured safe logging, and `/healthz` in `app.py`.

**Checkpoint**: Database migrations and sample data are repeatable, and the
shared app/security foundation is ready for story implementation.

---

## Phase 3: User Story 1 - View and manage support tickets (Priority: P1)

**Goal**: Let a signed-in user view all Lakebase tickets and inspect any
ticket's complete message history.

**Independent Test**: With the sample seed loaded, verify all tickets and
statuses appear from Lakebase, a selected ticket shows its messages in
chronological order, and a ticket with no messages displays an empty state.

### Tests for User Story 1

- [ ] T013 [P] [US1] Write failing ticket-list acceptance tests in `tests/integration/test_ticket_list.py` proving every persisted ticket and status is displayed without hard-coded app data.
- [ ] T014 [P] [US1] Write failing ticket-detail acceptance tests in `tests/integration/test_ticket_detail.py` for chronological messages, empty message state, and unknown-ticket `404`.

### Implementation for User Story 1

- [ ] T015 [US1] Implement `list_tickets()` and `get_ticket_with_messages()` in `ticket_service.py` with parameterized queries and stable ordering from `specs/001-lakebase-support-app/data-model.md`.
- [ ] T016 [US1] Add `GET /` and `GET /tickets/<ticket_id>` handlers in `app.py` that render Lakebase results and return `404` for an unknown ticket.
- [ ] T017 [US1] Create `templates/ticket_list.html` and `templates/ticket_detail.html` to display all ticket statuses, ticket details, chronological messages, and the no-messages state.

**Checkpoint**: User Story 1 is independently usable as a read-only ticket
viewer backed by Lakebase.

---

## Phase 4: User Story 2 - Create a ticket and add progress updates (Priority: P1)

**Goal**: Let a signed-in user create a ticket and add attributed messages,
persisting both in Lakebase.

**Independent Test**: Create a ticket, add a message to it, refresh the app,
and verify both records and the signed-in actor identities persist.

### Tests for User Story 2

- [ ] T018 [P] [US2] Write failing ticket-creation tests in `tests/integration/test_ticket_creation.py` for persisted ticket fields, default `open` status, creator attribution, and rejection of blank or over-200-character titles.
- [ ] T019 [P] [US2] Write failing message tests in `tests/integration/test_ticket_messages.py` for persisted author attribution, ticket linkage, chronological display, and rejection of blank or over-5000-character messages.

### Implementation for User Story 2

- [ ] T020 [US2] Implement `create_ticket()` and `add_ticket_message()` in `ticket_service.py`; enforce `title` as `Text, required, trimmed, 1–200 characters` and `message_text` as `Text, required, trimmed, 1–5000 characters`, and derive `created_by`/`author` from the trusted signed-in identity.
- [ ] T021 [US2] Add `POST /tickets` and `POST /tickets/<ticket_id>/messages` in `app.py` with CSRF validation, field-level errors, Lakebase persistence, and Post/Redirect/Get responses.
- [ ] T022 [P] [US2] Add the new-ticket form and validation feedback to `templates/ticket_list.html`.
- [ ] T023 [P] [US2] Add the message form and validation feedback to `templates/ticket_detail.html`.

**Checkpoint**: User Story 2 can create tickets and messages in Lakebase,
including records that remain available after refresh.

---

## Phase 5: User Story 3 - Update ticket status and preserve data across refreshes (Priority: P2)

**Goal**: Let signed-in users change a ticket's status without losing status
history or silently overwriting a concurrent change.

**Independent Test**: Change a ticket through valid statuses, refresh to
confirm persistence, verify each change has an audit record, then submit a
stale version and confirm it is rejected without changing the latest status.

### Tests for User Story 3

- [ ] T024 [P] [US3] Write failing status-transition tests in `tests/integration/test_ticket_status.py` for `open`, `in_progress`, and `resolved` values, persisted updates, version increments, and audit attribution.
- [ ] T025 [P] [US3] Write failing concurrent-update tests in `tests/integration/test_ticket_status_conflict.py` proving a stale version creates no status or audit write and yields a reload conflict.

### Implementation for User Story 3

- [ ] T026 [US3] Implement `update_ticket_status()` in `ticket_service.py` to validate the three supported statuses and atomically update the ticket plus audit row only when the submitted version matches.
- [ ] T027 [US3] Add `POST /tickets/<ticket_id>/status` in `app.py` and the status/version form in `templates/ticket_detail.html`; reject invalid states and show a reload message for stale updates.

**Checkpoint**: User Story 3 persists valid status changes and prevents
silent last-write-wins conflicts.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish safe failure behavior, usability, documentation, and
deployed acceptance validation.

- [ ] T028 Write failing database-outage and safe-error tests in `tests/integration/test_failure_handling.py` confirming no credentials/message text leak and `/healthz` reports process liveness independently of Lakebase.
- [ ] T029 Handle expected Lakebase failures in `app.py` and `lakebase.py` with request-correlated logs, safe user messages, and no broad success-shaped fallback.
- [ ] T030 [P] Add consistent responsive styling in `static/app.css` and shared page layout in `templates/base.html`.
- [ ] T031 [P] Document Databricks resource setup, app permissions, migration/seed startup behavior, tests, and deployment in `README.md`, referencing `specs/001-lakebase-support-app/quickstart.md`.
- [ ] T032 Deploy the Databricks App and execute every scenario in `specs/001-lakebase-support-app/quickstart.md`; record pass/fail results and any environment-specific notes in `README.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No prerequisites; tasks T001–T003 can run in parallel.
- **Foundational (Phase 2)**: Begins after dependencies are defined. Schema
  contract tests (T005) precede the schema and migration implementation
  (T006–T008); sample assertions (T009) precede the seed script (T010);
  identity/CSRF tests (T011) precede the shared Flask setup (T012). This phase
  blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on setup, foundation, and seeded data.
- **User Story 2 (Phase 4)**: Follows User Story 1 because its forms and
  handlers extend the list/detail pages created there.
- **User Story 3 (Phase 5)**: Follows User Story 2 because its status form
  extends the same ticket-detail route and template.
- **Polish (Phase 6)**: Depends on all three stories; deployment acceptance is
  last.

```text
Phase 1 Setup
    ↓
Phase 2 Foundation
    ↓
Phase 3 US1: View tickets and messages
    ↓
Phase 4 US2: Create tickets and add messages
    ↓
Phase 5 US3: Update status and preserve history
    ↓
Phase 6 Polish and deployed acceptance
```

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on another user story.
- **US2 (P1)**: Builds on the list/detail screens from US1; its create and
  message flows are independently tested against seeded tickets.
- **US3 (P2)**: Builds on the ticket detail page from US1/US2; independently
  tested using both seeded and newly created tickets.

### Parallel Opportunities

- Setup tasks T001–T003 use different files and can proceed concurrently.
- Foundational schema work T006 and Lakebase helper work T007 use different
  files and can proceed concurrently after T005; their tests are separate from
  each other.
- US1 acceptance tests T013 and T014 target separate test files and can be
  written in parallel before implementation.
- US2 acceptance tests T018 and T019 target separate test files and can be
  written in parallel; after T021, form tasks T022 and T023 touch separate
  templates.
- US3 acceptance tests T024 and T025 target separate test files and can be
  written in parallel before the status service and route.
- Polish styling T030 and documentation T031 use separate paths and can proceed
  in parallel; T028 must precede the error-handling changes in T029.

## Parallel Examples

### User Story 1

```text
In parallel, write:
- T013: tests/integration/test_ticket_list.py
- T014: tests/integration/test_ticket_detail.py
Then implement T015–T017 in dependency order.
```

### User Story 2

```text
In parallel, write:
- T018: tests/integration/test_ticket_creation.py
- T019: tests/integration/test_ticket_messages.py
After T020–T021, implement T022 and T023 in parallel on separate templates.
```

### User Story 3

```text
In parallel, write:
- T024: tests/integration/test_ticket_status.py
- T025: tests/integration/test_ticket_status_conflict.py
Then implement T026 before T027.
```

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Setup and Foundational phases, including repeatable sample data.
2. Complete User Story 1.
3. Validate that all seeded tickets/statuses and their messages load from
   Lakebase, including an empty-message ticket.
4. Deploy a read-only demonstration if useful; do not claim the full feature is
   complete until write stories and deployment acceptance are done.

### Incremental Delivery

1. Complete Setup + Foundation and verify migrations, seed data, and app access.
2. Deliver US1 as the read-only ticket viewer.
3. Add US2 ticket and message creation; verify persistence after refresh.
4. Add US3 status updates, audit history, and stale-write handling.
5. Complete cross-cutting failure, presentation, and Databricks deployment
   acceptance tasks.

## Format Validation

Every implementation task is an unchecked Markdown checkbox with a sequential
`T###` identifier, a `[P]` marker only for parallelizable work, a `[US#]` label
on user-story tasks only, and at least one concrete file path.
