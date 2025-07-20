"""Add tax return tables

Revision ID: 1a2b3c4d5e6f
Revises: 0a9b8c7d6e5f
Create Date: 2025-07-19 14:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = '0a9b8c7d6e5f'
branch_labels = None
depends_on = None

def upgrade():
    # Create tax_returns table
    op.create_table(
        'tax_returns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('return_type', sa.String(length=50), nullable=False),
        sa.Column('filing_frequency', sa.String(length=20), nullable=False),
        sa.Column('tax_period_start', sa.DateTime(), nullable=False),
        sa.Column('tax_period_end', sa.DateTime(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('filing_date', sa.DateTime(), nullable=True),
        sa.Column('paid_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('jurisdiction_code', sa.String(length=10), nullable=False),
        sa.Column('tax_authority_id', sa.String(length=100), nullable=True),
        sa.Column('total_taxable_amount', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('total_tax_amount', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('total_paid_amount', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('total_due_amount', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('filing_reference', sa.String(length=100), nullable=True),
        sa.Column('confirmation_number', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('filed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create tax_return_line_items table
    op.create_table(
        'tax_return_line_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tax_return_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('line_item_code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('amount', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('tax_type', sa.String(length=50), nullable=True),
        sa.Column('tax_rate', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tax_amount', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tax_return_id'], ['tax_returns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create tax_return_attachments table
    op.create_table(
        'tax_return_attachments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tax_return_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tax_return_id'], ['tax_returns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create tax_payments table
    op.create_table(
        'tax_payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tax_return_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_date', sa.DateTime(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tax_return_id'], ['tax_returns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_tax_returns_company_id'), 'tax_returns', ['company_id'], unique=False)
    op.create_index(op.f('ix_tax_returns_status'), 'tax_returns', ['status'], unique=False)
    op.create_index(op.f('ix_tax_returns_return_type'), 'tax_returns', ['return_type'], unique=False)
    op.create_index(op.f('ix_tax_returns_jurisdiction_code'), 'tax_returns', ['jurisdiction_code'], unique=False)
    op.create_index(op.f('ix_tax_returns_due_date'), 'tax_returns', ['due_date'], unique=False)
    op.create_index(op.f('ix_tax_returns_created_at'), 'tax_returns', ['created_at'], unique=False)
    op.create_index(op.f('ix_tax_return_line_items_tax_return_id'), 'tax_return_line_items', ['tax_return_id'], unique=False)
    op.create_index(op.f('ix_tax_return_attachments_tax_return_id'), 'tax_return_attachments', ['tax_return_id'], unique=False)
    op.create_index(op.f('ix_tax_payments_tax_return_id'), 'tax_payments', ['tax_return_id'], unique=False)
    op.create_index(op.f('ix_tax_payments_payment_date'), 'tax_payments', ['payment_date'], unique=False)
    op.create_index(op.f('ix_tax_payments_status'), 'tax_payments', ['status'], unique=False)


def downgrade():
    # Drop indexes first
    op.drop_index(op.f('ix_tax_payments_status'), table_name='tax_payments')
    op.drop_index(op.f('ix_tax_payments_payment_date'), table_name='tax_payments')
    op.drop_index(op.f('ix_tax_payments_tax_return_id'), table_name='tax_payments')
    op.drop_index(op.f('ix_tax_return_attachments_tax_return_id'), table_name='tax_return_attachments')
    op.drop_index(op.f('ix_tax_return_line_items_tax_return_id'), table_name='tax_return_line_items')
    op.drop_index(op.f('ix_tax_returns_created_at'), table_name='tax_returns')
    op.drop_index(op.f('ix_tax_returns_due_date'), table_name='tax_returns')
    op.drop_index(op.f('ix_tax_returns_jurisdiction_code'), table_name='tax_returns')
    op.drop_index(op.f('ix_tax_returns_return_type'), table_name='tax_returns')
    op.drop_index(op.f('ix_tax_returns_status'), table_name='tax_returns')
    op.drop_index(op.f('ix_tax_returns_company_id'), table_name='tax_returns')
    
    # Drop tables in reverse order of creation
    op.drop_table('tax_payments')
    op.drop_table('tax_return_attachments')
    op.drop_table('tax_return_line_items')
    op.drop_table('tax_returns')
