-- silver model: silver_fact_network_usage.sql
-- canonical network usage fact derived from staging output

with base as (
    select
        usage_pk,
        customer_key_hash,
        timestamp,
        bytes_dl,
        bytes_ul,
        network_type,
        source_system,
        ingest_timestamp
    from `default`.`stg_fact_network_usage`
    where timestamp >= now() - interval 3 day
)

select
    usage_pk,
    customer_key_hash,
    timestamp,
    bytes_dl,
    bytes_ul,
    bytes_dl + bytes_ul as total_bytes,
    network_type,
    source_system,
    ingest_timestamp
from base