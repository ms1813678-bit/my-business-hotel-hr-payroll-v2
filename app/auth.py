from datetime import datetime, timezone
from typing import Optional

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AdminAccount
from app.security import verify_password


def authenticate_admin(db: Session, username: str, password: str) -> Optional[AdminAccount]:
    admin = db.scalar(select(AdminAccount).where(AdminAccount.username == username))
    if admin is None:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    admin.last_login_at = datetime.now(timezone.utc)
    db.add(admin)
    db.commit()
    return admin


def get_current_admin(request: Request) -> Optional[str]:
    return request.session.get("admin_username")
