{% test no_rows(model) %}
-- Generic test that fails if the target relation returns any rows
select 1 as failed
from {{ model }}
limit 1
{% endtest %}
