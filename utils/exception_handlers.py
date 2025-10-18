"""
Exception Handlers
Global exception handlers for FastAPI application
"""
import os
import logging
import traceback

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from .restful import BusinessError, not_found
from .biz_code import NOT_FOUND

logger = logging.getLogger("app")


def register_exception_handlers(app):
    """
    Register all exception handlers to the FastAPI app
    
    Args:
        app: FastAPI application instance
    """
    
    # Business Error Handler - must be before HTTPException handler
    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError):
        """Handle BusinessError exceptions"""
        logger.warning("BusinessError: %s %s -> BizCode:%s, %s", request.method, request.url, exc.biz_code, exc.message)
        return exc.to_response()

    # 全局异常处理器：HTTPException（保留状态码与 detail）
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning("HTTPException: %s %s -> %s", request.method, request.url, exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    # 全局验证错误：RequestValidationError -> 422，返回详细 errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error: %s %s -> %s", request.method, request.url, exc.errors())
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "body": exc.body},
        )

    # SQLAlchemy 错误处理（避免泄露敏感信息）
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error("Database error: %s %s -> %s", request.method, request.url, str(exc))
        # 可根据开发/生产环境返回更详细或更简短的信息
        debug = os.getenv("APP_DEBUG", "false").lower() in ("1", "true", "yes")
        content = {"detail": "Database error"}
        if debug:
            content["error"] = str(exc)
        return JSONResponse(status_code=500, content=content)

    # 通用异常处理：记录完整堆栈并返回 500
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        tb = traceback.format_exc()
        logger.exception("Unhandled exception: %s %s\n%s", request.method, request.url, tb)
        debug = os.getenv("APP_DEBUG", "false").lower() in ("1", "true", "yes")
        content = {"detail": "Internal server error"}
        if debug:
            content["error"] = str(exc)
            content["traceback"] = tb
        return JSONResponse(status_code=500, content=content)

    # 404 Handler - Route not found
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        """Handle 404 Not Found errors with standardized response"""
        logger.warning("Route not found: %s %s", request.method, request.url.path)
        return not_found(
            biz_code=NOT_FOUND,
            errors={"message": f"路由 {request.url.path} 不存在", "path": request.url.path}
        )
