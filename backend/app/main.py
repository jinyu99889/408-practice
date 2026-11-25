from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.health import router as health_router
from app.errors import (
    AppError,
    app_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    """创建应用实例并注册版本化路由与统一异常处理器。"""
    application = FastAPI(title="真练真会 API", version="0.1.0")
    application.include_router(health_router, prefix=API_PREFIX)
    application.add_exception_handler(AppError, app_error_handler)
    application.add_exception_handler(
        StarletteHTTPException, http_exception_handler
    )
    application.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )
    application.add_exception_handler(Exception, unhandled_exception_handler)
    return application


app = create_app()
