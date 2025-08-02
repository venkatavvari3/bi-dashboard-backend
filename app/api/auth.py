from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import User, TokenResponse
from app.services.auth_service import AuthService, get_current_user
from app.db.database import get_db


router = APIRouter(prefix="/api", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(user: User, db=Depends(get_db)):
    """Login endpoint supporting both username/password and Google OAuth."""
    
    # Traditional username/password login
    if user.username and user.password:
        persona = AuthService.authenticate_user(user.username, user.password, db)
        if persona:
            token = AuthService.create_access_token(user.username, persona)
            return TokenResponse(access_token=token)
        raise HTTPException(status_code=401, detail="Auth failed")
    
    # Google OAuth credential login
    if user.credential:
        user_email = AuthService.verify_google_token(user.credential)
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        
        # Optionally map persona for Google users (by prefix, domain, etc.)
        persona = AuthService.get_persona_for_username(user_email.split('@')[0], db)
        token = AuthService.create_access_token(user_email, persona)
        return TokenResponse(access_token=token)
    
    raise HTTPException(status_code=400, detail="Missing login payload")
