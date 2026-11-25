from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.errors import AppError
from app.main import API_PREFIX, create_app


def _client_with_route(path: str, handler) -> TestClient:
    """创建挂载临时测试路由且返回错误响应的客户端。"""
    app: FastAPI = create_app()
    app.add_api_route(f"{API_PREFIX}{path}", handler, methods=["GET"])
    return TestClient(app, raise_server_exceptions=False)


def test_validation_error_identifies_invalid_field() -> None:
    """验证请求校验失败时统一响应能定位无效字段。"""
    def accepts_int(value: int) -> dict[str, int]:
        """声明只接受整数的临时接口参数。"""
        return {"value": value}

    with _client_with_route("/_test/validation", accepts_int) as client:
        response = client.get("/api/v1/_test/validation", params={"value": "nope"})

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert any("value" in error["loc"] for error in body["details"]["errors"])


def test_unhandled_error_does_not_leak_exception() -> None:
    """验证未处理异常返回通用 500 且不泄露异常细节。"""
    def fail() -> None:
        """模拟抛出未处理运行时异常的接口。"""
        raise RuntimeError("private failure detail")

    with _client_with_route("/_test/failure", fail) as client:
        response = client.get("/api/v1/_test/failure")

    assert response.status_code == 500
    assert response.json() == {
        "code": "INTERNAL_ERROR",
        "message": "Internal server error",
        "details": None,
    }
    assert "private failure detail" not in response.text


def test_app_error_fields_are_returned_unchanged() -> None:
    """验证业务异常的状态码和字段透传到响应。"""
    def fail() -> None:
        """模拟抛出带业务详情的应用异常。"""
        raise AppError("X", "说明", 409, {"a": 1})

    with _client_with_route("/_test/app-error", fail) as client:
        response = client.get("/api/v1/_test/app-error")

    assert response.status_code == 409
    assert response.json() == {
        "code": "X",
        "message": "说明",
        "details": {"a": 1},
    }


def test_openapi_contains_versioned_health_path() -> None:
    """验证 OpenAPI 文档公开带版本前缀的健康检查路由。"""
    with TestClient(create_app()) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/health" in response.json()["paths"]
