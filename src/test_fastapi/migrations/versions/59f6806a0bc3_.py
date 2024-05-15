"""empty message

Revision ID: 59f6806a0bc3
Revises: d126a43541e4
Create Date: 2024-05-11 20:52:04.435519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '59f6806a0bc3'
down_revision: Union[str, None] = 'd126a43541e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('User', 'password',
               existing_type=mysql.VARCHAR(length=500),
               type_=sa.String(length=20),
               existing_nullable=False)
    op.create_unique_constraint(op.f('uq_User_User_NickName'), 'User', ['User_NickName'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq_User_User_NickName'), 'User', type_='unique')
    op.alter_column('User', 'password',
               existing_type=sa.String(length=20),
               type_=mysql.VARCHAR(length=500),
               existing_nullable=False)
    # ### end Alembic commands ###