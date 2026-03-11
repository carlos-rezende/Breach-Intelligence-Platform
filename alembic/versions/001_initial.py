"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'])

    op.create_table(
        'breach_checks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('breach_count', sa.Integer(), nullable=False),
        sa.Column('providers_used', sa.String(500), nullable=True),
        sa.Column('risk_score', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_breach_checks_email'), 'breach_checks', ['email'])

    op.create_table(
        'breach_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('breach_check_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('provider', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['breach_check_id'], ['breach_checks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('breach_records')
    op.drop_table('breach_checks')
    op.drop_table('users')
