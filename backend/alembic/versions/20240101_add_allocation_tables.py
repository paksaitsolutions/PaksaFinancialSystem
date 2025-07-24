"""Add allocation tables

Revision ID: 20240101_add_allocation_tables
Revises: 20240101_add_intercompany_tables
Create Date: 2024-01-01 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '20240101_add_allocation_tables'
down_revision = '20240101_add_intercompany_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create allocation_rules table
    op.create_table(
        'allocation_rules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('rule_name', sa.String(100), nullable=False),
        sa.Column('rule_code', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('allocation_method', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('source_account_id', UUID(as_uuid=True), nullable=True),
        sa.Column('source_department_id', UUID(as_uuid=True), nullable=True),
        sa.Column('source_cost_center_id', UUID(as_uuid=True), nullable=True),
        sa.Column('effective_from', sa.Date, nullable=False),
        sa.Column('effective_to', sa.Date, nullable=True),
        sa.Column('priority', sa.Integer, nullable=False, default=100),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create allocation_rule_lines table
    op.create_table(
        'allocation_rule_lines',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('allocation_rule_id', UUID(as_uuid=True), sa.ForeignKey('allocation_rules.id'), nullable=False),
        sa.Column('target_account_id', UUID(as_uuid=True), nullable=False),
        sa.Column('target_department_id', UUID(as_uuid=True), nullable=True),
        sa.Column('target_cost_center_id', UUID(as_uuid=True), nullable=True),
        sa.Column('allocation_percentage', sa.Numeric(5, 2), nullable=True),
        sa.Column('fixed_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('weight', sa.Numeric(10, 4), nullable=True),
        sa.Column('formula', sa.Text, nullable=True),
        sa.Column('line_order', sa.Integer, nullable=False, default=1),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create allocations table
    op.create_table(
        'allocations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('allocation_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('allocation_date', sa.Date, nullable=False),
        sa.Column('source_journal_entry_id', UUID(as_uuid=True), nullable=False),
        sa.Column('source_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('allocation_rule_id', UUID(as_uuid=True), sa.ForeignKey('allocation_rules.id'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='posted'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create allocation_entries table
    op.create_table(
        'allocation_entries',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('allocation_id', UUID(as_uuid=True), sa.ForeignKey('allocations.id'), nullable=False),
        sa.Column('target_account_id', UUID(as_uuid=True), nullable=False),
        sa.Column('target_department_id', UUID(as_uuid=True), nullable=True),
        sa.Column('target_cost_center_id', UUID(as_uuid=True), nullable=True),
        sa.Column('allocated_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('allocation_percentage', sa.Numeric(5, 2), nullable=True),
        sa.Column('journal_entry_id', UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_allocation_rules_effective_dates', 'allocation_rules', ['effective_from', 'effective_to'])
    op.create_index('ix_allocation_rules_priority', 'allocation_rules', ['priority'])
    op.create_index('ix_allocation_rule_lines_rule_order', 'allocation_rule_lines', ['allocation_rule_id', 'line_order'])
    op.create_index('ix_allocations_date_rule', 'allocations', ['allocation_date', 'allocation_rule_id'])


def downgrade():
    op.drop_table('allocation_entries')
    op.drop_table('allocations')
    op.drop_table('allocation_rule_lines')
    op.drop_table('allocation_rules')