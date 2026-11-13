# Data Model: Lakebase Support App

All operational entities are stored in Lakebase PostgreSQL. Identifiers use
UUIDs; creation and change timestamps use timezone-aware timestamps in UTC.

## Ticket

Represents one support request.

| Field | Type / rule | Notes |
|---|---|---|
| `ticket_id` | UUID, primary key, generated on creation | Stable identity; not user-editable |
| `title` | Text, required, trimmed, 1–200 characters | Reject empty or over-limit values |
| `status` | Text, required, one of `open`, `in_progress`, `resolved`; defaults to `open` | Any transition among valid states is permitted, including reopening |
| `created_by` | Text, required | Derived from the signed-in Databricks user's trusted forwarded identity |
| `created_at` | Timestamp with time zone, required, server/database generated | Immutable creation time |
| `updated_at` | Timestamp with time zone, required, server/database generated | Refreshed on a successful status change |
| `version` | Positive integer, required, starts at 1 | Incremented for each status change; guards against stale concurrent updates |

Tickets are listed newest first by `created_at`, with a stable `ticket_id`
tie-breaker. Index `created_at` for list ordering.

## Ticket Message

Represents an immutable message attached to a ticket.

| Field | Type / rule | Notes |
|---|---|---|
| `message_id` | UUID, primary key, generated on creation | Stable identity |
| `ticket_id` | UUID, required foreign key to `Ticket.ticket_id` | Prevents orphan messages; deletion is not exposed in v1 |
| `message_text` | Text, required, trimmed, 1–5000 characters | Reject empty or over-limit values |
| `author` | Text, required | Derived from the signed-in Databricks user's trusted forwarded identity |
| `created_at` | Timestamp with time zone, required, server/database generated | Immutable message time |

Messages are displayed oldest first by `created_at`, then `message_id`. Index
`(ticket_id, created_at, message_id)` for thread retrieval.

## Ticket Status Change

An append-only audit record for each successful status change.

| Field | Type / rule | Notes |
|---|---|---|
| `status_change_id` | UUID, primary key, generated on change | Stable audit identity |
| `ticket_id` | UUID, required foreign key to `Ticket.ticket_id` | Index by ticket and time |
| `previous_status` | Text, required, valid ticket status | State before the change |
| `new_status` | Text, required, valid ticket status | State after the change; must differ from previous |
| `changed_by` | Text, required | Signed-in Databricks user identity |
| `changed_at` | Timestamp with time zone, required, database generated | Immutable event time |

The ticket update and corresponding status-change row MUST be committed in one
transaction. When a submitted `version` does not match the stored ticket
version, neither update nor audit row is written; the UI reports that the
ticket changed and asks the user to reload.

## Relationships and lifecycle

- One ticket has zero or more messages; every message belongs to exactly one
  ticket.
- One ticket has zero or more status-change audit records.
- New tickets start in `open`; no initial status-change audit row is required.
- A valid status change updates `status`, `updated_at`, and `version`, and adds
  exactly one audit row atomically.
- Messages are append-only in v1. Ticket deletion and message editing/deletion
  are out of scope.

## Seed data

The repeatable seed operation MUST produce at least three support tickets,
at least two messages per seeded ticket, and at least two different statuses.
Use stable sample IDs and conflict-safe inserts so running the seed operation
again does not duplicate records or overwrite later user changes.
