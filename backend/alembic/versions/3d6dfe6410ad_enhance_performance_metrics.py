"""enhance_performance_metrics

Revision ID: 3d6dfe6410ad
Revises: 5fa55f02cbff
Create Date: 2024-11-20 20:40:03.302414+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d6dfe6410ad'
down_revision: Union[str, None] = '5fa55f02cbff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
