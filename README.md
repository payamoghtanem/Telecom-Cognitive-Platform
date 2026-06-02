# Telecom Cognitive Platform

## 1. Project Mission & Objectives

The Telecom Cognitive Platform is a production-grade data platform designed to ingest high-velocity network telemetry, quarantine anomalous or malformed records through a Dead Letter Queue (DLQ), and deliver clean, auditable analytical schemas across Staging, Silver, and Core layers.

Core value propositions:

- **100% Data Parity:** Every transformed analytical record is reconciled against source Bronze data with strict row- and aggregate-level validation.
- **Automated CI/CD Gating:** Pull request validation is enforced by Jinja-aware SQL linting and reconciliation test rules to prevent regressions.
- **Zero-Data-Loss:** Malformed or unexpected records are quarantined to DLQ storage instead of being silently dropped.

## 2. Architecture & System Design

### Architectural Layers

- **Landing & Ingest Layer**
  - Built in Python with configurable JSON ingestion settings.
  - Reads raw network usage input, validates each row, and writes Bronze output as Parquet.
  - Invalid rows are routed to a DLQ for downstream remediation.

- **Medallion Storage Layer**
  - Implemented on ClickHouse with dbt.
  - Bronze: source Parquet files representing raw, ingested telemetry.
  - Staging: deterministic staging views that normalize schema, timestamps, and surrogate keys.
  - Silver: canonical fact model with business-ready aggregates and a late-arrival watermark window.
  - Core: star-schema dimensions and fact tables optimized for analytics and lineage.

- **Security & PII Governance**
  - Customer identifiers are protected with hashed keys using salted SHA-256 / MD5 hashing.
  - This ensures customer identity is masked while preserving referential integrity.

### Key Entities

- `Network Usage Raw`
  - Raw telemetry data arriving into the landing zone.
  - Stored as source Parquet after validation and normalization.

- `stg_fact_network_usage`
  - Staging layer model that applies deterministic primary keys and preserves cleaned raw fields.
  - Normalizes timestamp semantics and prepares data for reconciliation.

- `silver_fact_network_usage`
  - Canonical fact model that applies business rules and enforces the 3-day late-arrival watermark window.
  - Produces analytically consistent metrics for downstream consumers.

- `dim_customer`
  - Core dimension model offering hashed customer identifiers and enriched customer attributes.
  - Designed for safe, privacy-aware joins with fact models.

- `audit_reconciliation`
  - Reconciliation model acting as a strict gate.
  - Compares staging and silver outputs for row counts and aggregate bytes.
  - Fails pipeline validation when parity rules are not satisfied.

## 3. Dataflow & Workflow (Interconnections)

### Data Movement

1. **Ingester** reads inbound telemetry and applies schema validation.
2. **Validation Guard** quarantines malformed records to the DLQ and allows only clean records to reach Bronze.
3. **Bronze Parquet** persists normalized raw data with stable timestamp typing.
4. **Staging** consumes Bronze and generates deterministic surrogate keys for each network usage row.
5. **Silver** materializes canonical facts using a 3-day late-arrival watermark window, ensuring late data is included correctly.
6. **Core** produces dimensions and enterprise-ready fact structures for analytics and reporting.

### CI/CD Quality Gates

- **Pre-commit hooks** review SQL and prevent obvious issues before code reaches source control.
- **`sql_validator.py`** performs Jinja-aware SQL validation across dbt models and macros.
- **GitHub Actions** run service containers with ClickHouse and mount `data/bronze` into a user-files volume.
- **`no_rows` reconciliation test** is enforced as a failure rule, ensuring any parity mismatch breaks the pipeline.

## 4. Product Backlog, User Stories & Tasks

### Epics

- **Epic 1: Ingestion & DLQ Protection**
  - Build a resilient ingest pipeline that handles network telemetry and quarantines invalid rows.
  - Status: **ACTIVE**

- **Epic 2: Core Star-Schema Transforms**
  - Implement staging, canonical silver facts, and core dimension models.
  - Status: **PENDING**

- **Epic 3: Observability & Monitoring**
  - Add audit gating, reconciliation metrics, and CI visibility for data quality.
  - Status: **PENDING**

### User Stories

- **Story 1:** As a Network Analyst, I want late-arriving records up to 3 days to be automatically reconciled so analytics remain accurate.
  - Acceptance Criteria:
    - Silver fact model applies a 3-day watermark.
    - Reconciliation test verifies row and byte parity.
    - Late-arriving records are included in the canonical fact when within the window.

- **Story 2:** As a Data Engineer, I want malformed network records quarantined to a DLQ so no invalid data enters the analytical pipeline.
  - Acceptance Criteria:
    - Invalid rows are detected during ingest.
    - Clean records are written to Bronze Parquet.
    - DLQ JSON captures the original malformed payload and error context.

- **Story 3:** As a Platform Owner, I want every deployment gated by automated CI rules so regressions are blocked before entering production.
  - Acceptance Criteria:
    - SQL validation runs on every PR.
    - ClickHouse container mount is used in GitHub Actions.
    - `no_rows` reconciliation failure stops the build.

### Current Task Status

- `TS-000: Core-Setup` — **DONE**
- `TS-001: ingest` — **ACTIVE**
- `TS-002: dbt-silver` — **PENDING**

## 5. Modern Executive Status Report

- **Ingest & Staging:** 100% DONE
- **CI/CD Gating:** Fully green and enforced
- **Core Transforms:** ACTIVE

> This platform is now a production-ready blueprint for telecom telemetry ingestion, audit-grade reconciliation, and enterprise analytics on ClickHouse and dbt.
