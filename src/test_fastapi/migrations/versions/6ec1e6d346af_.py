"""empty message

Revision ID: 6ec1e6d346af
Revises: 766309cce1a8
Create Date: 2024-05-12 23:47:29.095309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '6ec1e6d346af'
down_revision: Union[str, None] = '766309cce1a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('User', 'password',
               existing_type=mysql.VARCHAR(length=30),
               type_=sa.String(length=100),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('User', 'password',
               existing_type=sa.String(length=100),
               type_=mysql.VARCHAR(length=30),
               existing_nullable=False)
    # ### end Alembic commands ###