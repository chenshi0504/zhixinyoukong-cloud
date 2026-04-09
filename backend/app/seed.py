"""
数据库初始数据：创建默认 admin 和 teacher 账号。
在 lifespan 启动时自动调用，仅当 users 表为空时才插入。
"""
from sqlalchemy.orm import Session
from .models.user import User
from .models.organization import Organization
from .models.classroom import Class
from .services.auth import hash_password


def _ensure_default_org(db: Session) -> Organization:
    org = db.query(Organization).order_by(Organization.id.asc()).first()
    if org is None:
        org = Organization(name="示例机构")
        db.add(org)
        db.flush()
    return org


def seed_default_users(db: Session) -> None:
    if db.query(User).first() is not None:
        return

    admin = User(
        username="admin",
        password_hash=hash_password("123456"),
        role="super_admin",
        real_name="超级管理员",
        is_active=True,
    )
    db.add(admin)

    org = _ensure_default_org(db)
    teacher = User(
        username="teacher",
        password_hash=hash_password("123456"),
        role="teacher",
        real_name="示例教师",
        org_id=org.id,
        is_active=True,
    )
    db.add(teacher)

    student = User(
        username="student",
        password_hash=hash_password("123456"),
        role="student",
        real_name="示例学生",
        org_id=org.id,
        is_active=True,
    )
    db.add(student)

    db.commit()
    print("[seed] 已创建默认账号: admin/teacher/student 密码均为 123456")
