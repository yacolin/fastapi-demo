"""
RESTful API Response Utilities
统一的RESTful响应工具
"""
from typing import Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

from .biz_code import get_message, get_http_status, BizCode


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
        biz_code: Union[int, BizCode],
        http_code: Optional[int] = None,
        details: Optional[Any] = None,
        error: Optional[Exception] = None
    ):
        """
        初始化业务错误
        
        Args:
            biz_code: 业务状态码 (int or BizCode Enum)
            http_code: HTTP状态码（可选，不提供则自动推断）
            details: 错误详情
            error: 原始异常对象
        """
        self.raw_biz_code = biz_code
        self.biz_code = biz_code.code if isinstance(biz_code, BizCode) else biz_code
        self.http_code = http_code or get_http_status(self.raw_biz_code)
        self.details = details
        self.error = error
        self.message = get_message(self.raw_biz_code)
        
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"BizCode: {self.biz_code}, HttpCode: {self.http_code}, Details: {self.details}"
    
    def to_response(self) -> JSONResponse:
        """转换为JSON响应"""
        return error_response(
            http_status=self.http_code,
            biz_code=self.raw_biz_code,
            errors=self.details
        )


def success(
    biz_code: Union[int, BizCode] = BizCode.OK,
    data: Optional[Any] = None,
    http_status: Optional[int] = None
) -> JSONResponse:
    """
    成功响应
    
    Args:
        biz_code: 业务状态码，默认BizCode.OK
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
    biz_code: Union[int, BizCode],
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
    code_val = biz_code.code if isinstance(biz_code, BizCode) else biz_code

    response = ApiResponse(
        code=code_val,
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


# 业务错误工厂函数
def new_business_error(
    biz_code: Union[int, BizCode],
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
