"""数据库连接和会话管理。"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool, QueuePool

from app.config import settings

# Render 平台自动注入 RENDER=true；也可在 .env 手动设置 USE_NULL_POOL=true
_use_null_pool = os.environ.get("RENDER") == "true" or os.environ.get("USE_NULL_POOL") == "true"

if _use_null_pool:
    # NullPool + Supabase Transaction Pooler（pgbouncer）
    # prepare_threshold=None：禁用 psycopg3 的 prepared statement，
    # pgbouncer transaction 模式不支持 PREPARE 命令。
    engine = create_engine(
        settings.database_url,
        poolclass=NullPool,
        connect_args={"prepare_threshold": None},
        pool_pre_ping=True,
        echo=False,
    )
else:
    engine = create_engine(
        settings.database_url,
        poolclass=QueuePool,
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
