"""Create AR tables fixed

Revision ID: 002_ar_tables_fixed
Revises: 001_ar_tables
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers
revision = '002_ar_tables_fixed'
down_revision = '001_ar_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Create customers_ar table (renamed to avoid conflicts)
    op.create_table('customers_ar',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column('tenant_id', sa.String(36), nullable=False, default='12345678-1234-5678-9012-123456789012'),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('credit_limit', sa.Float(), nullable=True, default=0.0),
        sa.Column('balance', sa.Float(), nullable=True, default=0.0),
        sa.Column('payment_terms', sa.String(length=50), nullable=True, default='net30'),
        sa.Column('status', sa.String(length=20), nullable=True, default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now()),
    )
    
    # Create invoices_ar table
    op.create_table('invoices_ar',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column('tenant_id', sa.String(36), nullable=False, default='12345678-1234-5678-9012-123456789012'),
        sa.Column('customer_id', sa.String(36), nullable=False),
        sa.Column('invoice_number', sa.String(length=50), nullable=False),
        sa.Column('invoice_date', sa.DateTime(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('paid_amount', sa.Float(), nullable=True, default=0.0),
        sa.Column('status', sa.String(length=20), nullable=True, default='draft'),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['customer_id'], ['customers_ar.id'], ),
        sa.UniqueConstraint('invoice_number')
    )
    
    # Create payments_ar table
    op.create_table('payments_ar',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column('tenant_id', sa.String(36), nullable=False, default='12345678-1234-5678-9012-123456789012'),
        sa.Column('invoice_id', sa.String(36), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('payment_date', sa.DateTime(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices_ar.id'], ),
    )

    # Insert sample data
    op.execute("""
        INSERT INTO customers_ar (id, tenant_id, name, email, phone, address, credit_limit, balance, payment_terms, status)
        VALUES 
        ('1', '12345678-1234-5678-9012-123456789012', 'ABC Corporation', 'contact@abc.com', '555-0123', '123 Business St', 50000, 15000, 'net30', 'active'),
        ('2', '12345678-1234-5678-9012-123456789012', 'XYZ Industries', 'info@xyz.com', '555-0456', '456 Industry Ave', 75000, -2500, 'net30', 'active'),
        ('3', '12345678-1234-5678-9012-123456789012', 'Tech Solutions Ltd', 'hello@tech.com', '555-0789', '789 Tech Blvd', 25000, 8750, 'net15', 'active')
    """)

def downgrade():
    op.drop_table('payments_ar')
    op.drop_table('invoices_ar')
    op.drop_table('customers_ar')