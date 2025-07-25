"""Add missing foreign key constraints

Revision ID: add_fk_constraints
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_fk_constraints'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add foreign key constraints for data integrity
    
    # Journal entries to accounts
    op.create_foreign_key(
        'fk_journal_entries_account_id',
        'journal_entries', 'accounts',
        ['account_id'], ['id'],
        ondelete='RESTRICT'
    )
    
    # Budget lines to accounts
    op.create_foreign_key(
        'fk_budget_lines_account_id',
        'budget_lines', 'accounts',
        ['account_id'], ['id'],
        ondelete='RESTRICT'
    )
    
    # Transactions to accounts
    op.create_foreign_key(
        'fk_transactions_account_id',
        'transactions', 'accounts',
        ['account_id'], ['id'],
        ondelete='RESTRICT'
    )
    
    # Employee records to companies
    op.create_foreign_key(
        'fk_employees_company_id',
        'employees', 'companies',
        ['company_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Vendor records to companies
    op.create_foreign_key(
        'fk_vendors_company_id',
        'vendors', 'companies',
        ['company_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade():
    # Remove foreign key constraints
    op.drop_constraint('fk_journal_entries_account_id', 'journal_entries', type_='foreignkey')
    op.drop_constraint('fk_budget_lines_account_id', 'budget_lines', type_='foreignkey')
    op.drop_constraint('fk_transactions_account_id', 'transactions', type_='foreignkey')
    op.drop_constraint('fk_employees_company_id', 'employees', type_='foreignkey')
    op.drop_constraint('fk_vendors_company_id', 'vendors', type_='foreignkey')