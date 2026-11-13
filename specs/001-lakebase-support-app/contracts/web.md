# Web Contract: Lakebase Support App

The application exposes a same-origin, server-rendered HTML interface for
signed-in Databricks workspace users. It does not expose a public or
machine-to-machine ticket API in this feature.

## Authentication and actor identity

- Databricks authentication and app permissions gate access to the application.
- Every permitted signed-in user can read and update all tickets.
- The server derives `created_by`, `author`, and `changed_by` from the trusted
  Databricks-forwarded identity; clients MUST NOT supply or override these
  values in forms.
- Write forms include a valid CSRF token. Missing/invalid identity or CSRF data
  MUST NOT result in a database write.

## Routes

| Method and path | Behavior | Success |
|---|---|---|
| `GET /` | Show all tickets and the new-ticket form | HTML page; tickets read from Lakebase |
| `GET /tickets/<ticket_id>` | Show ticket details, current status, and complete message history | HTML page, or `404` for an unknown ticket |
| `POST /tickets` | Create a ticket from a title | Validate title; create with status `open` and server-derived creator; redirect to new ticket |
| `POST /tickets/<ticket_id>/messages` | Add a message to an existing ticket | Validate message and ticket; create with server-derived author; redirect to ticket |
| `POST /tickets/<ticket_id>/status` | Change status using a value and observed ticket version | Validate status and version; atomically update ticket and status history; redirect to ticket |
| `GET /healthz` | Report process liveness for deployment checks | Small non-sensitive response; no ticket data |

Successful form writes use Post/Redirect/Get. Request fields and database
queries MUST be parameterized; rendered user text MUST be escaped by the
template engine.

## Validation and failures

- Blank or out-of-range ticket titles, messages, or unknown status values are
  rejected without a write; the form returns an actionable field-level error.
- Unknown ticket IDs return `404` for detail and write operations.
- A stale status version returns `409` or a rendered conflict state, does not
  overwrite the current status, and prompts the user to reload.
- A Lakebase outage returns a user-safe availability error and is logged with a
  request identifier. Logs MUST NOT contain credentials or message contents.
- Missing trusted user identity or invalid CSRF token rejects the write.
- The health response and user-facing failures MUST NOT expose connection
  strings, tokens, stack traces, or sensitive database details.
