-- staging model: stg_fact_network_usage.sql
-- reads directly from Bronze ingest output and applies staging contracts

with raw_events as (
    select
        md5(concat(customer_key, 'SECRET_SALT')) as customer_key_hash,
        timestamp as event_timestamp,
        bytes_dl,
        bytes_ul,
        network_type,
        source_system,
        ingest_timestamp
    from file('bronze/network_usage.parquet', 'Parquet')
    where timestamp >= now() - interval 3 day
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
