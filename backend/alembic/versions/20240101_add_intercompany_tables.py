"""Add intercompany tables

Revision ID: 20240101_add_intercompany_tables
Revises: 20240101_add_currency_tables
Create Date: 2024-01-01 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '20240101_add_intercompany_tables'
down_revision = '20240101_add_currency_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create intercompany_transactions table
    op.create_table(
        'intercompany_transactions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('transaction_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('transaction_type', sa.String(30), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='draft'),
        sa.Column('source_company_id', UUID(as_uuid=True), nullable=False),
        sa.Column('target_company_id', UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency_id', UUID(as_uuid=True), sa.ForeignKey('currencies.id'), nullable=False),
        sa.Column('transaction_date', sa.Date, nullable=False),
        sa.Column('due_date', sa.Date, nullable=True),
        sa.Column('source_account_id', UUID(as_uuid=True), nullable=False),
        sa.Column('target_account_id', UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('reference_number', sa.String(100), nullable=True),
        sa.Column('source_journal_entry_id', UUID(as_uuid=True), nullable=True),
        sa.Column('target_journal_entry_id', UUID(as_uuid=True), nullable=True),
        sa.Column('approved_by', UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint("amount > 0", name="ck_intercompany_amount_positive"),
        sa.CheckConstraint("source_company_id != target_company_id", name="ck_intercompany_different_companies")
    )
    
    # Create intercompany_reconciliations table
    op.create_table(
        'intercompany_reconciliations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('reconciliation_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('reconciliation_date', sa.Date, nullable=False),
        sa.Column('company_a_id', UUID(as_uuid=True), nullable=False),
        sa.Column('company_b_id', UUID(as_uuid=True), nullable=False),
        sa.Column('period_start', sa.Date, nullable=False),
        sa.Column('period_end', sa.Date, nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='draft'),
        sa.Column('company_a_balance', sa.Numeric(15, 2), nullable=False, default=0),
        sa.Column('company_b_balance', sa.Numeric(15, 2), nullable=False, default=0),
        sa.Column('difference', sa.Numeric(15, 2), nullable=False, default=0),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('reconciled_by', UUID(as_uuid=True), nullable=True),
        sa.Column('reconciled_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint("company_a_id != company_b_id", name="ck_reconciliation_different_companies")
    )
    
    # Create indexes
    op.create_index('ix_intercompany_transactions_companies', 'intercompany_transactions', ['source_company_id', 'target_company_id'])
    op.create_index('ix_intercompany_transactions_date_status', 'intercompany_transactions', ['transaction_date', 'status'])
    op.create_index('ix_intercompany_reconciliations_companies', 'intercompany_reconciliations', ['company_a_id', 'company_b_id'])
    op.create_index('ix_intercompany_reconciliations_period', 'intercompany_reconciliations', ['period_start', 'period_end'])


def upgrade():
    op.drop_table('intercompany_reconciliations')
    op.drop_table('intercompany_transactions')