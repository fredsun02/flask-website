"""empty message

Revision ID: 1922eed9233d
Revises: 25461607db7d
Create Date: 2025-03-16 04:00:26.581891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1922eed9233d'
down_revision = '25461607db7d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author_name', sa.String(length=64), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_column('author_name')

    # ### end Alembic commands ###
