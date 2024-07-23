import asyncio
import logging.config

import alembic.context
import yaml
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

import events_service.models
import events_service.settings

settings = events_service.settings.settings
config = alembic.context.config
config.set_main_option(
    "sqlalchemy.url",
    str(settings.default_database_url),
)

if settings.default_log_config is not None:
    with settings.default_log_config.open("r") as stream:
        logging.config.dictConfig(yaml.safe_load(stream))


target_metadata = events_service.models.Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    alembic.context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    alembic.context.configure(
        connection=connection, target_metadata=target_metadata
    )

    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if alembic.context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
