"""Create tax tables

Revision ID: 20250124_03_create_tax_tables
Revises: 20250124_02_enhanced_company_settings
Create Date: 2025-01-24 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20250124_03_create_tax_tables'
down_revision = '20250124_02_enhanced_company_settings'
branch_labels = None
depends_on = None

def upgrade():
    # Create tax_rates table
    op.create_table('tax_rates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('rate', sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column('tax_type', sa.String(length=20), nullable=False),
        sa.Column('jurisdiction', sa.String(length=100), nullable=False),
        sa.Column('country_code', sa.String(length=2), nullable=False),
        sa.Column('state_code', sa.String(length=10), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_tax_rates_name'), 'tax_rates', ['name'], unique=False)
    op.create_index(op.f('ix_tax_rates_code'), 'tax_rates', ['code'], unique=False)
    op.create_index(op.f('ix_tax_rates_tax_type'), 'tax_rates', ['tax_type'], unique=False)

    # Create tax_transactions table
    op.create_table('tax_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=20), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tax_rate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('taxable_amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['tax_rate_id'], ['tax_rates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tax_transactions_transaction_id'), 'tax_transactions', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_tax_transactions_entity_id'), 'tax_transactions', ['entity_id'], unique=False)

    # Create tax_exemptions table
    op.create_table('tax_exemptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('certificate_number', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=20), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exemption_type', sa.String(length=50), nullable=False),
        sa.Column('tax_types', sa.JSON(), nullable=True),
        sa.Column('jurisdiction', sa.String(length=100), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('issuing_authority', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('attachment_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('certificate_number')
    )
    op.create_index(op.f('ix_tax_exemptions_certificate_number'), 'tax_exemptions', ['certificate_number'], unique=False)
    op.create_index(op.f('ix_tax_exemptions_entity_id'), 'tax_exemptions', ['entity_id'], unique=False)

    # Create tax_returns table
    op.create_table('tax_returns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('return_number', sa.String(length=50), nullable=False),
        sa.Column('tax_type', sa.String(length=20), nullable=False),
        sa.Column('jurisdiction', sa.String(length=100), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('gross_sales', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('taxable_sales', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('exempt_sales', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('tax_collected', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('tax_paid', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('tax_due', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('filed_date', sa.Date(), nullable=True),
        sa.Column('payment_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('return_number')
    )

    # Create tax_return_line_items table
    op.create_table('tax_return_line_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tax_return_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['tax_return_id'], ['tax_returns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create tax_jurisdictions table
    op.create_table('tax_jurisdictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('jurisdiction_type', sa.String(length=20), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tax_id_required', sa.Boolean(), nullable=True),
        sa.Column('tax_id_format', sa.String(length=100), nullable=True),
        sa.Column('filing_frequency', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['tax_jurisdictions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_tax_jurisdictions_name'), 'tax_jurisdictions', ['name'], unique=False)
    op.create_index(op.f('ix_tax_jurisdictions_code'), 'tax_jurisdictions', ['code'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_tax_jurisdictions_code'), table_name='tax_jurisdictions')
    op.drop_index(op.f('ix_tax_jurisdictions_name'), table_name='tax_jurisdictions')
    op.drop_table('tax_jurisdictions')
    op.drop_table('tax_return_line_items')
    op.drop_table('tax_returns')
    op.drop_index(op.f('ix_tax_exemptions_entity_id'), table_name='tax_exemptions')
    op.drop_index(op.f('ix_tax_exemptions_certificate_number'), table_name='tax_exemptions')
    op.drop_table('tax_exemptions')
    op.drop_index(op.f('ix_tax_transactions_entity_id'), table_name='tax_transactions')
    op.drop_index(op.f('ix_tax_transactions_transaction_id'), table_name='tax_transactions')
    op.drop_table('tax_transactions')
    op.drop_index(op.f('ix_tax_rates_tax_type'), table_name='tax_rates')
    op.drop_index(op.f('ix_tax_rates_code'), table_name='tax_rates')
    op.drop_index(op.f('ix_tax_rates_name'), table_name='tax_rates')
    op.drop_table('tax_rates')