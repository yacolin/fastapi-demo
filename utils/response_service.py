"""
Response Service
Encapsulates RESTful response functionality into a service class
Each method has a default biz_code bound to it for consistency
"""
from typing import Any, Optional
from fastapi.responses import JSONResponse

from .restful import (
    success as _success,
    unauthorized as _unauthorized,
    bad_request as _bad_request,
    internal_error as _internal_error,
    created as _created,
    updated as _updated,
    deleted as _deleted,
    not_found as _not_found,
    BusinessError,
)
from .biz_code import (
    OK,
    CREATED,
    UPDATED,
    DELETED,
    BAD_REQUEST,
    UNAUTHORIZED,
    NOT_FOUND,
    ERR_INTERNAL,
)


class ResponseService:
    """
    Response service for handling standardized API responses
    Provides a clean interface with built-in business codes
    
    Each method has a default biz_code that can be overridden if needed
    """
    
    @staticmethod
    def success(data: Optional[Any] = None, biz_code: int = OK) -> JSONResponse:
        """
        Return a success response
        
        Args:
            data: Response data
            biz_code: Business status code (default: OK=2000)
            
        Returns:
            JSONResponse with success format
        """
        return _success(biz_code=biz_code, data=data)
    
    @staticmethod
    def created(data: Optional[Any] = None, biz_code: int = CREATED) -> JSONResponse:
        """
        Return a created response (201)
        
        Args:
            data: Response data
            biz_code: Business status code (default: CREATED=2001)
            
        Returns:
            JSONResponse with created format
        """
        return _created(data=data)
    
    @staticmethod
    def updated(data: Optional[Any] = None, biz_code: int = UPDATED) -> JSONResponse:
        """
        Return an updated response (200)
        
        Args:
            data: Response data
            biz_code: Business status code (default: UPDATED=2005)
            
        Returns:
            JSONResponse with updated format
        """
        return _updated(data=data)
    
    @staticmethod
    def deleted(biz_code: int = DELETED) -> JSONResponse:
        """
        Return a deleted response (204)
        
        Args:
            biz_code: Business status code (default: DELETED=2004)
            
        Returns:
            JSONResponse with deleted format
        """
        return _deleted()
    
    @staticmethod
    def bad_request(message: str, biz_code: int = BAD_REQUEST) -> JSONResponse:
        """
        Return a bad request error response (400)
        
        Args:
            message: Error message
            biz_code: Business error code (default: BAD_REQUEST=4000)
            
        Returns:
            JSONResponse with error format
        """
        return _bad_request(biz_code=biz_code, errors={"message": message})
    
    @staticmethod
    def unauthorized(message: str, biz_code: int = UNAUTHORIZED) -> JSONResponse:
        """
        Return an unauthorized error response (401)
        
        Args:
            message: Error message
            biz_code: Business error code (default: UNAUTHORIZED=4001)
            
        Returns:
            JSONResponse with error format
        """
        return _unauthorized(biz_code=biz_code, errors={"message": message})
    
    @staticmethod
    def not_found(message: str, biz_code: int = NOT_FOUND) -> JSONResponse:
        """
        Return a not found error response (404)
        
        Args:
            message: Error message
            biz_code: Business error code (default: NOT_FOUND=4004)
            
        Returns:
            JSONResponse with error format
        """
        return _not_found(biz_code=biz_code, errors={"message": message})
    
    @staticmethod
    def internal_error(message: str, biz_code: int = ERR_INTERNAL) -> JSONResponse:
        """
        Return an internal server error response (500)
        
        Args:
            message: Error message
            biz_code: Business error code (default: ERR_INTERNAL=5000)
            
        Returns:
            JSONResponse with error format
        """
        return _internal_error(biz_code=biz_code, errors={"message": message})
    
    # Expose BusinessError for raising exceptions
    Error = BusinessError
