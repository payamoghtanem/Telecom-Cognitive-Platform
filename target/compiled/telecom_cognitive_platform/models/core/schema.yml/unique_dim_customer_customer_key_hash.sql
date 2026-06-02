
    
    

select
    customer_key_hash as unique_field,
    count(*) as n_records

from `default`.`dim_customer`
where customer_key_hash is not null
group by customer_key_hash
having count(*) > 1


