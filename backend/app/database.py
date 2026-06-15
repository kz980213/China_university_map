"""数据库连接和会话管理。"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool, QueuePool

from app.config import settings

# Render 环境变量（平台自动注入），或显式设置 USE_NULL_POOL=true
# 配合 Supabase Transaction Pooler 使用 NullPool：SQLAlchemy 不维护自己的连接池，
# 每次请求从 pgbouncer 借连接、用完立即归还，大幅降低内存占用。
_use_null_pool = os.environ.get("RENDER") == "true" or os.environ.get("USE_NULL_POOL") == "true"

engine = create_engine(
    settings.database_url,
    poolclass=NullPool if _use_null_pool else QueuePool,
    # 本地开发保留小连接池；生产走 NullPool，以下参数无效但不影响
    pool_size=2,
    max_overflow=3,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依赖：提供数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
