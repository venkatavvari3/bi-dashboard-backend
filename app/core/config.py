import os
from typing import List


class Settings:
    # Application settings
    SECRET_KEY: str = os.getenv("SECRET", "CHANGE_ME")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # OAuth settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    
    # Email settings
    EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "https://bi-dashboard-frontend-git-main-venkatavvari3s-projects.vercel.app",
        "https://bi-dashboard-frontend.vercel.app",
        "https://bi-dashboard-frontend-venkatavvari3s-projects.vercel.app",
        "http://localhost:3000"
    ]
    
    # JWT settings
    JWT_ALGORITHM: str = "HS256"


settings = Settings()
