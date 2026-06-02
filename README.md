# 📡 Telecom Cognitive Data Platform (TCDP)

An enterprise-grade, high-velocity cognitive analytics data platform designed to ingest network usage metrics, guarantee zero-data-loss, quarantine anomalies via a Dead Letter Queue (DLQ), and deliver an auditable, multi-layered Medallion warehouse using **ClickHouse** and **dbt**.

## 1. Project Mission & Objectives
The primary objective of TCDP is to bridge the gap between volatile, high-frequency network telemetric streams and actionable cognitive business intelligence.

### Core Value Propositions
* **100% Data Parity**: End-to-end alignment between raw source metrics and analytical dimensions.
* **Zero-Data-Loss Architecture**: Enforced via a strict, automated data reconciliation gate built directly into the continuous integration cycle.
* **Fault-Tolerant Ingestion**: Automated schema validation and isolation of malformed telemetric records into a secure Dead Letter Queue (DLQ).

## 2. Architecture & System Design
The platform implements a modern decoupling of storage and compute, leveraging **ClickHouse** for localized columnar processing and **dbt** for maintaining transformation states.

### Data Platform Layers
1. **Landing & Ingest Layer**: Stateless Python ingestion engine (`network_usage_ingester.py`) driven by dynamic configuration matrices. It reads raw feeds and streams them into a structured **Bronze Parquet format**.
2. **Medallion Warehouse (ClickHouse)**:
   * **Staging Layer**: Materializes schema abstractions, flattens Parquet payloads, and generates deterministic Primary Keys (`usage_pk`) along with salted, cryptographically secure customer key hashes (`customer_key_hash`).
   * **Silver Layer**: Eradicates late-arrival volatility by applying a sliding **3-day watermark window**.
   * **Core Analytical Layer**: A structured **Star-Schema** layout exposing optimized dimensional entities (`dim_customer`, `dim_time`, `dim_network_type`) and canonical fact components.

## 3. Interconnections, Dataflow & Workflows

### End-to-End Dataflow
```text
[Raw Feed] ──► [Ingestion Engine] ──┬──► (Valid Records) ──► [Bronze Parquet] ──► [Staging Views] ──► [Silver Facts] ──► [Core Dims]
                                    └──► (Malformed)     ──► [DLQ (JSON)]
```

### Operational Workflow
* **Ingest**: Raw telemetry is validated, normalized, and written to Bronze as Parquet; bad rows are quarantined to DLQ.
* **Staging**: Bronze records are transformed into deterministic staging views that preserve provenance and allow strict parity auditing.
* **Silver**: Canonical facts are generated with temporal resilience, using a configurable 3-day late-arrival watermark.
* **Core**: Star-schema dimensions and fact views are exposed for analytics, reporting, and downstream consumption.

### CI/CD and Quality Gates
* **Pre-commit hooks** validate formatting and static checks before code is committed.
* **`sql_validator.py`** performs Jinja-aware validation of SQL assets and enforces safe join patterns.
* **GitHub Actions** run service containers using ClickHouse and mount the Bronze dataset into the test environment.
* **Reconciliation gate** uses a `no_rows` dbt test to block deployments when staging and silver parity criteria are not met.

## 4. Enterprise Documentation
This repository is designed to serve as both a working data platform and an engineering blueprint for production teams. Key design assets include:
* `specs/platform_spec.md`
* `specs/implementation_design.md`
* `ai_factory/shared_memory/project_status.md`
* `ai_factory/tools/sql_validator.py`

## 5. Project Hygiene & Governance
* Build and runtime artifacts are intentionally excluded via `.gitignore`.
* Source code and documentation are maintained at the repository root and in structured subdirectories.
* A dedicated `tests/` folder houses integration and validation test cases.
* The platform is engineered for repeatable deployment, auditability, and enterprise readiness.

## 6. GitHub Projects Sync
* Automated synchronization is enabled via `.github/workflows/github_project_sync.yml`.
* The workflow reads `ai_factory/shared_memory/sprint_backlog.json` and `ai_factory/shared_memory/project_status.md` on every push to `main`.
* Configure `PROJECT_RECON_TOKEN` in repository secrets with a fine-grained PAT that has repository and project board read/write access.
* This ensures features, user stories, and task statuses remain aligned between the repo and GitHub Projects.
