"""
Workflow Engine - Approval Workflows, Email Notifications, Hierarchy, Delegation
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

from email.mime.multipart import MimeMultipart
from email.mime.text import MimeText
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
import smtplib
import uuid

from app.models.financial_core import *


class WorkflowEngine:
    """Core workflow processing engine"""
    
    @staticmethod
    def create_workflow(db: Session, workflow_type: str, entity_id: str, 
                       amount: float, created_by: str) -> str:
        """Create Workflow."""
        """Create new workflow instance"""
        from app.models.workflow import WorkflowInstance, WorkflowStep
        
        # Get workflow definition
        definition = WorkflowEngine._get_workflow_definition(workflow_type, amount)
        
        # Create workflow instance
        workflow = WorkflowInstance(
            workflow_type=workflow_type,
            entity_id=entity_id,
            entity_type=WorkflowEngine._get_entity_type(workflow_type),
            status='pending',
            current_step=1,
            total_steps=len(definition['steps']),
            amount=amount,
            created_by=created_by,
            workflow_data=json.dumps(definition)
        )
        
        db.add(workflow)
        db.flush()
        
        # Create workflow steps
        for i, step_def in enumerate(definition['steps'], 1):
            step = WorkflowStep(
                workflow_id=workflow.id,
                step_number=i,
                step_name=step_def['name'],
                approver_role=step_def.get('role'),
                approver_user=step_def.get('user'),
                required_approvals=step_def.get('required_approvals', 1),
                status='pending' if i == 1 else 'waiting',
                due_date=datetime.now() + timedelta(days=step_def.get('due_days', 3))
            )
            db.add(step)
        
        db.commit()
        
        # Send initial notification
        WorkflowEngine._send_notification(db, workflow.id, 'workflow_created')
        
        return workflow.id
    
    @staticmethod
    def approve_step(db: Session, workflow_id: str, step_number: int, 
                    approver_id: str, comments: str = None) -> Dict:
        """Approve Step."""
        """Approve workflow step"""
        from app.models.workflow import WorkflowInstance, WorkflowStep, WorkflowApproval
        
        workflow = db.query(WorkflowInstance).filter(
            WorkflowInstance.id == workflow_id
        ).first()
        
        if not workflow:
            raise ValueError("Workflow not found")
        
        step = db.query(WorkflowStep).filter(
            and_(
                WorkflowStep.workflow_id == workflow_id,
                WorkflowStep.step_number == step_number
            )
        ).first()
        
        if not step:
            raise ValueError("Workflow step not found")
        
        if step.status != 'pending':
            raise ValueError("Step is not pending approval")
        
        # Check if user can approve
        if not WorkflowEngine._can_approve(db, step, approver_id):
            raise ValueError("User not authorized to approve this step")
        
        # Create approval record
        approval = WorkflowApproval(
            workflow_id=workflow_id,
            step_id=step.id,
            approver_id=approver_id,
            action='approved',
            comments=comments,
            approved_at=datetime.now()
        )
        db.add(approval)
        
        # Check if step is complete
        current_approvals = db.query(WorkflowApproval).filter(
            and_(
                WorkflowApproval.step_id == step.id,
                WorkflowApproval.action == 'approved'
            )
        ).count()
        
        if current_approvals >= step.required_approvals:
            step.status = 'approved'
            step.completed_at = datetime.now()
            
            # Move to next step or complete workflow
            if step_number < workflow.total_steps:
                workflow.current_step = step_number + 1
                next_step = db.query(WorkflowStep).filter(
                    and_(
                        WorkflowStep.workflow_id == workflow_id,
                        WorkflowStep.step_number == step_number + 1
                    )
                ).first()
                if next_step:
                    next_step.status = 'pending'
                    WorkflowEngine._send_notification(db, workflow_id, 'step_pending', next_step.id)
            else:
                workflow.status = 'approved'
                workflow.completed_at = datetime.now()
                WorkflowEngine._execute_final_action(db, workflow)
                WorkflowEngine._send_notification(db, workflow_id, 'workflow_approved')
        
        db.commit()
        
        return {
            'workflow_id': workflow_id,
            'step_number': step_number,
            'status': step.status,
            'workflow_status': workflow.status
        }
    
    @staticmethod
    def reject_step(db: Session, workflow_id: str, step_number: int, 
                   approver_id: str, comments: str) -> Dict:
        """Reject Step."""
        """Reject workflow step"""
        from app.models.workflow import WorkflowInstance, WorkflowStep, WorkflowApproval
        
        workflow = db.query(WorkflowInstance).filter(
            WorkflowInstance.id == workflow_id
        ).first()
        
        step = db.query(WorkflowStep).filter(
            and_(
                WorkflowStep.workflow_id == workflow_id,
                WorkflowStep.step_number == step_number
            )
        ).first()
        
        if not WorkflowEngine._can_approve(db, step, approver_id):
            raise ValueError("User not authorized to reject this step")
        
        # Create rejection record
        approval = WorkflowApproval(
            workflow_id=workflow_id,
            step_id=step.id,
            approver_id=approver_id,
            action='rejected',
            comments=comments,
            approved_at=datetime.now()
        )
        db.add(approval)
        
        # Reject workflow
        step.status = 'rejected'
        workflow.status = 'rejected'
        workflow.completed_at = datetime.now()
        
        db.commit()
        
        WorkflowEngine._send_notification(db, workflow_id, 'workflow_rejected')
        
        return {
            'workflow_id': workflow_id,
            'step_number': step_number,
            'status': 'rejected',
            'workflow_status': 'rejected'
        }
    
    @staticmethod
    def delegate_approval(db: Session, workflow_id: str, step_number: int, 
                         from_user: str, to_user: str, reason: str) -> Dict:
        """Delegate Approval."""
        """Delegate approval to another user"""
        from app.models.workflow import WorkflowStep, WorkflowDelegation
        
        step = db.query(WorkflowStep).filter(
            and_(
                WorkflowStep.workflow_id == workflow_id,
                WorkflowStep.step_number == step_number
            )
        ).first()
        
        if not step:
            raise ValueError("Workflow step not found")
        
        # Create delegation record
        delegation = WorkflowDelegation(
            workflow_id=workflow_id,
            step_id=step.id,
            from_user=from_user,
            to_user=to_user,
            reason=reason,
            delegated_at=datetime.now(),
            is_active=True
        )
        db.add(delegation)
        
        # Update step approver
        step.delegated_to = to_user
        
        db.commit()
        
        WorkflowEngine._send_notification(db, workflow_id, 'approval_delegated', step.id)
        
        return {
            'workflow_id': workflow_id,
            'step_number': step_number,
            'delegated_from': from_user,
            'delegated_to': to_user
        }
    
    @staticmethod
    def _get_workflow_definition(workflow_type: str, amount: float) -> Dict:
        definitions = {
            'journal_entry': {
                'steps': [
                    {'name': 'Supervisor Review', 'role': 'supervisor', 'due_days': 2},
                    {'name': 'Manager Approval', 'role': 'manager', 'due_days': 3} if amount > 10000 else None
                ]
            },
            'vendor_payment': {
                'steps': [
                    {'name': 'AP Review', 'role': 'ap_clerk', 'due_days': 1},
                    {'name': 'Manager Approval', 'role': 'manager', 'due_days': 2},
                    {'name': 'CFO Approval', 'role': 'cfo', 'due_days': 3} if amount > 50000 else None
                ]
            },
            'purchase_order': {
                'steps': [
                    {'name': 'Department Head', 'role': 'dept_head', 'due_days': 2},
                    {'name': 'Procurement Review', 'role': 'procurement', 'due_days': 3},
                    {'name': 'Executive Approval', 'role': 'executive', 'due_days': 5} if amount > 100000 else None
                ]
            }
        }
        
        definition = definitions.get(workflow_type, {'steps': []})
        definition['steps'] = [step for step in definition['steps'] if step is not None]
        
        return definition
    
    @staticmethod
    def _get_entity_type(workflow_type: str) -> str:
        mapping = {
            'journal_entry': 'JournalEntry',
            'vendor_payment': 'VendorPayment',
            'purchase_order': 'PurchaseOrder',
            'invoice': 'Invoice',
            'bill': 'Bill'
        }
        return mapping.get(workflow_type, 'Unknown')
    
    @staticmethod
    def _can_approve(db: Session, step, user_id: str) -> bool:
        # Check direct assignment
        if step.approver_user == user_id:
            return True
        
        # Check delegation
        if step.delegated_to == user_id:
            return True
        
        # Check role-based approval
        if step.approver_role:
            from app.models.user_enhanced import User
            user = db.query(User).filter(User.id == user_id).first()
            if user and hasattr(user, 'roles'):
                user_roles = [role.name for role in user.roles]
                return step.approver_role in user_roles
        
        return False
    
    @staticmethod
    def _execute_final_action(db: Session, workflow):
        if workflow.entity_type == 'JournalEntry':
            # Auto-post journal entry
            entry = db.query(JournalEntry).filter(JournalEntry.id == workflow.entity_id).first()
            if entry:
                entry.status = 'approved'
        
        elif workflow.entity_type == 'VendorPayment':
            # Process payment
            payment = db.query(VendorPayment).filter(VendorPayment.id == workflow.entity_id).first()
            if payment:
                payment.status = 'approved'
    
    @staticmethod
    def _send_notification(db: Session, workflow_id: str, notification_type: str, step_id: str = None):
        try:
            EmailNotificationService.send_workflow_notification(
                db, workflow_id, notification_type, step_id
            )
        except Exception as e:
            print(f"Failed to send notification: {e}")

class EmailNotificationService:
    """Email notification service for workflows"""
    
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USERNAME = "noreply@paksa.com"
    SMTP_PASSWORD = "your_app_password"
    
    @staticmethod
    def send_workflow_notification(db: Session, workflow_id: str, 
                                 notification_type: str, step_id: str = None):
        """Send Workflow Notification."""
        """Send workflow email notification"""
        from app.models.workflow import WorkflowInstance, WorkflowStep
        from app.models.user_enhanced import User
        
        workflow = db.query(WorkflowInstance).filter(
            WorkflowInstance.id == workflow_id
        ).first()
        
        if not workflow:
            return
        
        # Get recipients based on notification type
        recipients = EmailNotificationService._get_recipients(db, workflow, notification_type, step_id)
        
        # Generate email content
        subject, body = EmailNotificationService._generate_email_content(
            workflow, notification_type, step_id
        )
        
        # Send emails
        for recipient_email in recipients:
            EmailNotificationService._send_email(recipient_email, subject, body)
    
    @staticmethod
    def _get_recipients(db: Session, workflow, notification_type: str, step_id: str = None) -> List[str]:
        from app.models.workflow import WorkflowStep
        from app.models.user_enhanced import User
        
        recipients = []
        
        if notification_type == 'workflow_created':
            # Notify first approver
            first_step = db.query(WorkflowStep).filter(
                and_(
                    WorkflowStep.workflow_id == workflow.id,
                    WorkflowStep.step_number == 1
                )
            ).first()
            
            if first_step:
                if first_step.approver_user:
                    user = db.query(User).filter(User.id == first_step.approver_user).first()
                    if user:
                        recipients.append(user.email)
                elif first_step.approver_role:
                    # Get users with role
                    role_users = db.query(User).join(User.roles).filter(
                        User.roles.any(name=first_step.approver_role)
                    ).all()
                    recipients.extend([user.email for user in role_users])
        
        elif notification_type == 'step_pending' and step_id:
            step = db.query(WorkflowStep).filter(WorkflowStep.id == step_id).first()
            if step:
                if step.delegated_to:
                    user = db.query(User).filter(User.id == step.delegated_to).first()
                    if user:
                        recipients.append(user.email)
                elif step.approver_user:
                    user = db.query(User).filter(User.id == step.approver_user).first()
                    if user:
                        recipients.append(user.email)
        
        elif notification_type in ['workflow_approved', 'workflow_rejected']:
            # Notify creator
            creator = db.query(User).filter(User.id == workflow.created_by).first()
            if creator:
                recipients.append(creator.email)
        
        return recipients
    
    @staticmethod
    def _generate_email_content(workflow, notification_type: str, step_id: str = None) -> tuple:
        base_url = "http://localhost:3000"
        
        subjects = {
            'workflow_created': f"New {workflow.workflow_type} requires your approval",
            'step_pending': f"{workflow.workflow_type} approval required",
            'workflow_approved': f"Your {workflow.workflow_type} has been approved",
            'workflow_rejected': f"Your {workflow.workflow_type} has been rejected",
            'approval_delegated': f"{workflow.workflow_type} approval delegated to you"
        }
        
        bodies = {
            'workflow_created': f"""
A new {workflow.workflow_type} has been submitted and requires your approval.

Amount: ${workflow.amount:,.2f}
Created by: {workflow.created_by}
Created on: {workflow.created_at}

Please review and approve at: {base_url}/workflows/{workflow.id}
            """,
            'step_pending': f"""
A {workflow.workflow_type} is pending your approval.

Amount: ${workflow.amount:,.2f}
Current Step: {workflow.current_step} of {workflow.total_steps}

Please review at: {base_url}/workflows/{workflow.id}
            """,
            'workflow_approved': f"""
Your {workflow.workflow_type} has been fully approved and processed.

Amount: ${workflow.amount:,.2f}
Approved on: {workflow.completed_at}

View details at: {base_url}/workflows/{workflow.id}
            """,
            'workflow_rejected': f"""
Your {workflow.workflow_type} has been rejected.

Amount: ${workflow.amount:,.2f}
Rejected on: {workflow.completed_at}

View details at: {base_url}/workflows/{workflow.id}
            """
        }
        
        subject = subjects.get(notification_type, "Workflow Notification")
        body = bodies.get(notification_type, "Please check your workflow dashboard.")
        
        return subject, body
    
    @staticmethod
    def _send_email(to_email: str, subject: str, body: str):
        try:
            msg = MimeMultipart()
            msg['From'] = EmailNotificationService.SMTP_USERNAME
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(EmailNotificationService.SMTP_SERVER, EmailNotificationService.SMTP_PORT)
            server.starttls()
            server.login(EmailNotificationService.SMTP_USERNAME, EmailNotificationService.SMTP_PASSWORD)
            
            text = msg.as_string()
            server.sendmail(EmailNotificationService.SMTP_USERNAME, to_email, text)
            server.quit()
            
            print(f"Email sent to {to_email}")
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")

class ApprovalHierarchy:
    """Approval hierarchy management"""
    
    @staticmethod
    def get_approval_chain(db: Session, workflow_type: str, amount: float, 
                          department: str = None) -> List[Dict]:
        """Get Approval Chain."""
        """Get approval chain for workflow"""
        chain = []
        
        # Basic approval levels based on amount
        if amount <= 1000:
            chain.append({'role': 'supervisor', 'level': 1})
        elif amount <= 10000:
            chain.extend([
                {'role': 'supervisor', 'level': 1},
                {'role': 'manager', 'level': 2}
            ])
        elif amount <= 50000:
            chain.extend([
                {'role': 'supervisor', 'level': 1},
                {'role': 'manager', 'level': 2},
                {'role': 'director', 'level': 3}
            ])
        else:
            chain.extend([
                {'role': 'supervisor', 'level': 1},
                {'role': 'manager', 'level': 2},
                {'role': 'director', 'level': 3},
                {'role': 'cfo', 'level': 4}
            ])
        
        # Add workflow-specific requirements
        if workflow_type == 'vendor_payment' and amount > 100000:
            chain.append({'role': 'ceo', 'level': 5})
        
        return chain
    
    @staticmethod
    def get_next_approver(db: Session, workflow_id: str) -> Optional[Dict]:
        from app.models.workflow import WorkflowInstance, WorkflowStep
        
        workflow = db.query(WorkflowInstance).filter(
            WorkflowInstance.id == workflow_id
        ).first()
        
        if not workflow:
            return None
        
        next_step = db.query(WorkflowStep).filter(
            and_(
                WorkflowStep.workflow_id == workflow_id,
                WorkflowStep.step_number == workflow.current_step,
                WorkflowStep.status == 'pending'
            )
        ).first()
        
        if next_step:
            return {
                'step_id': next_step.id,
                'step_number': next_step.step_number,
                'approver_role': next_step.approver_role,
                'approver_user': next_step.approver_user,
                'due_date': next_step.due_date
            }
        
        return None

class WorkflowDashboard:
    """Workflow dashboard and reporting"""
    
    @staticmethod
    def get_pending_approvals(db: Session, user_id: str) -> List[Dict]:
        from app.models.workflow import WorkflowInstance, WorkflowStep
        
        # Direct assignments
        direct_steps = db.query(WorkflowStep).join(WorkflowInstance).filter(
            and_(
                WorkflowStep.approver_user == user_id,
                WorkflowStep.status == 'pending'
            )
        ).all()
        
        # Delegated assignments
        delegated_steps = db.query(WorkflowStep).join(WorkflowInstance).filter(
            and_(
                WorkflowStep.delegated_to == user_id,
                WorkflowStep.status == 'pending'
            )
        ).all()
        
        all_steps = direct_steps + delegated_steps
        
        pending = []
        for step in all_steps:
            pending.append({
                'workflow_id': step.workflow_id,
                'step_id': step.id,
                'workflow_type': step.workflow.workflow_type,
                'amount': step.workflow.amount,
                'created_by': step.workflow.created_by,
                'created_at': step.workflow.created_at,
                'due_date': step.due_date,
                'step_name': step.step_name,
                'is_delegated': step.delegated_to == user_id
            })
        
        return sorted(pending, key=lambda x: x['due_date'])
    
    @staticmethod
    def get_workflow_history(db: Session, user_id: str, limit: int = 50) -> List[Dict]:
        from app.models.workflow import WorkflowInstance, WorkflowApproval
        
        # Workflows created by user
        created_workflows = db.query(WorkflowInstance).filter(
            WorkflowInstance.created_by == user_id
        ).order_by(WorkflowInstance.created_at.desc()).limit(limit).all()
        
        # Workflows approved by user
        approved_workflows = db.query(WorkflowInstance).join(WorkflowApproval).filter(
            WorkflowApproval.approver_id == user_id
        ).order_by(WorkflowInstance.created_at.desc()).limit(limit).all()
        
        all_workflows = list(set(created_workflows + approved_workflows))
        
        history = []
        for workflow in all_workflows:
            history.append({
                'workflow_id': workflow.id,
                'workflow_type': workflow.workflow_type,
                'amount': workflow.amount,
                'status': workflow.status,
                'created_at': workflow.created_at,
                'completed_at': workflow.completed_at,
                'current_step': workflow.current_step,
                'total_steps': workflow.total_steps
            })
        
        return sorted(history, key=lambda x: x['created_at'], reverse=True)
    
    @staticmethod
    def get_workflow_metrics(db: Session, start_date: datetime, end_date: datetime) -> Dict:
        from app.models.workflow import WorkflowInstance
        
        total_workflows = db.query(WorkflowInstance).filter(
            and_(
                WorkflowInstance.created_at >= start_date,
                WorkflowInstance.created_at <= end_date
            )
        ).count()
        
        approved_workflows = db.query(WorkflowInstance).filter(
            and_(
                WorkflowInstance.created_at >= start_date,
                WorkflowInstance.created_at <= end_date,
                WorkflowInstance.status == 'approved'
            )
        ).count()
        
        rejected_workflows = db.query(WorkflowInstance).filter(
            and_(
                WorkflowInstance.created_at >= start_date,
                WorkflowInstance.created_at <= end_date,
                WorkflowInstance.status == 'rejected'
            )
        ).count()
        
        pending_workflows = db.query(WorkflowInstance).filter(
            and_(
                WorkflowInstance.created_at >= start_date,
                WorkflowInstance.created_at <= end_date,
                WorkflowInstance.status == 'pending'
            )
        ).count()
        
        return {
            'total_workflows': total_workflows,
            'approved_workflows': approved_workflows,
            'rejected_workflows': rejected_workflows,
            'pending_workflows': pending_workflows,
            'approval_rate': (approved_workflows / total_workflows * 100) if total_workflows > 0 else 0,
            'rejection_rate': (rejected_workflows / total_workflows * 100) if total_workflows > 0 else 0
        }