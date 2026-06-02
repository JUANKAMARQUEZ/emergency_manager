"""add active field manually

Revision ID: 900ad1d01300
Revises: 
Create Date: 2026-06-02 15:15:46.036295

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '900ad1d01300'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                'active',
                sa.Boolean(),
                nullable=False,
                server_default=sa.text('true')
            )
        )


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:

        batch_op.drop_column('active')
