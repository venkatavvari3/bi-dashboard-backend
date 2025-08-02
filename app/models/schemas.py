from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    credential: Optional[str] = None


class EmailRequest(BaseModel):
    to: str
    message: str
    image: Optional[str] = None


class ScheduleRequest(BaseModel):
    repeatFrequency: str
    scheduledTime: str
    reportFormat: str
    email: str


class TokenResponse(BaseModel):
    access_token: str


class MessageResponse(BaseModel):
    message: str
    success: Optional[bool] = True
