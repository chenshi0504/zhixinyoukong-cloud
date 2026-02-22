"""
管理后台 Dashboard 路由。
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_role
from ..models.organization import Organization
from ..models.license import License
from ..models.report import Report

router = APIRouter(prefix="/api/cloud/admin", tags=["管理后台"])


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    _=Depends(require_role("super_admin", "org_admin")),
):
    total_orgs = db.query(sa_func.count(Organization.id)).scalar() or 0
    total_licenses = db.query(sa_func.count(License.id)).scalar() or 0
    active_licenses = db.query(sa_func.count(License.id)).filter(License.is_active == True).scalar() or 0
    pending_reports = db.query(sa_func.count(Report.id)).filter(Report.status == "submitted").scalar() or 0

    return {
        "total_organizations": total_orgs,
        "total_licenses": total_licenses,
        "active_licenses": active_licenses,
        "pending_reports": pending_reports,
    }
