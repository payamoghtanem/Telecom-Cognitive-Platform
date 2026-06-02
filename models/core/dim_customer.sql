-- core dimension: dim_customer.sql
-- canonical customer dimension derived from staging with hashed customer keys

select
    distinct customer_key_hash,
    now() as load_timestamp
from {{ ref('stg_fact_network_usage') }}
