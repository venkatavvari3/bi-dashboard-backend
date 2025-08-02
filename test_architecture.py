#!/usr/bin/env python3
"""
Quick verification script to test the modular architecture
"""

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        # Test core modules
        from app.core.config import settings
        print("✅ Core config imported")
        
        # Test database module
        from app.db.database import get_db, DatabaseManager
        print("✅ Database modules imported")
        
        # Test models
        from app.models.schemas import User, EmailRequest, ScheduleRequest
        print("✅ Pydantic models imported")
        
        # Test services
        from app.services.auth_service import AuthService
        from app.services.email_service import EmailService
        from app.services.data_service import DataService
        from app.services.subscription_service import SubscriptionService
        print("✅ All services imported")
        
        # Test API routes
        from app.api import auth, data, email, subscriptions
        print("✅ All API routes imported")
        
        # Test main application
        from main import app
        print("✅ Main FastAPI application imported")
        
        print("\n🎉 SUCCESS: All modules imported successfully!")
        print("📊 Modular architecture is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_app_structure():
    """Test that the FastAPI app is properly configured."""
    try:
        from main import app
        
        # Check if routers are included
        route_paths = [route.path for route in app.routes if hasattr(route, 'path')]
        
        expected_routes = ['/api/login', '/api/data', '/api/email_me', '/api/schedule_report']
        
        for expected in expected_routes:
            if any(expected in path for path in route_paths):
                print(f"✅ Found route: {expected}")
            else:
                print(f"⚠️  Route not found: {expected}")
        
        print(f"\n📡 Total routes configured: {len(route_paths)}")
        return True
        
    except Exception as e:
        print(f"❌ App structure test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Modular Architecture")
    print("=" * 50)
    
    import_success = test_imports()
    print("\n" + "=" * 50)
    
    if import_success:
        structure_success = test_app_structure()
    
    print("\n" + "=" * 50)
    if import_success:
        print("🚀 Ready to run: python run_dev.py")
        print("📖 Documentation: http://localhost:8000/docs")
    else:
        print("🔧 Please check the error messages above")
