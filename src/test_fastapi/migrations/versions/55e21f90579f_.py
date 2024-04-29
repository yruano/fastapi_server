"""empty message

Revision ID: 55e21f90579f
Revises: acbdbd1b949c
Create Date: 2024-04-30 02:19:48.992816

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55e21f90579f'
down_revision: Union[str, None] = 'acbdbd1b949c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
