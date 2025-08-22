"""
Notification service.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx

from app.core.config import settings
from app.core.logging import logger

class EmailService:
    """Email notification service."""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send email notification."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
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
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

class SlackService:
    """Slack notification service."""
    
    def __init__(self):
        self.webhook_url = settings.SLACK_WEBHOOK_URL
    
    async def send_message(self, message: str, channel: Optional[str] = None) -> bool:
        """Send Slack message."""
        try:
            payload = {"text": message}
            if channel:
                payload["channel"] = channel
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Failed to send Slack message: {str(e)}")
            return False

class NotificationService:
    """Central notification service."""
    
    def __init__(self):
        self.email_service = EmailService()
        self.slack_service = SlackService()
        self.notification_templates = {
            "invoice_created": {
                "subject": "New Invoice Created - {invoice_number}",
                "body": "A new invoice {invoice_number} has been created for {customer_name}."
            },
            "payment_received": {
                "subject": "Payment Received - {invoice_number}",
                "body": "Payment of {amount} received for invoice {invoice_number}."
            },
            "expense_approved": {
                "subject": "Expense Approved - {expense_id}",
                "body": "Your expense report {expense_id} has been approved."
            },
            "budget_exceeded": {
                "subject": "Budget Alert - {department}",
                "body": "Budget for {department} has exceeded {percentage}% of allocated amount."
            }
        }
    
    async def send_notification(
        self,
        notification_type: str,
        recipient: str,
        data: Dict[str, Any],
        channels: List[str] = ["email"]
    ) -> bool:
        """Send notification through specified channels."""
        template = self.notification_templates.get(notification_type)
        if not template:
            logger.error(f"Unknown notification type: {notification_type}")
            return False
        
        subject = template["subject"].format(**data)
        body = template["body"].format(**data)
        
        success = True
        
        if "email" in channels:
            email_success = await self.email_service.send_email(
                recipient, subject, body
            )
            success = success and email_success
        
        if "slack" in channels:
            slack_message = f"*{subject}*\n{body}"
            slack_success = await self.slack_service.send_message(slack_message)
            success = success and slack_success
        
        return success
    
    async def send_bulk_notification(
        self,
        notification_type: str,
        recipients: List[str],
        data: Dict[str, Any],
        channels: List[str] = ["email"]
    ) -> Dict[str, bool]:
        """Send notification to multiple recipients."""
        results = {}
        for recipient in recipients:
            results[recipient] = await self.send_notification(
                notification_type, recipient, data, channels
            )
        return results

notification_service = NotificationService()