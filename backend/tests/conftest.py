import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def app() -> FastAPI:
    """为每个测试创建独立的 FastAPI 应用实例。"""
    return create_app()


@pytest.fixture
def client(app: FastAPI):
    """提供不会重新抛出服务端异常的测试客户端。"""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
