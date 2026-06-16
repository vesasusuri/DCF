#!/usr/bin/env python3
"""Idempotent startup seed for the Portfolio Manager account in Supabase.

Ensures the user exists in:
  1. Supabase Auth (auth.users) via Admin API
  2. Application users table (public.profiles)

Default credentials (override via .env):
  PORTFOLIO_MANAGER_EMAIL=pm@example.com
  PORTFOLIO_MANAGER_PASSWORD=Pm1234!

Role label: PORTFOLIO_MANAGER (stored as app_role enum value: portfolio_manager)

---------------------------------------------------------------------------
Supabase Admin API calls used
---------------------------------------------------------------------------

1) Find auth user by email (paginated list):
   GET {SUPABASE_URL}/auth/v1/admin/users?page={n}&per_page=200
   Headers:
     apikey: {SUPABASE_SERVICE_ROLE_KEY}
     Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}

2) Create auth user (only if step 1 finds no match):
   POST {SUPABASE_URL}/auth/v1/admin/users
   Body:
     {
       "email": "pm@example.com",
       "password": "Pm1234!",
       "email_confirm": true,
       "user_metadata": {
         "role": "portfolio_manager",
         "full_name": "Portfolio Manager"
       }
     }

3) Update auth user (if step 1 finds a match):
   PUT {SUPABASE_URL}/auth/v1/admin/users/{user_id}
   Body: same shape as create (password + metadata refresh)

4) Check application profile:
   GET {SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}&select=id,email,role

5) Upsert application profile:
   POST {SUPABASE_URL}/rest/v1/profiles
   Headers include: Prefer: resolution=merge-duplicates
   Body:
     {
       "id": "{user_id}",
       "email": "pm@example.com",
       "full_name": "Portfolio Manager",
       "role": "portfolio_manager"
     }

---------------------------------------------------------------------------
Equivalent SQL (profiles check / upsert)
---------------------------------------------------------------------------

-- Check auth user
SELECT id, email
FROM auth.users
WHERE email = 'pm@example.com';

-- Check application user
SELECT id, email, full_name, role
FROM public.profiles
WHERE email = 'pm@example.com';

-- Upsert application user (service role bypasses RLS)
INSERT INTO public.profiles (id, email, full_name, role)
VALUES (
  '{user_id}',
  'pm@example.com',
  'Portfolio Manager',
  'portfolio_manager'::public.app_role
)
ON CONFLICT (id) DO UPDATE
SET
  email = EXCLUDED.email,
  full_name = EXCLUDED.full_name,
  role = EXCLUDED.role;
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

from supabase import Client, create_client

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [portfolio-manager-seed] %(message)s",
)
logger = logging.getLogger(__name__)

ROLE_LABEL = "PORTFOLIO_MANAGER"
ROLE_VALUE = "portfolio_manager"
DEFAULT_EMAIL = "pm@example.com"
DEFAULT_PASSWORD = "Pm1234!"
DEFAULT_FULL_NAME = "Portfolio Manager"


def get_client() -> Client:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        logger.error(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in the project root .env"
        )
        sys.exit(1)
    return create_client(url, key)


def get_migration_database_url() -> str | None:
    url = (
        os.environ.get("DATABASE_MIGRATION_URL", "").strip()
        or os.environ.get("DIRECT_URL", "").strip()
    )
    if not url:
        return None
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def ensure_portfolio_manager_role_enum() -> None:
    """Add portfolio_manager to public.app_role when missing (idempotent)."""
    database_url = get_migration_database_url()
    if not database_url:
        logger.warning(
            "DATABASE_MIGRATION_URL not set — cannot auto-apply app_role enum; "
            "run supabase/portfolio_managers.sql manually if profile upsert fails"
        )
        return

    try:
        import psycopg2
    except ImportError:
        logger.warning("psycopg2 not installed — cannot auto-apply app_role enum")
        return

    sql = """
    DO $$ BEGIN
      ALTER TYPE public.app_role ADD VALUE 'portfolio_manager';
    EXCEPTION
      WHEN duplicate_object THEN NULL;
    END $$;
    """
    logger.info(
        "Ensuring public.app_role includes 'portfolio_manager' — direct SQL via DATABASE_MIGRATION_URL"
    )
    try:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        logger.info("SUCCESS: app_role enum ready (portfolio_manager)")
    except Exception as exc:
        logger.error("FAILED: Could not apply app_role enum migration: %s", exc)
        raise


def find_auth_user_id_by_email(client: Client, email: str) -> str | None:
    page = 1
    while True:
        logger.info(
            "Checking Supabase Auth for %s — GET /auth/v1/admin/users?page=%s&per_page=200",
            email,
            page,
        )
        response = client.auth.admin.list_users(page=page, per_page=200)
        users = response if isinstance(response, list) else getattr(response, "users", [])
        if not users:
            return None
        for user in users:
            user_email = getattr(user, "email", None) or user.get("email")
            if user_email == email:
                user_id = getattr(user, "id", None) or user.get("id")
                logger.info("Auth user already exists: %s (id=%s)", email, user_id)
                return user_id
        if len(users) < 200:
            return None
        page += 1


def get_profile(client: Client, user_id: str) -> dict[str, Any] | None:
    logger.info(
        "Checking public.profiles — GET /rest/v1/profiles?id=eq.%s&select=id,email,full_name,role",
        user_id,
    )
    result = (
        client.table("profiles")
        .select("id,email,full_name,role")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    profile = result.data
    if profile:
        logger.info(
            "Application profile already exists: email=%s role=%s",
            profile.get("email"),
            profile.get("role"),
        )
    else:
        logger.info("Application profile not found for user id=%s", user_id)
    return profile


def ensure_auth_user(
    client: Client,
    *,
    email: str,
    password: str,
    full_name: str,
) -> str:
    user_id = find_auth_user_id_by_email(client, email)
    payload = {
        "password": password,
        "email_confirm": True,
        "user_metadata": {"role": ROLE_VALUE, "full_name": full_name},
    }

    if user_id:
        logger.info("Updating auth user — PUT /auth/v1/admin/users/%s", user_id)
        client.auth.admin.update_user_by_id(user_id, payload)
        logger.info("SUCCESS: Auth user updated (%s)", email)
        return user_id

    logger.info("Creating auth user — POST /auth/v1/admin/users")
    created = client.auth.admin.create_user(
        {
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"role": ROLE_VALUE, "full_name": full_name},
        }
    )
    user_id = getattr(created.user, "id", None) or created.user.get("id")
    if not user_id:
        logger.error("FAILED: Supabase Auth did not return a user id after create")
        sys.exit(1)
    logger.info("SUCCESS: Auth user created (%s, id=%s)", email, user_id)
    return user_id


def ensure_profile(
    client: Client,
    *,
    user_id: str,
    email: str,
    full_name: str,
) -> None:
    existing = get_profile(client, user_id)
    row = {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "role": ROLE_VALUE,
    }

    if existing:
        if (
            existing.get("email") == email
            and existing.get("full_name") == full_name
            and existing.get("role") == ROLE_VALUE
        ):
            logger.info("SUCCESS: Application profile already up to date (no write needed)")
            return
        logger.info(
            "Updating application profile — POST /rest/v1/profiles (upsert on id=%s)",
            user_id,
        )
    else:
        logger.info(
            "Creating application profile — POST /rest/v1/profiles (upsert on id=%s)",
            user_id,
        )

    try:
        client.table("profiles").upsert(row).execute()
    except Exception as exc:
        message = str(exc)
        if "portfolio_manager" in message and "app_role" in message:
            logger.error(
                "FAILED: Database enum public.app_role does not include 'portfolio_manager' yet."
            )
            logger.error(
                "Run this SQL in the Supabase SQL editor before re-running the seed:\n"
                "  supabase/portfolio_managers.sql\n"
                "Or at minimum:\n"
                "  ALTER TYPE public.app_role ADD VALUE IF NOT EXISTS 'portfolio_manager';"
            )
        raise
    logger.info("SUCCESS: Application profile upserted (role=%s / %s)", ROLE_VALUE, ROLE_LABEL)


def main() -> None:
    email = os.environ.get("PORTFOLIO_MANAGER_EMAIL", DEFAULT_EMAIL).strip()
    password = os.environ.get("PORTFOLIO_MANAGER_PASSWORD", DEFAULT_PASSWORD)
    full_name = os.environ.get("PORTFOLIO_MANAGER_FULL_NAME", DEFAULT_FULL_NAME).strip()

    logger.info("Starting Portfolio Manager startup seed")
    logger.info("Email: %s", email)
    logger.info("Role: %s (stored as %s)", ROLE_LABEL, ROLE_VALUE)

    try:
        ensure_portfolio_manager_role_enum()
        client = get_client()
        user_id = ensure_auth_user(
            client,
            email=email,
            password=password,
            full_name=full_name,
        )
        ensure_profile(
            client,
            user_id=user_id,
            email=email,
            full_name=full_name,
        )
    except Exception as exc:
        logger.exception("FAILED: Portfolio Manager seed error: %s", exc)
        sys.exit(1)

    logger.info("Portfolio Manager seed completed successfully")
    logger.info("Login: %s / %s", email, password)


if __name__ == "__main__":
    main()
