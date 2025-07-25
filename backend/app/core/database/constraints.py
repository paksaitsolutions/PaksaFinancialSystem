"""Database-level data validation constraints"""
from sqlalchemy import CheckConstraint, Index
from sqlalchemy.schema import DDL

# Check constraints for data validation
ACCOUNT_BALANCE_CHECK = CheckConstraint(
    'balance >= -999999999.99 AND balance <= 999999999.99',
    name='check_account_balance_range'
)

TRANSACTION_AMOUNT_CHECK = CheckConstraint(
    'amount > 0',
    name='check_transaction_amount_positive'
)

EMAIL_FORMAT_CHECK = CheckConstraint(
    "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'",
    name='check_email_format'
)

# Indexes for performance
TENANT_INDEXES = [
    Index('idx_accounts_tenant_id', 'tenant_id'),
    Index('idx_transactions_tenant_id', 'tenant_id'),
    Index('idx_employees_tenant_id', 'tenant_id'),
]

def apply_database_constraints(engine):
    """Apply database-level constraints"""
    with engine.connect() as conn:
        # Apply constraints would go here
        conn.commit()