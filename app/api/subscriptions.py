from fastapi import APIRouter, Depends
from app.models.schemas import ScheduleRequest, MessageResponse
from app.services.subscription_service import SubscriptionService
from app.services.auth_service import get_current_user
from app.db.database import get_db


router = APIRouter(prefix="/api", tags=["subscriptions"])


@router.post("/schedule_report", response_model=MessageResponse)
def schedule_report(request: ScheduleRequest, user=Depends(get_current_user), db=Depends(get_db)):
    """Schedule a report subscription."""
    message = SubscriptionService.create_subscription(
        request.email, 
        request.repeatFrequency, 
        request.scheduledTime, 
        request.reportFormat, 
        db
    )
    return MessageResponse(message=message)
