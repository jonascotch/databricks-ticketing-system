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

## Run locally without the Databricks CLI

1. Install and start Docker Desktop with Docker Compose. If you use the Ubuntu
   terminal through WSL, enable Docker Desktop's WSL integration for that
   distribution.
2. From the project root, build and start the app and PostgreSQL database:

```bash
docker compose up --build
```

3. Wait until the `app` and `db` services report ready, then open
   [http://localhost:8000](http://localhost:8000). The app attributes local
   changes to `local-developer`.

Compose builds the Flask app container and starts a PostgreSQL container. On
the database's first startup, it runs `db/schema.sql` and `db/seed.sql`
automatically. Local mode uses the development-only `LOCAL_DEV_USER` identity
and PostgreSQL credentials in `docker-compose.yml`; it does not request
Databricks credentials or require the Databricks CLI.

To stop the foreground services, press **Ctrl+C**. To start them in the
background, use `docker compose up --build --detach`; view app logs with
`docker compose logs --follow app` and stop the services with
`docker compose down`.

The database persists in a Docker volume across restarts. To delete the local
database and all its data (including tickets you created), run
`docker compose down --volumes`; the next `docker compose up --build`
initializes it again. The SQL initialization scripts run only when the database
volume is empty. These credentials and the local identity are for development
only. Databricks deployment continues to use the managed Lakebase resource and
OAuth credentials.

## Deploy and verify

Deploy this project as a Databricks App with the Lakebase resource attached
and grant app access to the intended signed-in workspace users. Follow the
workflow in
[`specs/001-lakebase-support-app/quickstart.md`](specs/001-lakebase-support-app/quickstart.md)
to verify ticket listing, message history, ticket and message creation,
validation, status changes, and persistence after refresh.
