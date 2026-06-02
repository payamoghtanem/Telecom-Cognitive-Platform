
-- Generic test that fails if the target relation returns any rows
select 1 as failed
from `default`.`audit_reconciliation`
limit 1
