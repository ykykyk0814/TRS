from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

import os
import sys
from dotenv import load_dotenv

# Add app folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load .env
load_dotenv()

# Import your Base metadata
from app.db import Base

# Alembic Config object
config = context.config

# Configure logging
fileConfig(config.config_file_name)

# Get async DB URL from .env
async_db_url = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/travel_recommendation",
)

# Convert to sync DB URL for Alembic
if async_db_url.startswith("postgresql+asyncpg"):
    sync_db_url = async_db_url.replace("postgresql+asyncpg", "postgresql")
else:
    sync_db_url = async_db_url

# Set SQLAlchemy URL for Alembic
config.set_main_option("sqlalchemy.url", sync_db_url)

# Point to your models' metadata
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
