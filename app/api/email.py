from fastapi import APIRouter, Depends
from app.models.schemas import EmailRequest, MessageResponse
from app.services.email_service import EmailService
from app.services.auth_service import get_current_user


router = APIRouter(prefix="/api", tags=["email"])


@router.post("/email_me", response_model=MessageResponse)
def email_me(request: EmailRequest, user=Depends(get_current_user)):
    """Send email with optional image attachment."""
    EmailService.send_email(request.to, request.message, request.image)
    return MessageResponse(message="Email sent successfully", success=True)
