"""20220610更

Revision ID: 1fcf18bd7d15
Revises: 
Create Date: 2022-06-10 21:58:06.777007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1fcf18bd7d15'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('LaitGood_Newsdata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image', sa.String(length=80), nullable=False),
    sa.Column('title', sa.String(length=80), nullable=False),
    sa.Column('slogan', sa.String(length=80), nullable=True),
    sa.Column('content', sa.String(length=80), nullable=True),
    sa.Column('newsdate', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('LaitGood_UserRegister',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=80), nullable=False),
    sa.Column('password_hash', sa.String(length=50), nullable=False),
    sa.Column('agreecheck', sa.Boolean(), nullable=True),
    sa.Column('registered_on', sa.DateTime(), nullable=False),
    sa.Column('confirm', sa.Boolean(), nullable=True),
    sa.Column('confirmed_on', sa.DateTime(), nullable=True),
    sa.Column('roles', sa.Boolean(), nullable=True),
    sa.Column('birthday', sa.DateTime(), nullable=True),
    sa.Column('gender', sa.String(length=5), nullable=True),
    sa.Column('cellphone', sa.Integer(), nullable=True),
    sa.Column('phone', sa.Integer(), nullable=True),
    sa.Column('address', sa.String(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('LaitGood_commends_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image', sa.String(length=80), nullable=False),
    sa.Column('title', sa.String(length=80), nullable=False),
    sa.Column('slogan', sa.String(length=80), nullable=True),
    sa.Column('url', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('posts')
    op.drop_table('LaitGood_commends_data')
    op.drop_table('LaitGood_UserRegister')
    op.drop_table('LaitGood_Newsdata')
    # ### end Alembic commands ###
