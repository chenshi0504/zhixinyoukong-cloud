import os
import logging
from logging.handlers import RotatingFileHandler
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import engine, Base

settings = get_settings()

# ---- Logging: stdout + rotating file ----
_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(_LOG_DIR, exist_ok=True)
_LOG_FMT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_LOG_LEVEL = logging.DEBUG if settings.debug else logging.INFO
logging.basicConfig(level=_LOG_LEVEL, format=_LOG_FMT)
_fh = RotatingFileHandler(os.path.join(_LOG_DIR, "cloud.log"), maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
_fh.setLevel(_LOG_LEVEL)
_fh.setFormatter(logging.Formatter(_LOG_FMT))
logging.getLogger().addHandler(_fh)
_logger = logging.getLogger(__name__)
# 导入所有模型，确保 Base.metadata 包含所有表
from .models import *  # noqa: F401, F403

# CORS 允许的来源（环境变量配置，逗号分隔；默认允许所有）
_allowed_origins_str = settings.allowed_origins
ALLOWED_ORIGINS = (
    ["*"] if _allowed_origins_str == "*"
    else [o.strip() for o in _allowed_origins_str.split(",") if o.strip()]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 开发环境：直接建表；生产环境改为 alembic upgrade head
    Base.metadata.create_all(bind=engine)
    # 初始化默认账号（仅首次启动、数据库为空时）
    from .database import SessionLocal
    from .seed import seed_default_users
    db = SessionLocal()
    try:
        seed_default_users(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="智信优控云端管理平台 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Global exception handlers ----
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(status_code=exc.status_code, content={"success": False, "detail": detail})
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": {"code": f"HTTP_{exc.status_code}", "message": str(detail)}})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"field": ".".join(str(l) for l in e.get("loc", [])), "message": e.get("msg", "")} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"success": False, "error": {"code": "VALIDATION_ERROR", "message": "请求参数验证失败", "details": errors}})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    _logger.exception(f"Unhandled error on {request.method} {request.url.path}")
    return JSONResponse(status_code=500, content={"success": False, "error": {"code": "INTERNAL_ERROR", "message": "服务器内部错误"}})


# ---- Request logging middleware ----
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = datetime.now()
    response = await call_next(request)
    dur = (datetime.now() - start).total_seconds()
    _logger.info(f"{request.method} {request.url.path} - {response.status_code} - {dur:.3f}s")
    return response


from .routers import auth as auth_router
from .routers import organizations as org_router
from .routers import licenses as license_router
from .routers import users as users_router
from .routers import tasks as tasks_router
from .routers import reports as reports_router
from .routers import analytics as analytics_router
from .routers import updates as updates_router
from .routers import sync as sync_router
from .routers import admin as admin_router
from .routers import classes as classes_router
from .routers import public as public_router

app.include_router(auth_router.router)
app.include_router(org_router.router)
app.include_router(license_router.router)
app.include_router(users_router.router)
app.include_router(classes_router.router)
app.include_router(tasks_router.router)
app.include_router(reports_router.router)
app.include_router(analytics_router.router)
app.include_router(updates_router.router)
app.include_router(sync_router.router)
app.include_router(admin_router.router)
app.include_router(public_router.router)


@app.get("/api/cloud/health")
def health():
    return {"status": "ok"}


# ---------- 静态前端文件 ----------
_frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.isdir(_frontend_dist):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(_frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(_frontend_dist, "index.html"))

