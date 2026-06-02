
    
    

with child as (
    select customer_key_hash as from_field
    from `default`.`silver_fact_network_usage`
    where customer_key_hash is not null
),

parent as (
    select customer_key_hash as to_field
    from `default`.`dim_customer`
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null
-- end_of_sql
settings join_use_nulls = 1


