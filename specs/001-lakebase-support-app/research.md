# Research: Lakebase Support App

**Date**: 2026-11-13

## Decision 1: Reuse the reference app's structure, not its unrelated features

**Decision**: Use one Flask application, server-rendered Jinja templates, and a
small Lakebase helper module. Do not copy the reference's Massive API client,
batch sync, stock watchlist, or unrelated dependencies.

**Rationale**: The reference is organized around `app.py`, `lakebase.py`,
`templates/`, and `app.yaml`, which fits the small ticket workflows. A
server-rendered app avoids the extra deployment and integration work of a
separate frontend and API.

**Alternatives considered**:

- **Copy the repository unchanged**: rejected because its Massive API data
  model and synchronization features are unrelated.
- **FastAPI plus a separate frontend**: rejected because the assignment needs
  only a small set of form-and-list workflows.
- **Streamlit**: viable for a prototype, but Flask/Jinja more closely follows
  the requested reference structure.

## Decision 2: Use a managed Lakebase resource and app identity

**Decision**: Attach Lakebase Autoscaling as a Databricks App resource and use
the documented app identity/OAuth connection flow with psycopg. Do not use a
static-password URL.

**Rationale**: The app resource configures the app's database connection and
managed role. The app's service principal is the shared database identity;
app permissions determine who can access the app. A forwarded user identity
can be recorded for ticket attribution, but does not make database queries run
as each visitor.

**Alternatives considered**:

- **Static native-password URL**: rejected because the managed app resource is
  the supported simpler course setup.
- **Per-user Lakebase access**: not needed for the clarified shared access
  model and requires additional OAuth role handling.
- **Lakebase Data API**: not needed for this small server-rendered app.

## Decision 3: Keep database initialization to two SQL files

**Decision**: Keep the two-table schema in `db/schema.sql` and the required
sample records in `db/seed.sql`. Run them in Lakebase SQL Editor as part of
workspace setup. Make seed inserts repeatable without overwriting later user
changes.

**Rationale**: The course requires a simple schema and sample data, not a
migration framework. A manual SQL Editor workflow is sufficient and keeps the
database setup visible and easy to explain.

**Operational caveat**: Objects created by the SQL Editor identity are not
automatically accessible to the app's service principal. Grant the app's
Lakebase role the necessary schema and table permissions, or create the
objects under the app role. With public access disabled, multi-statement SQL
may partially commit if a statement fails.

**Alternatives considered**:

- **Versioned migrations with a lock and migration table**: rejected as
  unnecessary infrastructure for the fixed course schema.
- **Create tables during requests or each app start**: rejected because
  request handling should not perform setup DDL.

## Decision 4: Keep required verification focused

**Decision**: Validate the deployed app by exercising list/detail, ticket
creation, message creation, status update, and refresh persistence.

**Rationale**: These checks directly cover the assignment's acceptance
criteria. Broad coverage, load, concurrency, and resilience suites are
disproportionate to the course scope.

## Sources

- User-provided reference repository: [databricks-lakebase-app-day-1](https://github.com/jonascotch/databricks-lakebase-app-day-1).
- Databricks, [Add a Lakebase resource to a Databricks App](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/lakebase).
- Databricks, [Databricks Apps resources](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/resources).
- Databricks, [App environment variables](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/environment-variables).
- Databricks, [Lakebase connection tutorial for Databricks Apps](https://docs.databricks.com/aws/en/oltp/projects/tutorial-databricks-apps-autoscaling).
- Databricks, [Lakebase authentication](https://docs.databricks.com/aws/en/oltp/projects/authentication).
- Databricks, [Lakebase SQL Editor](https://docs.databricks.com/aws/en/oltp/projects/sql-editor).
- Databricks, [Databricks Apps authorization](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/auth).
- Databricks, [Lakebase Postgres roles](https://docs.databricks.com/aws/en/oltp/projects/postgres-roles).

**Environment note**: The Databricks documentation URLs use the AWS
documentation set. Confirm the matching instructions for the workspace cloud
before deployment.
