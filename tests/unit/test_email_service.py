import pytest
from unittest.mock import Mock, patch, MagicMock
import base64
from fastapi import HTTPException
from app.services.email_service import EmailService


class TestEmailService:
    """Test email service functionality."""
    
    @patch('app.services.email_service.smtplib.SMTP_SSL')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending."""
        # Setup mock SMTP
        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        result = EmailService.send_email(
            "recipient@example.com",
            "Test message"
        )
        
        assert result is True
        mock_smtp_instance.login.assert_called_once()
        mock_smtp_instance.sendmail.assert_called_once()
    
    def test_send_email_invalid_recipient(self):
        """Test email sending with invalid recipient."""
        with pytest.raises(HTTPException) as exc_info:
            EmailService.send_email("invalid_email", "Test message")
        
        assert exc_info.value.status_code == 400
        assert "Valid recipient email is required" in exc_info.value.detail
    
    def test_send_email_empty_recipient(self):
        """Test email sending with empty recipient."""
        with pytest.raises(HTTPException) as exc_info:
            EmailService.send_email("", "Test message")
        
        assert exc_info.value.status_code == 400
    
    @patch('app.services.email_service.smtplib.SMTP_SSL')
    def test_send_email_with_image(self, mock_smtp):
        """Test email sending with image attachment."""
        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Create test image data
        test_image_data = base64.b64encode(b"fake_image_data").decode()
        image_data_url = f"data:image/png;base64,{test_image_data}"
        
        result = EmailService.send_email(
            "recipient@example.com",
            "Test message",
            image_data_url
        )
        
        assert result is True
        mock_smtp_instance.login.assert_called_once()
        mock_smtp_instance.sendmail.assert_called_once()
    
    @patch('app.services.email_service.smtplib.SMTP_SSL')
    def test_send_email_smtp_error(self, mock_smtp):
        """Test email sending with SMTP error."""
        mock_smtp_instance = Mock()
        mock_smtp_instance.login.side_effect = Exception("SMTP Error")
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        with pytest.raises(HTTPException) as exc_info:
            EmailService.send_email("recipient@example.com", "Test message")
        
        assert exc_info.value.status_code == 500
        assert "Failed to send email" in exc_info.value.detail
    
    def test_attach_image_valid_format(self):
        """Test image attachment with valid format."""
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        test_image_data = base64.b64encode(b"fake_image_data").decode()
        image_data_url = f"data:image/png;base64,{test_image_data}"
        
        # This should not raise an exception
        EmailService._attach_image(msg, image_data_url)
        
        # Check that an attachment was added
        assert len(msg.get_payload()) > 0
    
    def test_attach_image_invalid_format(self):
        """Test image attachment with invalid format."""
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        invalid_image_data = "not_a_valid_data_url"
        
        # This should not raise an exception but should print error
        with patch('builtins.print') as mock_print:
            EmailService._attach_image(msg, invalid_image_data)
            mock_print.assert_called_once_with("Image field is not a valid data URL")
    
    @patch('app.services.email_service.smtplib.SMTP_SSL')
    def test_email_content_structure(self, mock_smtp):
        """Test that email has correct structure."""
        mock_smtp_instance = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        to_email = "recipient@example.com"
        message = "Test message content"
        
        EmailService.send_email(to_email, message)
        
        # Verify sendmail was called with correct parameters
        args, kwargs = mock_smtp_instance.sendmail.call_args
        from_email, recipients, email_content = args
        
        assert to_email in recipients
        assert message in email_content
        assert "Message from BI Dashboard" in email_content
