"""
Paksa Financial System - Security Event Service
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

Service for managing and processing security events and alerts.
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple, Union
from uuid import UUID, uuid4

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text

from .. import models, schemas, exceptions
from ...core.database import Base
from ...core.config import settings


class SecurityEventService:
    """
    Service for managing and processing security events and alerts.
    
    This service handles the creation, retrieval, and processing of security events,
    as well as generating alerts and notifications for suspicious activities.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_event(
        self,
        event_type: models.SecurityEventType,
        severity: models.SecurityEventSeverity,
        source: str,
        description: str,
        user_id: Optional[UUID] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> models.SecurityEvent:
        """
        Create a new security event.
        
        Args:
            event_type: Type of the security event
            severity: Severity level of the event
            source: Source of the event (e.g., 'auth', 'api', 'application')
            description: Human-readable description of the event
            user_id: ID of the user associated with the event (if any)
            username: Username of the user associated with the event (if any)
            ip_address: IP address where the event originated
            user_agent: User agent string of the client
            resource_type: Type of resource affected by the event
            resource_id: ID of the resource affected by the event
            details: Additional event details as a dictionary
            metadata: Additional metadata for the event
            
        Returns:
            The created security event
            
        Raises:
            SecurityEventError: If there's an error creating the event
        """
        try:
            event = models.SecurityEvent(
                id=uuid4(),
                event_type=event_type,
                severity=severity,
                source=source,
                description=description,
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                details=details or {},
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            
            # Check if this event should trigger any alerts
            self._check_for_alerts(event)
            
            return event
            
        except Exception as e:
            self.db.rollback()
            raise exceptions.SecurityEventError(f"Failed to create security event: {str(e)}")
