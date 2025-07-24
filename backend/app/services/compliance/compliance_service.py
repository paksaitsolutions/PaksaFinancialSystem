"""
Compliance reporting service.
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.compliance import ComplianceReport, CompliancePolicy, ComplianceReportType, ComplianceReportStatus
from app.models.audit import AuditLog
from app.models.user import User
from app.models.session import UserSession
from app.services.audit.audit_service import AuditService


class ComplianceService:
    """Service for generating compliance reports."""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
    
    def generate_report(
        self,
        report_type: str,
        start_date: datetime,
        end_date: datetime,
        requested_by: UUID,
        filters: Optional[Dict] = None,
        description: Optional[str] = None
    ) -> ComplianceReport:
        """Generate a compliance report."""
        report_number = self._generate_report_number(report_type)
        
        report = ComplianceReport(
            report_name=self._get_report_name(report_type),
            report_type=report_type,
            report_number=report_number,
            start_date=start_date,
            end_date=end_date,
            filters=filters or {},
            status=ComplianceReportStatus.GENERATING,
            requested_by=requested_by,
            description=description,
            created_by=requested_by,
            updated_by=requested_by
        )
        
        self.db.add(report)
        self.db.flush()
        
        try:
            # Generate report data based on type
            report_data = self._generate_report_data(report_type, start_date, end_date, filters)
            
            report.report_data = report_data
            report.status = ComplianceReportStatus.COMPLETED
            report.generated_at = datetime.utcnow()
            
        except Exception as e:
            report.status = ComplianceReportStatus.FAILED
            report.report_data = {"error": str(e)}
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def get_report(self, report_id: UUID) -> Optional[ComplianceReport]:
        """Get a compliance report by ID."""
        return self.db.query(ComplianceReport).filter(
            ComplianceReport.id == report_id
        ).first()
    
    def list_reports(
        self,
        report_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ComplianceReport]:
        """List compliance reports with filters."""
        query = self.db.query(ComplianceReport)
        
        if report_type:
            query = query.filter(ComplianceReport.report_type == report_type)
        
        if status:
            query = query.filter(ComplianceReport.status == status)
        
        return query.order_by(desc(ComplianceReport.created_at))\
                   .offset(skip).limit(limit).all()
    
    def create_policy(self, policy_data: Dict[str, Any], created_by: UUID) -> CompliancePolicy:
        """Create a compliance policy."""
        policy = CompliancePolicy(
            policy_name=policy_data['policy_name'],
            policy_code=policy_data['policy_code'],
            description=policy_data.get('description'),
            requirements=policy_data.get('requirements'),
            compliance_framework=policy_data.get('compliance_framework'),
            effective_date=policy_data['effective_date'],
            review_date=policy_data.get('review_date'),
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    def list_policies(self, active_only: bool = True) -> List[CompliancePolicy]:
        """List compliance policies."""
        query = self.db.query(CompliancePolicy)
        
        if active_only:
            query = query.filter(CompliancePolicy.is_active == True)
        
        return query.order_by(CompliancePolicy.policy_name).all()
    
    def _generate_report_data(
        self,
        report_type: str,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate report data based on report type."""
        if report_type == ComplianceReportType.AUDIT_TRAIL:
            return self._generate_audit_trail_report(start_date, end_date, filters)
        elif report_type == ComplianceReportType.ACCESS_CONTROL:
            return self._generate_access_control_report(start_date, end_date, filters)
        elif report_type == ComplianceReportType.USER_ACTIVITY:
            return self._generate_user_activity_report(start_date, end_date, filters)
        elif report_type == ComplianceReportType.SECURITY_ASSESSMENT:
            return self._generate_security_assessment_report(start_date, end_date, filters)
        elif report_type == ComplianceReportType.SOX_COMPLIANCE:
            return self._generate_sox_compliance_report(start_date, end_date, filters)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
    
    def _generate_audit_trail_report(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate audit trail compliance report."""
        logs = self.audit_service.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        # Analyze audit logs
        total_actions = len(logs)
        unique_users = len(set(log.user_id for log in logs if log.user_id))
        
        actions_by_type = {}
        actions_by_user = {}
        
        for log in logs:
            # Count by action type
            actions_by_type[log.action] = actions_by_type.get(log.action, 0) + 1
            
            # Count by user
            if log.user_id:
                actions_by_user[str(log.user_id)] = actions_by_user.get(str(log.user_id), 0) + 1
        
        return {
            "report_type": "Audit Trail Compliance Report",
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_actions": total_actions,
                "unique_users": unique_users,
                "actions_by_type": actions_by_type,
                "top_users": dict(sorted(actions_by_user.items(), key=lambda x: x[1], reverse=True)[:10])
            },
            "audit_logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "user_id": str(log.user_id) if log.user_id else None,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "ip_address": log.ip_address,
                    "description": log.description
                }
                for log in logs[:1000]  # Limit to first 1000 for report size
            ]
        }
    
    def _generate_access_control_report(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate access control compliance report."""
        # Get user sessions in period
        sessions = self.db.query(UserSession).filter(
            and_(
                UserSession.created_at >= start_date,
                UserSession.created_at <= end_date
            )
        ).all()
        
        # Get login attempts
        login_logs = self.audit_service.get_audit_logs(
            action="login",
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        # Analyze access patterns
        unique_users = len(set(session.user_id for session in sessions))
        total_sessions = len(sessions)
        failed_logins = len([log for log in login_logs if "failed" in (log.description or "").lower()])
        
        return {
            "report_type": "Access Control Compliance Report",
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "unique_users": unique_users,
                "total_sessions": total_sessions,
                "failed_logins": failed_logins,
                "success_rate": ((len(login_logs) - failed_logins) / max(len(login_logs), 1)) * 100
            },
            "sessions": [
                {
                    "user_id": str(session.user_id),
                    "created_at": session.created_at.isoformat(),
                    "ip_address": session.ip_address,
                    "status": session.status,
                    "duration_minutes": (session.last_activity - session.created_at).total_seconds() / 60
                }
                for session in sessions[:500]
            ]
        }
    
    def _generate_user_activity_report(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate user activity compliance report."""
        # Get all users
        users = self.db.query(User).all()
        
        user_activities = []
        for user in users:
            activity_logs = self.audit_service.get_user_activity(
                user.id,
                days=(end_date - start_date).days
            )
            
            # Filter logs by date range
            filtered_logs = [
                log for log in activity_logs
                if start_date <= log.timestamp <= end_date
            ]
            
            if filtered_logs:
                user_activities.append({
                    "user_id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "total_actions": len(filtered_logs),
                    "last_activity": max(log.timestamp for log in filtered_logs).isoformat(),
                    "actions_by_type": {
                        action: len([log for log in filtered_logs if log.action == action])
                        for action in set(log.action for log in filtered_logs)
                    }
                })
        
        return {
            "report_type": "User Activity Compliance Report",
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_users": len(users),
                "active_users": len(user_activities),
                "inactive_users": len(users) - len(user_activities)
            },
            "user_activities": user_activities
        }
    
    def _generate_security_assessment_report(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate security assessment compliance report."""
        # Get security-related audit logs
        security_logs = self.audit_service.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        # Filter for security events
        security_events = [
            log for log in security_logs
            if log.action in ["login", "logout", "create", "update", "delete"]
            or "password" in (log.description or "").lower()
            or "security" in (log.description or "").lower()
        ]
        
        # Analyze security metrics
        failed_attempts = len([log for log in security_events if "failed" in (log.description or "").lower()])
        password_changes = len([log for log in security_events if "password" in (log.description or "").lower()])
        
        return {
            "report_type": "Security Assessment Compliance Report",
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_security_events": len(security_events),
                "failed_attempts": failed_attempts,
                "password_changes": password_changes,
                "unique_ip_addresses": len(set(log.ip_address for log in security_events if log.ip_address))
            },
            "security_events": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "action": log.action,
                    "user_id": str(log.user_id) if log.user_id else None,
                    "ip_address": log.ip_address,
                    "description": log.description
                }
                for log in security_events[:500]
            ]
        }
    
    def _generate_sox_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate SOX compliance report."""
        # Get financial-related audit logs
        financial_logs = self.audit_service.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        # Filter for financial operations
        financial_events = [
            log for log in financial_logs
            if log.resource_type in ["journal_entries", "invoices", "payments", "financial_statements"]
        ]
        
        return {
            "report_type": "SOX Compliance Report",
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_financial_events": len(financial_events),
                "journal_entries": len([log for log in financial_events if log.resource_type == "journal_entries"]),
                "invoice_operations": len([log for log in financial_events if log.resource_type == "invoices"]),
                "payment_operations": len([log for log in financial_events if log.resource_type == "payments"])
            },
            "financial_events": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "user_id": str(log.user_id) if log.user_id else None,
                    "description": log.description
                }
                for log in financial_events[:500]
            ]
        }
    
    def _get_report_name(self, report_type: str) -> str:
        """Get human-readable report name."""
        names = {
            ComplianceReportType.AUDIT_TRAIL: "Audit Trail Compliance Report",
            ComplianceReportType.ACCESS_CONTROL: "Access Control Compliance Report",
            ComplianceReportType.USER_ACTIVITY: "User Activity Compliance Report",
            ComplianceReportType.SECURITY_ASSESSMENT: "Security Assessment Report",
            ComplianceReportType.SOX_COMPLIANCE: "SOX Compliance Report"
        }
        return names.get(report_type, f"Compliance Report - {report_type}")
    
    def _generate_report_number(self, report_type: str) -> str:
        """Generate unique report number."""
        prefix = report_type.upper()[:3]
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{prefix}-{timestamp}"