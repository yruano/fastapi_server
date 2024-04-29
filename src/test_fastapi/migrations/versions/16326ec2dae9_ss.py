"""ss

Revision ID: 16326ec2dae9
Revises: 55e21f90579f
Create Date: 2024-04-30 02:49:50.112617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16326ec2dae9'
down_revision: Union[str, None] = '55e21f90579f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
