# Tasks: Lakebase Support App

**Input**: Design documents from `specs/001-lakebase-support-app/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/web.md`

**Tests**: No automated test suite is requested. Verify behavior through the deployed-app workflow in `quickstart.md`.

**Organization**: Tasks are grouped by user story so each story can be implemented and checked as an increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other marked tasks because it edits separate files and has no unmet dependencies.
- **[Story]**: User-story label mapping to `spec.md` (US1, US2, US3).
- Each task names the file or files to create or update.

## Phase 1: Setup

**Purpose**: Configure the Python dependencies and Databricks App entry point.

- [X] T001 [P] Create `requirements.txt` with Flask, psycopg 3, Databricks SDK, and Gunicorn dependencies.
- [X] T002 [P] Configure the Databricks App runtime, Gunicorn command, and `/healthz` deployment health check in `app.yaml`.

## Phase 2: Foundational

**Purpose**: Establish the shared Flask shell, Lakebase connection, and required relational schema before implementing user workflows.

- [X] T003 [P] Create the Flask application entry point, `/healthz` liveness route, and shared page layout in `app.py` and `templates/base.html`.
- [X] T004 [P] Define the `tickets` and `ticket_messages` tables with database-generated UUID primary keys, text fields, required fields, and timestamps in `db/schema.sql`; enforce title length "1–200 characters", message length "1–5000 characters", and statuses `open`, `in_progress`, or `resolved`.
- [X] T005 [P] Implement the Lakebase resource connection using the managed app identity in `lakebase.py`; use parameterized SQL for route queries and do not log database credentials.

**Checkpoint**: App shell and shared database foundation are ready for story work.

## Phase 3: User Story 1 - View and manage support tickets (Priority: P1) 🎯 MVP

**Goal**: Load tickets from Lakebase and let users inspect ticket details and the complete message history, including an empty-message state.

**Independent Test**: With schema and sample data loaded, deploy the app and confirm the ticket list shows Lakebase records/statuses, opening a ticket shows its complete unpaginated message history, and a ticket with no messages displays an empty state.

- [X] T006 [P] [US1] Add repeatable sample inserts to `db/seed.sql` that leave at least three tickets, at least two messages per seeded ticket, and at least two statuses without overwriting later user changes.
- [X] T007 [US1] Implement Lakebase-backed ticket list and detail routes in `app.py`, rendering ticket records and full message history without pagination, including an empty state, in `templates/ticket_list.html` and `templates/ticket_detail.html`.

**Checkpoint**: Users can browse seeded tickets and inspect complete message threads from Lakebase.

## Phase 4: User Story 2 - Create a ticket and add progress updates (Priority: P1)

**Goal**: Let signed-in users create tickets and add attributed messages, with clear required-input validation.

**Independent Test**: In the deployed app, create a valid ticket and message; confirm signed-in actor attribution and persistence after refresh. Submit empty and over-limit values and confirm validation feedback with no database write.

- [X] T008 [US2] Implement ticket creation in `app.py` and `templates/ticket_list.html`; trim and validate the title as required, "1–200 characters", set status to `open`, and record the signed-in actor in `tickets.created_by`, never from submitted form data.
- [X] T009 [US2] Implement message submission in `app.py` and `templates/ticket_detail.html`; trim and validate message text as required, "1–5000 characters", link it to the selected ticket, and record the signed-in actor in `ticket_messages.author`, never from submitted form data.

**Checkpoint**: Users can create tickets and append attributed messages; invalid required input is rejected with clear feedback.

## Phase 5: User Story 3 - Update ticket status and preserve data across refreshes (Priority: P2)

**Goal**: Let users update a ticket to a supported status and see the persisted value after refresh, including recovery feedback when an update fails.

**Independent Test**: Change a ticket to another supported status and confirm the value remains after refresh. If a competing status update fails, verify an error is shown and the ticket is rendered with its latest database state.

- [X] T010 [US3] Add a status form to `templates/ticket_detail.html` and a Lakebase-backed update route in `app.py`; accept only `open`, `in_progress`, or `resolved`, let the database handle concurrent writes, and on update failure reload the latest ticket state and display an error banner or toast.

**Checkpoint**: Status changes persist and a failed update displays the latest ticket state with an error.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Provide actionable errors, course-scale styling and setup guidance, and final acceptance verification.

- [X] T011 [P] Add actionable database setup/connection error feedback in `app.py` and `templates/error.html` without displaying or logging credentials or internal connection details.
- [X] T012 [P] Add a small application stylesheet in `static/style.css` and link it from `templates/base.html`.
- [X] T013 [P] Document Lakebase resource setup, running `db/schema.sql` and `db/seed.sql`, app-role grants when SQL Editor creates the tables, app deployment, and workflow checks in `README.md`.
- [ ] T014 Run the deployed-app acceptance steps in `specs/001-lakebase-support-app/quickstart.md`; verify required workflows and refresh persistence without timing or first-attempt percentage measurements.

T014 remains unverified because this workspace has no configured Databricks
authentication or connected Lakebase endpoint; local mocked route checks do
not replace deployed-app acceptance.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on the schema and Lakebase helper in Phase 2.
- **User Story 2 (Phase 4)**: Depends on Phase 2 and the list/detail pages from US1, which provide the ticket creation and message destinations.
- **User Story 3 (Phase 5)**: Depends on Phase 2 and the ticket detail page from US1, where the status form is displayed. It does not depend on US2.
- **Polish (Phase 6)**: Error feedback can be implemented after the app shell; stylesheet and README setup guidance are independent. Run final acceptance only after US1–US3 and deployment setup are complete.

### User Story Dependencies

- **US1 (P1)**: Starts after the shared foundation; first independently demonstrable increment.
- **US2 (P1)**: Starts after US1 because ticket creation redirects to the detail view and message submission uses that view.
- **US3 (P2)**: Starts after US1 because status selection is presented on the ticket detail page. It does not depend on US2.

### Parallel Opportunities

- T001 and T002 edit separate setup files and can run in parallel.
- T003, T004, and T005 edit separate files and can be developed in parallel after Setup.
- Within US1, T006 (seed SQL) and T007 (browse routes/templates) can be developed in parallel after the foundation.
- US2 ticket creation and message submission tasks both update `app.py`; complete them sequentially to avoid conflicts.
- US2 and US3 share `app.py` and `templates/ticket_detail.html`; implement them sequentially even though US3 does not require US2 behavior.
- T011, T012, and T013 can be developed in parallel once the app structure is established; T014 follows deployment and implementation.

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Setup and Foundational phases.
2. Complete US1, including sample data and ticket list/detail views.
3. Deploy and verify the Lakebase-backed list, complete message history, and empty-message state using the US1 independent test.

### Incremental Delivery

1. Add US2 ticket creation and message submission; verify actor attribution, validation, and refresh persistence.
2. Add US3 status updates; verify status persistence and latest-state feedback if an update fails.
3. Complete the focused deployed-app acceptance run from `quickstart.md`.

## Format Validation

All implementation tasks use the required unchecked-checkbox format, sequential IDs, `[P]` only for independent parallel work, story labels only in user-story phases, and explicit file paths.
