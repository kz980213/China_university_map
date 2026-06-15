"""FastAPI 应用入口。

第一阶段仅提供基础骨架和 /api/health 接口。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, schools, filters, majors, stats, admission, volunteer

app = FastAPI(
    title="全国高校地图查询系统 API",
    version="0.1.0",
    description="第一阶段 MVP：后端基础骨架",
)

# 配置 CORS，允许本地前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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
