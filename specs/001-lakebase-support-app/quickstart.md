# Quickstart: Lakebase Support App

This guide is the end-to-end implementation and deployment validation target.
The source files it references are planned in [plan.md](plan.md).

## Prerequisites

- A Databricks workspace with Databricks Apps and Lakebase Autoscaling available.
- Permission to create/use a Lakebase database and Databricks App, and to grant
  the app service principal least-privilege database access.
- A Git folder or other supported app source location containing this project.
- Python 3.11 for local checks.

## Configure and deploy

1. Create or select a Lakebase Autoscaling database.
2. Create a Databricks App and attach the Lakebase database as an app resource.
   Grant the app's service principal only the database/schema privileges needed
   for migrations and ticket reads/writes. Do not configure a static-password
   URL in source control.
3. Configure the app's allowed-user permission for signed-in workspace users.
   The application records each user's trusted forwarded identity, while the
   attached Lakebase resource uses the app identity.
4. Install project dependencies and run the focused test suite:

   ```text
   python -m pip install -r requirements.txt
   python -m pytest
   ```

5. Configure the Flask/CSRF signing key using a Databricks secret resource.
   The Lakebase resource supplies the database connection credentials; do not
   create or commit a static Lakebase URL.
6. Deploy the app from the configured source using Databricks Apps. App startup
   applies ordered SQL migrations under a database advisory lock, seeds the
   demonstration data idempotently, then starts the production web server.
   Confirm the health check succeeds before exercising ticket flows.

## End-to-end acceptance run

1. Open the deployed app as a signed-in workspace user. Confirm the ticket list
   and statuses match the Lakebase records.
2. Open one seeded ticket and confirm both seeded messages appear in
   chronological order.
3. Create a ticket with a non-empty title. Confirm it appears with `open`
   status and the signed-in identity as creator.
4. Add a non-empty message to that ticket. Confirm it appears with the signed-in
   identity as author.
5. Change the status to `in_progress`, then refresh. Confirm the status and
   message remain persisted.
6. Change the status again to `resolved`; confirm a status-history entry was
   recorded. Submit an old version from a second browser/session and confirm
   the stale update is rejected without replacing the newer status.
7. Attempt to submit a blank title/message and an invalid status. Confirm
   helpful validation appears and no database records are added.
8. Confirm all actions work for any signed-in workspace user with app access,
   while unsigned or unauthorized users cannot reach the application.
9. Temporarily make the database unavailable in a non-production test
   environment. Confirm users receive a safe error and logs identify the
   failure without exposing secrets or message contents. Confirm `/healthz`
   reports process liveness independently of database availability.

## Expected outcome

The deployed app reads and writes tickets and messages in Lakebase, records the
signed-in actor, preserves data across refreshes, rejects invalid and stale
updates, and provides a verifiable minimal support workflow.
