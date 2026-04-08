"""
认证路由：登录、登出、刷新 Token、教师注册、修改密码。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models.user import User
from ..models.organization import Organization
from ..models.classroom import Class
from ..schemas.user import (
    LoginRequest, LoginResponse, UserRead,
    TokenRefreshRequest, TokenRefreshResponse,
    TeacherRegisterRequest, TeacherRegisterResponse,
    UserRegisterRequest, UserRegisterResponse,
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
    user = authenticate_user(db, body.username, body.password, body.org_id)
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


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)


@router.post("/register", response_model=TeacherRegisterResponse)
def register_teacher(body: TeacherRegisterRequest, db: Session = Depends(get_db)):
    """教师自助注册：提交姓名、机构名、密码，系统自动分配账号。"""
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度不能少于6位")
    if not body.real_name.strip():
        raise HTTPException(status_code=400, detail="姓名不能为空")
    if body.org_id is None and not (body.org_name and body.org_name.strip()):
        raise HTTPException(status_code=400, detail="请选择所属机构")

    if body.org_id is not None:
        org = db.query(Organization).filter(Organization.id == body.org_id).first()
        if org is None:
            raise HTTPException(status_code=400, detail="机构不存在")
    else:
        org_name = body.org_name.strip()
        org = db.query(Organization).filter(Organization.name == org_name).first()
        if org is None:
            org = Organization(name=org_name)
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
        org_id=org.id,
        org_name=org.name,
    )


@router.post("/register/user", response_model=UserRegisterResponse)
def register_user(body: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    学生实名注册：选择机构+班级，系统自动分配用户名。
    用户名规则：stu + 班级ID(补零4位) + 序号(补零3位)，如 stu0001001
    """
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度不能少于6位")
    if not body.real_name or not body.real_name.strip():
        raise HTTPException(status_code=400, detail="真实姓名不能为空")

    # 验证机构
    org = db.query(Organization).filter(Organization.id == body.org_id).first()
    if not org:
        raise HTTPException(status_code=400, detail="机构不存在")

    # 验证班级
    cls = db.query(Class).filter(Class.id == body.class_id, Class.org_id == body.org_id).first()
    if not cls:
        raise HTTPException(status_code=400, detail="班级不存在或不属于该机构")

    # 自动生成用户名：stu + 班级ID(4位) + 序号(3位)
    prefix = f"stu{body.class_id:04d}"
    count = db.query(User).filter(User.username.like(f"{prefix}%")).count()
    username = f"{prefix}{count + 1:03d}"
    while db.query(User).filter(User.username == username).first() is not None:
        count += 1
        username = f"{prefix}{count + 1:03d}"

    user = User(
        username=username,
        password_hash=hash_password(body.password),
        role="student",
        real_name=body.real_name.strip(),
        org_id=body.org_id,
        is_active=True,
    )
    db.add(user)
    db.flush()

    # 将学生加入班级
    if user not in cls.students:
        cls.students.append(user)

    db.commit()
    db.refresh(user)

    return UserRegisterResponse(user=UserRead.model_validate(user))


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
