from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.notification import Notification, NotificationType, NotificationPriority
from datetime import datetime
import uuid

def seed_notifications():
    """Create sample notifications for testing"""
    db = next(get_db())
    
    # Sample notifications
    notifications = [
        {
            "title": "New Invoice Created",
            "message": "Invoice INV-001 has been created and is pending approval",
            "type": NotificationType.INFO,
            "priority": NotificationPriority.MEDIUM,
            "action_url": "/ar/invoices/1"
        },
        {
            "title": "Payment Overdue", 
            "message": "Payment for Bill BILL-002 is 5 days overdue",
            "type": NotificationType.WARNING,
            "priority": NotificationPriority.HIGH,
            "action_url": "/ap/bills/2"
        },
        {
            "title": "Cash Flow Alert",
            "message": "Cash balance is below minimum threshold",
            "type": NotificationType.ERROR,
            "priority": NotificationPriority.URGENT,
            "action_url": "/cash/dashboard"
        },
        {
            "title": "Budget Variance",
            "message": "Marketing budget is 15% over allocated amount",
            "type": NotificationType.WARNING,
            "priority": NotificationPriority.MEDIUM,
            "action_url": "/budget/reports"
        },
        {
            "title": "Payroll Processed",
            "message": "Monthly payroll has been successfully processed",
            "type": NotificationType.SUCCESS,
            "priority": NotificationPriority.LOW,
            "action_url": "/payroll/reports"
        }
    ]
    
    for notif_data in notifications:
        notification = Notification(
            id=uuid.uuid4(),
            user_id="demo-user",  # Using demo user for testing
            title=notif_data["title"],
            message=notif_data["message"],
            type=notif_data["type"],
            priority=notif_data["priority"],
            action_url=notif_data["action_url"],
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        db.add(notification)
    
    db.commit()
    print(f"Created {len(notifications)} sample notifications")

if __name__ == "__main__":
    seed_notifications()