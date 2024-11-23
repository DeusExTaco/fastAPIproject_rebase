"""unique_email

Revision ID: 7928c4cd20c0
Revises: 3d6dfe6410ad
Create Date: 2024-11-20 20:40:30.525586+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7928c4cd20c0'
down_revision: Union[str, None] = '3d6dfe6410ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add unique constraint to email column
    op.create_unique_constraint('uq_users_email', 'users', ['email'])

def downgrade() -> None:
    # Remove unique constraint from email column
    op.drop_constraint('uq_users_email', 'users')
