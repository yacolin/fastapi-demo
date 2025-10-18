# __init__.py
# Utils package exports

from .biz_code import (
    # Success codes
    OK,
    CREATED,
    NO_CONTENT,
    ACCEPTED,
    DELETED,
    UPDATED,
    # Client error codes
    BAD_REQUEST,
    UNAUTHORIZED,
    FORBIDDEN,
    NOT_FOUND,
    INVALID_PWD,
    INVALID_PAGE,
    INVALID_PRICE,
    MISSING_ID,
    MISSING_NAME,
    NO_DATA,
    # Token error codes
    TK_GEN,
    ACCESS_TK_GEN,
    REFRESH_TK_GEN,
    TK_INVALID,
    TK_EXPIRED,
    TK_NOT_FOUND,
    TK_FORMAT,
    TK_SIGN,
    TK_CLAIMS,
    TK_USER_ID,
    TK_USER_NAME,
    TK_AUDIENCE,
    # Server error codes
    ERR_INTERNAL,
    DB_QUERY,
    DB_COUNT,
    DB_DELETE,
    DB_UPDATE,
    DB_CREATE,
    DB_DUP,
    USER_NOT_FOUND,
    # Utilities
    CODE_MESSAGES,
    get_message,
    get_http_status,
)

from .restful import (
    ApiResponse,
    BusinessError,
    success,
    error_response,
    
    new_business_error,
)

from .exception_handlers import register_exception_handlers

from .auth_service import AuthService
from .response_service import ResponseService

__all__ = [
    # Business codes
    "OK",
    "CREATED",
    "NO_CONTENT",
    "ACCEPTED",
    "DELETED",
    "UPDATED",
    "BAD_REQUEST",
    "UNAUTHORIZED",
    "FORBIDDEN",
    "NOT_FOUND",
    "INVALID_PWD",
    "INVALID_PAGE",
    "INVALID_PRICE",
    "MISSING_ID",
    "MISSING_NAME",
    "NO_DATA",
    "TK_GEN",
    "ACCESS_TK_GEN",
    "REFRESH_TK_GEN",
    "TK_INVALID",
    "TK_EXPIRED",
    "TK_NOT_FOUND",
    "TK_FORMAT",
    "TK_SIGN",
    "TK_CLAIMS",
    "TK_USER_ID",
    "TK_USER_NAME",
    "TK_AUDIENCE",
    "ERR_INTERNAL",
    "DB_QUERY",
    "DB_COUNT",
    "DB_DELETE",
    "DB_UPDATE",
    "DB_CREATE",
    "DB_DUP",
    "USER_NOT_FOUND",
    "CODE_MESSAGES",
    "get_message",
    "get_http_status",

    # RESTful utilities
    "ApiResponse",
    "BusinessError",
    "success",
    "error_response",
    
    "new_business_error",

    # Exception handlers
    "register_exception_handlers",

    # Service classes
    "AuthService",
    "ResponseService",
]