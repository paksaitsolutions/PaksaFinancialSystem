"""
Notification service for sending emails, SMS, and push notifications.
"""
from datetime import datetime
from typing import Dict, List, Any, Optional

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from app.core.config import settings
from app.core.logging import logger



# Try to import httpx, but make it optional
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

class EmailService:
    """Email notification service."""
    
    def __init__(self):
        """  Init  ."""
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'localhost')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@paksa.com')
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send Email."""
        """Send email notification."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_username and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

class SMSService:
    """SMS notification service."""
    
    def __init__(self):
        """  Init  ."""
        self.api_key = getattr(settings, 'SMS_API_KEY', '')
        self.api_url = getattr(settings, 'SMS_API_URL', '')
    
    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send Sms."""
        """Send SMS notification."""
        if not HTTPX_AVAILABLE:
            logger.warning("SMS service not available - httpx not installed")
            return False
        
        if not self.api_key or not self.api_url:
            logger.warning("SMS service not configured")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json={
                        "to": phone_number,
                        "message": message
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                
                if response.status_code == 200:
                    logger.info(f"SMS sent successfully to {phone_number}")
                    return True
                else:
                    logger.error(f"Failed to send SMS: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            return False

class PushNotificationService:
    """Push notification service."""
    
    def __init__(self):
        """  Init  ."""
        self.fcm_key = getattr(settings, 'FCM_SERVER_KEY', '')
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
    
    async def send_push_notification(
        self, 
        device_token: str, 
        title: str, 
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send Push Notification."""
        """Send push notification."""
        if not HTTPX_AVAILABLE:
            logger.warning("Push notification service not available - httpx not installed")
            return False
        
        if not self.fcm_key:
            logger.warning("Push notification service not configured")
            return False
        
        try:
            payload = {
                "to": device_token,
                "notification": {
                    "title": title,
                    "body": body
                }
            }
            
            if data:
                payload["data"] = data
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.fcm_url,
                    json=payload,
                    headers={
                        "Authorization": f"key={self.fcm_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"Push notification sent successfully to {device_token}")
                    return True
                else:
                    logger.error(f"Failed to send push notification: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to send push notification to {device_token}: {e}")
            return False

class NotificationService:
    """Main notification service that coordinates all notification types."""
    
    def __init__(self):
        """  Init  ."""
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushNotificationService()
    
    async def send_notification(
        self,
        notification_type: str,
        recipient: str,
        subject: str,
        message: str,
        **kwargs
    ) -> bool:
        """Send Notification."""
        """Send notification via specified type."""
        if notification_type == "email":
            return await self.email_service.send_email(
                recipient, subject, message, kwargs.get('html_body')
            )
        elif notification_type == "sms":
            return await self.sms_service.send_sms(recipient, message)
        elif notification_type == "push":
            return await self.push_service.send_push_notification(
                recipient, subject, message, kwargs.get('data')
            )
        else:
            logger.error(f"Unknown notification type: {notification_type}")
            return False
    
    async def send_multi_channel_notification(
        self,
        channels: List[str],
        recipients: Dict[str, str],
        subject: str,
        message: str,
        **kwargs
    ) -> Dict[str, bool]:
        """Send Multi Channel Notification."""
        """Send notification via multiple channels."""
        results = {}
        
        for channel in channels:
            if channel in recipients:
                results[channel] = await self.send_notification(
                    channel, recipients[channel], subject, message, **kwargs
                )
            else:
                results[channel] = False
                logger.warning(f"No recipient specified for channel: {channel}")
        
        return results

notification_service = NotificationService()