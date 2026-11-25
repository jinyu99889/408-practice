from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """返回服务存活状态，供部署环境执行探活。"""
    return {"status": "ok"}
