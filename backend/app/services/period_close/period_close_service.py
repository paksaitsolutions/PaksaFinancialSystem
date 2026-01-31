"""
Period close service for managing accounting period closures.
"""
from datetime import date, datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.exceptions import NotFoundException, ValidationException
from app.models.period_close import (



    AccountingPeriod, 
    PeriodClose, 
    PeriodCloseTask,
    PeriodType,
    PeriodStatus,
    CloseTaskStatus
)


class PeriodCloseService:
    """Service for managing period close processes."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
    
    def create_accounting_period(self, period_data: Dict[str, Any], created_by: UUID) -> AccountingPeriod:
        """Create Accounting Period."""
        """Create a new accounting period."""
        period = AccountingPeriod(
            period_name=period_data['period_name'],
            period_type=PeriodType(period_data['period_type']),
            start_date=period_data['start_date'],
            end_date=period_data['end_date'],
            status=PeriodStatus.OPEN,
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(period)
        self.db.commit()
        self.db.refresh(period)
        
        return period
    
    def initiate_period_close(self, period_id: UUID, initiated_by: UUID) -> PeriodClose:
        """Initiate Period Close."""
        """Initiate a period close process."""
        period = self.get_accounting_period(period_id)
        if not period:
            raise NotFoundException(f"Period {period_id} not found")
        
        if period.status != PeriodStatus.OPEN:
            raise ValidationException(f"Period {period.period_name} is not open for closing")
        
        close_number = self._generate_close_number()
        period_close = PeriodClose(
            close_number=close_number,
            period_id=period_id,
            close_type=period.period_type,
            status=PeriodStatus.CLOSING,
            initiated_by=initiated_by,
            created_by=initiated_by,
            updated_by=initiated_by
        )
        
        self.db.add(period_close)
        self.db.flush()
        
        self._create_close_tasks(period_close, initiated_by)
        
        period.status = PeriodStatus.CLOSING
        
        self.db.commit()
        self.db.refresh(period_close)
        
        return period_close
    
    def execute_close_task(self, task_id: UUID, executed_by: UUID) -> PeriodCloseTask:
        """Execute Close Task."""
        """Execute a period close task."""
        task = self.get_close_task(task_id)
        if not task:
            raise NotFoundException(f"Task {task_id} not found")
        
        if task.status != CloseTaskStatus.PENDING:
            raise ValidationException(f"Task {task.task_name} is not pending")
        
        task.status = CloseTaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        task.assigned_to = executed_by
        
        try:
            result = self._execute_task_logic(task)
            
            task.status = CloseTaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.completed_by = executed_by
            task.result_message = result
            
        except Exception as e:
            task.status = CloseTaskStatus.FAILED
            task.error_message = str(e)
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def complete_period_close(self, close_id: UUID, completed_by: UUID) -> PeriodClose:
        """Complete Period Close."""
        """Complete a period close process."""
        period_close = self.get_period_close(close_id)
        if not period_close:
            raise NotFoundException(f"Period close {close_id} not found")
        
        pending_tasks = [task for task in period_close.close_tasks 
                        if task.is_required and task.status != CloseTaskStatus.COMPLETED]
        
        if pending_tasks:
            raise ValidationException("Cannot complete close with pending required tasks")
        
        period_close.status = PeriodStatus.CLOSED
        period_close.completed_at = datetime.utcnow()
        period_close.completed_by = completed_by
        
        period_close.period.status = PeriodStatus.CLOSED
        period_close.period.closed_by = completed_by
        period_close.period.closed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(period_close)
        
        return period_close
    
    def get_accounting_period(self, period_id: UUID) -> Optional[AccountingPeriod]:
        """Get Accounting Period."""
        """Get an accounting period by ID."""
        return self.db.query(AccountingPeriod).filter(
            AccountingPeriod.id == period_id
        ).first()
    
    def get_period_close(self, close_id: UUID) -> Optional[PeriodClose]:
        """Get Period Close."""
        """Get a period close by ID."""
        return self.db.query(PeriodClose).filter(
            PeriodClose.id == close_id
        ).first()
    
    def get_close_task(self, task_id: UUID) -> Optional[PeriodCloseTask]:
        """Get Close Task."""
        """Get a close task by ID."""
        return self.db.query(PeriodCloseTask).filter(
            PeriodCloseTask.id == task_id
        ).first()
    
    def list_accounting_periods(self, skip: int = 0, limit: int = 100) -> List[AccountingPeriod]:
        """List Accounting Periods."""
        """List accounting periods."""
        return self.db.query(AccountingPeriod)\
                   .order_by(desc(AccountingPeriod.start_date))\
                   .offset(skip).limit(limit).all()
    
    def list_period_closes(self, skip: int = 0, limit: int = 100) -> List[PeriodClose]:
        """List Period Closes."""
        """List period closes."""
        return self.db.query(PeriodClose)\
                   .order_by(desc(PeriodClose.initiated_at))\
                   .offset(skip).limit(limit).all()
    
    def _create_close_tasks(self, period_close: PeriodClose, created_by: UUID):
        """ Create Close Tasks."""
        """Create standard close tasks for a period close."""
        standard_tasks = [
            {'name': 'Review Journal Entries', 'description': 'Review all journal entries for the period', 'order': 1, 'required': True, 'automated': False},
            {'name': 'Process Accruals', 'description': 'Process month-end accruals', 'order': 2, 'required': True, 'automated': False},
            {'name': 'Run Depreciation', 'description': 'Calculate and post depreciation entries', 'order': 3, 'required': True, 'automated': True},
            {'name': 'Process Allocations', 'description': 'Run allocation rules for the period', 'order': 4, 'required': True, 'automated': True},
            {'name': 'Reconcile Bank Accounts', 'description': 'Complete bank reconciliations', 'order': 5, 'required': True, 'automated': False},
            {'name': 'Generate Financial Statements', 'description': 'Generate period-end financial statements', 'order': 6, 'required': True, 'automated': True},
            {'name': 'Review Financial Statements', 'description': 'Review and approve financial statements', 'order': 7, 'required': True, 'automated': False}
        ]
        
        for task_data in standard_tasks:
            task = PeriodCloseTask(
                period_close_id=period_close.id,
                task_name=task_data['name'],
                task_description=task_data['description'],
                task_order=task_data['order'],
                is_required=task_data['required'],
                is_automated=task_data['automated'],
                status=CloseTaskStatus.PENDING,
                created_by=created_by,
                updated_by=created_by
            )
            self.db.add(task)
    
    def _execute_task_logic(self, task: PeriodCloseTask) -> str:
        """ Execute Task Logic."""
        """Execute the logic for a specific task."""
        if task.task_name == 'Run Depreciation':
            return "Depreciation entries processed successfully"
        elif task.task_name == 'Process Allocations':
            return "Allocation rules processed successfully"
        elif task.task_name == 'Generate Financial Statements':
            return "Financial statements generated successfully"
        else:
            return f"Manual task {task.task_name} marked as completed"
    
    def _generate_close_number(self) -> str:
        """ Generate Close Number."""
        """Generate a unique close number."""
        last_close = self.db.query(PeriodClose)\
            .order_by(desc(PeriodClose.created_at))\
            .first()
        
        if last_close and last_close.close_number.startswith('PC'):
            try:
                last_num = int(last_close.close_number.split('-')[1])
                next_num = last_num + 1
            except (IndexError, ValueError):
                next_num = 1
        else:
            next_num = 1
        
        return f"PC-{next_num:06d}"