Plan: Create specs, agent identities, and SQL validator based on research_file.md blueprint

Goal
- Implement six artifacts strictly following the unified HLD/LLD, coding guardrails, and agent identity rules from the research blueprint.

Deliverables (files)
1. specs/platform_spec.md
   - Telecom core business rules: subscriber identifier rules, event taxonomy (CDR, usage, provisioning), canonical entity keys.
   - Time semantics: event timestamps, ingestion vs event time, watermark policy, allowed lateness and reconciliation windows.
   - Late-arriving data policy: hold-back window, replay handling, idempotency rules, reconciliation cadence and audit metrics.
   - Data quality & lineage: required validation gates, mandatory source tags, error handling and DLQ rules.

2. specs/coding_standards.md
   - SQL and pipeline casing: require lowercase SQL keywords, snake_case for identifiers, kebab-free filenames.
   - Join constraints: explicit JOIN with ON/USING required; forbid comma-style joins, CROSS JOIN, NATURAL JOIN, and joins without equality predicates unless temporally-bounded.
   - Naming and typing: canonical column names, primary key definitions, fixed varchar lengths, no SELECT *.
   - Testing & review rules: unit test coverage targets, pre-merge checks, commit message format, PR acceptance criteria.

3. specs/implementation_design.md
   - Phase-sequenced timeline: Discovery -> Ingest -> Staging -> Core transforms -> Validation -> Deploy -> Monitor.
   - Phase outputs, entry/exit criteria, owners, and estimated durations per phase.
   - Rollout strategy: feature flags, canary thresholds, backout plan, data migration steps.

4. ai_factory/agents/po_agent/agent.md
   - Product Owner persona: responsibilities, decision authority, acceptance criteria template, communication cadence with stakeholders and devs.
   - Boundaries: decisions PO may not make (architecture, infra budget), escalation flow, and SLAs for review/answers.
   - Guardrails: tone, allowed actions the agent can perform, and constraints per research_file.md.

5. ai_factory/agents/dev_agent/agent.md
   - Developer identity: responsibilities, coding guardrails from the blueprint (linting, tests, commit format), review responsibilities.
   - Allowed tool actions: create/modify code, run tests, propose migrations; disallowed actions (production DB writes, bypassing reviews).
   - Error and incident handling roles.

6. ai_factory/tools/sql_validator.py
   - Purpose: parse SQL, detect forbidden join patterns, enforce lowercase SQL keywords, and surface actionable errors.
   - Implementation notes: use `sqlglot` to validate syntax and optionally to normalize; use regex as a second layer to detect implicit/comma joins and uppercase keywords.
   - API: `validate_sql(sql: str) -> List[str]` returns error strings; `suggest_lowercase(sql: str) -> str` returns a keyword-lowercased version.

Execution steps
- Step A: Create the six files with outlined content above (populate content strictly following research_file.md).
- Step B: Implement `sql_validator.py` with tests and a small CLI helper to validate a SQL file or snippet.
- Step C: Run quick lint and unit checks locally; iterate if issues found.

Notes and assumptions
- This plan is strictly derived from the research blueprint referenced by the user (research_file.md). Exact wording and specific rules will be pulled into each file when creating them.
- Filenames and paths follow the workspace layout; all artifacts will be placed under `specs/` and `ai_factory/` as specified.

Next actions
- Create the six files and implement the validator. Request confirmation to proceed, or reply "go" to start file creation and implementation now.
