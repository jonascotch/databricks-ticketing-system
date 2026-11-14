# Web Contract: Lakebase Support App

The application exposes a same-origin, server-rendered HTML interface for
signed-in Databricks workspace users. It does not expose a public or
machine-to-machine ticket API.

## Access and attribution

- Databricks authentication and configured app permissions gate application
  access.
- Any signed-in user with app access can view and change all tickets and
  messages.
- The server records the `X-Forwarded-Preferred-Username` value as the signed-in
  ticket creator or message author; clients cannot choose another identity
  through form fields.
- Database queries use the Lakebase app resource's shared app identity.

## Routes

| Method and path | Behavior | Success |
|---|---|---|
| `GET /` | Show all tickets and the new-ticket form | HTML page; tickets read from Lakebase |
| `GET /tickets/<ticket_id>` | Show ticket details and the complete message history without pagination | HTML page, or `404` for an unknown ticket |
| `POST /tickets` | Create a ticket from a title | Validate title; create with status `open` and signed-in creator; redirect to new ticket |
| `POST /tickets/<ticket_id>/messages` | Add a message to an existing ticket | Validate message and ticket; create with signed-in author; redirect to ticket |
| `POST /tickets/<ticket_id>/status` | Change ticket status | Validate status and persist the update; redirect to ticket |

Successful form writes use Post/Redirect/Get. User input must be validated;
queries must be parameterized and rendered user text escaped by the template
engine.

## Validation and failures

- Blank or invalid ticket titles, messages, and status values are rejected
  without a database write and receive clear feedback.
- Unknown ticket IDs return `404` for detail and write operations.
- The database handles concurrent status updates. If a status update fails,
  the app reloads the latest ticket state and displays an error banner or
  toast with that state.
- Ordinary database setup or connection errors receive actionable feedback
  without exposing credentials or implementation details; credentials must
  not be written to logs.
