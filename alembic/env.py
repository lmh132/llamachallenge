import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# ─── STEP 1: Make sure backend/ is importable ────────────────
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ─── STEP 2: Load .env file ──────────────────────────────────
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

# ─── STEP 3: Load config and metadata ────────────────────────
from backend.database import Base  # must come after sys.path.append
from backend import models         # ensure all models are registered

config = context.config

# This sets up Python logging from alembic.ini
if config.config_file_name:
    fileConfig(config.config_file_name)

# Inject the DB URL from the environment (.env)
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

target_metadata = Base.metadata

# ─── STEP 4: Offline mode ─────────────────────────────────────
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# ─── STEP 5: Online (asyncpg) mode ────────────────────────────
def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def run_migrations(connection):
        context.configure(connection=connection, target_metadata=target_metadata)

        async with context.begin_transaction():
            await context.run_migrations()

    import asyncio
    async def run():
        async with connectable.connect() as connection:
            await connection.run_sync(run_migrations)

        await connectable.dispose()

    import asyncio
    asyncio.run(run())
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
