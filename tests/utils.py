import jwt
from typing import Optional
from app.core.config import settings


def create_test_token(username: str = "testuser", persona: Optional[str] = "Srini") -> str:
    """Create a test JWT token for authentication testing."""
    payload = {"sub": username, "persona": persona}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_auth_headers(token: str) -> dict:
    """Create authorization headers with Bearer token."""
    return {"Authorization": f"Bearer {token}"}


def assert_error_response(response, expected_status: int, expected_detail: str = None):
    """Assert that response contains expected error."""
    assert response.status_code == expected_status
    if expected_detail:
        data = response.json()
        assert "detail" in data
        assert expected_detail in data["detail"]


def assert_success_response(response, expected_keys: list = None):
    """Assert that response is successful and contains expected keys."""
    assert response.status_code == 200
    if expected_keys:
        data = response.json()
        for key in expected_keys:
            assert key in data


class MockDatabase:
    """Mock database helper for testing."""
    
    def __init__(self):
        self.queries = []
        self.inserts = []
        self.mock_results = {}
    
    def set_query_result(self, query_pattern: str, result: tuple):
        """Set mock result for a query pattern."""
        self.mock_results[query_pattern] = result
    
    def execute_query(self, query: str, params: tuple = None):
        """Mock query execution."""
        self.queries.append((query, params))
        
        # Find matching mock result
        for pattern, result in self.mock_results.items():
            if pattern in query:
                return result
        
        return ([], [])
    
    def execute_insert(self, query: str, params: tuple):
        """Mock insert execution."""
        self.inserts.append((query, params))
    
    def create_table_if_not_exists(self, query: str):
        """Mock table creation."""
        pass


class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_user_data(username: str = "testuser", email: str = "test@example.com"):
        """Create test user data."""
        return {
            "username": username,
            "email": email,
            "password": "password"
        }
    
    @staticmethod
    def create_sales_data(count: int = 1):
        """Create test sales data."""
        return [
            {
                "date": f"2023-01-{i+1:02d}",
                "product_name": f"Product {i+1}",
                "category": "Electronics",
                "store_name": f"Store {i+1}",
                "city": "New York",
                "customer_name": f"Customer {i+1}",
                "units_sold": 10 + i,
                "revenue": 1000.0 + (i * 100),
                "profit": 300.0 + (i * 30)
            }
            for i in range(count)
        ]
    
    @staticmethod
    def create_email_request(to: str = "test@example.com", message: str = "Test message"):
        """Create test email request."""
        return {
            "to": to,
            "message": message,
            "image": None
        }
    
    @staticmethod
    def create_schedule_request(
        frequency: str = "daily",
        time: str = "09:00",
        format_type: str = "PDF",
        email: str = "test@example.com"
    ):
        """Create test schedule request."""
        return {
            "repeatFrequency": frequency,
            "scheduledTime": time,
            "reportFormat": format_type,
            "email": email
        }
