
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
-- Generic test that fails if the target relation returns any rows
select 1 as failed
from `default`.`audit_reconciliation`
limit 1

  
  
    ) dbt_internal_test