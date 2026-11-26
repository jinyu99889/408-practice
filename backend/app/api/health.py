from fastapi import APIRouter

# 健康检查路由：curl http://127.0.0.1:8000/api/v1/health 可用于探活。
router = APIRouter()


@router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """返回服务存活状态，供部署环境执行探活。"""
    return {"status": "ok"}