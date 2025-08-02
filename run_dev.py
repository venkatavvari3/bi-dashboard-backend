#!/usr/bin/env python3
"""
Development startup script for BI Dashboard Backend
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting BI Dashboard Backend...")
    print("📊 Modular architecture loaded successfully!")
    print("🌐 Access API documentation at: http://localhost:8000/docs")
    print("📡 Health check at: http://localhost:8000/")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
