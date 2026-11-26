import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from app.config import Settings
from app.main import configure_database

from app.main import create_app


@pytest.fixture
def app() -> FastAPI:
    """为每个测试创建独立的 FastAPI 应用实例。"""
    return create_app(enable_startup=False)


@pytest.fixture
def client(app: FastAPI):
    """提供不会重新抛出服务端异常的测试客户端。"""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def test_engine() -> Engine:
    """只连接明确命名为测试库的 PostgreSQL，并在测试前清空 public schema。"""
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for PostgreSQL integration tests")
    from sqlalchemy.engine import make_url

    test_url = make_url(url)
    database = test_url.database
    app_url = make_url(Settings().database_url)
    if not database or "test" not in database.lower():
        pytest.fail("TEST_DATABASE_URL must target a database whose name contains 'test'")
    if (
        test_url.host,
        test_url.port,
        test_url.database,
    ) == (app_url.host, app_url.port, app_url.database):
        pytest.fail("TEST_DATABASE_URL must not target the configured application database")
    test_engine = create_engine(url, pool_pre_ping=True)
    with test_engine.begin() as connection:
        connection.exec_driver_sql("DROP SCHEMA public CASCADE")
        connection.exec_driver_sql("CREATE SCHEMA public")
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def initialized_test_db(test_engine: Engine, tmp_path):
    """通过应用 lifespan 初始化独立 PostgreSQL 测试库。"""
    settings = Settings(_env_file=None, data_dir=tmp_path)
    application = create_app(settings=settings, db_engine=test_engine)
    configure_database(application, settings=settings, db_engine=test_engine)
    with TestClient(application):
        yield application
