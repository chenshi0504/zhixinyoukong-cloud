"""
认证路由：登录、登出、刷新 Token、教师注册、修改密码。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models.user import User
from ..models.organization import Organization
from ..schemas.user import (
    LoginRequest, LoginResponse, UserRead,
    TokenRefreshRequest, TokenRefreshResponse,
    TeacherRegisterRequest, TeacherRegisterResponse,
    PasswordChangeRequest,
)
from ..services.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    validate_refresh_token,
    revoke_refresh_token,
    hash_password,
    verify_password,
    revoke_all_refresh_tokens,
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


@router.post("/register", response_model=TeacherRegisterResponse)
def register_teacher(body: TeacherRegisterRequest, db: Session = Depends(get_db)):
    """教师自助注册：提交姓名、机构名、密码，系统自动分配账号。"""
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度不能少于6位")
    if not body.real_name.strip():
        raise HTTPException(status_code=400, detail="姓名不能为空")
    if not body.org_name.strip():
        raise HTTPException(status_code=400, detail="机构名不能为空")

    # 查找或创建机构
    org = db.query(Organization).filter(Organization.name == body.org_name.strip()).first()
    if org is None:
        org = Organization(name=body.org_name.strip())
        db.add(org)
        db.flush()

    # 自动生成账号：teacher_ + 序号
    count = db.query(User).filter(User.role == "teacher").count()
    username = f"teacher{count + 1}"
    # 确保不重复
    while db.query(User).filter(User.username == username).first() is not None:
        count += 1
        username = f"teacher{count + 1}"

    user = User(
        username=username,
        password_hash=hash_password(body.password),
        role="teacher",
        real_name=body.real_name.strip(),
        org_id=org.id,
        is_active=True,
    )
    db.add(user)
    db.commit()

    return TeacherRegisterResponse(
        username=username,
        real_name=body.real_name.strip(),
        org_name=body.org_name.strip(),
    )


@router.post("/change-password", status_code=200)
def change_password(
    body: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """修改当前用户密码。"""
    if not verify_password(body.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度不能少于6位")
    current_user.password_hash = hash_password(body.new_password)
    # 吊销所有 refresh token，强制重新登录
    revoke_all_refresh_tokens(db, current_user.id)
    db.commit()
    return {"message": "密码修改成功，请重新登录"}


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
