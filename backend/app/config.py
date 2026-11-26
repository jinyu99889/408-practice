from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """保存服务端口、数据库连接和本地数据目录配置。"""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=REPOSITORY_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # HTTP 服务监听端口。
    port: int = 8000
    # PostgreSQL 连接字符串，默认本机 408_practice 库。
    database_url: str = "postgresql+psycopg://localhost/408_practice"
    # 运行时数据目录：上传文件、媒体插图、密钥，不进版本库。
    data_dir: Path = REPOSITORY_ROOT / "data"


@lru_cache
def get_settings() -> Settings:
    """读取并缓存当前进程的应用配置。"""
    return Settings()