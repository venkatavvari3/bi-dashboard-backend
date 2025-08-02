import jwt
import requests
from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.db.database import DatabaseManager


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthService:
    """Authentication service for handling login and token verification."""
    
    @staticmethod
    def get_persona_for_username(username: str, db_conn) -> Optional[str]:
        """Get persona for a given username."""
        query = "SELECT persona FROM persona_users WHERE username = %s"
        rows, _ = DatabaseManager.execute_query(db_conn, query, (username.lower(),))
        return rows[0][0] if rows else None
    
    @staticmethod
    def verify_google_token(token: str) -> Optional[str]:
        """Verify Google OAuth token and return email."""
        try:
            response = requests.get(
                "https://oauth2.googleapis.com/tokeninfo", 
                params={"id_token": token}
            )
            data = response.json()
            if response.status_code == 200 and data.get("aud") == settings.GOOGLE_CLIENT_ID:
                return data.get("email")
        except Exception:
            pass
        return None
    
    @staticmethod
    def create_access_token(username: str, persona: Optional[str] = None) -> str:
        """Create JWT access token."""
        payload = {"sub": username, "persona": persona}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    @staticmethod
    def authenticate_user(username: str, password: str, db_conn) -> Optional[str]:
        """Authenticate user with username/password."""
        persona = AuthService.get_persona_for_username(username, db_conn)
        if persona and password == "password":  # Simple password check - should be hashed in production
            return persona
        return None


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get current user from token."""
    return AuthService.verify_token(token)
