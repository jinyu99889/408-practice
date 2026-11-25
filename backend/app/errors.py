import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """携带业务错误码、HTTP 状态码和补充详情的应用异常。"""

    def __init__(
        self,
        code: str,
        message: str,
        status: int,
        details: Any = None,
    ) -> None:
        """初始化可透传到统一错误响应的业务错误信息。"""
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details


def _error_response(
    status: int, code: str, message: str, details: Any
) -> JSONResponse:
    """构造统一结构的 JSON 错误响应。"""
    return JSONResponse(
        status_code=status,
        content={"code": code, "message": message, "details": details},
    )


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    """将业务异常字段原样转换为 HTTP 错误响应。"""
    return _error_response(exc.status, exc.code, exc.message, exc.details)


async def http_exception_handler(
    _: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """将框架 HTTP 异常转换为统一错误格式。"""
    message = exc.detail if isinstance(exc.detail, str) else "HTTP request failed"
    return _error_response(
        exc.status_code,
        "HTTP_ERROR",
        message,
        {"status_code": exc.status_code},
    )


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    """返回参数校验错误，并保留出错字段位置。"""
    errors = [
        {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]
    return _error_response(
        422,
        "VALIDATION_ERROR",
        "Request validation failed",
        {"errors": errors},
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """记录未处理异常并返回不包含内部细节的 500 响应。"""
    logger.exception("Unhandled application exception", exc_info=exc)
    return _error_response(
        500,
        "INTERNAL_ERROR",
        "Internal server error",
        None,
    )
