import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
import jwt
from app.core.config import settings


class TestDataAPI:
    """Integration tests for data API endpoints."""
    
    def create_test_token(self, username="testuser", persona="Srini"):
        """Helper to create test JWT token."""
        payload = {"sub": username, "persona": persona}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    def test_get_data_with_auth(self, test_client, sample_sales_data, mock_db_connection):
        """Test getting sales data with authentication."""
        token = self.create_test_token()
        
        with patch('app.services.data_service.DataService.get_sales_data') as mock_get_data:
            mock_get_data.return_value = sample_sales_data
            
            response = test_client.get(
                "/api/data",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["product_name"] == "Test Product"
            
            # Verify service was called with correct persona and database connection
            mock_get_data.assert_called_once_with("Srini", mock_db_connection)
    
    def test_get_data_without_auth(self, test_client):
        """Test getting sales data without authentication."""
        response = test_client.get("/api/data")
        
        assert response.status_code == 401
    
    def test_get_data_invalid_token(self, test_client):
        """Test getting sales data with invalid token."""
        response = test_client.get(
            "/api/data",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_get_products(self, test_client):
        """Test getting products data."""
        with patch('app.services.data_service.DataService.get_products') as mock_get_products:
            mock_get_products.return_value = [
                {"product_id": 1, "product_name": "Test Product", "category": "Electronics", "brand": "TestBrand"}
            ]
            
            response = test_client.get("/api/products")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["product_name"] == "Test Product"
    
    def test_get_stores(self, test_client):
        """Test getting stores data."""
        with patch('app.services.data_service.DataService.get_stores') as mock_get_stores:
            mock_get_stores.return_value = [
                {"store_id": 1, "store_name": "Test Store", "city": "New York", "state": "NY"}
            ]
            
            response = test_client.get("/api/stores")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["store_name"] == "Test Store"
    
    def test_get_ppdata_with_auth(self, test_client, mock_db_connection):
        """Test getting PP data with authentication."""
        token = self.create_test_token(persona="Venkat")
        
        with patch('app.services.data_service.DataService.get_pp_data') as mock_get_pp_data:
            mock_get_pp_data.return_value = [
                {"date": "2023-01-01", "product_name": "PP Product", "store_name": "PP Store"}
            ]
            
            response = test_client.get(
                "/api/ppdata",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["product_name"] == "PP Product"
            
            # Verify service was called with Venkat persona
            mock_get_pp_data.assert_called_once_with("Venkat", mock_db_connection)
    
    def test_get_ppproducts(self, test_client):
        """Test getting PP products data."""
        with patch('app.services.data_service.DataService.get_pp_products') as mock_get_pp_products:
            mock_get_pp_products.return_value = [
                {"product_id": "SKU123", "product_name": "PP Product", "Category": "Electronics"}
            ]
            
            response = test_client.get("/api/ppproducts")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["product_id"] == "SKU123"
    
    def test_get_ppstores(self, test_client):
        """Test getting PP stores data."""
        with patch('app.services.data_service.DataService.get_pp_stores') as mock_get_pp_stores:
            mock_get_pp_stores.return_value = [
                {"store_id": 1, "store_name": 1, "city": "Test City", "state": "Test State"}
            ]
            
            response = test_client.get("/api/ppstores")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["city"] == "Test City"
    
    def test_persona_filtering_different_users(self, test_client, mock_db_connection):
        """Test that different personas get different data filtering."""
        with patch('app.services.data_service.DataService.get_sales_data') as mock_get_data:
            mock_get_data.return_value = []
            
            # Test Srini persona
            srini_token = self.create_test_token(persona="Srini")
            response = test_client.get(
                "/api/data",
                headers={"Authorization": f"Bearer {srini_token}"}
            )
            assert response.status_code == 200
            mock_get_data.assert_called_with("Srini", mock_db_connection)
            
            # Test Venkat persona
            venkat_token = self.create_test_token(persona="Venkat")
            response = test_client.get(
                "/api/data",
                headers={"Authorization": f"Bearer {venkat_token}"}
            )
            assert response.status_code == 200
            mock_get_data.assert_called_with("Venkat", mock_db_connection)
            
            # Test no persona
            no_persona_token = self.create_test_token(persona=None)
            response = test_client.get(
                "/api/data",
                headers={"Authorization": f"Bearer {no_persona_token}"}
            )
            assert response.status_code == 200
            mock_get_data.assert_called_with(None, mock_db_connection)
