# Research: Lakebase Support App

**Date**: 2026-11-13

## Decision 1: Reuse the reference app's shape, not its ingestion system

**Decision**: Use one Flask application, server-rendered Jinja templates, and a
separate Lakebase connection/helper module. Keep ticket-domain operations in a
small service module. Do not copy the reference's Massive API client, batch
sync, stock watchlist, or unrelated dependencies.

**Rationale**: The reference is a compact Databricks App organized around
`app.py`, `lakebase.py`, `templates/`, and `app.yaml`, which is a good fit for a
small internal ticket workflow. The app's data ingestion and external API
features do not serve this feature. A single server-rendered app avoids the
operational overhead of a separate frontend and API.

**Alternatives considered**:

- **Copy the repository unchanged**: rejected because its Massive API data
  model, sync endpoints, and runtime `CREATE TABLE IF NOT EXISTS` calls are
  unrelated to ticketing.
- **FastAPI plus a separate single-page frontend**: rejected for now because
  the feature has a small number of form-and-list workflows and no requirement
  for a separate client.
- **Streamlit**: viable for a quick data-entry prototype, but less suitable
  than Flask/Jinja for a custom ticket conversation interface and explicit
  route/form behavior.

## Decision 2: Use a managed Lakebase app resource and OAuth

**Decision**: Attach Lakebase to the Databricks App as a database resource and
use the supported app identity/OAuth credential flow with psycopg 3. Do not
reuse the reference's static-password connection URL stored in a secret scope.

**Rationale**: The reference helper retrieves a long-lived URL containing a
native database password. Current Databricks Apps guidance provides a managed
Lakebase resource and app identity so the deployed application can connect
without copying a static credential into its configuration. The app's database
role remains separate from the signed-in user identity used for attribution.
OAuth credentials are short-lived, so the connection helper must obtain current
credentials when establishing connections rather than retaining an expired
token indefinitely.

**Alternatives considered**:

- **Static native-password URL**: supported in some configurations and simple
  to reason about, but requires password storage and rotation; not preferred
  when the managed app resource is available.
- **Lakebase Data API**: could provide REST CRUD without a custom database
  helper, but adds OAuth/Postgres-role and row-level-security requirements
  without reducing complexity for this server-rendered application.

## Decision 3: Keep schema changes versioned and sample seeding repeatable

**Decision**: Store ordered SQL migrations in the repository and apply them as
a deployment/startup migration step, not from individual request handlers.
Seed the required demonstration records with stable identifiers and conflict
handling so repeated runs do not create duplicates.

**Rationale**: This preserves reproducibility and prevents concurrent requests
from racing to create tables. A small SQL migration runner is sufficient for
the initial schema; adopting an ORM migration framework is not necessary for
three core entities.

**Alternatives considered**:

- **Create tables during each request**: rejected because it couples normal
  app use to DDL, hides deployment readiness problems, and races across
  concurrent requests.
- **Manual one-off schema edits only**: rejected because they are difficult to
  reproduce and validate in another workspace.

## Decision 4: Separate app access from ticket actor attribution

**Decision**: Require a signed-in Databricks user with permission to use the
app. The app uses its Lakebase resource identity for database access, while
ticket `created_by` and message `author` are derived server-side from the
trusted identity forwarded by Databricks. Do not accept actor identity from
form fields.

**Rationale**: The clarified product rule gives all signed-in workspace users
the same read/write access. The app's shared service identity is appropriate
for Lakebase access, but would otherwise lose which person created each record.
Actor attribution preserves traceability without introducing role-based
authorization that the feature does not require.

**Security details**: Limit app availability through Databricks app
permissions, validate the expected forwarded identity header, protect
cookie-backed form submissions with CSRF tokens, store the app's CSRF/session
signing key in an app secret resource, and never log database credentials or
ticket message bodies.

## Decision 5: Keep status history and reject stale edits

**Decision**: Record status transitions with actor and time in a related audit
table. Include a monotonically increasing ticket version in status forms and
apply status plus audit writes in one transaction. If the submitted version is
stale, do not overwrite; ask the user to reload the ticket.

**Rationale**: This preserves prior state and avoids silent lost updates,
meeting the project constitution's data-integrity requirements without
introducing a generalized event-sourcing architecture.

**Alternatives considered**:

- **Last-write-wins status changes**: rejected because concurrent users could
  silently erase one another's updates.
- **Full event-sourced ticket model**: rejected as unnecessary for the small,
  fixed workflow.

## Sources

- User-provided reference repository: [databricks-lakebase-app-day-1](https://github.com/jonascotch/databricks-lakebase-app-day-1). Its root layout includes `app.py`, `lakebase.py`, `app.yaml`, `requirements.txt`, and `templates/`; the app also contains unrelated Massive ingestion and static-password secret URL handling.
- Reference implementation, pinned for review: [`app.py`](https://github.com/jonascotch/databricks-lakebase-app-day-1/blob/c7ee2d4ff1cc7de0465116ccf594f33ba0c84cc3/app.py), [`lakebase.py`](https://github.com/jonascotch/databricks-lakebase-app-day-1/blob/c7ee2d4ff1cc7de0465116ccf594f33ba0c84cc3/lakebase.py), [`app.yaml`](https://github.com/jonascotch/databricks-lakebase-app-day-1/blob/c7ee2d4ff1cc7de0465116ccf594f33ba0c84cc3/app.yaml).
- Databricks, [Build applications with Lakebase](https://docs.databricks.com/aws/en/oltp/projects/build-applications).
- Databricks, [Databricks Apps with Lakebase](https://docs.databricks.com/aws/en/oltp/projects/databricks-apps).
- Databricks, [Lakebase resources for Databricks Apps](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/lakebase).
- Databricks, [Lakebase authentication](https://docs.databricks.com/aws/en/oltp/projects/authentication).
- Databricks, [Databricks Apps authorization](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/auth) and [app permissions](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/permissions).
- Databricks, [HTTP headers in Databricks Apps](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/http-headers).
- Databricks, [Databricks Apps runtime](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-runtime) and [deployment](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/deploy).
- Databricks, [Lakebase connection pooling](https://docs.databricks.com/aws/en/oltp/projects/connection-pooling).
- OWASP, [Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

**Environment note**: Databricks documentation URLs above use the AWS documentation
set. Confirm the workspace cloud and matching resource/runtime instructions before
deployment.
