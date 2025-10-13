"""
Unified Notification System
Cross-module notification management and delivery
"""
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel, AuditMixin
from datetime import datetime, timedelta
from enum import Enum
import asyncio

class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    APPROVAL_REQUEST = "approval_request"
    REMINDER = "reminder"
    ALERT = "alert"

class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class UnifiedNotification(BaseModel, AuditMixin):
    """Unified notification for all modules"""
    __tablename__ = "unified_notifications"
    
    # Core notification fields
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    recipient_user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    sender_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Notification content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(20), default=NotificationType.INFO, index=True)
    
    # Source context
    module_name = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True, index=True)
    resource_id = Column(String, nullable=True, index=True)
    
    # Delivery configuration
    channels = Column(JSON, nullable=False)  # Array of channels to use
    priority = Column(Integer, default=1)  # 1=low, 2=normal, 3=high, 4=urgent
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Status tracking
    status = Column(String(20), default=NotificationStatus.PENDING, index=True)
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Action configuration
    action_url = Column(String(500))  # URL for action button
    action_text = Column(String(100))  # Text for action button
    action_data = Column(JSON)  # Additional data for actions
    
    # Metadata
    tags = Column(JSON)  # Array of tags for categorization
    metadata = Column(JSON)  # Additional metadata
    
    # Relationships
    company = relationship("Company", viewonly=True)
    recipient = relationship("User", foreign_keys=[recipient_user_id], viewonly=True)
    sender = relationship("User", foreign_keys=[sender_user_id], viewonly=True)
    
    __table_args__ = (
        {"extend_existing": True},
    )

class NotificationTemplate(BaseModel, AuditMixin):
    """Templates for notifications"""
    __tablename__ = "notification_templates"
    
    template_name = Column(String(100), nullable=False, unique=True)
    module_name = Column(String(50), nullable=False)
    event_type = Column(String(100), nullable=False)
    
    # Template content
    title_template = Column(String(200), nullable=False)
    message_template = Column(Text, nullable=False)
    notification_type = Column(String(20), default=NotificationType.INFO)
    
    # Default configuration
    default_channels = Column(JSON, nullable=False)
    default_priority = Column(Integer, default=1)
    
    # Conditions
    conditions = Column(JSON)  # Conditions for when to use this template
    
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        {"extend_existing": True},
    )

class NotificationPreference(BaseModel, AuditMixin):
    """User notification preferences"""
    __tablename__ = "notification_preferences"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    
    # Preference configuration
    module_name = Column(String(50), nullable=False)
    event_type = Column(String(100), nullable=False)
    enabled_channels = Column(JSON, nullable=False)  # Array of enabled channels
    
    # Timing preferences
    quiet_hours_start = Column(String(5))  # HH:MM format
    quiet_hours_end = Column(String(5))    # HH:MM format
    timezone = Column(String(50), default="UTC")
    
    # Frequency settings
    digest_frequency = Column(String(20))  # immediate, hourly, daily, weekly
    
    # Relationships
    user = relationship("User", viewonly=True)
    company = relationship("Company", viewonly=True)
    
    __table_args__ = (
        {"extend_existing": True},
    )

class UnifiedNotificationService:
    """Service for unified notification management"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.channel_handlers = {}
        self.template_engine = None
    
    def register_channel_handler(self, channel: str, handler):
        """Register a handler for a notification channel"""
        self.channel_handlers[channel] = handler
    
    async def send_notification(self,
                               company_id: str,
                               recipient_user_id: str,
                               title: str,
                               message: str,
                               module_name: str,
                               notification_type: str = NotificationType.INFO,
                               channels: List[str] = None,
                               resource_type: str = None,
                               resource_id: str = None,
                               sender_user_id: str = None,
                               priority: int = 1,
                               scheduled_at: datetime = None,
                               expires_at: datetime = None,
                               action_url: str = None,
                               action_text: str = None,
                               action_data: Dict = None,
                               tags: List[str] = None,
                               metadata: Dict = None) -> UnifiedNotification:
        """Send a notification"""
        
        # Use default channels if not specified
        if not channels:
            channels = await self._get_user_preferred_channels(recipient_user_id, company_id, module_name)
        
        notification = UnifiedNotification(
            company_id=company_id,
            recipient_user_id=recipient_user_id,
            sender_user_id=sender_user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            module_name=module_name,
            resource_type=resource_type,
            resource_id=resource_id,
            channels=channels,
            priority=priority,
            scheduled_at=scheduled_at,
            expires_at=expires_at,
            action_url=action_url,
            action_text=action_text,
            action_data=action_data,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.db.add(notification)
        await self.db.commit()
        
        # Send immediately if not scheduled
        if not scheduled_at:
            await self._deliver_notification(notification)
        
        return notification
    
    async def send_from_template(self,
                                template_name: str,
                                company_id: str,
                                recipient_user_id: str,
                                template_data: Dict[str, Any],
                                **kwargs) -> UnifiedNotification:
        """Send notification using a template"""
        
        template = await self.db.query(NotificationTemplate).filter(
            NotificationTemplate.template_name == template_name,
            NotificationTemplate.is_active == True
        ).first()
        
        if not template:
            raise Exception(f"Template not found: {template_name}")
        
        # Render template
        title = self._render_template(template.title_template, template_data)
        message = self._render_template(template.message_template, template_data)
        
        return await self.send_notification(
            company_id=company_id,
            recipient_user_id=recipient_user_id,
            title=title,
            message=message,
            module_name=template.module_name,
            notification_type=template.notification_type,
            channels=template.default_channels,
            priority=template.default_priority,
            **kwargs
        )
    
    async def _deliver_notification(self, notification: UnifiedNotification):
        """Deliver notification through configured channels"""
        
        try:
            for channel in notification.channels:
                handler = self.channel_handlers.get(channel)
                if handler:
                    await handler(notification)
            
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            await self.db.commit()
            
        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.metadata = notification.metadata or {}
            notification.metadata['error'] = str(e)
            await self.db.commit()
    
    async def mark_as_read(self, notification_id: str, user_id: str):
        """Mark notification as read"""
        notification = await self.db.query(UnifiedNotification).filter(
            UnifiedNotification.id == notification_id,
            UnifiedNotification.recipient_user_id == user_id
        ).first()
        
        if notification:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.utcnow()
            await self.db.commit()
    
    async def get_user_notifications(self,
                                    user_id: str,
                                    company_id: str,
                                    unread_only: bool = False,
                                    module_name: str = None,
                                    limit: int = 50) -> List[UnifiedNotification]:
        """Get notifications for a user"""
        
        query = self.db.query(UnifiedNotification).filter(
            UnifiedNotification.recipient_user_id == user_id,
            UnifiedNotification.company_id == company_id
        )
        
        if unread_only:
            query = query.filter(UnifiedNotification.status != NotificationStatus.READ)
        
        if module_name:
            query = query.filter(UnifiedNotification.module_name == module_name)
        
        return await query.order_by(UnifiedNotification.created_at.desc()).limit(limit).all()
    
    async def _get_user_preferred_channels(self, user_id: str, company_id: str, module_name: str) -> List[str]:
        """Get user's preferred notification channels"""
        
        preference = await self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id,
            NotificationPreference.company_id == company_id,
            NotificationPreference.module_name == module_name
        ).first()
        
        if preference:
            return preference.enabled_channels
        
        # Default channels
        return [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
    
    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Render notification template with data"""
        # Simple template rendering - can be enhanced with Jinja2
        result = template
        for key, value in data.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
    
    async def process_scheduled_notifications(self):
        """Process scheduled notifications"""
        now = datetime.utcnow()
        
        scheduled_notifications = await self.db.query(UnifiedNotification).filter(
            UnifiedNotification.status == NotificationStatus.PENDING,
            UnifiedNotification.scheduled_at <= now
        ).all()
        
        for notification in scheduled_notifications:
            await self._deliver_notification(notification)
    
    async def cleanup_expired_notifications(self, days: int = 30):
        """Clean up old notifications"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        await self.db.query(UnifiedNotification).filter(
            UnifiedNotification.created_at < cutoff_date,
            UnifiedNotification.status == NotificationStatus.READ
        ).delete()
        
        await self.db.commit()

# Default notification templates
DEFAULT_TEMPLATES = {
    "ap_invoice_approval_request": {
        "template_name": "AP Invoice Approval Request",
        "module_name": "ap",
        "event_type": "invoice_approval_required",
        "title_template": "Invoice Approval Required: {invoice_number}",
        "message_template": "Invoice {invoice_number} from {vendor_name} for ${amount} requires your approval.",
        "notification_type": NotificationType.APPROVAL_REQUEST,
        "default_channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL],
        "default_priority": 3
    },
    "payroll_run_completed": {
        "template_name": "Payroll Run Completed",
        "module_name": "payroll",
        "event_type": "payroll_run_completed",
        "title_template": "Payroll Run Completed: {pay_period}",
        "message_template": "Payroll run for {pay_period} has been completed. {employee_count} employees processed.",
        "notification_type": NotificationType.SUCCESS,
        "default_channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL],
        "default_priority": 2
    },
    "invoice_overdue": {
        "template_name": "Invoice Overdue",
        "module_name": "ar",
        "event_type": "invoice_overdue",
        "title_template": "Overdue Invoice: {invoice_number}",
        "message_template": "Invoice {invoice_number} for {customer_name} is {days_overdue} days overdue. Amount: ${amount}",
        "notification_type": NotificationType.WARNING,
        "default_channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL],
        "default_priority": 3
    },
    "low_inventory_alert": {
        "template_name": "Low Inventory Alert",
        "module_name": "inventory",
        "event_type": "low_inventory",
        "title_template": "Low Inventory Alert: {item_name}",
        "message_template": "Item {item_name} is running low. Current quantity: {current_quantity}, Reorder level: {reorder_level}",
        "notification_type": NotificationType.ALERT,
        "default_channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL],
        "default_priority": 2
    }
}

# Channel handlers (to be implemented)
class EmailNotificationHandler:
    async def __call__(self, notification: UnifiedNotification):
        # Implement email sending logic
        pass

class SMSNotificationHandler:
    async def __call__(self, notification: UnifiedNotification):
        # Implement SMS sending logic
        pass

class PushNotificationHandler:
    async def __call__(self, notification: UnifiedNotification):
        # Implement push notification logic
        pass