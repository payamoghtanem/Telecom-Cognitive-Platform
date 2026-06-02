{% test bytes_non_negative(model) %}
select *
from {{ model }}
where coalesce(bytes_dl, 0) < 0 or coalesce(bytes_ul, 0) < 0
{% endtest %}
