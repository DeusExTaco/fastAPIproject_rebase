# noinspection SpellCheckingInspection
"""add timestamp fields

Revision ID: 5fa55f02cbff
Revises: 
Create Date: 2024-11-18 04:51:14.410890+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
# noinspection SpellCheckingInspection
revision: str = '5fa55f02cbff'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Add timestamp fields to user profiles and addresses tables"""

    # 1. Add timestamp columns as nullable initially
    op.add_column('user_profiles',
                  sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('user_profiles',
                  sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True))

    op.add_column('user_addresses',
                  sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('user_addresses',
                  sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True))

    # 2. Update existing records with current timestamp
    op.execute("""
        UPDATE user_profiles 
        SET created_at = CURRENT_TIMESTAMP, 
            updated_at = CURRENT_TIMESTAMP
    """)

    op.execute("""
        UPDATE user_addresses 
        SET created_at = CURRENT_TIMESTAMP, 
            updated_at = CURRENT_TIMESTAMP
    """)

    # 3. Modify columns to be non-nullable with default values
    # For user_profiles
    op.execute("""
        ALTER TABLE user_profiles 
        MODIFY created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    """)

    op.execute("""
        ALTER TABLE user_profiles 
        MODIFY updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    """)

    # For user_addresses
    op.execute("""
        ALTER TABLE user_addresses 
        MODIFY created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    """)

    op.execute("""
        ALTER TABLE user_addresses 
        MODIFY updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    """)


def downgrade():
    """Remove timestamp fields from user profiles and addresses tables"""

    # Remove the columns from user_profiles
    op.drop_column('user_profiles', 'updated_at')
    op.drop_column('user_profiles', 'created_at')

    # Remove the columns from user_addresses
    op.drop_column('user_addresses', 'updated_at')
    op.drop_column('user_addresses', 'created_at')
