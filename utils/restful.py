"""
RESTful API Response Utilities
统一的RESTful响应工具
"""
from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

from .biz_code import get_message, get_http_status


class ApiResponse(BaseModel):
    """统一API响应结构体"""
    code: int = Field(..., description="业务状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    errors: Optional[Any] = Field(None, description="错误详情")
    timestamp: int = Field(..., description="响应时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 2000,
                "message": "请求成功",
                "data": {"id": 1, "name": "example"},
                "errors": None,
                "timestamp": 1729260645
            }
        }
        


class BusinessError(Exception):
    """自定义业务错误"""
    
    def __init__(
        self,
        biz_code: int,
        http_code: Optional[int] = None,
        details: Optional[Any] = None,
        error: Optional[Exception] = None
    ):
        """
        初始化业务错误
        
        Args:
            biz_code: 业务状态码
            http_code: HTTP状态码（可选，不提供则自动推断）
            details: 错误详情
            error: 原始异常对象
        """
        self.biz_code = biz_code
        self.http_code = http_code or get_http_status(biz_code)
        self.details = details
        self.error = error
        self.message = get_message(biz_code)
        
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"BizCode: {self.biz_code}, HttpCode: {self.http_code}, Details: {self.details}"
    
    def to_response(self) -> JSONResponse:
        """转换为JSON响应"""
        return error_response(
            http_status=self.http_code,
            biz_code=self.biz_code,
            errors=self.details
        )


def success(
    biz_code: int = 2000,
    data: Optional[Any] = None,
    http_status: Optional[int] = None
) -> JSONResponse:
    """
    成功响应
    
    Args:
        biz_code: 业务状态码，默认2000（请求成功）
        data: 响应数据
        http_status: HTTP状态码，不提供则根据biz_code自动推断
        
    Returns:
        JSONResponse对象
    """
    http_status = http_status or get_http_status(biz_code)
    
    response = ApiResponse(
        code=0,  # 成功时code为0
        message=get_message(biz_code),
        data=data,
        errors=None,
        timestamp=int(datetime.now().timestamp())
    )
    
    # Use dict() for compatibility
    try:
        content = response.model_dump(exclude_none=True)
    except AttributeError:
        content = response.dict(exclude_none=True)
    
    return JSONResponse(
        status_code=http_status,
        content=content
    )


def error_response(
    http_status: int,
    biz_code: int,
    errors: Optional[Any] = None
) -> JSONResponse:
    """
    错误响应
    
    Args:
        http_status: HTTP状态码
        biz_code: 业务状态码
        errors: 错误详情
        
    Returns:
        JSONResponse对象
    """
    response = ApiResponse(
        code=biz_code,
        message=get_message(biz_code),
        data=None,
        errors=errors,
        timestamp=int(datetime.now().timestamp())
    )
    
    # Use dict() for compatibility
    try:
        content = response.model_dump(exclude_none=True)
    except AttributeError:
        content = response.dict(exclude_none=True)
    
    return JSONResponse(
        status_code=http_status,
        content=content
    )


def created(data: Optional[Any] = None) -> JSONResponse:
    """创建成功响应 (201)"""
    return success(biz_code=2001, data=data, http_status=201)


def no_content() -> JSONResponse:
    """无内容响应 (204)"""
    return success(biz_code=2002, data=None, http_status=204)


def accepted(data: Optional[Any] = None) -> JSONResponse:
    """已接受响应 (202)"""
    return success(biz_code=2003, data=data, http_status=202)


def deleted() -> JSONResponse:
    """删除成功响应 (204)"""
    return success(biz_code=2004, data=None, http_status=204)


def updated(data: Optional[Any] = None) -> JSONResponse:
    """更新成功响应 (200)"""
    return success(biz_code=2005, data=data, http_status=200)


def bad_request(errors: Optional[Any] = None, biz_code: int = 4000) -> JSONResponse:
    """错误请求响应 (400)"""
    return error_response(http_status=400, biz_code=biz_code, errors=errors)


def unauthorized(errors: Optional[Any] = None, biz_code: int = 4001) -> JSONResponse:
    """未授权响应 (401)"""
    return error_response(http_status=401, biz_code=biz_code, errors=errors)


def forbidden(errors: Optional[Any] = None, biz_code: int = 4003) -> JSONResponse:
    """禁止访问响应 (403)"""
    return error_response(http_status=403, biz_code=biz_code, errors=errors)


def not_found(errors: Optional[Any] = None, biz_code: int = 4004) -> JSONResponse:
    """未找到响应 (404)"""
    return error_response(http_status=404, biz_code=biz_code, errors=errors)


def internal_error(errors: Optional[Any] = None, biz_code: int = 5000) -> JSONResponse:
    """服务器内部错误响应 (500)"""
    return error_response(http_status=500, biz_code=biz_code, errors=errors)


def db_error(errors: Optional[Any] = None, biz_code: int = 5100) -> JSONResponse:
    """数据库错误响应 (500)"""
    return error_response(http_status=500, biz_code=biz_code, errors=errors)


# 业务错误工厂函数
def new_business_error(
    biz_code: int,
    http_code: Optional[int] = None,
    details: Optional[Any] = None,
    error: Optional[Exception] = None
) -> BusinessError:
    """
    创建业务错误
    
    Args:
        biz_code: 业务状态码
        http_code: HTTP状态码（可选）
        details: 错误详情
        error: 原始异常
        
    Returns:
        BusinessError实例
    """
    return BusinessError(
        biz_code=biz_code,
        http_code=http_code,
        details=details,
        error=error
    )
