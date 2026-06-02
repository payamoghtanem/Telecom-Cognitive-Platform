-- staging model: stg_fact_network_usage.sql
-- compliant with validator: lowercase keywords, explicit joins avoided where not needed

with raw_events as (
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
