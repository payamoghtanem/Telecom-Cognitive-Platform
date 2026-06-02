import json
import os
import sys
from pathlib import Path

# ensure workspace root is on path for imports when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd

from ai_factory.ingest.network_usage_ingester import run_ingest


def test_ingest_routing(tmp_path: Path):
    landing_dir = tmp_path / "landing"
    bronze_dir = tmp_path / "bronze"
    dlq_dir = tmp_path / "dlq"
    landing_dir.mkdir(parents=True)
    bronze_dir.mkdir(parents=True)
    dlq_dir.mkdir(parents=True)

    good_file = landing_dir / "good.csv"
    good_file.write_text(
        "timestamp,customer_key,bytes_dl,bytes_ul,network_type\n"
        "2026-06-01 12:00:00,custA,100,10,4G\n"
        "2026-06-02 13:00:00,custB,200,20,5G\n"
    )

    bad_file = landing_dir / "bad.csv"
    bad_file.write_text(
        "timestamp,customer_key,bytes_dl,bytes_ul,network_type\n"
        ",custC,50,5,4G\n"
        "2026-06-03 14:00:00,custD,-10,0,5G\n"
        "2026-06-04 15:00:00,,30,15,4G\n"
    )

    config_path = tmp_path / "ingest_config.json"
    config_path.write_text(
        json.dumps(
            {
                "landing_path": str(landing_dir),
                "bronze_path": str(bronze_dir / "network_usage.parquet"),
                "dlq_path": str(dlq_dir / "malformed_records.json"),
                "required_columns": ["timestamp", "customer_key", "bytes_dl", "bytes_ul"],
                "bytes_minimum": 0,
                "timestamp_format": None,
            },
            indent=2,
        )
    )

    run_ingest(str(config_path))

    bronze_file = bronze_dir / "network_usage.parquet"
    assert bronze_file.exists(), "Bronze file was not written"

    bronze_df = pd.read_parquet(bronze_file)
    assert len(bronze_df) == 2
    assert "ingest_timestamp" in bronze_df.columns
    assert "source_file" in bronze_df.columns
    assert set(bronze_df["customer_key"]) == {"custA", "custB"}

    dlq_file = dlq_dir / "malformed_records.json"
    assert dlq_file.exists(), "DLQ file was not created"

    dlq_records = json.loads(dlq_file.read_text())
    assert len(dlq_records) == 3
    reasons = {record["error_reason"] for record in dlq_records}
    assert any("missing or empty required column 'timestamp'" in reason for reason in reasons)
    assert any("bytes_dl value below minimum" in reason for reason in reasons)
    assert any("missing or empty required column 'customer_key'" in reason for reason in reasons)
