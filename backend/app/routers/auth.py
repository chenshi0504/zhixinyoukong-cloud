"""
认证路由：登录、登出、刷新 Token。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models.user import User
from ..schemas.user import (
    LoginRequest, LoginResponse, UserRead,
    TokenRefreshRequest, TokenRefreshResponse,
)
from ..services.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    validate_refresh_token,
    revoke_refresh_token,
)

router = APIRouter(prefix="/api/cloud/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, body.username, body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(db, user)
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    user = validate_refresh_token(db, body.refresh_token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token 无效或已过期",
        )
    access_token = create_access_token(user)
    return TokenRefreshResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    body: TokenRefreshRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    revoke_refresh_token(db, body.refresh_token)
