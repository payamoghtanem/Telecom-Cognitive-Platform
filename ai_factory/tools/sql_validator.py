"""sql_validator.py

Deterministic AST + pattern validator for SQL assets.
Implements basic checks required by the platform blueprint:
- Detects comma-style joins, NATURAL/CROSS/FULL joins
- Flags JOINs that lack ON/USING within a reasonable lookahead
- Suggests lowercase keywords normalization when required by agent guardrails

This module relies on `sqlglot` for parsing and normalization. See requirements.txt for dependency.
"""

from __future__ import annotations

import re
import sys
from typing import List

try:
    import sqlglot
    from sqlglot import parse_one
except Exception:  # pragma: no cover - allows module import even if sqlglot missing
    sqlglot = None

SQL_KEYWORDS = [
    "SELECT",
    "FROM",
    "WHERE",
    "JOIN",
    "ON",
    "USING",
    "INNER",
    "LEFT",
    "RIGHT",
    "FULL",
    "OUTER",
    "CROSS",
    "NATURAL",
    "GROUP",
    "ORDER",
    "BY",
    "HAVING",
    "LIMIT",
    "OFFSET",
    "INSERT",
    "UPDATE",
    "DELETE",
    "CREATE",
    "ALTER",
    "DROP",
]


def _find_uppercase_keywords(sql: str) -> List[str]:
    issues: List[str] = []
    for kw in SQL_KEYWORDS:
        # find occurrences of the keyword ignoring case
        for m in re.finditer(r"\b" + re.escape(kw) + r"\b", sql, flags=re.IGNORECASE):
            token = m.group(0)
            # If any character in the token is uppercase, the token isn't strictly lowercase
            if any(c.isupper() for c in token):
                if token != token.lower():
                    issues.append(f"Keyword casing: expected lowercase keyword '{kw.lower()}', found '{token}' at pos {m.start()}")
    return issues


def _find_comma_joins(sql: str) -> List[str]:
    issues: List[str] = []
    # Simple heuristic: look for 'FROM <anything>,' patterns (could be across whitespace/newlines)
    if re.search(r"\bFROM\b[\s\S]*?,", sql, flags=re.IGNORECASE):
        issues.append("Comma-style join detected in FROM clause; use explicit JOIN ... ON/USING instead.")
    return issues


def _find_natural_cross_full_joins(sql: str) -> List[str]:
    issues: List[str] = []
    for pattern, msg in [
        (r"\bNATURAL\s+JOIN\b", "NATURAL JOIN is forbidden."),
        (r"\bCROSS\s+JOIN\b", "CROSS JOIN is forbidden."),
        (r"\bFULL\s+JOIN\b", "FULL JOIN is forbidden unless explicitly approved."),
    ]:
        if re.search(pattern, sql, flags=re.IGNORECASE):
            issues.append(msg)
    return issues


def _find_joins_without_on_using(sql: str) -> List[str]:
    issues: List[str] = []
    # Find all positions of 'JOIN' and ensure 'ON' or 'USING' appears within next 200 chars
    for m in re.finditer(r"\bJOIN\b", sql, flags=re.IGNORECASE):
        start = m.end()
        window = sql[start : start + 400]  # lookahead window to find ON/USING before next clause
        if not re.search(r"\b(ON|USING)\b", window, flags=re.IGNORECASE):
            issues.append(f"JOIN without ON/USING near position {m.start()}. Provide an equality predicate or document a temporal join.")
    return issues


def validate_sql(sql: str) -> List[str]:
    """Validate SQL string and return a list of error messages (empty if compliant).

    Checks implemented:
    - Syntax parse via sqlglot (if available).
    - Comma-style joins, forbidden join kinds, joins missing ON/USING.
    - Keyword casing: enforces lowercase SQL keywords (per agent guardrails).
    """
    errors: List[str] = []

    # Normalize templating (basic) to avoid parser failure on Jinja-like placeholders
    cleaned = re.sub(r"\{\{[\s\S]*?\}\}", "mock_table", sql)

    # 1) Syntax via sqlglot if available
    if sqlglot is not None:
        try:
            parse_one(cleaned, read="clickhouse")
        except Exception as e:  # syntax errors
            errors.append(f"SyntaxError: {e}")
    else:
        # If sqlglot not present, we still run regex-based checks and note that parsing was skipped
        errors.append("Note: sqlglot not installed; AST parsing skipped. Install via requirements.txt to enable full validation.")

    # 2) Structural checks
    errors.extend(_find_comma_joins(sql))
    errors.extend(_find_natural_cross_full_joins(sql))
    errors.extend(_find_joins_without_on_using(sql))

    # 3) Keyword casing checks (platform enforces lowercase keywords for agent outputs)
    errors.extend(_find_uppercase_keywords(sql))

    return errors


def suggest_lowercase(sql: str) -> str:
    """Return a suggestion string where common SQL keywords are replaced with lowercase equivalents.

    This attempts a best-effort normalization; use sqlglot for production normalization.
    """
    normalized = sql
    for kw in sorted(SQL_KEYWORDS, key=len, reverse=True):
        normalized = re.sub(r"\b" + re.escape(kw) + r"\b", kw.lower(), normalized, flags=re.IGNORECASE)
    return normalized


def main(argv: List[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: python ai_factory/tools/sql_validator.py <sql-file>\nor: echo \"SELECT ...\" | python ai_factory/tools/sql_validator.py -")
        return 2

    if argv[0] == "-":
        sql = sys.stdin.read()
    else:
        path = argv[0]
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

    errs = validate_sql(sql)
    if errs:
        print("SQL VALIDATION ERRORS:")
        for e in errs:
            print(" -", e)
        print("\nSuggested normalization:\n")
        print(suggest_lowercase(sql))
        return 1

    print("SQL is compliant.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
