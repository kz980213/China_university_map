"""应用配置模块。"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/china_university_map"

    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    amap_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()