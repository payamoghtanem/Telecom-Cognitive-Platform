select customers.id as customer_id, customers.name as customer_name
from customers
join payments on customers.id = payments.customer_id
where payments.amount > 0
