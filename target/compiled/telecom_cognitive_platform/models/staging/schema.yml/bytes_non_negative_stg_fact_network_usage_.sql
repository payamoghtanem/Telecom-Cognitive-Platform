
select *
from `default`.`stg_fact_network_usage`
where coalesce(bytes_dl, 0) < 0 or coalesce(bytes_ul, 0) < 0
