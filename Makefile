.PHONY: up down test lint migrate seed reset-db install-backend install-frontend

COMPOSE ?= docker compose

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

install-backend:
	cd backend && pip install -e ".[dev]"

install-frontend:
	cd frontend && npm ci

lint:
	cd backend && ruff check app tests
	cd backend && ruff format --check app tests
	cd frontend && npm run lint
	cd frontend && npm run type-check

test:
	cd backend && pytest tests/ -q

migrate:
	cd backend && alembic upgrade head

seed:
	@echo "Seed script not yet implemented — add pilot data in a future phase."

reset-db:
	cd backend && alembic downgrade base && alembic upgrade head
