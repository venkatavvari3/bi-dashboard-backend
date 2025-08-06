import pytest
import os
from unittest.mock import patch
from app.core.config import Settings, settings


class TestSettings:
    """Test configuration settings."""
    
    def test_default_settings(self):
        """Test default settings initialization."""
        test_settings = Settings()
        assert test_settings.JWT_ALGORITHM == "HS256"
        assert test_settings.SMTP_SERVER == "smtp.gmail.com"
        assert test_settings.SMTP_PORT == 465
        assert "http://localhost:3000" in test_settings.ALLOWED_ORIGINS
    
    def test_settings_from_environment(self):
        """Test settings loaded from environment variables."""
        with patch.dict(os.environ, {
            'SECRET': 'test-secret',
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'EMAIL_ADDRESS': 'test@example.com'
        }):
            # Import settings module to get fresh instance
            from importlib import reload
            from app.core import config
            reload(config)
            test_settings = config.Settings()
            assert test_settings.SECRET_KEY == 'test-secret'
            assert test_settings.DATABASE_URL == 'postgresql://test:test@localhost/test'
            assert test_settings.EMAIL_ADDRESS == 'test@example.com'
    
    def test_cors_origins_configuration(self):
        """Test CORS origins are properly configured."""
        test_settings = Settings()
        expected_origins = [
            "https://bi-dashboard-frontend-git-main-venkatavvari3s-projects.vercel.app",
            "https://bi-dashboard-frontend.vercel.app",
            "https://bi-dashboard-frontend-venkatavvari3s-projects.vercel.app",
            "http://localhost:3000"
        ]
        for origin in expected_origins:
            assert origin in test_settings.ALLOWED_ORIGINS
    
    def test_settings_singleton(self):
        """Test that settings is a singleton instance."""
        assert settings is not None
        assert isinstance(settings, Settings)
