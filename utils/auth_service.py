"""
Authentication Service
Encapsulates authentication-related functionality into a service class
"""
from typing import Optional
from .jwt_utils import (
    hash_password as _hash_password,
    check_password_hash as _check_password_hash,
    generate_access_token as _generate_access_token,
    generate_refresh_token as _generate_refresh_token,
    decode_token as _decode_token,
)


class AuthService:
    """
    Authentication service for handling password hashing and JWT operations
    Provides a clean interface for authentication-related operations
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return _hash_password(password)
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            password: Plain text password
            hashed: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return _check_password_hash(password, hashed)
    
    @staticmethod
    def create_access_token(user_id: int) -> str:
        """
        Generate an access token for a user
        
        Args:
            user_id: User ID
            
        Returns:
            JWT access token (15 minutes expiry)
        """
        return _generate_access_token(user_id)
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """
        Generate a refresh token for a user
        
        Args:
            user_id: User ID
            
        Returns:
            JWT refresh token (7 days expiry)
        """
        return _generate_refresh_token(user_id)
    
    @staticmethod
    def validate_token(token: str) -> Optional[dict]:
        """
        Decode and validate a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded claims if valid, None otherwise
        """
        return _decode_token(token)
    
    @staticmethod
    def create_token_pair(user_id: int) -> dict:
        """
        Generate both access and refresh tokens
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        return {
            "access_token": _generate_access_token(user_id),
            "refresh_token": _generate_refresh_token(user_id)
        }
