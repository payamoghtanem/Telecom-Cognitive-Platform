import os
import sys

# ensure workspace root is on path for imports when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ai_factory.tools.sql_validator as validator

SAMPLE_SQL = '''select customers.id as customer_id, customers.name as customer_name
from customers
join payments on customers.id = payments.customer_id
where payments.amount > 0
'''

STAGING_MODEL = '''with raw_events as (
    select
        md5(concat(raw_msisdn, 'SECRET_SALT')) as customer_key_hash,
        event_timestamp as event_timestamp,
        bytes_dl,
        bytes_ul,
        network_type,
        source_system,
        ingest_timestamp
    from {{ ref('stg_raw_network_events') }}
    where event_timestamp >= now() - interval 3 day
)
select
    md5(concat(customer_key_hash, '-', toString(toUnixTimestamp(event_timestamp)), '-', network_type)) as usage_pk,
    customer_key_hash,
    event_timestamp as timestamp,
    bytes_dl,
    bytes_ul,
    network_type,
    source_system,
    ingest_timestamp
from raw_events
'''

COMMA_JOIN_SQL = '''select a.id, b.name
from table_a, table_b
where a.id = b.id
'''

FUNCTION_WITH_COMMAS = '''select concat(col1, '-', col2) as combined_col
from my_table
where status = 'active'
'''


def test_validator_compliant():
    errs = validator.validate_sql(SAMPLE_SQL)
    assert errs == [], f"Validator returned errors: {errs}"


def test_staging_model_compliant():
    """Test that staging model with commas in SELECT/function args passes validation."""
    errs = validator.validate_sql(STAGING_MODEL)
    # Filter out uppercase keyword errors (expected) but no comma-join errors
    comma_join_errors = [e for e in errs if "Comma-style join" in e]
    assert comma_join_errors == [], f"Staging model incorrectly flagged as comma join: {comma_join_errors}"


def test_comma_join_detected():
    """Test that actual comma-style joins are detected."""
    errs = validator.validate_sql(COMMA_JOIN_SQL)
    comma_join_errors = [e for e in errs if "Comma-style join" in e]
    assert len(comma_join_errors) > 0, "Comma-style join not detected"


def test_function_with_commas_compliant():
    """Test that commas in function arguments do not trigger comma-join detection."""
    errs = validator.validate_sql(FUNCTION_WITH_COMMAS)
    comma_join_errors = [e for e in errs if "Comma-style join" in e]
    assert comma_join_errors == [], f"Function commas incorrectly flagged as join: {comma_join_errors}"
