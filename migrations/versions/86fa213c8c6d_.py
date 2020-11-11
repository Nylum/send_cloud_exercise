"""
Revision ID: 86fa213c8c6d
Revises: ff8ab16dc11a
Create Date: 2020-11-10 16:34:07.567419

"""
from alembic import op
import sqlalchemy as sa

revision = '86fa213c8c6d'
down_revision = 'ff8ab16dc11a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('users', 'email')


def downgrade():
    op.add_column('users', sa.Column('email', sa.VARCHAR(length=254), autoincrement=False, nullable=True))
