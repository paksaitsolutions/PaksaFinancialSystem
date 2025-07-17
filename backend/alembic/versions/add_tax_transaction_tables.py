"""Add tax transaction tables

Revision ID: 1234567890ab
Revises: 9876543210zy
Create Date: 2025-07-17 12:48:11.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1234567890ab'
down_revision = '9876543210zy'
branch_labels = None
depends_on = None

def upgrade():
    # Create enum types
    tax_transaction_status = postgresql.ENUM(
        'draft', 'posted', 'voided', 'adjusted',
        name='taxtransactionstatus',
        create_type=True
    )
    tax_transaction_status.create(op.get_bind())
    
    tax_transaction_type = postgresql.ENUM(
        'sale', 'purchase', 'use', 'import', 'export', 'tax_adjustment',
        name='taxtransactiontype',
        create_type=True
    )
    tax_transaction_type.create(op.get_bind())
    
    # Create tax_transactions table
    op.create_table(
        'tax_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_date', sa.DateTime(), nullable=False),
        sa.Column('posting_date', sa.DateTime(), nullable=True),
        sa.Column('document_number', sa.String(length=100), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tax_type', sa.String(length=50), nullable=False),
        sa.Column('tax_rate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('taxable_amount', sa.Numeric(19, 4), nullable=False, server_default='0'),
        sa.Column('tax_amount', sa.Numeric(19, 4), nullable=False, server_default='0'),
        sa.Column('total_amount', sa.Numeric(19, 4), nullable=False, server_default='0'),
        sa.Column('jurisdiction_code', sa.String(length=20), nullable=True),
        sa.Column('tax_jurisdiction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', tax_transaction_status, nullable=False, server_default='draft'),
        sa.Column('transaction_type', tax_transaction_type, nullable=False),
        sa.Column('source_document_type', sa.String(length=50), nullable=True),
        sa.Column('source_document_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('posted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['posted_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tax_jurisdiction_id'], ['tax_jurisdictions.id'], ),
        sa.ForeignKeyConstraint(['tax_rate_id'], ['tax_rates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create tax_transaction_components table
    op.create_table(
        'tax_transaction_components',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tax_component', sa.String(length=100), nullable=False),
        sa.Column('tax_rate', sa.Numeric(10, 6), nullable=False),
        sa.Column('taxable_amount', sa.Numeric(19, 4), nullable=False),
        sa.Column('tax_amount', sa.Numeric(19, 4), nullable=False),
        sa.Column('jurisdiction_level', sa.String(length=50), nullable=True),
        sa.Column('jurisdiction_name', sa.String(length=100), nullable=True),
        sa.Column('jurisdiction_code', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['transaction_id'], ['tax_transactions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_tax_transactions_company_dates', 'tax_transactions', 
                   ['company_id', 'transaction_date', 'posting_date'], unique=False)
    op.create_index('idx_tax_transactions_source', 'tax_transactions', 
                   ['source_document_type', 'source_document_id'], unique=False)
    op.create_index('idx_tax_transactions_status_type', 'tax_transactions', 
                   ['status', 'transaction_type'], unique=False)
    op.create_index('idx_tax_components_transaction', 'tax_transaction_components', 
                   ['transaction_id'], unique=False)
    op.create_index('idx_tax_components_jurisdiction', 'tax_transaction_components', 
                   ['jurisdiction_code'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index('idx_tax_components_jurisdiction', table_name='tax_transaction_components')
    op.drop_index('idx_tax_components_transaction', table_name='tax_transaction_components')
    op.drop_index('idx_tax_transactions_status_type', table_name='tax_transactions')
    op.drop_index('idx_tax_transactions_source', table_name='tax_transactions')
    op.drop_index('idx_tax_transactions_company_dates', table_name='tax_transactions')
    
    # Drop tables
    op.drop_table('tax_transaction_components')
    op.drop_table('tax_transactions')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS taxtransactiontype')
    op.execute('DROP TYPE IF EXISTS taxtransactionstatus')
