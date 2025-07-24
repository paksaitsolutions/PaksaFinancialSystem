"""Create tax tables

Revision ID: 20240116_create_tax_tables
Revises: 20240115_create_gl_tables
Create Date: 2024-01-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20240116_create_tax_tables'
down_revision = '20240115_create_gl_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Create tax_jurisdictions table
    op.create_table('tax_jurisdictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('level', sa.Enum('country', 'state', 'county', 'city', name='jurisdiction_level'), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['tax_jurisdictions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create tax_rates table
    op.create_table('tax_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('tax_type', sa.Enum('INCOME', 'SALES', 'VAT', 'GST', 'PAYROLL', 'PROPERTY', 'EXCISE', name='taxtype'), nullable=False),
        sa.Column('jurisdiction_id', sa.Integer(), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['jurisdiction_id'], ['tax_jurisdictions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create tax_transactions table
    op.create_table('tax_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('document_number', sa.String(length=50), nullable=False),
        sa.Column('reference_number', sa.String(length=50), nullable=True),
        sa.Column('tax_rate_id', sa.Integer(), nullable=False),
        sa.Column('taxable_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tax_rate_id'], ['tax_rates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create tax_transaction_components table
    op.create_table('tax_transaction_components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('tax_component', sa.String(length=50), nullable=False),
        sa.Column('component_rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('component_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['transaction_id'], ['tax_transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create tax_exemptions table
    op.create_table('tax_exemptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exemption_type', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('certificate_number', sa.String(length=50), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('jurisdiction_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['jurisdiction_id'], ['tax_jurisdictions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create tax_returns table
    op.create_table('tax_returns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('return_number', sa.String(length=50), nullable=False),
        sa.Column('tax_type', sa.Enum('INCOME', 'SALES', 'VAT', 'GST', 'PAYROLL', 'PROPERTY', 'EXCISE', name='taxtype'), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('filing_date', sa.Date(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('total_tax_due', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('return_number')
    )

def downgrade():
    op.drop_table('tax_returns')
    op.drop_table('tax_exemptions')
    op.drop_table('tax_transaction_components')
    op.drop_table('tax_transactions')
    op.drop_table('tax_rates')
    op.drop_table('tax_jurisdictions')
    op.execute('DROP TYPE taxtype')
    op.execute('DROP TYPE jurisdiction_level')