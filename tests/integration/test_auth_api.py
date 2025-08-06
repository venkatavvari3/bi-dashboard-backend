import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from app.core.config import settings
import jwt


class TestAuthAPI:
    """Integration tests for authentication API endpoints."""
    
    def test_login_username_password_success(self, test_client):
        """Test successful login with username and password."""
        with patch('app.services.auth_service.AuthService.authenticate_user') as mock_auth:
            mock_auth.return_value = "Srini"
            
            response = test_client.post("/api/login", json={
                "username": "testuser",
                "password": "password"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            
            # Verify token contains correct payload
            token = data["access_token"]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            assert payload["sub"] == "testuser"
            assert payload["persona"] == "Srini"
    
    def test_login_username_password_failure(self, test_client):
        """Test failed login with invalid credentials."""
        with patch('app.services.auth_service.AuthService.authenticate_user') as mock_auth:
            mock_auth.return_value = None
            
            response = test_client.post("/api/login", json={
                "username": "testuser",
                "password": "wrongpassword"
            })
            
            assert response.status_code == 401
            assert response.json()["detail"] == "Auth failed"
    
    def test_login_google_oauth_success(self, test_client):
        """Test successful Google OAuth login."""
        with patch('app.services.auth_service.AuthService.verify_google_token') as mock_verify:
            mock_verify.return_value = "test@example.com"
            
            with patch('app.services.auth_service.AuthService.get_persona_for_username') as mock_persona:
                mock_persona.return_value = "Venkat"
                
                response = test_client.post("/api/login", json={
                    "credential": "valid_google_token"
                })
                
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                
                # Verify token
                token = data["access_token"]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                assert payload["sub"] == "test@example.com"
                assert payload["persona"] == "Venkat"
    
    def test_login_google_oauth_failure(self, test_client):
        """Test failed Google OAuth login."""
        with patch('app.services.auth_service.AuthService.verify_google_token') as mock_verify:
            mock_verify.return_value = None
            
            response = test_client.post("/api/login", json={
                "credential": "invalid_google_token"
            })
            
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid Google token"
    
    def test_login_missing_payload(self, test_client):
        """Test login with missing credentials."""
        response = test_client.post("/api/login", json={})
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Missing login payload"
    
    def test_login_invalid_json(self, test_client):
        """Test login with invalid JSON format."""
        response = test_client.post("/api/login", data="invalid json")
        
        assert response.status_code == 422  # Unprocessable Entity
