"""add full_name to users

Revision ID: 34e5ec15f23c
Revises: 69d0b2be3d24
Create Date: 2025-07-18 02:24:18.306306

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "34e5ec15f23c"
down_revision = "69d0b2be3d24"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'full_name')
