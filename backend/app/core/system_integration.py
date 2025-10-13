"""
System Integration Service
Coordinates all unified systems and provides central integration point
"""
from typing import Dict, Any, Optional, List
from app.core.unified_settings import UnifiedSettingsService
from app.core.unified_rbac import UnifiedRBACService
from app.core.unified_audit import UnifiedAuditService
from app.core.unified_workflow import UnifiedWorkflowEngine
from app.core.unified_notifications import UnifiedNotificationService

class SystemIntegrationService:
    """Central service for system integration"""
    
    def __init__(self, db_session):
        self.db = db_session
        
        # Initialize all unified services
        self.settings = UnifiedSettingsService(db_session)
        self.rbac = UnifiedRBACService(db_session)
        self.audit = UnifiedAuditService(db_session)
        self.workflow = UnifiedWorkflowEngine(db_session)
        self.notifications = UnifiedNotificationService(db_session)
        
        # Setup integrations
        self._setup_integrations()
    
    def _setup_integrations(self):
        """Setup integrations between systems"""
        
        # Register workflow step handlers
        self.workflow.register_step_handler("approval", self._handle_approval_step)
        self.workflow.register_step_handler("notification", self._handle_notification_step)
        self.workflow.register_step_handler("audit", self._handle_audit_step)
        
        # Register notification channel handlers
        from app.core.unified_notifications import EmailNotificationHandler, SMSNotificationHandler
        self.notifications.register_channel_handler("email", EmailNotificationHandler())
        self.notifications.register_channel_handler("sms", SMSNotificationHandler())
    
    async def _handle_approval_step(self, step, step_instance, workflow_instance):
        """Handle approval workflow steps"""
        
        # Send approval notification
        await self.notifications.send_notification(
            company_id=workflow_instance.company_id,
            recipient_user_id=step.approver_user_id,
            title=f"Approval Required: {workflow_instance.instance_name}",
            message=f"Please review and approve: {step.step_name}",
            module_name=step.target_module,
            notification_type="approval_request",
            action_url=f"/approvals/{step_instance.id}",
            action_text="Review"
        )
        
        # Log audit event
        await self.audit.log_action(
            company_id=workflow_instance.company_id,
            user_id=None,
            module_name="workflow",
            action_type="APPROVAL_REQUESTED",
            resource_type="workflow_step",
            resource_id=step_instance.id,
            description=f"Approval requested for {step.step_name}"
        )
        
        return {"status": "approval_requested"}
    
    async def _handle_notification_step(self, step, step_instance, workflow_instance):
        """Handle notification workflow steps"""
        
        config = step.action_config or {}
        
        await self.notifications.send_notification(
            company_id=workflow_instance.company_id,
            recipient_user_id=config.get("recipient_user_id"),
            title=config.get("title", "Workflow Notification"),
            message=config.get("message", "Workflow step completed"),
            module_name=step.target_module,
            notification_type=config.get("type", "info")
        )
        
        return {"status": "notification_sent"}
    
    async def _handle_audit_step(self, step, step_instance, workflow_instance):
        """Handle audit workflow steps"""
        
        config = step.action_config or {}
        
        await self.audit.log_action(
            company_id=workflow_instance.company_id,
            user_id=config.get("user_id"),
            module_name=step.target_module,
            action_type=config.get("action_type", "WORKFLOW_ACTION"),
            resource_type=config.get("resource_type"),
            resource_id=config.get("resource_id"),
            description=config.get("description", f"Workflow step: {step.step_name}")
        )
        
        return {"status": "audit_logged"}
    
    async def initialize_company_defaults(self, company_id: str):
        """Initialize default settings, roles, and workflows for a new company"""
        
        # Initialize default settings
        from app.core.unified_settings import DEFAULT_SETTINGS
        for module, settings in DEFAULT_SETTINGS.items():
            for key, value in settings.items():
                await self.settings.set_setting(company_id, module, key, value)
        
        # Initialize default roles and permissions
        from app.core.unified_rbac import DEFAULT_PERMISSIONS, DEFAULT_ROLES
        
        # Create module permissions
        for module, permissions in DEFAULT_PERMISSIONS.items():
            for perm_code, perm_name in permissions:
                # Create permission if not exists
                pass  # Implementation would create ModulePermission records
        
        # Create default roles
        for role_name, role_config in DEFAULT_ROLES.items():
            # Create role with permissions
            pass  # Implementation would create UnifiedRole records
        
        # Initialize default workflows
        from app.core.unified_workflow import DEFAULT_WORKFLOWS
        for workflow_name, workflow_config in DEFAULT_WORKFLOWS.items():
            # Create workflow
            pass  # Implementation would create UnifiedWorkflow records
        
        # Initialize default notification templates
        from app.core.unified_notifications import DEFAULT_TEMPLATES
        for template_name, template_config in DEFAULT_TEMPLATES.items():
            # Create template
            pass  # Implementation would create NotificationTemplate records
    
    async def check_user_access(self, user_id: str, company_id: str, module: str, action: str) -> bool:
        """Check if user has access to perform an action"""
        
        # Check RBAC permissions
        has_permission = await self.rbac.check_permission(user_id, company_id, module, action)
        
        # Log access attempt
        await self.audit.log_action(
            company_id=company_id,
            user_id=user_id,
            module_name="security",
            action_type="ACCESS_CHECK",
            resource_type="permission",
            description=f"Access check for {module}.{action}: {'GRANTED' if has_permission else 'DENIED'}"
        )
        
        return has_permission
    
    async def trigger_cross_module_event(self, module: str, event: str, data: Dict[str, Any]):
        """Trigger cross-module events and workflows"""
        
        # Trigger workflows
        workflow_instances = await self.workflow.trigger_workflow(
            module=module,
            event=event,
            data=data
        )
        
        # Log event
        await self.audit.log_action(
            company_id=data.get('company_id'),
            user_id=data.get('user_id'),
            module_name=module,
            action_type="EVENT_TRIGGERED",
            resource_type="event",
            description=f"Event triggered: {event}",
            new_values=data
        )
        
        return workflow_instances
    
    async def get_user_dashboard_data(self, user_id: str, company_id: str) -> Dict[str, Any]:
        """Get unified dashboard data for user"""
        
        # Get user permissions to determine what they can see
        permissions = await self.rbac.get_user_permissions(user_id, company_id)
        
        # Get recent notifications
        notifications = await self.notifications.get_user_notifications(
            user_id=user_id,
            company_id=company_id,
            unread_only=True,
            limit=10
        )
        
        # Get pending approvals (if user has approval permissions)
        pending_approvals = []
        if any("approve" in perm for perm in permissions):
            # Get workflow steps awaiting this user's approval
            pass  # Implementation would query UnifiedWorkflowStepInstance
        
        # Get recent activity
        recent_activity = await self.audit.get_user_activity(user_id, company_id, days=7)
        
        return {
            "permissions": list(permissions),
            "notifications": [
                {
                    "id": n.id,
                    "title": n.title,
                    "message": n.message,
                    "type": n.notification_type,
                    "module": n.module_name,
                    "created_at": n.created_at,
                    "action_url": n.action_url,
                    "action_text": n.action_text
                }
                for n in notifications
            ],
            "pending_approvals": pending_approvals,
            "recent_activity": [
                {
                    "id": a.id,
                    "action": a.action_type,
                    "resource": a.resource_type,
                    "module": a.module_name,
                    "timestamp": a.timestamp,
                    "description": a.description
                }
                for a in recent_activity[:10]
            ]
        }

# Global integration service instance
integration_service = None

def get_integration_service(db_session) -> SystemIntegrationService:
    """Get or create integration service instance"""
    global integration_service
    if not integration_service:
        integration_service = SystemIntegrationService(db_session)
    return integration_service