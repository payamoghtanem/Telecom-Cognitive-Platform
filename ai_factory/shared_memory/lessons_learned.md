# Lessons Learned & Troubleshooting Notes

Project work summary for Telecom Cognitive Platform:

- Completed work:
  - Implemented ingest pipeline fixes to preserve UTC-aware Bronze Parquet timestamps.
  - Added staging/silver/core models and reconciliation gate (`audit_reconciliation`).
  - Created enterprise-grade root `README.md` and cleaned repo structure (`tests/`, `.gitignore`).
  - Added automated GitHub Projects sync workflow and helper script.
  - Documented GitHub Projects sync setup in `README.md`.

- Lessons learned:
  - GitHub Actions workflows require explicit `projects: write` permissions for Projects V2 API access.
  - `GITHUB_TOKEN` can be used as a fallback for automation, but a dedicated PAT secret is preferred for project board access.
  - `dbt_project.yml` and `.pre-commit-config.yaml` should remain at repo root for standard dbt and pre-commit operation.
  - ClickHouse/Parquet timestamp fields must be stable and UTC-aware to avoid adapter/type mismatch failures.
  - Generated build artifacts must be excluded from git with `.gitignore` and removed from cache to keep repo clean.
  - Automating project board sync requires precise parsing of backlog/status files and mapping statuses to GitHub Project fields.

- Problems encountered:
  - Initial workflow failure due to missing `PROJECT_RECON_TOKEN` secret.
  - Shell quoting issues when overwriting `README.md` in workflow/terminal commands.
  - Prior tracked `target/` and `logs/` build artifacts polluted git history until cleaned.
  - `dbt` command resolution required using the local `.venv` executable because the system dbt installation lacked adapter modules.
  - GitHub Actions runner default permission set did not include Projects write access by default.
