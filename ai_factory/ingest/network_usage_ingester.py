from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


def load_config(config_path: Path) -> Dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def ensure_directories(config: Dict[str, Any]) -> None:
    Path(config["landing_path"]).mkdir(parents=True, exist_ok=True)
    Path(config["bronze_path"]).parent.mkdir(parents=True, exist_ok=True)
    Path(config["dlq_path"]).parent.mkdir(parents=True, exist_ok=True)


def list_landing_files(landing_path: Path) -> List[Path]:
    return sorted(
        [
            p
            for p in landing_path.iterdir()
            if p.suffix.lower() in {".csv", ".parquet"} and p.is_file()
        ]
    )


def read_landing_file(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return pd.read_parquet(path)


def validate_dataframe(df: pd.DataFrame, source_file: str, config: Dict[str, Any]) -> tuple[pd.DataFrame, List[Dict[str, Any]]]:
    required_columns = config["required_columns"]
    bytes_minimum = config["bytes_minimum"]

    invalid_records: List[Dict[str, Any]] = []
    valid_rows: List[Dict[str, Any]] = []

    for _, row in df.iterrows():
        row_data = row.to_dict()
        errors: List[str] = []

        for col in required_columns:
            if col not in row_data or pd.isna(row_data[col]) or str(row_data[col]).strip() == "":
                errors.append(f"missing or empty required column '{col}'")

        if "timestamp" in row_data and not pd.isna(row_data.get("timestamp")):
            try:
                pd.to_datetime(row_data["timestamp"], errors="raise")
            except Exception:
                errors.append("invalid timestamp format")

        for metric in ["bytes_dl", "bytes_ul"]:
            if metric in row_data and not pd.isna(row_data.get(metric)):
                try:
                    numeric_value = float(row_data[metric])
                    if numeric_value < bytes_minimum:
                        errors.append(f"{metric} value below minimum {bytes_minimum}")
                except Exception:
                    errors.append(f"{metric} must be numeric")

        if errors:
            invalid_records.append(
                {
                    "source_file": source_file,
                    "row": row_data,
                    "error_reason": "; ".join(errors),
                }
            )
        else:
            valid_rows.append(row_data)

    valid_df = pd.DataFrame(valid_rows)
    return valid_df, invalid_records


def write_bronze(valid_df: pd.DataFrame, bronze_path: Path) -> None:
    if valid_df.empty:
        return

    if bronze_path.exists():
        existing = pd.read_parquet(bronze_path)
        valid_df = pd.concat([existing, valid_df], ignore_index=True)

    valid_df.to_parquet(bronze_path, index=False)


def write_dlq(invalid_records: List[Dict[str, Any]], dlq_path: Path) -> None:
    if not invalid_records:
        return

    existing: List[Dict[str, Any]] = []
    if dlq_path.exists():
        with dlq_path.open("r", encoding="utf-8") as fh:
            try:
                existing = json.load(fh)
            except Exception:
                existing = []

    existing.extend(invalid_records)
    with dlq_path.open("w", encoding="utf-8") as fh:
        json.dump(existing, fh, indent=2)


def run_ingest(config_path: Path | str) -> None:
    config_file = Path(config_path)
    config = load_config(config_file)
    ensure_directories(config)

    landing_path = Path(config["landing_path"])
    bronze_path = Path(config["bronze_path"])
    dlq_path = Path(config["dlq_path"])

    landing_files = list_landing_files(landing_path)
    all_valid_frames: List[pd.DataFrame] = []
    all_invalid_records: List[Dict[str, Any]] = []

    for path in landing_files:
        df = read_landing_file(path)
        source_file = str(path.name)

        valid_df, invalid_records = validate_dataframe(df, source_file, config)
        if not valid_df.empty:
            valid_df["ingest_timestamp"] = datetime.now(timezone.utc).isoformat()
            valid_df["source_file"] = source_file
            all_valid_frames.append(valid_df)

        all_invalid_records.extend(invalid_records)

    if all_valid_frames:
        combined_valid = pd.concat(all_valid_frames, ignore_index=True)
        write_bronze(combined_valid, bronze_path)

    write_dlq(all_invalid_records, dlq_path)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Network usage ingest pipeline")
    parser.add_argument(
        "--config",
        default="ai_factory/ingest/ingest_config.json",
        help="Path to ingest configuration JSON",
    )
    args = parser.parse_args()
    run_ingest(Path(args.config))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
