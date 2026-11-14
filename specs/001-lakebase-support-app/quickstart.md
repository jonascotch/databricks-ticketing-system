# Quickstart: Lakebase Support App

This guide is the focused setup and end-to-end verification target. The source
files it references are planned in [plan.md](plan.md).

## Prerequisites

- A Databricks workspace with Databricks Apps and Lakebase Autoscaling.
- Permission to create or use a Lakebase database and Databricks App.
- Python 3.11 for dependency installation if needed.

## Configure and deploy

1. Create or select a Lakebase Autoscaling database.
2. Create a Databricks App and attach the Lakebase database as an app resource.
   The resource provides the app's managed database identity and connection
   settings; do not configure a static-password URL in source control.
3. Run `db/schema.sql` and then `db/seed.sql` in Lakebase SQL Editor.
   If the SQL Editor identity created the tables, grant the app's Lakebase role
   the schema and table permissions it needs to read and write ticket data.
4. Configure app permissions for the intended signed-in workspace users.
5. Install dependencies from `requirements.txt` if needed and deploy the app
   using Databricks Apps.
6. Open the deployed app and confirm that the seeded ticket list loads.

## End-to-end acceptance run

1. Confirm the ticket list shows seeded records and their statuses.
2. Open a seeded ticket and confirm at least two messages appear.
3. Create a ticket with a non-empty title. Confirm it appears with `open`
   status and the signed-in user as creator.
4. Add a non-empty message to that ticket. Confirm it appears in the thread
   with the signed-in user as author.
5. Change the status and refresh the app. Confirm the status and message remain
   persisted in Lakebase.
6. Submit a blank title or message and confirm the app shows a clear
   validation error without creating a record.
7. Open a ticket with several messages and confirm the full thread is shown
   without pagination. When testing competing status updates, if an update
   fails, confirm that the app shows an error and re-renders the ticket's
   latest database state.
8. Confirm a signed-in user with app access can use the workflows and a user
   without app access cannot open the app.

## Expected outcome

The deployed Databricks App reads and writes tickets and messages in Lakebase,
records the signed-in creator/author, and preserves changes after refresh.
