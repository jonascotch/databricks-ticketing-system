<!-- Sync Impact Report
Version change: 1.0.0 → 2.0.0
Modified principles:
- I. User Value & Ticket Clarity (core assignment prioritized over optional bonuses)
- II. Data Integrity & Traceability (reduced to assignment-required persistence and relationships)
- III. Least-Privilege Security → III. Essential Databricks Security
- IV. Test-First Change Control → IV. Focused Testing & Verification
- V. Reliable Operations & Observability → V. Course-Scale Simplicity
Added sections: None
Removed sections: None
Modified sections:
- Data & Security Requirements
- Delivery Workflow & Quality Gates
Follow-up TODOs: None
-->

# Databricks Ticketing System Constitution

## Core Principles

### I. User Value & Ticket Clarity
The application MUST prioritize the course assignment's required ticket
workflows and Databricks feature use. Bonus features are optional and MUST NOT
delay the required outcome. Each implemented capability MUST have a clear user
purpose; avoid complexity that does not support an assignment requirement or
demonstration.

### II. Data Integrity & Traceability
Ticket and message records MUST persist in Lakebase and satisfy the fields,
relationships, and behavior required by the assignment. Required creator,
author, and timestamp information MUST be recorded, and invalid required input
MUST be rejected. Additional audit-history systems, concurrency controls, and
generalized recovery mechanisms are not required unless the assignment or a
specific observed failure calls for them.

### III. Essential Databricks Security
The application MUST use Databricks-managed authentication and app permissions
for access, and MUST use the supported Lakebase app resource or another
explicitly configured approved connection. Credentials MUST NOT be committed
to source control or exposed in logs. The app MUST NOT add custom identity
fallbacks, role hierarchies, or security layers beyond platform defaults and
assignment requirements unless a concrete risk requires them.

### IV. Focused Testing & Verification
Validation MUST cover the required user workflows, Lakebase persistence, and
Databricks deployment. Prefer a small set of focused automated or repeatable
checks over broad test suites. Full coverage targets, load testing, resilience
testing, and mandatory test-first development for every change are not
required unless the assignment or a specific risk requires them.

### V. Course-Scale Simplicity
Operations MUST provide enough feedback to demonstrate successful use and
diagnose ordinary setup or connection errors. A basic health check and
actionable user-facing errors are sufficient. Production-grade availability,
automated failover, extensive telemetry, and retry frameworks are out of
scope unless explicitly required by the assignment.

## Data & Security Requirements

The project MUST use Lakebase as the source of truth for ticketing data and
implement the required ticket/message relationship and sample records. It
MUST validate required user inputs and avoid hard-coded application data.
Databricks and Lakebase credentials MUST be supplied through supported app
resources or approved secret storage, never hard-coded in application files
or committed.

The app MUST rely on Databricks authentication and the configured app access
permissions. It MUST avoid logging credentials and unnecessary ticket content.
Separate user roles, custom authentication fallbacks, extensive audit
infrastructure, and additional security controls are optional unless the
assignment, platform, or a concrete identified risk requires them.

## Delivery Workflow & Quality Gates

Work MUST be scoped to the required course outcomes first: create and seed the
Lakebase schema, implement the required ticket workflows, deploy the Databricks
App, and verify persistence after refresh. Focused checks MUST demonstrate
those outcomes before the feature is considered complete. Optional bonuses
MAY be added after the required workflows are verified.

Reviews, test suites, documentation, and operational controls MUST remain
proportionate to this course project. Production-grade process is not required
unless the project is later adopted for real operational use. If the project
scope changes, the constitution and relevant design artifacts MUST be reviewed
for appropriate updates.

## Governance

This constitution governs the Databricks ticketing system and supersedes
informal process when they conflict. Amendments require written rationale, a
clear impact assessment, and explicit approval by the project maintainer or
designated reviewer before the policy takes effect.

All work MUST be evaluated against this constitution during review. The
project MUST version amendments using semantic versioning: major for
incompatible governance changes, minor for new or materially expanded
principles, and patch for clarifications or non-semantic wording updates.
Compliance expectations MUST remain proportionate to the course assignment;
production controls become applicable only if project scope changes.

**Version**: 2.0.0 | **Ratified**: 2026-11-13 | **Last Amended**: 2026-11-13
