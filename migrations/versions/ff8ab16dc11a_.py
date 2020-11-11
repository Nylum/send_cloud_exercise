"""
Revision ID: ff8ab16dc11a
Revises:
Create Date: 2020-11-10 16:33:36.751068

"""
from alembic import op
import sqlalchemy as sa


revision = 'ff8ab16dc11a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('email', sa.String(length=254), nullable=True))


def downgrade():
    op.drop_column('users', 'email')
