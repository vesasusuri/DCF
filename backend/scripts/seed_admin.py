#!/usr/bin/env python3
"""Create or update seeded admin and demo user accounts in Supabase Auth."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

from supabase import Client, create_client


def get_client() -> Client:
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
        sys.exit(1)
    return create_client(url, key)


def find_user_id_by_email(client: Client, email: str) -> str | None:
    page = 1
    while True:
        response = client.auth.admin.list_users(page=page, per_page=200)
        users = response if isinstance(response, list) else getattr(response, "users", [])
        if not users:
            return None
        for user in users:
            user_email = getattr(user, "email", None) or user.get("email")
            if user_email == email:
                return getattr(user, "id", None) or user.get("id")
        if len(users) < 200:
            return None
        page += 1


def ensure_user(
    client: Client,
    *,
    email: str,
    password: str,
    role: str,
    full_name: str,
) -> None:
    user_id = find_user_id_by_email(client, email)

    if user_id:
        client.auth.admin.update_user_by_id(
            user_id,
            {
                "password": password,
                "email_confirm": True,
                "user_metadata": {"role": role, "full_name": full_name},
            },
        )
        client.table("profiles").upsert(
            {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "role": role,
            }
        ).execute()
        print(f"Updated existing user: {email} ({role})")
        return

    created = client.auth.admin.create_user(
        {
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"role": role, "full_name": full_name},
        }
    )
    created_id = getattr(created.user, "id", None) or created.user.get("id")
    if created_id:
        client.table("profiles").upsert(
            {
                "id": created_id,
                "email": email,
                "full_name": full_name,
                "role": role,
            }
        ).execute()
    print(f"Created user: {email} ({role})")


def main() -> None:
    client = get_client()

    admin_email = os.environ.get("SYSTEM_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("SYSTEM_ADMIN_PASSWORD", "Admin1234!")
    user_email = os.environ.get("DEMO_USER_EMAIL", "user@example.com")
    user_password = os.environ.get("DEMO_USER_PASSWORD", "User1234!")

    ensure_user(
        client,
        email=admin_email,
        password=admin_password,
        role="admin",
        full_name="System Admin",
    )
    ensure_user(
        client,
        email=user_email,
        password=user_password,
        role="user",
        full_name="Demo User",
    )

    print("\nSeeded accounts:")
    print(f"  Admin : {admin_email} / {admin_password}")
    print(f"  User  : {user_email} / {user_password}")


if __name__ == "__main__":
    main()
