import os
import shutil
from datetime import datetime
from logging.config import fileConfig

from alembic import context, runtime
from alembic.migration import MigrationContext
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from app.repository.models import BaseModel

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/example.db")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


config.set_main_option("sqlalchemy.url", DATABASE_URL)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def create_backup(revision_id: str | None):
    db_path = DATABASE_URL.split("///")[-1]

    backup_path = f"{db_path}.{revision_id}.{datetime.now().strftime('%Y-%m-%dT%H_%M_%S.%f')}.backup"

    if os.path.exists(db_path):
        shutil.copyfile(db_path, backup_path)
        print(f"Backup created at {backup_path}")
    else:
        print(f"Database file {db_path} not found. No backup created.")


create_backup(revision_id=context.get_head_revision())


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
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
