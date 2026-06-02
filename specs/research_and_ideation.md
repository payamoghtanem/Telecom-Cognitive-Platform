```markdown
# 📡 TELECOM COGNITIVE & AGENTIC DATA PLATFORM
## 📘 Comprehensive Architecture, Engineering Blueprint, and Multi-Agent Lifecycle Contract
**Specification-Driven Development (SDD) Reference Standard — Year 2026**

---

## 🗺️ 1. Executive Vision & Architectural Pivot

### 1.1 Objective
The purpose of this platform is to move away from a traditional transactional microservice mesh (which incurs high configuration overhead without business differentiation) and instead implement a **Cognitive Data & Agentic Decision Platform**. The system treats upstream operational telecom entities (BSS/OSS) as pre-existing data streams. It is designed to ingest massive network activity logs, process them idempotently, run predictive machine learning routines (such as churn or network load analysis), and orchestrate a zero-trust multi-agent system that autonomously manages tasks, validates quality gates, and generates reports.

### 1.2 Core Philosophy
* **Specification-Driven Development (SDD):** System definitions, code formats, data contracts, and agent behaviors are locked in static markdown files before code execution.
* **Prompt Modularization (Agents-as-Code):** Large prompts are broken up. Agent identity, runtime skills, business context, and global standards are stored in distinct files to prevent context degradation and model hallucinations.
* **Zero-Trust Line Assembly:** No single agent compiles and pushes code directly to production without deterministic validation gates that run without LLM dependencies.

---

## 🏗️ 2. High-Level Design (HLD) & System Topology

### 2.1 Macro System Topology
The platform implements a cloud-native, decoupled Big Data Lakehouse layer closely coupled with an asynchronous multi-agent framework.


```

+---------------------------------------------------------------------------------------------------------+
|                                  MOCK LAYER (Python Data Synthesizer)                                   |
|                          - Generates high-velocity CDR (Call Detail Records)                           |
+----------------------------------------------------+----------------------------------------------------+
| (S3 API / Parquet Object Uploads)
v
+---------------------------------------------------------------------------------------------------------+
|                                INGESTION & STORAGE LAYER (Object Storage)                               |
|                         - MinIO / AWS S3 Bucket (data/bronze/ landing partition)                        |
+----------------------------------------------------+----------------------------------------------------+
| (dbt ClickHouse Adapter Pipelines)
v
+---------------------------------------------------------------------------------------------------------+
|                              ANALYTICS & COMPUTATIONAL WAREHOUSE (Silver Layer)                         |
|                 - ClickHouse Columnar DB (Star Schema Optimized with ReplacingMergeTree)                 |
+----------------------------------------------------+----------------------------------------------------+
| (SQL Queries / Python API Matrix)
v
+----------------------------------------------------+----------------------------------------------------+
|                                      COGNITIVE & PREDICTIVE LAYER                                       |
|  +------------------------------------------------+    +---------------------------------------------+  |
|  |             ML PREDICTIVE ENGINE               |    |                  BI PORTAL                  |  |
|  |     - XGBoost / PyTorch Churn Prediction       |    |     - Analytical Semantic Model / Reports   |  |
|  +---------------------------------------+--------+    +--------+------------------------------------+  |
+------------------------------------------|----------------------|---------------------------------------+
v                      v
+---------------------------------------------------------------------------------------------------------+
|                                    AGENTIC ORCHESTRATION ENGINE                                         |
|                       - Multi-Agent Line Assembly Graph (LangGraph / CrewAI Framework)                  |
+---------------------------------------------------------------------------------------------------------+
|                                     OBSERVABILITY & TELEMETRY                                           |
|                           - Prometheus Metrics Server & Grafana Dashboards                              |
+---------------------------------------------------------------------------------------------------------+

```

### 2.2 Core Tech Stack
* **Storage Layer:** MinIO or AWS S3 storing highly compressed `.parquet` files.
* **Compute Database:** ClickHouse Columnar Storage (utilizing `ReplacingMergeTree` for real-time deduplication).
* **Transformation Matrix:** dbt (Data Build Tool) utilizing the ClickHouse adapter.
* **Predictive Framework:** Python 3.11, Scikit-Learn, XGBoost.
* **Orchestration Matrix:** GitHub Codespaces / VS Code runtimes orchestrating LangGraph or CrewAI structures.
* **Deterministic Guardrails:** Native Python parser powered by the `sqlglot` abstract syntax tree engine.
* **Observability Vector:** Prometheus server paired with Grafana for runtime dashboards tracking pipeline throughput and agent metrics.

---

## 📊 3. Low-Level Design (LLD) & Data Contracts

### 3.1 Analytical Star Schema Model


```

```
    +---------------------------------+
    |          dim_customer           |
    +---------------------------------+
    | PK | customer_key_hash (MD5)    | <---------+
    |    | city                       |           |
    |    | state                      |           |
    |    | gdpr_marketing_allowed     |           |
    |    | gdpr_profiling_allowed     |           |
    +---------------------------------+           |
                                                  |
                                                  | (1:N Connection)
                                                  |
    +---------------------------------+           |
    |     fact_network_usage          |           |
    +---------------------------------+           |
    | PK | usage_pk (MD5)             |           |
    | FK | customer_key_hash          | ----------+
    |    | timestamp                  |
    |    | bytes_dl                   |
    |    | bytes_ul                   |
    |    | network_type (4G/5G)       |
    |    | speed_throttling_status    |
    +---------------------------------+

```

```

#### 3.1.1 Staging & Silver Layer Schema Contracts
1. **`dim_customer`**
   * `customer_key_hash` (String, FixedString(32)): Primary key generated via a deterministic salted cryptographic hash (`MD5(CONCAT(raw_msisdn, 'SECRET_SALT'))`).
   * `city` (String): Normalized customer location name.
   * `state` (String): Region name.
   * `gdpr_marketing_allowed` (UInt8): Explicit binary constraint flag (`0` = Denied, `1` = Approved).
   * `gdpr_profiling_allowed` (UInt8): Explicit profiling validation constraint flag.

2. **`fact_network_usage`**
   * `usage_pk` (String, FixedString(32)): Primary Key formed by: `MD5(CONCAT(customer_key_hash, '-', toString(timestamp), '-', network_type))`.
   * `customer_key_hash` (String, FixedString(32)): Foreign key linking to `dim_customer`.
   * `timestamp` (DateTime): Epoch time of network connection slice.
   * `bytes_dl` (UInt64): Total downlinked payload volume. Must be $\ge 0$.
   * `bytes_ul` (UInt64): Total uplinked payload volume. Must be $\ge 0$.
   * `network_type` (Enum8): Explicit domain strings constraint: `('4G' = 1, '5G' = 2)`.
   * `speed_throttling_status` (UInt8): Boolean indicating if a policy throttle was tripped.

3. **`fact_revenue`**
   * `transaction_pk` (String, FixedString(32)): Primary Key formed by `MD5(CONCAT(transaction_id, '-', customer_key_hash))`.
   * `customer_key_hash` (String, FixedString(32)): Foreign key linking to `dim_customer`.
   * `amount_vat_excluded` (Float64): Absolute net currency line item.
   * `vat_amount` (Float64): Applied tax value.
   * `payment_method` (Enum8): Local domain constraints: `('Direct Debit' = 1, 'Credit Card' = 2, 'Prepaid Balance' = 3)`.

---

## 🤖 4. Multi-Agent Ecosystem Framework

### 4.1 System Agents Identity Matrix


```

+-----------------------------------------------------------------------------------+
|                            MULTI-AGENT SYSTEM ECOSYSTEM                           |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  +---------------------------+                     +---------------------------+  |
|  |    PRODUCT OWNER AGENT    |                     |      DEVELOPER AGENT      |  |
|  | - Parses Specifications   |                     | - Generates SQL & Python  |  |
|  | - Manages Sprints/Status  |                     | - Focuses on Pipe Logic   |  |
|  +-------------+-------------+                     +-------------+-------------+  |
|                |                                                 |                |
|                | (State Transitions)                             | (Emits Code)   |
|                v                                                 v                |
|  +---------------------------+                     +---------------------------+  |
|  |    PROJECT STATUS REPORT  |                     |    COMPLIANCE AUDITOR     |  |
|  | - Markdown Matrix Tracking|                     | - AST sqlglot Execution   |  |
|  | - Bottleneck Logging      |                     | - Non-LLM Code Enforcement|  |
|  +---------------------------+                     +-------------+-------------+  |
|                                                                  |                |
|                                                                  | (Approved Code)|
|                                                                  v                |
|                                                    +---------------------------+  |
|                                                    |   QA AUTOMATION AGENT     |  |
|                                                    | - dbt test suites         |  |
|                                                    | - PyTest regressions      |  |
|                                                    +---------------------------+  |
+-----------------------------------------------------------------------------------+

```

#### 4.1.1 Product Owner Agent Specification Contract
* **File Target Location:** `ai_factory/agents/po_agent/agent.md`
* **Role Blueprint:** High-fidelity Requirements Decomposition Engineer and Scrum Master.
* **Operational Rules:**
  1. Parse `specs/platform_spec.md` to map dependencies and populate `ai_factory/shared_memory/sprint_backlog.json`.
  2. Maintain and format the tracking array inside `ai_factory/shared_memory/project_status.md` without data schema drift.
  3. Prohibited from compiling raw business source code strings.

#### 4.1.2 Developer Agent Specification Contract
* **File Target Location:** `ai_factory/agents/dev_agent/agent.md`
* **Role Blueprint:** Core Telecom Pipeline Engineer specializing in high-throughput ClickHouse transformations.
* **Operational Rules:**
  1. Pull active tasks from `sprint_backlog.json` marked as `READY_FOR_DEVELOPMENT`.
  2. Implement optimized modular dbt logic leveraging architectural patterns documented in `skill.md`.
  3. If parameters are ambiguous or conflicting, halt execution immediately and update the task state to `BLOCKED`.

#### 4.1.3 Compliance Auditor Agent Specification Contract
* **File Target Location:** `ai_factory/agents/auditor_agent/agent.md`
* **Role Blueprint:** Abstract Syntax Tree (AST) Guardrail and Formatting Enforcer.
* **Operational Rules:**
  1. Intercept any written `.sql` or `.py` asset before repository persistence.
  2. Programmatically invoke `ai_factory/tools/sql_validator.py` to evaluate queries.
  3. Reject code structures that contain forbidden keywords or styles. Do not use LLM tokens for standard checks.

#### 4.1.4 QA Automation Agent Specification Contract
* **File Target Location:** `ai_factory/agents/qa_agent/agent.md`
* **Role Blueprint:** Runtime Test Harness Suite Generator.
* **Operational Rules:**
  1. Read implemented staging tables and automatically generate YAML data test configurations.
  2. Execute structural boundary tests (`not_null`, `unique`, check ranges).
  3. Log failure reports to shared execution blocks.

---

## 🛠️ 5. Tool Specifications & Interface Contracts

### 5.1 Deterministic State Update Tool (`report_helper.py`)
* **Interface Specification:** Modifies the live markdown status matrix without destroying surrounding headers or metric annotations.
* **Method Profile:** `update_task_status(task_id: str, new_status: str, note: str) -> None`
* **Source Blueprint:**
```python
import os
from typing import List

class ProjectStatusReporter:
    def __init__(self, report_path: str = "ai_factory/shared_memory/project_status.md"):
        self.report_path = report_path

    def update_task_status(self, task_id: str, new_status: str, note: str = "") -> None:
        if not os.path.exists(self.report_path):
            return
        with open(self.report_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        updated_lines: List[str] = []
        for line in lines:
            if task_id in line and "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 6:
                    parts[5] = f"**{new_status}**" if any(x in new_status for x in ["🛑", "⏳"]) else new_status
                    if note:
                        parts[6] = note
                    line = " | ".join(parts) + "\n"
            updated_lines.append(line)
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

```

### 5.2 AST SQL Validation Engine (`sql_validator.py`)

* **Interface Specification:** Inspects queries for syntactical compliance. Uses the `sqlglot` library to detect uncapitalized keywords or prohibited join patterns.
* **Method Profile:** `validate_query(raw_sql: str) -> dict`
* **Source Blueprint:**

```python
import re
import sqlglot
from sqlglot import exp

class SQLComplianceValidator:
    def __init__(self, raw_sql: str):
        self.raw_sql = re.sub(r'\{\{[\s\S]*?\}\}', 'mock_table', raw_sql)
        self.errors = []

    def validate(self):
        for kw in ['select ', 'from ', 'where ', 'join ']:
            if re.search(r'\b' + kw + r'\b', self.raw_sql):
                self.errors.append(f"Standard Violation: Keyword '{kw.strip()}' must be UPPERCASE.")
        try:
            expression = sqlglot.parse_one(self.raw_sql, read="clickhouse")
            for join_node in expression.find_all(exp.Join):
                kind = join_node.args.get("method")
                if kind and kind.upper() in ["CROSS", "FULL"]:
                    self.errors.append(f"Security Violation: {kind.upper()} JOIN is forbidden.")
        except Exception as e:
            self.errors.append(f"Syntax Error Check Fail: {str(e)}")
        return {"is_compliant": len(self.errors) == 0, "errors": self.errors}

```

---

## 📜 6. Standards, Policies, and Data Governance

### 6.1 Late-Arriving Data & Idempotence Policy

* **3-Day Sliding Lookback Window:** Telecom network events (CDRs) can arrive delayed due to transmission lags across localized cellular towers.
* To resolve this without running expensive full-table scans, all silver-tier incremental dbt updates must enforce a rolling temporal boundary condition:

$$\text{Event\_Timestamp} \ge \text{Current\_Date} - \text{INTERVAL 3 DAY}$$


* Target tables must use the ClickHouse `ReplacingMergeTree(sign_column)` or define deterministic unique primary key hashes (`usage_pk`) to override duplicate event deliveries during merging windows.

### 6.2 GDPR & Privacy Enforcements

* **Cryptographic PII Shredding:** MSISDN (mobile numbers) or IMSI (SIM card identifiers) are strictly barred from appearing as plain text inside the lakehouse.
* Systems must execute a single-way SHA256 or MD5 evaluation using a secure cluster-level pepper-salt variable configuration.
* Right-to-be-forgotten requests must flip the `gdpr_marketing_allowed` and `gdpr_profiling_allowed` flags within `dim_customer` to `0`, triggering downstream automated blanking queries.

### 6.3 Code Quality Constraints Matrix

* **SQL Standards:** Reserved commands (`SELECT`, `INSERT`, `JOIN`, `PREWHERE`, `INCREMENTAL`) must be written in full uppercase. Table properties and column metrics must be strictly lowercase snake_case.
* **Python Standards:** Every runtime function must provide type hints. Bare `except:` catch wrappers are prohibited; error monitoring must capture specific exceptions (`ValueError`, `FileNotFoundError`) and route them through system log streams.

---

## 🔄 7. Operational Workflow & System Execution Sequences

### 7.1 Multi-Agent Processing Sequence

```
[Product Owner] ----> Read specifications & populate sprint_backlog.json
       |
       v
[Developer Agent] --> Read task -> Flag 'IN_PROGRESS' in project_status.md -> Write dbt SQL
       |
       v
[Auditor Agent] ----> Programmatically call sql_validator.py (Verify uppercase & no CROSS JOIN)
       |
       +---> If Compliant ----> Forward code to QA Agent
       +---> If Non-Compliant -> Mark 'BLOCKED' in project_status.md -> Halt & alert Human-in-the-Loop
       |
       v
[QA Automation] ----> Run data check tests -> Mark 'DONE' -> Complete pipeline lifecycle loop

```

### 7.2 Human-in-the-Loop (HITL) Interventions for Bottlenecks

* When an engineering bottleneck is encountered, the processing chain enters a safety state.
* The system changes the task status in the matrix to `🛑 BLOCKED`.
* A detailed explanation is written directly into the `⚠️ Bottlenecks & Critical Alerts` section of `project_status.md`.
* The system pauses processing loops and hooks into active workspace listeners, waiting for a human developer to modify the configuration or approve the exception path.

---

## 📂 8. Standardized Directory Tree

```text
.
├── specs/
│   ├── platform_spec.md            # Platform Core Specifications & Business Rules
│   ├── coding_standards.md         # Formatting Guardrails & Prohibited Structural Constraints
│   ├── implementation_design.md    # Phase Roadmap Sequences
│   └── research_and_ideation.md    # Domain Reference Ingestion History
├── data-synthesizer/
│   └── cdr_generator.py            # Automated High-Velocity Stream Generator Script
├── data/
│   └── bronze/                     # Landing Directory Partition for Raw Parquet Assets
├── ai_factory/
│   ├── agents/
│   │   ├── po_agent/
│   │   │   └── agent.md            # Product Owner Identity Definition File
│   │   ├── dev_agent/
│   │   │   ├── agent.md            # Software Developer Identity Definition File
│   │   │   └── skill.md            # Analytical Coding Code-Blueprints
│   │   └── auditor_agent/
│   │       └── agent.md            # Compliance Auditor Boundary Constraints
│   ├── tools/
│   │   ├── report_helper.py        # Matrix State Mutation Asset
│   │   └── sql_validator.py        # Native AST Compliance Parser Tool
│   └── shared_memory/
│       ├── sprint_backlog.json     # Machine-Readable Task Array Queue
│       └── project_status.md       # Human-Readable Live Tracking Report Interface
└── README.md

```

---

## 🏁 9. Master Production Configuration State Template

### 9.1 Base Backlog Matrix Template (`sprint_backlog.json`)

```json
[
  {
    "task_id": "TS-001-STG-USAGE",
    "component": "dbt-silver",
    "user_story": "As a downstream BI Agent, I want network usage records aggregated with a 3-day sliding lookback window so that late-arriving logs are processed idempotently without full-table scans.",
    "acceptance_criteria": [
      "Generate composite primary key named usage_pk using MD5(CONCAT(customer_key, '-', date_key, '-', geo_key)).",
      "Implement dbt incremental filtering using template condition: event_date >= tomorrow() - INTERVAL 3 DAY.",
      "Enforce data contracts: bytes_dl and bytes_ul must be greater than or equal to 0."
    ],
    "context_anchor": "specs/platform_spec.md#section-2",
    "status": "READY_FOR_DEVELOPMENT"
  }
]

```

### 9.2 Base Report Presentation Layout Template (`project_status.md`)

```markdown
# 📊 Live Project Status Report (State: Initialized)

## 🎯 Current Phase: Phase 1 - Multi-Agent Engine Verification

## 🏎️ Task Matrix Overview
| Task ID | Component | Description | Assigned Agent | Status | Notes / Blockers |
| :--- | :--- | :--- | :--- | :--- | :--- |
| TS-000 | Core-Setup | Initialize Multi-Agent Folder Structure & SSOT Specs | Product Owner | ✅ DONE | System environment successfully verified on disk |
| TS-001 | dbt-silver | Staging fact network usage tracking model | Developer | 📝 TODO | Awaiting multi-agent ingestion pipeline execution |

## ⚠️ Bottlenecks & Critical Alerts
- *No critical operational blocks or data exceptions are currently logged.*

## 📝 Engineering Log Entries
- Baseline specifications locked. Environment ready for full automated execution sweeps.

```

```

```