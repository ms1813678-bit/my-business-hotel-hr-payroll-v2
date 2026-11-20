from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.auth import get_current_admin


def require_admin(request: Request) -> str:
    username = get_current_admin(request)
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")
    return username


DbSession = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[str, Depends(require_admin)]
