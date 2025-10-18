"""
JWT Authentication Middleware
Dependency for protecting routes with JWT authentication
"""
from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from configs import get_session
from utils.restful import BusinessError
from utils.biz_code import UNAUTHORIZED, TK_NOT_FOUND, TK_FORMAT, TK_INVALID, TK_CLAIMS, TK_USER_ID, NOT_FOUND
from utils.jwt_utils import decode_token


async def get_current_user(
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session)
):
    """
    JWT Authentication Middleware
    Extract and validate user from Authorization header
    
    Args:
        authorization: Authorization header (Bearer token)
        session: Database session
        
    Returns:
        User object from database
        
    Raises:
        BusinessError: If token is missing, invalid, or user not found
    """
    # Check if Authorization header exists
    if not authorization:
        raise BusinessError(
            biz_code=TK_NOT_FOUND,
            http_code=401,
            details={"message": "Authorization header not found"}
        )
    
    # Parse Bearer token
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer":
        raise BusinessError(
            biz_code=TK_FORMAT,
            http_code=401,
            details={"message": "Invalid token format. Expected 'Bearer <token>'"}
        )
    
    token_str = parts[1]
    
    # Decode token
    claims = decode_token(token_str)
    if not claims:
        raise BusinessError(
            biz_code=TK_INVALID,
            http_code=401,
            details={"message": "Invalid or expired token"}
        )
    
    # Extract user_id from claims
    user_id = claims.get("user_id")
    if not user_id:
        raise BusinessError(
            biz_code=TK_USER_ID,
            http_code=401,
            details={"message": "Token missing user_id claim"}
        )
    
    # Import here to avoid circular dependency
    from controllers.user import User
    
    # Fetch user from database
    user = await session.get(User, user_id)
    if not user:
        raise BusinessError(
            biz_code=NOT_FOUND,
            http_code=401,
            details={"message": "User not found"}
        )
    
    return user
