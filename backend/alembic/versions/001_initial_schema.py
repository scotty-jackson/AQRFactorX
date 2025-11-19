"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create factor_group table
    op.create_table(
        'factor_group',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_factor_group_code'), 'factor_group', ['code'], unique=True)
    op.create_index(op.f('ix_factor_group_id'), 'factor_group', ['id'], unique=False)

    # Create factor table
    op.create_table(
        'factor',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('asset_class', sa.String(length=100), nullable=True),
        sa.Column('frequency', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('first_date', sa.Date(), nullable=True),
        sa.Column('last_date', sa.Date(), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('total_return', sa.Float(), nullable=True),
        sa.Column('annualized_return', sa.Float(), nullable=True),
        sa.Column('annualized_volatility', sa.Float(), nullable=True),
        sa.Column('max_drawdown', sa.Float(), nullable=True),
        sa.Column('sharpe_ratio', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['factor_group.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_factor_asset_class'), 'factor', ['asset_class'], unique=False)
    op.create_index(op.f('ix_factor_code'), 'factor', ['code'], unique=True)
    op.create_index(op.f('ix_factor_frequency'), 'factor', ['frequency'], unique=False)
    op.create_index(op.f('ix_factor_group_id'), 'factor', ['group_id'], unique=False)
    op.create_index(op.f('ix_factor_id'), 'factor', ['id'], unique=False)
    op.create_index(op.f('ix_factor_name'), 'factor', ['name'], unique=False)
    op.create_index(op.f('ix_factor_region'), 'factor', ['region'], unique=False)
    op.create_index('idx_factor_region_freq', 'factor', ['region', 'frequency'], unique=False)

    # Create factor_return table
    op.create_table(
        'factor_return',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('factor_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('return_value', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['factor_id'], ['factor.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_factor_return_date'), 'factor_return', ['date'], unique=False)
    op.create_index(op.f('ix_factor_return_factor_id'), 'factor_return', ['factor_id'], unique=False)
    op.create_index(op.f('ix_factor_return_id'), 'factor_return', ['id'], unique=False)
    op.create_index('idx_factor_return_date', 'factor_return', ['date'], unique=False)
    op.create_index('idx_factor_return_factor_date', 'factor_return', ['factor_id', 'date'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_factor_return_factor_date', table_name='factor_return')
    op.drop_index('idx_factor_return_date', table_name='factor_return')
    op.drop_index(op.f('ix_factor_return_id'), table_name='factor_return')
    op.drop_index(op.f('ix_factor_return_factor_id'), table_name='factor_return')
    op.drop_index(op.f('ix_factor_return_date'), table_name='factor_return')
    op.drop_table('factor_return')

    op.drop_index('idx_factor_region_freq', table_name='factor')
    op.drop_index(op.f('ix_factor_region'), table_name='factor')
    op.drop_index(op.f('ix_factor_name'), table_name='factor')
    op.drop_index(op.f('ix_factor_id'), table_name='factor')
    op.drop_index(op.f('ix_factor_group_id'), table_name='factor')
    op.drop_index(op.f('ix_factor_frequency'), table_name='factor')
    op.drop_index(op.f('ix_factor_code'), table_name='factor')
    op.drop_index(op.f('ix_factor_asset_class'), table_name='factor')
    op.drop_table('factor')

    op.drop_index(op.f('ix_factor_group_id'), table_name='factor_group')
    op.drop_index(op.f('ix_factor_group_code'), table_name='factor_group')
    op.drop_table('factor_group')
