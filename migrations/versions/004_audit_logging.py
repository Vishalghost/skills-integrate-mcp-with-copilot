"""Add audit logging

Revision ID: 004_audit_logging
Create Date: 2025-09-13
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '004_audit_logging'
down_revision = '003_rbac_and_clubs'
branch_labels = None
depends_on = None

def upgrade():
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('actor_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.Integer()),
        sa.Column('details', sa.String(1000)),
        sa.Column('ip_address', sa.String(45))
    )

    # Add indexes
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('ix_audit_logs_actor_id', 'audit_logs', ['actor_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])

def downgrade():
    # Drop indexes
    op.drop_index('ix_audit_logs_entity_type')
    op.drop_index('ix_audit_logs_action')
    op.drop_index('ix_audit_logs_actor_id')
    op.drop_index('ix_audit_logs_timestamp')

    # Drop table
    op.drop_table('audit_logs')