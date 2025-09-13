"""Add RBAC and club management

Revision ID: 003_rbac_and_clubs
Create Date: 2025-09-13
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '003_rbac_and_clubs'
down_revision = '002_initial_data'
branch_labels = None
depends_on = None

def upgrade():
    # Modify users table
    op.add_column('users', sa.Column('hashed_password', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

    # Modify clubs table
    op.add_column('clubs', sa.Column('category', sa.String(100), nullable=True))
    op.add_column('clubs', sa.Column('max_members', sa.Integer(), nullable=True))
    op.add_column('clubs', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

    # Create club_roles table
    op.create_table(
        'club_roles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('permissions', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('club_id', sa.Integer(), sa.ForeignKey('clubs.id'), nullable=False)
    )

    # Create club_members table
    op.create_table(
        'club_members',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('club_id', sa.Integer(), sa.ForeignKey('clubs.id'), nullable=False),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('club_roles.id'), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False)
    )

    # Create club_budgets table
    op.create_table(
        'club_budgets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('club_id', sa.Integer(), sa.ForeignKey('clubs.id'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False)
    )

    # Add indexes
    op.create_index('ix_club_roles_club_id', 'club_roles', ['club_id'])
    op.create_index('ix_club_members_user_id', 'club_members', ['user_id'])
    op.create_index('ix_club_members_club_id', 'club_members', ['club_id'])
    op.create_index('ix_club_budgets_club_id', 'club_budgets', ['club_id'])
    op.create_index('ix_club_budgets_created_by_id', 'club_budgets', ['created_by_id'])

def downgrade():
    # Drop indexes
    op.drop_index('ix_club_budgets_created_by_id')
    op.drop_index('ix_club_budgets_club_id')
    op.drop_index('ix_club_members_club_id')
    op.drop_index('ix_club_members_user_id')
    op.drop_index('ix_club_roles_club_id')

    # Drop tables
    op.drop_table('club_budgets')
    op.drop_table('club_members')
    op.drop_table('club_roles')

    # Remove columns from clubs
    op.drop_column('clubs', 'is_active')
    op.drop_column('clubs', 'max_members')
    op.drop_column('clubs', 'category')

    # Remove columns from users
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'hashed_password')