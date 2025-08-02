from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, data, email, subscriptions

# Create FastAPI application
app = FastAPI(
    title="BI Dashboard API",
    description="A modular BI Dashboard backend API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(data.router)
app.include_router(email.router)
app.include_router(subscriptions.router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "healthy", "message": "BI Dashboard API is running"}
