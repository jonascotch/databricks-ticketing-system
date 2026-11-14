# Databricks Lakebase Support App

A small Flask/Jinja ticketing app for a Databricks course assignment. Lakebase
PostgreSQL is the source of truth for tickets and messages.

## Set up Lakebase

1. Create a Lakebase Autoscaling database and attach it to the Databricks App
   using **App resources → Database**. The app resource provides the app's
   PostgreSQL role and connection environment variables.
2. Run `db/schema.sql` and then `db/seed.sql` in Lakebase SQL Editor.
3. If the SQL Editor user created the tables, grant the app service principal
   access to the `public` schema and tables. Replace `<APP_CLIENT_ID>` with the
   `DATABRICKS_CLIENT_ID` shown in the Databricks App environment:

   ```sql
   GRANT USAGE ON SCHEMA public TO "<APP_CLIENT_ID>";
   GRANT SELECT, INSERT, UPDATE
     ON tickets, ticket_messages
     TO "<APP_CLIENT_ID>";
   ```

The seed script uses stable IDs and `ON CONFLICT DO NOTHING`, so it can be
rerun without replacing later changes. It creates three tickets, two messages
per ticket, and multiple statuses.

## Run locally

Use the Databricks CLI to authenticate, then set the connection values for
your Lakebase endpoint. When running locally, `PGUSER` must be your Databricks
user identity, not the app service principal. `ENDPOINT_NAME` is the resource
endpoint path copied from the app resource configuration.

```text
PGHOST=<endpoint-host>
PGPORT=5432
PGDATABASE=<database-name>
PGUSER=<your-databricks-user>
PGSSLMODE=require
ENDPOINT_NAME=<lakebase-endpoint-path>
```

Install dependencies and start the app:

```bash
python -m pip install -r requirements.txt
python app.py
```

For local browser testing, send the Databricks identity header that the
platform reverse proxy supplies in deployment, for example:

```bash
curl -H "X-Forwarded-Preferred-Username: your-databricks-user" http://localhost:8000/
```

The app obtains a fresh OAuth database credential for each connection. Never
put database tokens or credentials in source files or logs.

## Deploy and verify

Deploy this project as a Databricks App with the Lakebase resource attached
and grant app access to the intended signed-in workspace users. Follow the
workflow in
[`specs/001-lakebase-support-app/quickstart.md`](specs/001-lakebase-support-app/quickstart.md)
to verify ticket listing, message history, ticket and message creation,
validation, status changes, and persistence after refresh.
