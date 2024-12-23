"""empty message

Revision ID: 245e170d06e0
Revises: 59f6806a0bc3
Create Date: 2024-05-11 21:07:09.205409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '245e170d06e0'
down_revision: Union[str, None] = '59f6806a0bc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('User', 'username',
               existing_type=mysql.VARCHAR(length=20),
               type_=sa.String(length=50),
               existing_nullable=False)
    op.alter_column('User', 'password',
               existing_type=mysql.VARCHAR(length=500),
               type_=sa.String(length=30),
               existing_nullable=False)
    op.drop_index('uq_User_User_Imail', table_name='User')
    op.create_unique_constraint(op.f('uq_User_User_NickName'), 'User', ['User_NickName'])
    op.drop_column('User', 'User_Imail')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('User', sa.Column('User_Imail', mysql.VARCHAR(length=50), nullable=True))
    op.drop_constraint(op.f('uq_User_User_NickName'), 'User', type_='unique')
    op.create_index('uq_User_User_Imail', 'User', ['User_Imail'], unique=True)
    op.alter_column('User', 'password',
               existing_type=sa.String(length=30),
               type_=mysql.VARCHAR(length=500),
               existing_nullable=False)
    op.alter_column('User', 'username',
               existing_type=sa.String(length=50),
               type_=mysql.VARCHAR(length=20),
               existing_nullable=False)
    # ### end Alembic commands ###
