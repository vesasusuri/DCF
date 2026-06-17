#!/bin/sh
set -e

validate_required_env() {
  missing=0

  if [ -z "${DATABASE_URL:-}" ]; then
    echo "ERROR: DATABASE_URL is not set."
    echo "  Add your Supabase Postgres connection string to the project root .env file:"
    echo "  DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres"
    echo "  Find it in Supabase â†’ Project Settings â†’ Database â†’ Connection string."
    missing=1
  fi

  if [ -z "${SUPABASE_URL:-}" ]; then
    echo "ERROR: SUPABASE_URL is not set."
    echo "  Add to .env: SUPABASE_URL=https://[project-ref].supabase.co"
    missing=1
  fi

  if [ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
    echo "ERROR: SUPABASE_SERVICE_ROLE_KEY is not set."
    echo "  Add to .env from Supabase â†’ Project Settings â†’ API â†’ service_role key."
    missing=1
  fi

  if [ -z "${REDIS_URL:-}" ]; then
    echo "ERROR: REDIS_URL is not set."
    echo "  For Docker Compose use: REDIS_URL=redis://redis:6379/0"
    missing=1
  fi

  if [ "$missing" -ne 0 ]; then
    echo ""
    echo "Copy .env.example to .env and fill in the required Supabase values, then restart."
    exit 1
  fi
}

wait_for_redis() {
  echo "Waiting for Redis to accept connections..."
  python - <<'PY'
import os
import socket
import sys
import time
from urllib.parse import urlparse

redis_url = os.environ["REDIS_URL"]
timeout_seconds = int(os.environ.get("REDIS_WAIT_TIMEOUT", "30"))
parsed = urlparse(redis_url)
host = parsed.hostname or "redis"
port = parsed.port or 6379

for attempt in range(1, timeout_seconds + 1):
    try:
        with socket.create_connection((host, port), timeout=2):
            print("Redis is ready.")
            sys.exit(0)
    except OSError as exc:
        if attempt == timeout_seconds:
            print(
                f"Redis not ready after {timeout_seconds}s: {exc}",
                file=sys.stderr,
            )
            sys.exit(1)
        time.sleep(1)
PY
}

validate_required_env
wait_for_redis

if [ "${RUN_DB_MIGRATIONS:-true}" = "true" ]; then
  echo "Running database migrations..."
  if alembic upgrade head; then
    echo "Database migrations finished."
  else
    echo "ERROR: Database migrations failed."
    if [ "${DB_MIGRATIONS_REQUIRED:-true}" = "true" ]; then
      exit 1
    fi
  fi
fi

if [ "${RUN_STARTUP_SEED:-true}" = "true" ]; then
  echo "Running startup seed (Portfolio Manager)..."
  if python scripts/seed_portfolio_manager.py; then
    echo "Startup seed finished."
  else
    echo "ERROR: Portfolio Manager startup seed failed."
    if [ "${STARTUP_SEED_REQUIRED:-false}" = "true" ]; then
      exit 1
    fi
  fi
fi

echo "Starting FastAPI..."
UVICORN_ARGS="app.main:app --host 0.0.0.0 --port 8000"
if [ "${UVICORN_RELOAD:-false}" = "true" ]; then
  UVICORN_ARGS="$UVICORN_ARGS --reload"
fi
if [ "${UVICORN_ACCESS_LOG:-true}" = "false" ]; then
  UVICORN_ARGS="$UVICORN_ARGS --no-access-log"
fi
exec uvicorn $UVICORN_ARGS
