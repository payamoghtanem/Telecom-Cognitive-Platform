
    
    

select
    usage_pk as unique_field,
    count(*) as n_records

from `default`.`silver_fact_network_usage`
where usage_pk is not null
group by usage_pk
having count(*) > 1


