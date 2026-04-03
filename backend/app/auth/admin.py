from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings
from app.schemas.admin import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/admin", tags=["admin-auth"])
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    if body.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")

    payload = {
        "sub": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    secret = settings.JWT_SECRET or settings.ADMIN_PASSWORD
    token = jwt.encode(payload, secret, algorithm="HS256")
    return LoginResponse(token=token)


async def get_admin(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    try:
        secret = settings.JWT_SECRET or settings.ADMIN_PASSWORD
        payload = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=["HS256"],
        )
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
