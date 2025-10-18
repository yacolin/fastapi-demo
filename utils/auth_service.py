"""
Authentication Service
Encapsulates authentication-related functionality into a service class
"""
import os
from datetime import datetime, timedelta
from typing import Optional


from jose import JWTError, jwt
import bcrypt
from dotenv import load_dotenv

load_dotenv()

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 days


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
        # Bcrypt has a 72-byte limit, truncate if necessary
        password_bytes = password.encode('utf-8')[:72]
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        # Return as string for database storage
        return hashed.decode('utf-8')
    
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
        # Bcrypt has a 72-byte limit, truncate if necessary to match hashing
        password_bytes = password.encode('utf-8')[:72]
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    @staticmethod
    def create_access_token(user_id: int) -> str:
        """
        Generate an access token for a user
        
        Args:
            user_id: User ID
            
        Returns:
            JWT access token (15 minutes expiry)
        """
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        claims = {
            "user_id": user_id,
            "exp": expire,
        }
        token = jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """
        Generate a refresh token for a user
        
        Args:
            user_id: User ID
            
        Returns:
            JWT refresh token (7 days expiry)
        """
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        claims = {
            "user_id": user_id,
            "exp": expire,
        }
        token = jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def validate_token(token: str) -> Optional[dict]:
        """
        Decode and validate a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded claims if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
    
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
            "access_token": AuthService.create_access_token(user_id),
            "refresh_token": AuthService.create_refresh_token(user_id)
        }
