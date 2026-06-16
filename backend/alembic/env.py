from logging.config import fileConfig
<<<<<<< HEAD

from alembic import context
from sqlalchemy import engine_from_config, pool
=======
from urllib.parse import unquote, urlparse

import psycopg2
from alembic import context
from sqlalchemy import create_engine, pool
>>>>>>> 78bbf064389164fb8c5cdaeeb14794ec4034a572

from app.core.config import get_settings
from app.infrastructure.models.project_model import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


<<<<<<< HEAD
def get_url() -> str:
    return get_settings().alembic_url


def run_migrations_offline() -> None:
    url = get_url()
=======
def get_connect_args() -> dict[str, object]:
    get_settings.cache_clear()
    raw = get_settings().direct_url or get_settings().database_url
    parsed = urlparse(raw.split("?")[0])
    return {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "user": parsed.username,
        "password": unquote(parsed.password or ""),
        "dbname": (parsed.path or "/postgres").lstrip("/") or "postgres",
    }


def get_engine():
    args = get_connect_args()

    def connect() -> psycopg2.extensions.connection:
        return psycopg2.connect(**args)

    return create_engine(
        "postgresql+psycopg2://",
        poolclass=pool.NullPool,
        creator=connect,
    )


def run_migrations_offline() -> None:
    args = get_connect_args()
    url = (
        f"postgresql://{args['user']}:{args['password']}"
        f"@{args['host']}:{args['port']}/{args['dbname']}"
    )
>>>>>>> 78bbf064389164fb8c5cdaeeb14794ec4034a572
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
<<<<<<< HEAD
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
=======
    with get_engine().connect() as connection:
>>>>>>> 78bbf064389164fb8c5cdaeeb14794ec4034a572
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
