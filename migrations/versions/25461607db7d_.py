"""empty message

Revision ID: 25461607db7d
Revises: 6abd4fbeb3d7
Create Date: 2025-03-15 20:13:05.022787

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25461607db7d'
down_revision = '6abd4fbeb3d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('blog_tags',
    sa.Column('blog_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['blog_id'], ['blog.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('blog_id', 'tag_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blog_tags')
    op.drop_table('tag')
    # ### end Alembic commands ###
