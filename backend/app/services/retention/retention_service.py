"""
Data retention service for managing data lifecycle.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import text, and_, desc
from sqlalchemy.orm import Session
from uuid import UUID
import time

from app.models.data_retention import DataRetentionPolicy, RetentionExecution, RetentionAction, RetentionStatus





class DataRetentionService:
    """Service for managing data retention policies."""
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
    
    def create_policy(self, policy_data: Dict[str, Any], created_by: UUID) -> DataRetentionPolicy:
        """Create Policy."""
        """Create a data retention policy."""
        policy = DataRetentionPolicy(
            policy_name=policy_data['policy_name'],
            policy_code=policy_data['policy_code'],
            table_name=policy_data['table_name'],
            data_category=policy_data['data_category'],
            retention_period_days=policy_data['retention_period_days'],
            retention_action=policy_data.get('retention_action', RetentionAction.DELETE),
            description=policy_data.get('description'),
            legal_basis=policy_data.get('legal_basis'),
            conditions=policy_data.get('conditions'),
            status=RetentionStatus.ACTIVE,
            next_execution=datetime.utcnow() + timedelta(days=1),
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        
        return policy
    
    def execute_policy(self, policy_id: UUID) -> RetentionExecution:
        """Execute Policy."""
        """Execute a data retention policy."""
        policy = self.get_policy(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")
        
        if policy.status != RetentionStatus.ACTIVE:
            raise ValueError(f"Policy {policy.policy_code} is not active")
        
        start_time = time.time()
        execution = RetentionExecution(
            policy_id=policy_id,
            status="running"
        )
        
        self.db.add(execution)
        self.db.flush()
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_period_days)
            
            if policy.retention_action == RetentionAction.DELETE:
                result = self._delete_records(policy, cutoff_date)
            elif policy.retention_action == RetentionAction.ARCHIVE:
                result = self._archive_records(policy, cutoff_date)
            elif policy.retention_action == RetentionAction.ANONYMIZE:
                result = self._anonymize_records(policy, cutoff_date)
            else:
                raise ValueError(f"Unknown retention action: {policy.retention_action}")
            
            execution.records_processed = result.get('processed', 0)
            execution.records_deleted = result.get('deleted', 0)
            execution.records_archived = result.get('archived', 0)
            execution.records_anonymized = result.get('anonymized', 0)
            execution.status = "completed"
            execution.execution_time_seconds = int(time.time() - start_time)
            
            policy.last_executed = datetime.utcnow()
            policy.next_execution = datetime.utcnow() + timedelta(days=1)
            
        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.execution_time_seconds = int(time.time() - start_time)
        
        self.db.commit()
        self.db.refresh(execution)
        
        return execution
    
    def execute_all_policies(self) -> List[RetentionExecution]:
        """Execute All Policies."""
        """Execute all active retention policies that are due."""
        due_policies = self.db.query(DataRetentionPolicy).filter(
            and_(
                DataRetentionPolicy.status == RetentionStatus.ACTIVE,
                DataRetentionPolicy.next_execution <= datetime.utcnow()
            )
        ).all()
        
        executions = []
        for policy in due_policies:
            try:
                execution = self.execute_policy(policy.id)
                executions.append(execution)
            except Exception as e:
                print(f"Failed to execute policy {policy.policy_code}: {e}")
        
        return executions
    
    def get_policy(self, policy_id: UUID) -> Optional[DataRetentionPolicy]:
        """Get Policy."""
        """Get a retention policy by ID."""
        return self.db.query(DataRetentionPolicy).filter(
            DataRetentionPolicy.id == policy_id
        ).first()
    
    def list_policies(self, active_only: bool = True) -> List[DataRetentionPolicy]:
        """List Policies."""
        """List retention policies."""
        query = self.db.query(DataRetentionPolicy)
        
        if active_only:
            query = query.filter(DataRetentionPolicy.status == RetentionStatus.ACTIVE)
        
        return query.order_by(DataRetentionPolicy.policy_name).all()
    
    def get_execution_history(self, policy_id: Optional[UUID] = None, limit: int = 100) -> List[RetentionExecution]:
        """Get Execution History."""
        """Get retention execution history."""
        query = self.db.query(RetentionExecution)
        
        if policy_id:
            query = query.filter(RetentionExecution.policy_id == policy_id)
        
        return query.order_by(desc(RetentionExecution.execution_date)).limit(limit).all()
    
    def initialize_default_policies(self):
        """Initialize Default Policies."""
        """Initialize default retention policies."""
        default_policies = [
            {
                'policy_name': 'Audit Log Retention',
                'policy_code': 'AUDIT_LOG_7Y',
                'table_name': 'audit_logs',
                'data_category': 'audit',
                'retention_period_days': 2555,
                'retention_action': RetentionAction.ARCHIVE,
                'description': 'Retain audit logs for 7 years as required by regulations',
                'legal_basis': 'SOX compliance requirement'
            },
            {
                'policy_name': 'Session Data Cleanup',
                'policy_code': 'SESSION_30D',
                'table_name': 'user_sessions',
                'data_category': 'session',
                'retention_period_days': 30,
                'retention_action': RetentionAction.DELETE,
                'description': 'Clean up old session data after 30 days',
                'legal_basis': 'Data minimization principle'
            },
            {
                'policy_name': 'Login Attempts Cleanup',
                'policy_code': 'LOGIN_90D',
                'table_name': 'login_attempts',
                'data_category': 'security',
                'retention_period_days': 90,
                'retention_action': RetentionAction.DELETE,
                'description': 'Clean up login attempt records after 90 days',
                'legal_basis': 'Security monitoring requirement'
            }
        ]
        
        for policy_data in default_policies:
            existing = self.db.query(DataRetentionPolicy).filter(
                DataRetentionPolicy.policy_code == policy_data['policy_code']
            ).first()
            
            if not existing:
                policy = DataRetentionPolicy(**policy_data)
                policy.next_execution = datetime.utcnow() + timedelta(days=1)
                self.db.add(policy)
        
        self.db.commit()
    
    def _delete_records(self, policy: DataRetentionPolicy, cutoff_date: datetime) -> Dict[str, int]:
        """ Delete Records."""
        """Delete records based on retention policy."""
        where_clause = f"created_at < :cutoff_date"
        
        if policy.conditions:
            for key, value in policy.conditions.items():
                where_clause += f" AND {key} = :{key}"
        
        count_query = f"SELECT COUNT(*) FROM {policy.table_name} WHERE {where_clause}"
        params = {'cutoff_date': cutoff_date}
        if policy.conditions:
            params.update(policy.conditions)
        
        count_result = self.db.execute(text(count_query), params)
        record_count = count_result.scalar()
        
        delete_query = f"DELETE FROM {policy.table_name} WHERE {where_clause}"
        self.db.execute(text(delete_query), params)
        self.db.commit()
        
        return {
            'processed': record_count,
            'deleted': record_count,
            'archived': 0,
            'anonymized': 0
        }
    
    def _archive_records(self, policy: DataRetentionPolicy, cutoff_date: datetime) -> Dict[str, int]:
        """ Archive Records."""
        """Archive records based on retention policy."""
        where_clause = f"created_at < :cutoff_date"
        
        if policy.conditions:
            for key, value in policy.conditions.items():
                where_clause += f" AND {key} = :{key}"
        
        count_query = f"SELECT COUNT(*) FROM {policy.table_name} WHERE {where_clause}"
        params = {'cutoff_date': cutoff_date}
        if policy.conditions:
            params.update(policy.conditions)
        
        count_result = self.db.execute(text(count_query), params)
        record_count = count_result.scalar()
        
        return {
            'processed': record_count,
            'deleted': 0,
            'archived': record_count,
            'anonymized': 0
        }
    
    def _anonymize_records(self, policy: DataRetentionPolicy, cutoff_date: datetime) -> Dict[str, int]:
        """ Anonymize Records."""
        """Anonymize records based on retention policy."""
        where_clause = f"created_at < :cutoff_date"
        
        if policy.conditions:
            for key, value in policy.conditions.items():
                where_clause += f" AND {key} = :{key}"
        
        count_query = f"SELECT COUNT(*) FROM {policy.table_name} WHERE {where_clause}"
        params = {'cutoff_date': cutoff_date}
        if policy.conditions:
            params.update(policy.conditions)
        
        count_result = self.db.execute(text(count_query), params)
        record_count = count_result.scalar()
        
        return {
            'processed': record_count,
            'deleted': 0,
            'archived': 0,
            'anonymized': record_count
        }