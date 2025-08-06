import pytest
from unittest.mock import Mock, patch, MagicMock
import jwt
from fastapi import HTTPException
from app.services.auth_service import AuthService, get_current_user
from app.core.config import settings


class TestAuthService:
    """Test authentication service functionality."""
    
    def test_get_persona_for_username_found(self, mock_db_connection):
        """Test getting persona for existing username."""
        # Setup mock to return persona
        with patch('app.services.auth_service.DatabaseManager.execute_query') as mock_query:
            mock_query.return_value = ([('Srini',)], ['persona'])
            
            result = AuthService.get_persona_for_username("testuser", mock_db_connection)
            
            assert result == "Srini"
            mock_query.assert_called_once_with(
                mock_db_connection,
                "SELECT persona FROM persona_users WHERE username = %s",
                ("testuser",)
            )
    
    def test_get_persona_for_username_not_found(self, mock_db_connection):
        """Test getting persona for non-existing username."""
        with patch('app.services.auth_service.DatabaseManager.execute_query') as mock_query:
            mock_query.return_value = ([], [])
            
            result = AuthService.get_persona_for_username("nonexistent", mock_db_connection)
            
            assert result is None
    
    @patch('app.services.auth_service.requests.get')
    def test_verify_google_token_valid(self, mock_requests):
        """Test Google token verification with valid token."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "aud": settings.GOOGLE_CLIENT_ID,
            "email": "test@example.com"
        }
        mock_requests.return_value = mock_response
        
        result = AuthService.verify_google_token("valid_token")
        
        assert result == "test@example.com"
        mock_requests.assert_called_once_with(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": "valid_token"}
        )
    
    @patch('app.services.auth_service.requests.get')
    def test_verify_google_token_invalid(self, mock_requests):
        """Test Google token verification with invalid token."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_requests.return_value = mock_response
        
        result = AuthService.verify_google_token("invalid_token")
        
        assert result is None
    
    @patch('app.services.auth_service.requests.get')
    def test_verify_google_token_wrong_audience(self, mock_requests):
        """Test Google token verification with wrong audience."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "aud": "wrong_client_id",
            "email": "test@example.com"
        }
        mock_requests.return_value = mock_response
        
        result = AuthService.verify_google_token("token_with_wrong_aud")
        
        assert result is None
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        username = "testuser"
        persona = "Srini"
        
        token = AuthService.create_access_token(username, persona)
        
        # Decode token to verify contents
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == username
        assert payload["persona"] == persona
    
    def test_create_access_token_no_persona(self):
        """Test JWT token creation without persona."""
        username = "testuser"
        
        token = AuthService.create_access_token(username)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == username
        assert payload["persona"] is None
    
    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        payload = {"sub": "testuser", "persona": "Srini"}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        result = AuthService.verify_token(token)
        
        assert result["sub"] == "testuser"
        assert result["persona"] == "Srini"
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            AuthService.verify_token("invalid_token")
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"
    
    def test_authenticate_user_valid(self, mock_db_connection):
        """Test user authentication with valid credentials."""
        with patch.object(AuthService, 'get_persona_for_username') as mock_get_persona:
            mock_get_persona.return_value = "Srini"
            
            result = AuthService.authenticate_user("testuser", "password", mock_db_connection)
            
            assert result == "Srini"
            mock_get_persona.assert_called_once_with("testuser", mock_db_connection)
    
    def test_authenticate_user_invalid_password(self, mock_db_connection):
        """Test user authentication with invalid password."""
        with patch.object(AuthService, 'get_persona_for_username') as mock_get_persona:
            mock_get_persona.return_value = "Srini"
            
            result = AuthService.authenticate_user("testuser", "wrong_password", mock_db_connection)
            
            assert result is None
    
    def test_authenticate_user_no_persona(self, mock_db_connection):
        """Test user authentication with non-existent user."""
        with patch.object(AuthService, 'get_persona_for_username') as mock_get_persona:
            mock_get_persona.return_value = None
            
            result = AuthService.authenticate_user("nonexistent", "password", mock_db_connection)
            
            assert result is None


class TestGetCurrentUser:
    """Test get_current_user dependency function."""
    
    def test_get_current_user_valid_token(self):
        """Test getting current user with valid token."""
        payload = {"sub": "testuser", "persona": "Srini"}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        result = get_current_user(token)
        
        assert result["sub"] == "testuser"
        assert result["persona"] == "Srini"
    
    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user("invalid_token")
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"
