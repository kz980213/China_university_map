"""应用配置模块。"""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Render 注入 PORT；本地开发默认 8010
    port: int = int(os.environ.get("PORT", 8010))

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/china_university_map"

    # 逗号分隔的允许跨域来源，生产环境通过 BACKEND_CORS_ORIGINS 环境变量覆盖
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    amap_api_key: str | None = None

    anthropic_api_key: str | None = None

    deepseek_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()