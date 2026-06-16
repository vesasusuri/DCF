from logging.config import fileConfig
from urllib.parse import unquote, urlparse

import psycopg2
from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import get_settings
from app.infrastructure.models.project_model import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_connect_args() -> dict[str, object]:
    get_settings.cache_clear()
    settings = get_settings()
    raw = (
        settings.database_migration_url
        or settings.direct_url
        or settings.database_url
    ).strip()
    if not raw:
        raise RuntimeError(
            "Database URL is not configured. Set DATABASE_MIGRATION_URL, DIRECT_URL, "
            "or DATABASE_URL in the project root .env file."
        )
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
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with get_engine().connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
