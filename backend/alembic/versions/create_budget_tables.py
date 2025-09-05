"""create budget tables

Revision ID: budget_001
Revises: 
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'budget_001'
down_revision = None
depends_on = None

def upgrade():
    # Create budgets table
    op.create_table('budgets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_budgets_id'), 'budgets', ['id'], unique=False)

    # Create budget_line_items table
    op.create_table('budget_line_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('budget_id', sa.Integer(), nullable=False),
        sa.Column('account_code', sa.String(length=50), nullable=False),
        sa.Column('account_name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('budgeted_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('actual_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('variance', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['budget_id'], ['budgets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_budget_line_items_id'), 'budget_line_items', ['id'], unique=False)

    # Create budget_approvals table
    op.create_table('budget_approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('budget_id', sa.Integer(), nullable=False),
        sa.Column('approver_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['budget_id'], ['budgets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_budget_approvals_id'), 'budget_approvals', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_budget_approvals_id'), table_name='budget_approvals')
    op.drop_table('budget_approvals')
    op.drop_index(op.f('ix_budget_line_items_id'), table_name='budget_line_items')
    op.drop_table('budget_line_items')
    op.drop_index(op.f('ix_budgets_id'), table_name='budgets')
    op.drop_table('budgets')