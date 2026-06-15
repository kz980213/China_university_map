"""FastAPI 应用入口。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, schools, filters, majors, stats, admission, volunteer

app = FastAPI(
    title="全国高校地图查询系统 API",
    version="1.0.0",
)

_cors_origins = [o.strip() for o in settings.backend_cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router)
app.include_router(schools.router)
app.include_router(filters.router)
app.include_router(majors.router)
app.include_router(stats.router)
app.include_router(admission.router)
app.include_router(volunteer.router)
