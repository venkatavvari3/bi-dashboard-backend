import pytest
import os
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient
from app.core.config import Settings


@pytest.fixture
def test_settings():
    """Test settings with mock values."""
    return Settings(
        SECRET_KEY="test-secret-key",
        DATABASE_URL="postgresql://test:test@localhost:5432/test_db",
        GOOGLE_CLIENT_ID="test-google-client-id",
        EMAIL_ADDRESS="test@example.com",
        EMAIL_PASSWORD="test-password",
        SMTP_SERVER="smtp.test.com",
        SMTP_PORT=587,
        ALLOWED_ORIGINS=["http://localhost:3000"],
        JWT_ALGORITHM="HS256"
    )


@pytest.fixture
def mock_db_connection():
    """Mock database connection."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = None
    mock_cursor.description = []
    return mock_conn


@pytest.fixture
def mock_db_dependency(mock_db_connection):
    """Mock database dependency for FastAPI."""
    def _get_test_db():
        yield mock_db_connection
    return _get_test_db


@pytest.fixture
def test_client(mock_db_dependency):
    """Test client for FastAPI application with mocked database."""
    from main import app
    from app.db.database import get_db
    
    # Override the database dependency
    app.dependency_overrides[get_db] = mock_db_dependency
    
    client = TestClient(app)
    
    # Clean up after test
    yield client
    
    # Reset dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "password": "password",
        "email": "testuser@example.com"
    }


@pytest.fixture
def sample_jwt_payload():
    """Sample JWT payload for testing."""
    return {
        "sub": "testuser@example.com",
        "persona": "Srini"
    }


@pytest.fixture
def mock_email_service():
    """Mock email service."""
    mock_service = Mock()
    mock_service.send_email.return_value = True
    return mock_service


@pytest.fixture
def sample_sales_data():
    """Sample sales data for testing."""
    return [
        {
            "date": "2023-01-01",
            "product_name": "Test Product",
            "category": "Electronics",
            "store_name": "Test Store",
            "city": "New York",
            "customer_name": "John Doe",
            "units_sold": 10,
            "revenue": 1000.0,
            "profit": 300.0
        }
    ]


@pytest.fixture
def sample_email_request():
    """Sample email request data."""
    return {
        "to": "recipient@example.com",
        "message": "Test email message",
        "image": None
    }


@pytest.fixture
def sample_schedule_request():
    """Sample schedule request data."""
    return {
        "repeatFrequency": "daily",
        "scheduledTime": "09:00",
        "reportFormat": "PDF",
        "email": "user@example.com"
    }
