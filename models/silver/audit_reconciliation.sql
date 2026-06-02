-- audit reconciliation model
-- compares row counts and aggregated bytes between staging and silver for active partition

with stg as (
    select
        count(*) as stg_count,
        sum(coalesce(bytes_dl,0) + coalesce(bytes_ul,0)) as stg_total_bytes
    from {{ ref('stg_fact_network_usage') }}
    where timestamp >= now() - interval 3 day
),
silver as (
    select
        count(*) as silver_count,
        sum(coalesce(total_bytes,0)) as silver_total_bytes
    from {{ ref('silver_fact_network_usage') }}
    where timestamp >= now() - interval 3 day
)

select
    'counts' as metric,
    stg.stg_count as left_value,
    silver.silver_count as right_value,
    (stg.stg_count - silver.silver_count) as diff
from stg cross join silver
where stg.stg_count != silver.silver_count

union all

select
    'bytes' as metric,
    stg.stg_total_bytes as left_value,
    silver.silver_total_bytes as right_value,
    (coalesce(stg.stg_total_bytes,0) - coalesce(silver.silver_total_bytes,0)) as diff
from stg cross join silver
where coalesce(stg.stg_total_bytes,0) != coalesce(silver.silver_total_bytes,0)
