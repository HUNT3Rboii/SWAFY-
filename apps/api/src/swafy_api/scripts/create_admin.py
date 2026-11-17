from __future__ import annotations

import os
import sys

from sqlalchemy import select

from swafy_api.core.security import hash_password
from swafy_api.db import get_session_factory
from swafy_api.models import User, UserRole


def main() -> int:
    email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    password = os.environ.get("ADMIN_PASSWORD", "")
    display_name = os.environ.get("ADMIN_DISPLAY_NAME", "").strip()
    if not email or not password or not display_name:
        print(
            "Set ADMIN_EMAIL, ADMIN_PASSWORD and ADMIN_DISPLAY_NAME before running this command.",
            file=sys.stderr,
        )
        return 2
    if len(password) < 12:
        print("ADMIN_PASSWORD must be at least 12 characters.", file=sys.stderr)
        return 2

    db = get_session_factory()()
    try:
        if db.scalar(select(User.id).where(User.email == email)) is not None:
            print("A user with ADMIN_EMAIL already exists; no changes made.", file=sys.stderr)
            return 1
        db.add(
            User(
                email=email,
                display_name=display_name,
                password_hash=hash_password(password),
                role=UserRole.MUNICIPAL_ADMIN,
            )
        )
        db.commit()
        print(f"Municipal administrator created: {email}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
