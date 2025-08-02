import smtplib
import base64
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from fastapi import HTTPException
from app.core.config import settings


class EmailService:
    """Service for handling email operations."""
    
    @staticmethod
    def send_email(to_email: str, message: str, image_data: str = None) -> bool:
        """Send email with optional image attachment."""
        if not to_email or "@" not in to_email:
            raise HTTPException(status_code=400, detail="Valid recipient email is required.")
        
        msg = MIMEMultipart()
        msg["Subject"] = "Message from BI Dashboard"
        msg["From"] = settings.EMAIL_ADDRESS
        msg["To"] = to_email
        msg.attach(MIMEText(message, "plain"))
        
        # Handle image attachment
        if image_data:
            EmailService._attach_image(msg, image_data)
        
        try:
            with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as smtp:
                smtp.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
                smtp.sendmail(settings.EMAIL_ADDRESS, [to_email], msg.as_string())
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to send email.")
    
    @staticmethod
    def _attach_image(msg: MIMEMultipart, image_data: str):
        """Attach base64 image to email message."""
        match = re.match(r"data:image/(?P<ext>\w+);base64,(?P<data>.+)", image_data)
        if match:
            ext = match.group("ext")
            data = match.group("data")
            image_bytes = base64.b64decode(data)
            
            part = MIMEBase("image", ext)
            part.set_payload(image_bytes)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="image.{ext}"')
            msg.attach(part)
        else:
            print("Image field is not a valid data URL")
