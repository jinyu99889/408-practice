from fastapi.testclient import TestClient


def test_health_check_returns_ok(client: TestClient) -> None:
    """验证健康检查返回 200 和正常状态。"""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_route_uses_error_envelope(client: TestClient) -> None:
    """验证未知路由使用统一错误响应字段。"""
    response = client.get("/api/v1/nope")

    assert response.status_code == 404
    assert set(response.json()) == {"code", "message", "details"}
