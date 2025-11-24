"""
Response Service
Encapsulates RESTful response functionality into a service class
Each method has a default biz_code bound to it for consistency
"""
from typing import Any, Optional, Union
from fastapi.responses import JSONResponse

from .restful import (
    success as _success,
    error_response as _error_response,
    BusinessError,
)
from .biz_code import BizCode


class ResponseService:
    """
    Response service for handling standardized API responses
    Provides a clean interface with built-in business codes
    
    Each method has a default biz_code that can be overridden if needed
    """
    
    @staticmethod
    def success(data: Optional[Any] = None, biz_code: Union[int, BizCode] = BizCode.OK) -> JSONResponse:
        """
        Return a success response
        
        Args:
            data: Response data
            biz_code: Business status code (default: OK)
            
        Returns:
            JSONResponse with success format
        """
        return _success(biz_code=biz_code, data=data)
    
    @staticmethod
    def created(data: Optional[Any] = None, biz_code: Union[int, BizCode] = BizCode.CREATED) -> JSONResponse:
        """
        Return a created response (201)
        
        Args:
            data: Response data
            biz_code: Business status code (default: CREATED)
            
        Returns:
            JSONResponse with created format
        """
        return _success(biz_code=biz_code, data=data, http_status=201)

    @staticmethod
    def no_content(biz_code: Union[int, BizCode] = BizCode.DELETED) -> JSONResponse:
        """
        Return a no content response (204)
        
        Args:
            biz_code: Business status code (default: DELETED)
            
        Returns:
            JSONResponse with no content format
        """
        return _success(biz_code=biz_code, data=None, http_status=204)
    
    @staticmethod
    def accepted(data: Optional[Any] = None, biz_code: Union[int, BizCode] = BizCode.OK) -> JSONResponse:
        """
        Return an accepted response (202)
        
        Args:
            data: Response data
            biz_code: Business status code (default: OK)
            
        Returns:
            JSONResponse with accepted format
        """
        return _success(biz_code=biz_code, data=data, http_status=202)
    
    @staticmethod
    def updated(data: Optional[Any] = None, biz_code: Union[int, BizCode] = BizCode.UPDATED) -> JSONResponse:
        """
        Return an updated response (200)
        
        Args:
            data: Response data
            biz_code: Business status code (default: UPDATED)
            
        Returns:
            JSONResponse with updated format
        """
        return _success(biz_code=biz_code, data=data, http_status=200)
    
    @staticmethod
    def deleted(biz_code: Union[int, BizCode] = BizCode.DELETED) -> JSONResponse:
        """
        Return a deleted response (204)
        
        Args:
            biz_code: Business status code (default: DELETED)
            
        Returns:
            JSONResponse with deleted format
        """
        return _success(biz_code=biz_code, data=None, http_status=204)
    
    @staticmethod
    def bad_request(message: str, biz_code: Union[int, BizCode] = BizCode.BAD_REQUEST) -> JSONResponse:
        """
        Return a bad request error response (400)
        
        Args:
            message: Error message
            biz_code: Business error code (default: BAD_REQUEST)
            
        Returns:
            JSONResponse with error format
        """
        return _error_response(http_status=400, biz_code=biz_code, errors={"message": message})
    
    @staticmethod
    def unauthorized(message: str, biz_code: Union[int, BizCode] = BizCode.UNAUTHORIZED) -> JSONResponse:
        """
        Return an unauthorized error response (401)
        
        Args:
            message: Error message
            biz_code: Business error code (default: UNAUTHORIZED)
            
        Returns:
            JSONResponse with error format
        """
        return _error_response(http_status=401, biz_code=biz_code, errors={"message": message})
    

    @staticmethod
    def forbidden(message: str, biz_code: Union[int, BizCode] = BizCode.FORBIDDEN) -> JSONResponse:
        """
        Return a forbidden error response (403)
        
        Args:
            message: Error message
            biz_code: Business error code (default: FORBIDDEN)
            
        Returns:
            JSONResponse with error format
        """
        return _error_response(http_status=403, biz_code=biz_code, errors={"message": message})
    
    
    @staticmethod
    def not_found(message: str, biz_code: Union[int, BizCode] = BizCode.NOT_FOUND) -> JSONResponse:
        """
        Return a not found error response (404)
        
        Args:
            message: Error message
            biz_code: Business error code (default: NOT_FOUND)
            
        Returns:
            JSONResponse with error format
        """
        return _error_response(http_status=404, biz_code=biz_code, errors={"message": message})
    
    @staticmethod
    def internal_error(message: str, biz_code: Union[int, BizCode] = BizCode.ERR_INTERNAL) -> JSONResponse:
        """
        Return an internal server error response (500)
        
        Args:
            message: Error message
            biz_code: Business error code (default: ERR_INTERNAL)
            
        Returns:
            JSONResponse with error format
        """
        return _error_response(http_status=500, biz_code=biz_code, errors={"message": message}) 

    @staticmethod
    def db_error(message: str, biz_code: Union[int, BizCode] = BizCode.ERR_INTERNAL) -> JSONResponse:
        """
        Return a database error response (500)
        
        Args:
            message: Error message
            biz_code: Business error code (default: ERR_INTERNAL)
            
        Returns:
            JSONResponse with error format
        """
        return _error_response(http_status=500, biz_code=biz_code, errors={"message": message})
    
    # Expose BusinessError for raising exceptions
    Error = BusinessError
