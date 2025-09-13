"""Initial database setup

Revision ID: 001_initial
Create Date: 2025-09-13
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True),
        sa.Column('role', sa.String(50)),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime())
    )

    # Create clubs table
    op.create_table(
        'clubs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), unique=True, index=True),
        sa.Column('description', sa.String(1000)),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('leader_id', sa.Integer(), sa.ForeignKey('users.id'))
    )

    # Create activities table
    op.create_table(
        'activities',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), unique=True, index=True),
        sa.Column('description', sa.String(1000)),
        sa.Column('schedule', sa.String(255)),
        sa.Column('max_participants', sa.Integer()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('club_id', sa.Integer(), sa.ForeignKey('clubs.id'))
    )

    # Create activity_participants association table
    op.create_table(
        'activity_participants',
        sa.Column('activity_id', sa.Integer(), sa.ForeignKey('activities.id'), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), primary_key=True)
    )

def downgrade():
    op.drop_table('activity_participants')
    op.drop_table('activities')
    op.drop_table('clubs')
    op.drop_table('users')