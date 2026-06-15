import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# 将 backend/ 目录加入 sys.path，使 app.* 可被正常导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入 Base 及所有 model，确保 metadata 中包含所有表定义
from app.database import Base
import app.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_database_url() -> str:
    """优先从 app.config.settings 读取 DATABASE_URL，退回到 alembic.ini。"""
    try:
        from app.config import settings
        return settings.database_url
    except Exception:
        url = config.get_main_option("sqlalchemy.url", "")
        if not url:
            raise RuntimeError(
                "未找到数据库 URL。请设置 DATABASE_URL 环境变量，"
                "或在 alembic.ini 中填写 sqlalchemy.url。"
            )
        return url


def run_migrations_offline() -> None:
    context.configure(
        url=_get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _get_database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
