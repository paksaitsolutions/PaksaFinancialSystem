"""
Scheduled Reports Service

This service provides background job system for generating and distributing
reports on a scheduled basis.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import asyncio

from .reporting_engine import ReportingEngine, ReportType, ReportFormat
from celery import Celery
from croniter import croniter
from dataclasses import dataclass, asdict
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
import smtplib

from app.core.config import settings
from app.models.company import Company
from app.models.user import User





class ScheduleFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class ReportStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledReportConfig:
    """Configuration for a scheduled report."""
    id: str
    company_id: UUID
    report_type: ReportType
    report_name: str
    parameters: Dict[str, Any]
    format: ReportFormat
    frequency: ScheduleFrequency
    cron_expression: Optional[str]
    recipients: List[str]
    is_active: bool
    created_by: UUID
    created_at: datetime
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


@dataclass
class ReportExecution:
    """Record of a report execution."""
    id: str
    scheduled_report_id: str
    status: ReportStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None


# Initialize Celery for background tasks
celery_app = Celery(
    'scheduled_reports',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)


class ScheduledReportsService:
    """Service for managing scheduled reports."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.scheduled_reports: Dict[str, ScheduledReportConfig] = {}
        self.executions: Dict[str, ReportExecution] = {}

    async def create_scheduled_report(
        self,
        company_id: UUID,
        report_type: ReportType,
        report_name: str,
        parameters: Dict[str, Any],
        format: ReportFormat,
        frequency: ScheduleFrequency,
        recipients: List[str],
        created_by: UUID,
        cron_expression: Optional[str] = None
    ) -> ScheduledReportConfig:
        """Create Scheduled Report."""
        """Create a new scheduled report."""
        
        report_id = str(uuid4())
        
        # Generate cron expression if not provided
        if not cron_expression:
            cron_expression = self._generate_cron_expression(frequency)
        
        # Calculate next run time
        next_run = self._calculate_next_run(cron_expression)
        
        config = ScheduledReportConfig(
            id=report_id,
            company_id=company_id,
            report_type=report_type,
            report_name=report_name,
            parameters=parameters,
            format=format,
            frequency=frequency,
            cron_expression=cron_expression,
            recipients=recipients,
            is_active=True,
            created_by=created_by,
            created_at=datetime.now(),
            next_run=next_run
        )
        
        self.scheduled_reports[report_id] = config
        
        # Schedule the task
        await self._schedule_report_task(config)
        
        return config

    async def update_scheduled_report(
        self,
        report_id: str,
        updates: Dict[str, Any]
    ) -> Optional[ScheduledReportConfig]:
        """Update Scheduled Report."""
        """Update an existing scheduled report."""
        
        if report_id not in self.scheduled_reports:
            return None
        
        config = self.scheduled_reports[report_id]
        
        # Update fields
        for field, value in updates.items():
            if hasattr(config, field):
                setattr(config, field, value)
        
        # Recalculate next run if cron expression changed
        if 'cron_expression' in updates or 'frequency' in updates:
            if not config.cron_expression:
                config.cron_expression = self._generate_cron_expression(config.frequency)
            config.next_run = self._calculate_next_run(config.cron_expression)
        
        # Reschedule the task
        await self._schedule_report_task(config)
        
        return config

    async def delete_scheduled_report(self, report_id: str) -> bool:
        
        if report_id not in self.scheduled_reports:
            return False
        
        # Cancel any pending tasks
        await self._cancel_report_task(report_id)
        
        # Remove from memory
        del self.scheduled_reports[report_id]
        
        return True

    async def get_scheduled_report(self, report_id: str) -> Optional[ScheduledReportConfig]:
        return self.scheduled_reports.get(report_id)

    async def list_scheduled_reports(
        self,
        company_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> List[ScheduledReportConfig]:
        """List Scheduled Reports."""
        """List scheduled reports with optional filters."""
        
        reports = list(self.scheduled_reports.values())
        
        if company_id:
            reports = [r for r in reports if r.company_id == company_id]
        
        if is_active is not None:
            reports = [r for r in reports if r.is_active == is_active]
        
        return reports

    async def execute_scheduled_report(self, report_id: str) -> ReportExecution:
        
        config = self.scheduled_reports.get(report_id)
        if not config:
            raise ValueError(f"Scheduled report {report_id} not found")
        
        execution_id = str(uuid4())
        execution = ReportExecution(
            id=execution_id,
            scheduled_report_id=report_id,
            status=ReportStatus.RUNNING,
            started_at=datetime.now()
        )
        
        self.executions[execution_id] = execution
        
        try:
            # Generate the report
            reporting_engine = ReportingEngine(self.db, config.company_id)
            report_result = await reporting_engine.generate_report(
                config.report_type,
                config.parameters,
                config.format
            )
            
            if 'error' in report_result:
                execution.status = ReportStatus.FAILED
                execution.error_message = report_result['error']
            else:
                # Save report file
                file_path = await self._save_report_file(report_result, config)
                execution.file_path = file_path
                execution.file_size = len(str(report_result['data']))
                
                # Send to recipients
                await self._send_report_email(config, report_result, file_path)
                
                execution.status = ReportStatus.COMPLETED
                
                # Update last run time
                config.last_run = datetime.now()
                config.next_run = self._calculate_next_run(config.cron_expression)
            
        except Exception as e:
            execution.status = ReportStatus.FAILED
            execution.error_message = str(e)
        
        execution.completed_at = datetime.now()
        return execution

    async def get_execution_history(
        self,
        report_id: Optional[str] = None,
        limit: int = 50
    ) -> List[ReportExecution]:
        """Get Execution History."""
        """Get execution history for scheduled reports."""
        
        executions = list(self.executions.values())
        
        if report_id:
            executions = [e for e in executions if e.scheduled_report_id == report_id]
        
        # Sort by started_at descending
        executions.sort(key=lambda x: x.started_at, reverse=True)
        
        return executions[:limit]

    def _generate_cron_expression(self, frequency: ScheduleFrequency) -> str:
        
        expressions = {
            ScheduleFrequency.DAILY: "0 9 * * *",  # 9 AM daily
            ScheduleFrequency.WEEKLY: "0 9 * * 1",  # 9 AM every Monday
            ScheduleFrequency.MONTHLY: "0 9 1 * *",  # 9 AM on 1st of month
            ScheduleFrequency.QUARTERLY: "0 9 1 1,4,7,10 *",  # 9 AM on 1st of quarter
            ScheduleFrequency.YEARLY: "0 9 1 1 *"  # 9 AM on January 1st
        }
        
        return expressions.get(frequency, "0 9 * * *")

    def _calculate_next_run(self, cron_expression: str) -> datetime:
        
        cron = croniter(cron_expression, datetime.now())
        return cron.get_next(datetime)

    async def _schedule_report_task(self, config: ScheduledReportConfig) -> None:
        
        if not config.is_active or not config.next_run:
            return
        
        # Schedule the task to run at the specified time
        celery_app.send_task(
            'scheduled_reports.execute_report',
            args=[config.id],
            eta=config.next_run
        )

    async def _cancel_report_task(self, report_id: str) -> None:
        
        # This would cancel the Celery task
        # Implementation depends on your Celery setup
        pass

    async def _save_report_file(
        self,
        report_result: Dict[str, Any],
        config: ScheduledReportConfig
    ) -> str:
        """Save Report File."""
        """Save report to file system."""
        
        import os
        
        # Create reports directory if it doesn't exist
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{config.report_name}_{timestamp}.{config.format.value}"
        file_path = os.path.join(reports_dir, filename)
        
        # Save based on format
        if config.format == ReportFormat.JSON:
            import json
            with open(file_path, 'w') as f:
                json.dump(report_result['data'], f, indent=2, default=str)
        elif config.format == ReportFormat.CSV:
            with open(file_path, 'w') as f:
                f.write(report_result['data'])
        elif config.format == ReportFormat.EXCEL:
            with open(file_path, 'wb') as f:
                f.write(report_result['data'])
        
        return file_path

    async def _send_report_email(
        self,
        config: ScheduledReportConfig,
        report_result: Dict[str, Any],
        file_path: str
    ) -> None:
        """Send Report Email."""
        """Send report via email to recipients."""
        
        # Get company info
        company_query = select(Company).where(Company.id == config.company_id)
        company_result = await self.db.execute(company_query)
        company = company_result.scalar_one_or_none()
        
        if not company:
            return
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['Subject'] = f"Scheduled Report: {config.report_name}"
        
        # Email body
        body = f"""
        Dear Recipient,
        
        Please find attached the scheduled report "{config.report_name}" for {company.name}.
        
        Report Details:
        - Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        - Type: {config.report_type.value}
        - Format: {config.format.value}
        
        Best regards,
        Paksa Financial System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach report file
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(file_path)}'
                )
                msg.attach(part)
        
        # Send email to each recipient
        try:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            
            for recipient in config.recipients:
                msg['To'] = recipient
                server.send_message(msg)
                del msg['To']
            
            server.quit()
            
        except Exception as e:
            print(f"Failed to send email: {e}")


# Celery task for executing scheduled reports
@celery_app.task(name='scheduled_reports.execute_report')
def execute_report_task(report_id: str):
    
    # This would need to be implemented with proper async handling
    # and database session management for Celery
    pass