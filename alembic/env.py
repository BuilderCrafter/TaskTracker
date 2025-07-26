from __future__ import with_statement

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── make sure "app." imports resolve even if CWD == alembic/ ────────────────
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.database import Base  # Base = declarative_base() in your project

# ── Adding models to the migrations ─────────────────────────────────────────
from app.users import models as user_models  # noqa: F401
from app.tasks import models as task_models  # noqa: F401
from app.projects import models as project_models  # noqa: F401

# ── Alembic config & logging ────────────────────────────────────────────────
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject the runtime URL so it matches the application 1-to-1
config.set_main_option("sqlalchemy.url", settings.db_url)
target_metadata = Base.metadata


# ── OFFLINE (SQL script) mode ───────────────────────────────────────────────
def run_migrations_offline() -> None:
    context.configure(
        url=settings.db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── helper for the async path ───────────────────────────────────────────────
def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


# ── ONLINE async mode ───────────────────────────────────────────────────────
async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        poolclass=pool.NullPool,
        future=True,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


# ── Entrypoint ─────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
