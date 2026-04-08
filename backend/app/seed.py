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


def repair_teacher_orgs(db: Session) -> None:
    teachers = db.query(User).filter(User.role == "teacher", User.org_id.is_(None)).all()
    if not teachers:
        return

    orgs = db.query(Organization).order_by(Organization.id.asc()).all()
    fallback_org = None
    if len(orgs) == 1:
        fallback_org = orgs[0]
    elif len(orgs) == 0:
        fallback_org = _ensure_default_org(db)

    changed = False
    for teacher in teachers:
        managed_org_ids = [
            org_id
            for (org_id,) in db.query(Class.org_id)
            .filter(Class.teacher_id == teacher.id, Class.org_id.isnot(None))
            .distinct()
            .order_by(Class.org_id.asc())
            .all()
        ]
        target_org_id = managed_org_ids[0] if managed_org_ids else (fallback_org.id if fallback_org else None)
        if target_org_id is None:
            continue
        conflict = db.query(User).filter(
            User.id != teacher.id,
            User.username == teacher.username,
            User.org_id == target_org_id,
        ).first()
        if conflict is not None:
            continue
        teacher.org_id = target_org_id
        changed = True

    classes = db.query(Class).filter(Class.org_id.is_(None)).all()
    for cls in classes:
        teacher_org_id = cls.teacher.org_id if cls.teacher else None
        if teacher_org_id is None:
            continue
        cls.org_id = teacher_org_id
        changed = True

    if changed:
        db.commit()


def seed_default_users(db: Session) -> None:
    """如果数据库中没有任何用户，则创建默认账号。"""
    if db.query(User).first() is not None:
        repair_teacher_orgs(db)
        return

    # 创建超级管理员
    admin = User(
        username="admin",
        password_hash=hash_password("123456"),
        role="super_admin",
        real_name="超级管理员",
        is_active=True,
    )
    db.add(admin)

    # 创建示例教师账号
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

    db.commit()
    print("[seed] 已创建默认账号:")
    print("  - admin / 123456 (超级管理员)")
    print("  - teacher / 123456 (教师)")
