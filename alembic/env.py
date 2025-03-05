import sys
import os
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy import pool
from alembic import context
from src.models.base import Base

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations():
    """Run migrations."""
    connectable: AsyncEngine = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async def do_run_migrations(connection):
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

    async def run():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    import asyncio

    asyncio.run(run())


run_migrations()
