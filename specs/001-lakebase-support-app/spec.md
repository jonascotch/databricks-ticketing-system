# Feature Specification: Lakebase Support App

**Feature Branch**: `001-lakebase-support-app`

**Created**: 2026-11-13

**Status**: Draft

**Input**: User description: "

Build a Lakebase-Powered AI Support App

Objective
Build and deploy a small Databricks App backed by Lakebase. Your app will become the foundation for the context-engineering and AI-agent projects later in the boot camp.

Scenario
You are building an internal support system where users can create support tickets and add messages to those tickets.
Your application must store its operational data in Lakebase.

Requirements
1. Create the Lakebase schema

Create at least these two related tables:

tickets:
    ticket_id
    title
    status
    created_by
    created_at

ticket_messages
    message_id
    ticket_id
    message_text
    author
    created_at

The ticket_messages.ticket_id column must reference a ticket in the tickets table.
You may add additional columns or tables.

2. Add sample data

Your database must contain:
    At least three support tickets
    At least two messages for each ticket
    At least two different ticket statuses, such as open, in_progress, or resolved

3. Build a Databricks App

Create an app that allows a user to:
    View all support tickets
    Select a ticket and view its messages
    Create a new ticket
    Add a message to an existing ticket
    Update a ticket’s status

The app must read from and write to Lakebase. Hard-coded application data does not count.

4. Deploy and test the app

Deploy the app using Databricks Apps and confirm that:
    Existing tickets load from Lakebase
    A new ticket can be created
    A message can be added
    A ticket’s status can be updated
    Changes remain after refreshing the app

5. Bonus Challenges

Earn recognition for completing one or more of these:

    Add ticket priority or category
    Add filtering by ticket status
    Add input validation and helpful error messages
    Display ticket statistics
    Add delete functionality with a confirmation step
    Improve the visual design of the application"

## Clarifications

### Session 2026-11-13

- Q: Which access model should the internal support app use? → A: Any signed-in Databricks workspace user can view and change all tickets and messages.

### Session 2026-11-14

- The assignment lists input validation and helpful errors as a bonus, but this project selects that bonus and treats it as required implementation scope.
- Ticket `created_by` and message `author` values represent the signed-in user performing the action.
- Render the sample app's full ticket message history without pagination.
- Let the database handle concurrent status updates. If an update fails, show an error banner or toast and re-render the ticket with its latest database state.
- Remove the elapsed-time and first-attempt percentage success measures; validate the required behavior through the workflow checks below instead.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View and manage support tickets (Priority: P1)

An internal support team member opens the application and immediately sees the current support workload in a clear ticket list. They can pick a ticket to inspect its history, identify its current status, and determine the next action without relying on manual tracking.

**Why this priority**: This is the primary value of the product: the team must be able to see, review, and update open support work from a central operational view.

**Independent Test**: The app can be tested by loading the ticket list from Lakebase and confirming the full set of tickets and their statuses appears without any hard-coded sample data.

**Acceptance Scenarios**:

1. **Given** a Lakebase database containing multiple tickets, **When** the application loads, **Then** the user sees all tickets and their current status in a single list.
2. **Given** a user selects a ticket from the list, **When** the selection is made, **Then** the ticket details and its associated message history are shown.
3. **Given** a ticket has no messages yet, **When** the details are opened, **Then** the user sees an empty or clearly labeled message state rather than an error.
4. **Given** tickets have different statuses, **When** the user selects a status filter, **Then** the list shows only tickets with that status, with an option to show all tickets.

---

### User Story 2 - Create a ticket and add progress updates (Priority: P1)

A support user can create new tickets with a clear title and record follow-up messages that explain the work in progress. This ensures the ticket history remains visible and each ticket reflects the current support conversation.

**Why this priority**: Ticket creation and updates are core operational workflows; without them, the system cannot support real work or traceability.

**Independent Test**: A new ticket can be created and a message can be added in the app, and the resulting records remain in Lakebase after refresh.

**Acceptance Scenarios**:

1. **Given** a user is on the ticket creation form, **When** they enter a valid title and submit, **Then** a new ticket is created in Lakebase and appears in the ticket list.
2. **Given** an existing ticket is selected, **When** a user adds a message, **Then** the message is saved to the related ticket and becomes visible in the ticket thread.
3. **Given** a user submits an empty title or message, **When** the action is attempted, **Then** the app blocks the submission and shows a clear validation error.

---

### User Story 3 - Update ticket status and preserve data across refreshes (Priority: P2)

An operator updates a ticket as it moves through support states, such as open, in progress, or resolved. The app must persist that status update and keep it visible after a page refresh.

**Why this priority**: Status updates provide operational visibility and allow users to track work through completion without losing context.

**Independent Test**: A ticket can be marked resolved or moved to another state and the updated state remains visible after the app refreshes.

**Acceptance Scenarios**:

1. **Given** a ticket is open, **When** the user changes its status, **Then** the record updates in Lakebase and the new status is reflected in the ticket list.
2. **Given** the application is refreshed, **When** the page reloads, **Then** the latest ticket data and message history are still available.
3. **Given** a status update fails while users are making competing updates, **When** the app handles the failure, **Then** it shows an error and renders the latest ticket state from Lakebase.

---

### Edge Cases

- An empty ticket title or message is rejected with clear validation feedback and no database write.
- Render a ticket's full message history without pagination for this sample app.
- If Lakebase is unavailable, show an actionable error without exposing credentials or internal connection details.
- Let the database handle concurrent status updates. If an update fails, show an error and render the latest ticket state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST store support data in Lakebase and MUST NOT rely on hard-coded ticket data as the primary source of truth.
- **FR-002**: The system MUST create a `tickets` table with at least `ticket_id`, `title`, `status`, `created_by`, and `created_at` fields.
- **FR-003**: The system MUST create a `ticket_messages` table with at least `message_id`, `ticket_id`, `message_text`, `author`, and `created_at` fields.
- **FR-004**: The `ticket_messages.ticket_id` field MUST reference a valid record in the `tickets` table through a persistent relational link.
- **FR-005**: The system MUST include at least three sample tickets and at least two messages for each ticket in the seeded Lakebase data.
- **FR-006**: The system MUST support at least two distinct ticket states such as open, in_progress, or resolved.
- **FR-007**: The system MUST allow a user to view a complete list of support tickets and their current status.
- **FR-008**: The system MUST allow a user to select a ticket and view that ticket's full message history.
- **FR-009**: The system MUST allow a user to create a new ticket with a title and relevant metadata from the app interface.
- **FR-010**: The system MUST allow a user to add a message to an existing ticket and persist that message to Lakebase.
- **FR-011**: The system MUST allow a user to update a ticket's status and persist the new value.
- **FR-012**: The system MUST retain the latest ticket data and message history after a page refresh or application reload.
- **FR-013**: The system MUST provide clear feedback when required input is missing or invalid.
- **FR-014**: The system MUST be deployable as a Databricks App using Lakebase-backed operational data.
- **FR-015**: Any signed-in Databricks workspace user MUST be able to view and change all tickets and messages; the system MUST record the signed-in user as the creator or author of each new ticket or message.
- **FR-016**: The system MUST allow users to filter the ticket list by status and return to viewing all tickets.

### Key Entities *(include if feature involves data)*

- **Ticket**: Represents a support request or issue, with a unique identifier, title, current status, creator, and creation timestamp.
- **Ticket Message**: Represents a follow-up entry or update within a ticket conversation, linked to a specific ticket and attributed to an author with a timestamp.
- **Support User**: Represents any signed-in Databricks workspace user, who can view and change all tickets and messages; their identity is recorded when they create a ticket or message.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view all tickets and their most recent status in a single screen without manual lookup or data export.
- **SC-002**: Ticket data remains available and correct after refreshing the app, with no loss of newly created records or updates.
- **SC-003**: The app demonstrates a complete support workflow from ticket creation through progress updates to status resolution using Lakebase-backed storage.

## Assumptions

- Users are internal support staff who need a lightweight operational view of active and resolved issues.
- All signed-in Databricks workspace users share the same ticket access and update permissions.
- Lakebase is available as the application data store for this project and is the authoritative source for ticket records.
- The Databricks App deployment environment supports a web application that reads and writes to Lakebase.
- The initial version focuses on core support workflows rather than advanced analytics, permissions, or enterprise admin features.
- The app is expected to support a small operational dataset with a manageable number of concurrent users for the boot camp phase.
