import os
import sys

# ensure workspace root is on path for imports when running tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ai_factory.tools.sql_validator as validator

SAMPLE_SQL = '''select customers.id as customer_id, customers.name as customer_name
from customers
join payments on customers.id = payments.customer_id
where payments.amount > 0
'''


def test_validator_compliant():
    errs = validator.validate_sql(SAMPLE_SQL)
    assert errs == [], f"Validator returned errors: {errs}"
