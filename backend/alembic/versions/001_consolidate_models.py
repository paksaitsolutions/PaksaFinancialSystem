"""Consolidate models and fix foreign keys

Revision ID: 001_consolidate_models
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_consolidate_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Update foreign key references to use unified table names
    op.execute("UPDATE ap_invoice_line_items SET account_id = (SELECT id FROM chart_of_accounts WHERE account_code = (SELECT account_code FROM gl_chart_of_accounts WHERE id = account_id)) WHERE account_id IN (SELECT id FROM gl_chart_of_accounts)")
    op.execute("UPDATE ar_invoice_line_items SET account_id = (SELECT id FROM chart_of_accounts WHERE account_code = (SELECT account_code FROM gl_chart_of_accounts WHERE id = account_id)) WHERE account_id IN (SELECT id FROM gl_chart_of_accounts)")
    
    # Add source_module and source_id to journal_entries if not exists
    try:
        op.add_column('journal_entries', sa.Column('source_module', sa.String(50), nullable=True))
        op.add_column('journal_entries', sa.Column('source_id', sa.UUID(), nullable=True))
    except:
        pass


def downgrade():
    # Remove added columns
    try:
        op.drop_column('journal_entries', 'source_module')
        op.drop_column('journal_entries', 'source_id')
    except:
        pass