import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
# 导入所有模型，确保 Base.metadata 包含所有表
from .models import *  # noqa: F401, F403

# CORS 允许的来源（环境变量配置，逗号分隔；默认允许所有）
_allowed_origins_str = os.environ.get(
    "ALLOWED_ORIGINS",
    "https://chenshi0504.github.io,http://localhost:5173"
)
ALLOWED_ORIGINS = (
    ["*"] if _allowed_origins_str == "*"
    else [o.strip() for o in _allowed_origins_str.split(",") if o.strip()]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 开发环境：直接建表；生产环境改为 alembic upgrade head
    Base.metadata.create_all(bind=engine)
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

app.include_router(auth_router.router)
app.include_router(org_router.router)
app.include_router(license_router.router)
app.include_router(users_router.router)
app.include_router(tasks_router.router)
app.include_router(reports_router.router)
app.include_router(analytics_router.router)
app.include_router(updates_router.router)
app.include_router(sync_router.router)
app.include_router(admin_router.router)


@app.get("/api/cloud/health")
def health():
    return {"status": "ok"}
