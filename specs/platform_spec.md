# Platform Core Specifications & Business Rules

This document is derived strictly from the unified HLD/LLD blueprint (`specs/research_and_ideation.md`) and captures the core telecom business rules, time semantics, and late-arriving data policies required by the platform.

## 1. Core Business Rules

- Subscriber identifiers: no plain-text PII (MSISDN/IMSI) may appear in the lakehouse. All subscriber identifiers must be ingested as deterministic cryptographic hashes using a cluster-level pepper-salt. Recommended: `MD5(CONCAT(raw_msisdn, '<SECRET_SALT>'))` or `SHA256(...)` when needed for stronger guarantees.
- Canonical entities and primary keys:
  - `dim_customer.customer_key_hash`: FixedString(32) MD5 salted hash (PK).
  - `fact_network_usage.usage_pk`: FixedString(32) MD5 of `customer_key_hash + '-' + toString(timestamp) + '-' + network_type` (PK).
  - `fact_revenue.transaction_pk`: FixedString(32) MD5 of `transaction_id + '-' + customer_key_hash` (PK).
- Event taxonomy: CDRs and usage events are treated separately from provisioning events. Expected canonical event columns include `event_type`, `timestamp` (UTC), `source_system`, and `raw_payload_location` (S3 object reference).

## 2. Time Semantics and Watermarking

- Event time is authoritative. Ingestion time is recorded but downstream computations must use event timestamps.
- Watermarking policy: adopt a 3-day sliding lookback window as the default late-arrival tolerance for network events (CDRs).
- All silver-tier incremental transformations must include a temporal predicate similar to:

```
WHERE event_timestamp >= now() - INTERVAL 3 DAY
```

- Reconciliation windows: daily reconciliation jobs must compare the last 7 days to detect persistent lag or increases in late-arriving volumes.

## 3. Late-Arriving Data Policy

- Hold-back Window: by default, ingest and staging allow up to a 3-day late-arrival buffer. Data older than 3 days must be processed via a distinct historical replay path.
- Replay Handling: replay jobs must be idempotent and must write to replacing tables that use the deterministic PK strategy (see PK rules above) or utilize ClickHouse `ReplacingMergeTree(sign_column)` semantics.
- Idempotency: producers and transformers must produce stable PKs for the same logical event. Systems must avoid using ingest-time UUIDs for deduplication.
- Reconciliation cadence: daily reconciliation runs with audit reports containing counts of new, updated, and deduplicated records.

## 4. Data Quality, Validation & Lineage

- Required validation gates during ingest:
  - Mandatory presence of `event_type`, `timestamp`, and `customer_key_hash` (or raw_msisdn which must be hashed immediately).
  - Numeric volume fields (`bytes_dl`, `bytes_ul`) must be >= 0.
- Lineage: every silver-tier table must include `source_file` and `ingest_timestamp` metadata columns.
- Dead-letter queue (DLQ): malformed or policy-violating rows must be routed to a DLQ location in object storage with a manifest describing rejection reason.

## 5. Privacy & GDPR

- PII must be removed or pseudonymized at ingestion. Implement a single-way hash plus cluster pepper/salt.
- Right-to-be-forgotten: flipping `gdpr_*` flags to `0` in `dim_customer` must trigger automated blanking (downstream propagation) and a record in the audit trail.

## 6. Operational Metrics & Audit

- Audit metrics to capture:
  - `ingested_count`, `deduplicated_count`, `dlq_count`, `late_arrival_count`, `replay_count` per source per day.
- Monitoring: expose these metrics to Prometheus with labels for `source_system`, `table`, and `pipeline_stage`.


---

Last updated: See `specs/research_and_ideation.md` for authoritative source.