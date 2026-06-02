-- core dimension: dim_customer.sql
-- canonical customer dimension derived from staging with hashed customer keys
-- core dimension: dim_customer.sql
-- canonical customer dimension derived from staging with hashed customer keys

select
    customer_key_hash,
    min(timestamp) as first_seen,
    max(timestamp) as last_seen,
    case
        when max(case when network_type in ('5G','4G','3G','LTE') then 1 else 0 end) = 1 then 'mobile'
        else 'fixed'
    end as customer_type,
    '{}' as gdpr_flags,
    count(*) as activity_count,
    now() as load_timestamp
from `default`.`stg_fact_network_usage`
group by customer_key_hash