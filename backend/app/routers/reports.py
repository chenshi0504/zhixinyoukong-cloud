"""
报告管理路由：上传、列表、评分、下载。
"""
import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import get_current_user, require_role
from ..config import get_settings
from ..models.report import Report
from ..models.task import Task
from ..models.user import User
from ..schemas.report import ReportRead, GradeRequest
from ..schemas.common import PagedResponse

router = APIRouter(prefix="/api/cloud/reports", tags=["报告管理"])


def _get_accessible_report(db: Session, report_id: int, current_user: User) -> Report:
    q = db.query(Report).join(Task, Report.task_id == Task.id).filter(Report.id == report_id)
    if current_user.role == "org_admin":
        q = q.filter(Task.org_id == current_user.org_id)
    elif current_user.role == "teacher":
        q = q.filter(Task.teacher_id == current_user.id)
    report = q.options(joinedload(Report.student), joinedload(Report.task)).first()
    if report is None:
        raise HTTPException(status_code=404, detail="报告不存在")
    return report


@router.get("", response_model=PagedResponse[ReportRead])
def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    task_id: int | None = Query(None),
    student_id: int | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Report).join(Task, Report.task_id == Task.id)
    if current_user.role == "org_admin":
        q = q.filter(Task.org_id == current_user.org_id)
    elif current_user.role == "teacher":
        q = q.filter(Task.teacher_id == current_user.id)
    elif current_user.role == "student":
        q = q.filter(Report.student_id == current_user.id)
    if task_id:
        q = q.filter(Report.task_id == task_id)
    if student_id:
        q = q.filter(Report.student_id == student_id)
    if status_filter:
        q = q.filter(Report.status == status_filter)
    total = q.count()
    pages = (total + page_size - 1) // page_size if total > 0 else 1
    items = (
        q.options(joinedload(Report.student), joinedload(Report.task))
        .order_by(Report.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    # Populate student_name and task_title
    result = []
    for item in items:
        r = ReportRead.model_validate(item)
        if item.student:
            r.student_name = item.student.real_name or item.student.username
        if item.task:
            r.task_title = item.task.title
        result.append(r)
    return PagedResponse(items=result, total=total, page=page, page_size=page_size, pages=pages)


@router.post("/upload", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
def upload_report(
    file: UploadFile = File(...),
    task_id: int = Form(...),
    student_id: int = Form(...),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    upload_dir = os.path.join(settings.upload_dir, "reports")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, f"{task_id}_{student_id}_{file.filename}")
    content = file.file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    report = Report(
        task_id=task_id,
        student_id=student_id,
        file_path=file_path,
        original_filename=file.filename,
        file_size=len(content),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.put("/{report_id}/grade", response_model=ReportRead)
def grade_report(
    report_id: int,
    body: GradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "org_admin", "teacher")),
):
    report = _get_accessible_report(db, report_id, current_user)
    report.score = body.score
    report.feedback = body.feedback
    report.grader_id = current_user.id
    report.status = "graded"
    report.graded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(report)
    return report


@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin", "org_admin", "teacher")),
):
    report = _get_accessible_report(db, report_id, current_user)
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(report.file_path, filename=report.original_filename)
