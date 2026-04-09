"""
任务管理路由：CRUD + 发布。
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_role
from ..models.task import Task
from ..models.report import Report
from ..models.user import User
from ..schemas.task import TaskCreate, TaskRead, TaskUpdate
from ..schemas.common import PagedResponse

router = APIRouter(prefix="/api/cloud/tasks", tags=["任务管理"])


@router.get("", response_model=PagedResponse[TaskRead])
def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    org_id: int | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Task)
    if current_user.role in ("org_admin", "teacher"):
        q = q.filter(Task.org_id == current_user.org_id)
    elif org_id is not None:
        q = q.filter(Task.org_id == org_id)
    if status_filter:
        q = q.filter(Task.status == status_filter)
    total = q.count()
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    items = q.order_by(Task.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PagedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    body: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "org_admin", "teacher")),
):
    task = Task(
        title=body.title,
        description=body.description,
        module_id=body.module_id,
        teacher_id=current_user.id,
        org_id=body.org_id or current_user.org_id,
        deadline=body.deadline,
        max_score=body.max_score,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    body: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "org_admin", "teacher")),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "org_admin", "teacher")),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task.status == "published":
        report_count = db.query(sa_func.count(Report.id)).filter(Report.task_id == task_id).scalar() or 0
        if report_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="已发布任务有提交记录，无法删除",
            )
    db.delete(task)
    db.commit()


@router.post("/{task_id}/publish", response_model=TaskRead)
def publish_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "org_admin", "teacher")),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task.status != "draft":
        raise HTTPException(status_code=400, detail="只有草稿任务可以发布")
    task.status = "published"
    db.commit()
    db.refresh(task)
    return task
