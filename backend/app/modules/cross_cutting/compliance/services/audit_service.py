"""
Paksa Financial System - Audit Service
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

Service for managing audit logs and related operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.core.security import get_password_hash, verify_password
from .. import models, schemas, exceptions
from ...core.database import Base


class AuditService:
    """
    Service for managing audit logs and related operations.
    
    This service handles the creation, retrieval, and management of audit logs
    that track all significant system events for compliance and security purposes.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_audit_log(
        self,
        action: models.AuditActionType,
        resource_type: str,
        user_id: Optional[UUID] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_id: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> models.AuditLog:
        """
        Create a new audit log entry.
        
        Args:
            action: The type of action being logged
            resource_type: The type of resource being acted upon
            user_id: ID of the user performing the action (if any)
            username: Username of the user performing the action (if any)
            ip_address: IP address of the client
            user_agent: User agent string of the client
            resource_id: ID of the resource being acted upon (if any)
            status_code: HTTP status code of the response (if applicable)
            details: Additional details about the event
            
        Returns:
            The created audit log entry
        """
        try:
            log = models.AuditLog(
                id=uuid4(),
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                status_code=status_code,
                details=details or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            return log
        except Exception as e:
            self.db.rollback()
            raise exceptions.AuditLogError(f"Failed to create audit log: {str(e)}")
    
    def get_audit_log(self, log_id: UUID) -> models.AuditLog:
        """
        Retrieve an audit log entry by ID.
        
        Args:
            log_id: ID of the audit log to retrieve
            
        Returns:
            The requested audit log entry
            
        Raises:
            AuditLogNotFound: If no log exists with the given ID
        """
        log = self.db.query(models.AuditLog).filter(models.AuditLog.id == log_id).first()
        if not log:
            raise exceptions.AuditLogNotFound(log_id=log_id)
        return log
    
    def list_audit_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[UUID] = None,
        action: Optional[models.AuditActionType] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status_code: Optional[int] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "timestamp",
        order_desc: bool = True
    ) -> tuple[list[models.AuditLog], int]:
        """
        List audit logs with filtering and pagination.
        
        Args:
            start_date: Filter logs after this date
            end_date: Filter logs before this date
            user_id: Filter by user ID
            action: Filter by action type
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            status_code: Filter by status code
            username: Filter by username (case-insensitive partial match)
            ip_address: Filter by IP address
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_desc: Whether to sort in descending order
            
        Returns:
            A tuple containing:
                - List of audit logs
                - Total count of matching logs
        """
        query = self.db.query(models.AuditLog)
        
        # Apply filters
        if start_date:
            query = query.filter(models.AuditLog.timestamp >= start_date)
        if end_date:
            # Add 1 day to include the entire end date
            query = query.filter(models.AuditLog.timestamp < end_date + timedelta(days=1))
        if user_id:
            query = query.filter(models.AuditLog.user_id == user_id)
        if action:
            query = query.filter(models.AuditLog.action == action)
        if resource_type:
            query = query.filter(models.AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(models.AuditLog.resource_id == str(resource_id))
        if status_code is not None:
            query = query.filter(models.AuditLog.status_code == status_code)
        if username:
            query = query.filter(models.AuditLog.username.ilike(f"%{username}%"))
        if ip_address:
            query = query.filter(models.AuditLog.ip_address == ip_address)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply ordering
        order_field = getattr(models.AuditLog, order_by, models.AuditLog.timestamp)
        if order_desc:
            order_field = order_field.desc()
        query = query.order_by(order_field)
        
        # Apply pagination
        logs = query.offset(skip).limit(limit).all()
        
        return logs, total
    
    def get_audit_summary(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "day",
        user_id: Optional[UUID] = None,
        action: Optional[models.AuditActionType] = None,
        resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get a summary of audit logs grouped by time period.
        
        Args:
            start_date: Start date for the summary
            end_date: End date for the summary
            group_by: Time period to group by ('day', 'hour', 'month')
            user_id: Filter by user ID
            action: Filter by action type
            resource_type: Filter by resource type
            
        Returns:
            List of summary items with counts by time period
        """
        # Determine the date truncation function based on group_by
        if group_by == 'hour':
            trunc_func = func.date_trunc('hour', models.AuditLog.timestamp)
        elif group_by == 'day':
            trunc_func = func.date_trunc('day', models.AuditLog.timestamp)
        elif group_by == 'month':
            trunc_func = func.date_trunc('month', models.AuditLog.timestamp)
        else:
            trunc_func = func.date_trunc('day', models.AuditLog.timestamp)
        
        # Build the base query
        query = self.db.query(
            trunc_func.label('period'),
            models.AuditLog.action,
            models.AuditLog.resource_type,
            func.count().label('count')
        ).filter(
            models.AuditLog.timestamp.between(start_date, end_date)
        )
        
        # Apply filters
        if user_id:
            query = query.filter(models.AuditLog.user_id == user_id)
        if action:
            query = query.filter(models.AuditLog.action == action)
        if resource_type:
            query = query.filter(models.AuditLog.resource_type == resource_type)
        
        # Group and order
        query = query.group_by(
            'period',
            models.AuditLog.action,
            models.AuditLog.resource_type
        ).order_by('period')
        
        # Execute query and format results
        results = query.all()
        
        # Format results into a list of dictionaries
        summary = []
        for row in results:
            summary.append({
                'period': row.period,
                'action': row.action.value if hasattr(row.action, 'value') else row.action,
                'resource_type': row.resource_type,
                'count': row.count
            })
        
        return summary
    
    def cleanup_old_logs(
        self,
        older_than_days: int = 365,
        batch_size: int = 1000
    ) -> int:
        """
        Delete audit logs older than the specified number of days.
        
        Args:
            older_than_days: Delete logs older than this many days
            batch_size: Number of logs to delete in each batch
            
        Returns:
            Number of logs deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            
            # Delete in batches to avoid locking the table for too long
            total_deleted = 0
            while True:
                # Use a subquery to limit the number of rows to delete
                subquery = self.db.query(models.AuditLog.id)\
                    .filter(models.AuditLog.timestamp < cutoff_date)\
                    .limit(batch_size)\
                    .subquery()
                
                # Delete the batch
                result = self.db.query(models.AuditLog)\
                    .filter(models.AuditLog.id.in_(subquery))\
                    .delete(synchronize_session=False)
                
                self.db.commit()
                total_deleted += result
                
                # If we deleted fewer rows than the batch size, we're done
                if result < batch_size:
                    break
            
            return total_deleted
            
        except Exception as e:
            self.db.rollback()
            raise exceptions.AuditLogError(f"Failed to clean up old logs: {str(e)}")
