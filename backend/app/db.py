from contextlib import asynccontextmanager
from pathlib import Path
from typing import Iterator

from cryptography.fernet import Fernet
from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings, get_settings


# 测试场景通过 configure_database() 注入独立引擎，不影响这里的默认实例。
engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Iterator[Session]:
    """提供请求级数据库会话，并保证请求结束后释放连接。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _schema_path() -> Path:
    """返回建表脚本 schema.sql 在本机文件系统的绝对路径。"""
    return Path(__file__).resolve().parent / "resources" / "schema.sql"


def initialize_application(settings: Settings, db_engine: Engine) -> None:
    """创建本地运行资源、数据库结构，并清理上次中断的任务。"""
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "uploads").mkdir(exist_ok=True)
    (settings.data_dir / "media").mkdir(exist_ok=True)
    secret_path = settings.data_dir / "secret.key"
    if not secret_path.exists():
        # 首次启动时生成 Fernet 对称密钥，供 app_setting 中敏感配置加密存储。
        secret_path.write_bytes(Fernet.generate_key())

    with db_engine.begin() as connection:
        # 只以 paper 是否存在作为首次初始化信号，避免启动时覆盖已有数据。
        has_schema = connection.execute(
            text("SELECT to_regclass(:table_name)"), {"table_name": "paper"}
        ).scalar_one_or_none()
        if has_schema is None:
            connection.exec_driver_sql(_schema_path().read_text(encoding="utf-8"))
        # 进程异常退出后，下一次启动把不可恢复的进行中状态收敛到终态。
        connection.execute(
            text(
                "UPDATE import_job SET status = 'failed', "
                "error_message = '解析中断，请重试' WHERE status = 'processing'"
            )
        )
        connection.execute(
            text(
                "UPDATE exam_attempt SET status = 'abandoned' "
                "WHERE status = 'in_progress'"
            )
        )


@asynccontextmanager
async def app_lifespan(application: FastAPI):
    settings: Settings = application.state.settings
    db_engine: Engine = application.state.db_engine
    initialize_application(settings, db_engine)
    yield


def configure_database(
    application: FastAPI,
    settings: Settings | None = None,
    db_engine: Engine | None = None,
) -> None:
    """为应用注入配置和数据库引擎，便于测试使用独立数据库。"""
    application.state.settings = settings or get_settings()
    application.state.db_engine = db_engine or engine