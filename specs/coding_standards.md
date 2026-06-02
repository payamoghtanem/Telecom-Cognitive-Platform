# Coding Standards & Structural Constraints

Derived from `specs/research_and_ideation.md`. These standards are mandatory for all SQL, dbt, and Python assets produced by agents.

## 1. SQL Casing and Identifier Conventions

- SQL reserved keywords MUST be UPPERCASE (e.g., `SELECT`, `FROM`, `WHERE`, `JOIN`, `ON`).
- Table and column identifiers MUST be snake_case and lowercase (e.g., `dim_customer`, `customer_key_hash`).
- Filenames MUST avoid kebabs; prefer underscores and lowercase only.
- `SELECT *` is forbidden in all production models and transformations.

## 2. Join Constraints

- All joins MUST be explicit `JOIN` ... `ON` or `JOIN` ... `USING` with equality predicates for FK-PK joins.
- Forbidden join patterns:
  - Comma-style joins in `FROM` clauses (e.g., `FROM a, b`).
  - `NATURAL JOIN` and `CROSS JOIN` are prohibited.
  - Joins without an equality predicate (e.g., `JOIN t2` with no `ON`/`USING`) are prohibited unless the join is explicitly temporally-bounded and documented with a comment.

## 3. Naming, Typing and Schema Conventions

- Primary key columns must be explicitly named and defined in model docs (`usage_pk`, `customer_key_hash`).
- Use fixed string types with deterministic lengths where specified in the LLD (e.g., `FixedString(32)` for MD5 hashes).
- Enforce NOT NULL constraints on PK and critical business columns.

## 4. Testing, Reviews, and CI

- Unit test coverage targets: critical transform modules must include dbt tests (`not_null`, `unique`, custom range checks) and Python units for helper logic.
- PRs must include:
  - Description linking to `specs/platform_spec.md` or specific `sprint_backlog.json` task.
  - Generated dbt test plan or sample dataset to validate changes.
- Commit message format: `COMPONENT: Short description (TS-XXX)`.

## 5. Python Standards

- All functions and public callables MUST be type hinted.
- Avoid bare `except:` handlers; capture explicit exceptions and log through system observability channels.

## 6. Linting & Formatting

- SQL formatting: run SQL through `sqlglot` normalization and a standard SQL formatter in the pre-commit checks.
- Python: use `ruff`/`black` for linting/formatting in CI.

---

This file is normative: deviations require a documented exception in `ai_factory/shared_memory/project_status.md`.