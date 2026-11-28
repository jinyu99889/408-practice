from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.health import router as health_router
from app.api.media import router as media_router
from app.api.papers import router as papers_router
from app.api.questions import router as questions_router
from app.errors import (
    AppError,
    app_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.db import app_lifespan, configure_database

API_PREFIX = "/api/v1"


def create_app(settings=None, db_engine=None, enable_startup: bool = True) -> FastAPI:
    """创建应用实例并注册版本化路由与统一异常处理器。"""
    application = FastAPI(
        title="真练真会 API",
        version="0.1.0",
        lifespan=app_lifespan if enable_startup else None,
    )
    configure_database(application, settings=settings, db_engine=db_engine)
    application.include_router(health_router, prefix=API_PREFIX)
    application.include_router(media_router, prefix=API_PREFIX)
    application.include_router(papers_router, prefix=API_PREFIX)
    application.include_router(questions_router, prefix=API_PREFIX)
    application.add_exception_handler(AppError, app_error_handler)
    application.add_exception_handler(
        StarletteHTTPException, http_exception_handler
    )
    application.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )
    application.add_exception_handler(Exception, unhandled_exception_handler)
    return application


# uvicorn 启动入口实例：`uv run uvicorn app.main:app` 会导入并运行它。
app = create_app()
