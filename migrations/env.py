# migrations/env.py
import sys
from logging.config import fileConfig
from pathlib import Path

# Add the project root directory to the Python path
root_path = Path(__file__).parents[1]
sys.path.append(str(root_path))

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from backend.app.config import get_settings
from backend.app.db.base import Base
# These imports are needed for Alembic to detect model changes
# even though they appear unused
from backend.app.models.user import User  # noqa: F401
from backend.app.models.role import Role  # noqa: F401
from backend.app.models.profile import UserProfile  # noqa: F401

# Load application config
settings = get_settings()

# Alembic Config object
config = context.config

# Set sqlalchemy.url in alembic.ini from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set metadata target for migrations
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True  # Add type comparison for migrations
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()