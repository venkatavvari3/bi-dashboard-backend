import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
import jwt
from app.core.config import settings


class TestEmailAPI:
    """Integration tests for email API endpoints."""
    
    def create_test_token(self, username="testuser", persona="Srini"):
        """Helper to create test JWT token."""
        payload = {"sub": username, "persona": persona}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    def test_send_email_success(self, test_client, sample_email_request):
        """Test successful email sending."""
        token = self.create_test_token()
        
        with patch('app.services.email_service.EmailService.send_email') as mock_send_email:
            mock_send_email.return_value = True
            
            response = test_client.post(
                "/api/email_me",
                json=sample_email_request,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Email sent successfully"
            assert data["success"] is True
            
            # Verify service was called with correct parameters
            mock_send_email.assert_called_once_with(
                sample_email_request["to"],
                sample_email_request["message"],
                sample_email_request["image"]
            )
    
    def test_send_email_with_image(self, test_client):
        """Test sending email with image attachment."""
        token = self.create_test_token()
        
        email_request = {
            "to": "recipient@example.com",
            "message": "Test message with image",
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        }
        
        with patch('app.services.email_service.EmailService.send_email') as mock_send_email:
            mock_send_email.return_value = True
            
            response = test_client.post(
                "/api/email_me",
                json=email_request,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            mock_send_email.assert_called_once_with(
                email_request["to"],
                email_request["message"],
                email_request["image"]
            )
    
    def test_send_email_without_auth(self, test_client, sample_email_request):
        """Test sending email without authentication."""
        response = test_client.post("/api/email_me", json=sample_email_request)
        
        assert response.status_code == 401
    
    def test_send_email_invalid_token(self, test_client, sample_email_request):
        """Test sending email with invalid token."""
        response = test_client.post(
            "/api/email_me",
            json=sample_email_request,
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_send_email_invalid_recipient(self, test_client):
        """Test sending email with invalid recipient."""
        token = self.create_test_token()
        
        invalid_email_request = {
            "to": "invalid_email",
            "message": "Test message"
        }
        
        with patch('app.services.email_service.EmailService.send_email') as mock_send_email:
            from fastapi import HTTPException
            mock_send_email.side_effect = HTTPException(status_code=400, detail="Valid recipient email is required.")
            
            response = test_client.post(
                "/api/email_me",
                json=invalid_email_request,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 400
    
    def test_send_email_service_failure(self, test_client, sample_email_request):
        """Test email sending when service fails."""
        token = self.create_test_token()
        
        with patch('app.services.email_service.EmailService.send_email') as mock_send_email:
            from fastapi import HTTPException
            mock_send_email.side_effect = HTTPException(status_code=500, detail="Failed to send email.")
            
            response = test_client.post(
                "/api/email_me",
                json=sample_email_request,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 500
    
    def test_send_email_missing_fields(self, test_client):
        """Test sending email with missing required fields."""
        token = self.create_test_token()
        
        incomplete_request = {
            "message": "Test message"
            # Missing "to" field
        }
        
        response = test_client.post(
            "/api/email_me",
            json=incomplete_request,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_send_email_empty_message(self, test_client):
        """Test sending email with empty message."""
        token = self.create_test_token()
        
        empty_message_request = {
            "to": "recipient@example.com",
            "message": ""
        }
        
        with patch('app.services.email_service.EmailService.send_email') as mock_send_email:
            mock_send_email.return_value = True
            
            response = test_client.post(
                "/api/email_me",
                json=empty_message_request,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            mock_send_email.assert_called_once_with(
                "recipient@example.com",
                "",
                None
            )
    
    def test_email_response_format(self, test_client, sample_email_request):
        """Test that email response has correct format."""
        token = self.create_test_token()
        
        with patch('app.services.email_service.EmailService.send_email') as mock_send_email:
            mock_send_email.return_value = True
            
            response = test_client.post(
                "/api/email_me",
                json=sample_email_request,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert "message" in data
            assert "success" in data
            assert isinstance(data["success"], bool)
            assert isinstance(data["message"], str)
