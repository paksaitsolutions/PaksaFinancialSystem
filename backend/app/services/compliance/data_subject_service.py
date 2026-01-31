"""
Paksa Financial System - Data Subject Service
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

Service for managing data subject rights requests (GDPR/CCPA).
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json
import os

from .. import models, schemas, exceptions
from ...core.config import settings
from ...core.database import Base
from io import BytesIO
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
import zipfile

from app.core.security import get_password_hash, verify_password






class DataSubjectService:
    """
    Service for managing data subject rights requests and related operations.
    
    This service handles the creation, processing, and fulfillment of data subject
    rights requests under regulations like GDPR and CCPA.
    """
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
    
    def create_request(
        """Create Request."""
        self,
        request_data: schemas.DataSubjectRightsRequestCreate,
        user_id: Optional[UUID] = None
    ) -> models.DataSubjectRightsRequest:
        """Create Request."""
        """
        Create a new data subject rights request.
        
        Args:
            request_data: The request data
            user_id: ID of the user creating the request (if internal)
            
        Returns:
            The created request
            
        Raises:
            DataSubjectRequestError: If there's an error creating the request
        """
        try:
            # Check for duplicate pending requests from the same email
            existing = self.db.query(models.DataSubjectRightsRequest).filter(
                models.DataSubjectRightsRequest.subject_email == request_data.subject_email,
                models.DataSubjectRightsRequest.request_type == request_data.request_type,
                models.DataSubjectRightsRequest.status == models.DataSubjectRightsRequest.RequestStatus.PENDING
            ).first()
            
            if existing:
                raise exceptions.DataSubjectRequestError(
                    f"A pending {request_data.request_type.value} request already exists for this email"
            )
            
            # Create the request
            db_request = models.DataSubjectRightsRequest(
                id=uuid4(),
                request_type=request_data.request_type,
                subject_type=request_data.subject_type,
                subject_name=request_data.subject_name,
                subject_email=request_data.subject_email,
                subject_phone=request_data.subject_phone,
                subject_address=request_data.subject_address,
                description=request_data.description,
                requested_data=request_data.requested_data,
                status=models.DataSubjectRightsRequest.RequestStatus.PENDING,
                created_by=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(db_request)
            self.db.commit()
            self.db.refresh(db_request)
            
            return db_request
            
        except Exception as e:
            self.db.rollback()
            if isinstance(e, exceptions.DataSubjectRequestError):
                raise
            raise exceptions.DataSubjectRequestError(f"Failed to create request: {str(e)}")
    
    def get_request(self, request_id: UUID) -> models.DataSubjectRightsRequest:
        """Get Request."""
        """
        Retrieve a data subject rights request by ID.
        
        Args:
            request_id: ID of the request to retrieve
            
        Returns:
            The requested data subject rights request
            
        Raises:
            DataSubjectRequestNotFound: If no request exists with the given ID
        """
        request = self.db.query(models.DataSubjectRightsRequest).get(request_id)
        if not request:
            raise exceptions.DataSubjectRequestNotFound(request_id=request_id)
        return request
    
    def list_requests(
        """List Requests."""
        self,
        status: Optional[models.DataSubjectRightsRequest.RequestStatus] = None,
        request_type: Optional[models.DataSubjectRightsRequest.RequestType] = None,
        subject_type: Optional[models.DataSubjectType] = None,
        subject_email: Optional[str] = None,
        assigned_to: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> Tuple[List[models.DataSubjectRightsRequest], int]:
        """List Requests."""
        """
        List data subject rights requests with filtering and pagination.
        
        Args:
            status: Filter by request status
            request_type: Filter by request type
            subject_type: Filter by subject type
            subject_email: Filter by subject email (case-insensitive partial match)
            assigned_to: Filter by assigned user ID
            start_date: Filter requests created after this date
            end_date: Filter requests created before this date
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_desc: Whether to sort in descending order
            
        Returns:
            A tuple containing:
                - List of data subject rights requests
                - Total count of matching requests
        """
        query = self.db.query(models.DataSubjectRightsRequest)
        
        # Apply filters
        if status is not None:
            query = query.filter(models.DataSubjectRightsRequest.status == status)
        if request_type is not None:
            query = query.filter(models.DataSubjectRightsRequest.request_type == request_type)
        if subject_type is not None:
            query = query.filter(models.DataSubjectRightsRequest.subject_type == subject_type)
        if subject_email:
            query = query.filter(
                models.DataSubjectRightsRequest.subject_email.ilike(f"%{subject_email}%")
            )
        if assigned_to is not None:
            query = query.filter(models.DataSubjectRightsRequest.assigned_to == assigned_to)
        if start_date:
            query = query.filter(models.DataSubjectRightsRequest.created_at >= start_date)
        if end_date:
            query = query.filter(models.DataSubjectRightsRequest.created_at < end_date + timedelta(days=1))
        
        # Get total count before pagination
        total = query.count()
        
        # Apply ordering
        order_field = getattr(models.DataSubjectRightsRequest, order_by, models.DataSubjectRightsRequest.created_at)
        if order_desc:
            order_field = order_field.desc()
        query = query.order_by(order_field)
        
        # Apply pagination
        requests = query.offset(skip).limit(limit).all()
        
        return requests, total
    
    def update_request(
        """Update Request."""
        self,
        request_id: UUID,
        update_data: schemas.DataSubjectRightsRequestUpdate,
        user_id: UUID
    ) -> models.DataSubjectRightsRequest:
        """Update Request."""
        """
        Update a data subject rights request.
        
        Args:
            request_id: ID of the request to update
            update_data: The updated request data
            user_id: ID of the user performing the update
            
        Returns:
            The updated data subject rights request
            
        Raises:
            DataSubjectRequestNotFound: If no request exists with the given ID
            DataSubjectRequestError: If there's an error updating the request
        """
        try:
            request = self.get_request(request_id)
            
            # Update fields if provided
            if update_data.status is not None:
                request.status = update_data.status
                
                # Set completed_at if request is being completed
                if update_data.status == models.DataSubjectRightsRequest.RequestStatus.COMPLETED:
                    request.completed_at = datetime.utcnow()
            
            if update_data.assigned_to is not None:
                request.assigned_to = update_data.assigned_to
            
            if update_data.due_date is not None:
                request.due_date = update_data.due_date
            
            if update_data.verification_method is not None:
                request.verification_method = update_data.verification_method
            
            if update_data.verification_notes is not None:
                request.verification_notes = update_data.verification_notes
            
            if update_data.response_notes is not None:
                request.response_notes = update_data.response_notes
            
            if update_data.response_data is not None:
                request.response_data = update_data.response_data
            
            # Update timestamps
            request.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(request)
            
            return request
            
        except exceptions.DataSubjectRequestNotFound:
            raise
        except Exception as e:
            self.db.rollback()
            raise exceptions.DataSubjectRequestError(f"Failed to update request: {str(e)}")
    
    def verify_subject_identity(
        """Verify Subject Identity."""
        self,
        request_id: UUID,
        verification_method: str,
        verification_notes: Optional[str] = None,
        verified_by: Optional[UUID] = None
    ) -> models.DataSubjectRightsRequest:
        """Verify Subject Identity."""
        """
        Verify the identity of a data subject.
        
        Args:
            request_id: ID of the request
            verification_method: Method used for verification
            verification_notes: Optional notes about the verification
            verified_by: ID of the user performing the verification
            
        Returns:
            The updated data subject rights request
            
        Raises:
            DataSubjectRequestNotFound: If no request exists with the given ID
            DataSubjectRequestError: If there's an error verifying the identity
        """
        try:
            request = self.get_request(request_id)
            
            # Update verification details
            request.verification_method = verification_method
            request.verification_notes = verification_notes
            request.verified_at = datetime.utcnow()
            request.verified_by = verified_by
            request.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(request)
            
            return request
            
        except exceptions.DataSubjectRequestNotFound:
            raise
        except Exception as e:
            self.db.rollback()
            raise exceptions.DataSubjectVerificationFailed(
                f"Failed to verify subject identity: {str(e)}"
            )
    
    def process_request(
        """Process Request."""
        self,
        request_id: UUID,
        processed_by: UUID,
        notes: Optional[str] = None
    ) -> models.DataSubjectRightsRequest:
        """Process Request."""
        """
        Process a data subject rights request.
        
        Args:
            request_id: ID of the request to process
            processed_by: ID of the user processing the request
            notes: Optional processing notes
            
        Returns:
            The updated data subject rights request
            
        Raises:
            DataSubjectRequestNotFound: If no request exists with the given ID
            DataSubjectRequestError: If there's an error processing the request
        """
        try:
            request = self.get_request(request_id)
            
            # Verify the request is in a processable state
            if request.status != models.DataSubjectRightsRequest.RequestStatus.PENDING:
                raise exceptions.DataSubjectRequestError(
                    f"Cannot process request in status: {request.status.value}"
                )
            
            # Update request status
            request.status = models.DataSubjectRightsRequest.RequestStatus.IN_PROGRESS
            request.assigned_to = processed_by
            request.updated_at = datetime.utcnow()
            
            # Add processing notes if provided
            if notes:
                if request.notes:
                    request.notes += f"\n---\n{datetime.utcnow().isoformat()}: {notes}"
                else:
                    request.notes = notes
            
            self.db.commit()
            self.db.refresh(request)
            
            
            return request
            
        except exceptions.DataSubjectRequestNotFound:
            raise
        except exceptions.DataSubjectRequestError:
            raise
        except Exception as e:
            self.db.rollback()
            raise exceptions.DataSubjectRequestError(f"Failed to process request: {str(e)}")
    
    def complete_request(
        """Complete Request."""
        self,
        request_id: UUID,
        completed_by: UUID,
        response_data: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> models.DataSubjectRightsRequest:
        """Complete Request."""
        """
        Complete a data subject rights request.
        
        Args:
            request_id: ID of the request to complete
            completed_by: ID of the user completing the request
            response_data: Optional response data
            notes: Optional completion notes
            
        Returns:
            The completed data subject rights request
            
        Raises:
            DataSubjectRequestNotFound: If no request exists with the given ID
            DataSubjectRequestError: If there's an error completing the request
        """
        try:
            request = self.get_request(request_id)
            
            # Verify the request is in a completable state
            if request.status == models.DataSubjectRightsRequest.RequestStatus.COMPLETED:
                return request  # Already completed
                
            if request.status == models.DataSubjectRightsRequest.RequestStatus.REJECTED:
                raise exceptions.DataSubjectRequestError(
                    "Cannot complete a rejected request"
                )
            
            # Update request status and completion details
            request.status = models.DataSubjectRightsRequest.RequestStatus.COMPLETED
            request.completed_at = datetime.utcnow()
            request.completed_by = completed_by
            request.updated_at = datetime.utcnow()
            
            # Update response data if provided
            if response_data is not None:
                request.response_data = response_data
            
            # Add completion notes if provided
            if notes:
                if request.notes:
                    request.notes += f"\n---\n{datetime.utcnow().isoformat()}: {notes}"
                else:
                    request.notes = notes
            
            self.db.commit()
            self.db.refresh(request)
            
            
            return request
            
        except exceptions.DataSubjectRequestNotFound:
            raise
        except exceptions.DataSubjectRequestError:
            raise
        except Exception as e:
            self.db.rollback()
            raise exceptions.DataSubjectRequestError(f"Failed to complete request: {str(e)}")
    
    def reject_request(
        """Reject Request."""
        self,
        request_id: UUID,
        rejected_by: UUID,
        reason: str,
        notes: Optional[str] = None
    ) -> models.DataSubjectRightsRequest:
        """Reject Request."""
        """
        Reject a data subject rights request.
        
        Args:
            request_id: ID of the request to reject
            rejected_by: ID of the user rejecting the request
            reason: Reason for rejection
            notes: Optional rejection notes
            
        Returns:
            The rejected data subject rights request
            
        Raises:
            DataSubjectRequestNotFound: If no request exists with the given ID
            DataSubjectRequestError: If there's an error rejecting the request
        """
        try:
            request = self.get_request(request_id)
            
            # Verify the request is in a rejectable state
            if request.status in [
                models.DataSubjectRightsRequest.RequestStatus.COMPLETED,
                models.DataSubjectRightsRequest.RequestStatus.REJECTED,
                models.DataSubjectRightsRequest.RequestStatus.CANCELLED
            ]:
                raise exceptions.DataSubjectRequestError(
                    f"Cannot reject request in status: {request.status.value}"
                )
            
            # Update request status and rejection details
            request.status = models.DataSubjectRightsRequest.RequestStatus.REJECTED
            request.rejected_at = datetime.utcnow()
            request.rejected_by = rejected_by
            request.rejection_reason = reason
            request.updated_at = datetime.utcnow()
            
            # Add rejection notes if provided
            if notes:
                if request.notes:
                    request.notes += f"\n---\n{datetime.utcnow().isoformat()}: {notes}"
                else:
                    request.notes = notes
            
            self.db.commit()
            self.db.refresh(request)
            
            
            return request
            
        except exceptions.DataSubjectRequestNotFound:
            raise
        except exceptions.DataSubjectRequestError:
            raise
        except Exception as e:
            self.db.rollback()
            raise exceptions.DataSubjectRequestError(f"Failed to reject request: {str(e)}")
    
    def cancel_request(
        """Cancel Request."""
        self,
        request_id: UUID,
        cancelled_by: Optional[UUID] = None,
        reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> models.DataSubjectRightsRequest:
        """Cancel Request."""
        """
        Cancel a data subject rights request.
        
        Args:
            request_id: ID of the request to cancel
            cancelled_by: ID of the user cancelling the request (if any)
            reason: Reason for cancellation (if any)
            notes: Optional cancellation notes
            
        Returns:
            The cancelled data subject rights request
            
        Raises:
            DataSubjectRequestNotFound: If no request exists with the given ID
            DataSubjectRequestError: If there's an error cancelling the request
        """
        try:
            request = self.get_request(request_id)
            
            # Verify the request is in a cancellable state
            if request.status in [
                models.DataSubjectRightsRequest.RequestStatus.COMPLETED,
                models.DataSubjectRightsRequest.RequestStatus.REJECTED,
                models.DataSubjectRightsRequest.RequestStatus.CANCELLED
            ]:
                return request  # Already in a terminal state
            
            # Update request status and cancellation details
            request.status = models.DataSubjectRightsRequest.RequestStatus.CANCELLED
            request.cancelled_at = datetime.utcnow()
            request.cancelled_by = cancelled_by
            request.cancellation_reason = reason
            request.updated_at = datetime.utcnow()
            
            # Add cancellation notes if provided
            if notes:
                if request.notes:
                    request.notes += f"\n---\n{datetime.utcnow().isoformat()}: {notes}"
                else:
                    request.notes = notes
            
            self.db.commit()
            self.db.refresh(request)
            
            
            return request
            
        except exceptions.DataSubjectRequestNotFound:
            raise
        except Exception as e:
            self.db.rollback()
            raise exceptions.DataSubjectRequestError(f"Failed to cancel request: {str(e)}")
    
    def export_subject_data(
        """Export Subject Data."""
        self,
        request_id: UUID,
        export_format: str = "json",
        include_related: bool = True,
        encryption_key_id: Optional[UUID] = None
    ) -> Tuple[bytes, str]:
        """Export Subject Data."""
        """
        Export data for a data subject.
        
        Args:
            request_id: ID of the data subject rights request
            export_format: Format of the export ('json', 'csv', 'xml')
            include_related: Whether to include related data
            encryption_key_id: Optional encryption key ID
            
        Returns:
            A tuple containing:
                - The exported data as bytes
                - The filename for the export
            
        Raises:
            DataSubjectRequestNotFound: If no request exists with the given ID
            DataExportError: If there's an error exporting the data
        """
        try:
            request = self.get_request(request_id)
            
            # This is a placeholder implementation
            
            # Get the subject's data from various sources
            subject_data = {
                "request_id": str(request.id),
                "subject_type": request.subject_type.value,
                "subject_name": request.subject_name,
                "subject_email": request.subject_email,
                "subject_phone": request.subject_phone,
                "subject_address": request.subject_address,
                "request_type": request.request_type.value,
                "request_date": request.created_at.isoformat(),
                "status": request.status.value,
                "data": {
                    # Placeholder for actual data
                    "profile": {},
                    "preferences": {},
                    "activity": []
                }
            }
            
            # Convert to the requested format
            if export_format == "json":
                data = json.dumps(subject_data, indent=2, ensure_ascii=False).encode('utf-8')
                filename = f"data_export_{request.id}.json"
            elif export_format == "csv":
                # Simple CSV conversion (would need to be more sophisticated for nested data)
                import csv
                from io import StringIO
                
                output = StringIO()
                writer = csv.writer(output)
                
                # Flatten the data for CSV
                flat_data = []
                for key, value in subject_data.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            flat_data.append([f"{key}.{subkey}", str(subvalue)])
                    else:
                        flat_data.append([key, str(value)])
                
                writer.writerow(["Field", "Value"])
                writer.writerows(flat_data)
                
                data = output.getvalue().encode('utf-8')
                filename = f"data_export_{request.id}.csv"
            else:
                raise exceptions.DataExportError(f"Unsupported export format: {export_format}")
            
            
            return data, filename
            
        except exceptions.DataSubjectRequestNotFound:
            raise
        except exceptions.DataExportError:
            raise
        except Exception as e:
            raise exceptions.DataExportError(f"Failed to export data: {str(e)}")
    
    def anonymize_subject_data(
        """Anonymize Subject Data."""
        self,
        request_id: UUID,
        anonymization_map: Optional[Dict[str, str]] = None
    ) -> Dict[str, int]:
        """Anonymize Subject Data."""
        """
        Anonymize data for a data subject.
        
        Args:
            request_id: ID of the data subject rights request
            anonymization_map: Optional mapping of fields to anonymization methods
            
        Returns:
            A dictionary with anonymization statistics
            
        Raises:
            DataSubjectRequestNotFound: If no request exists with the given ID
            DataAnonymizationError: If there's an error anonymizing the data
        """
        try:
            request = self.get_request(request_id)
            
            # Default anonymization map if not provided
            if anonymization_map is None:
                anonymization_map = {
                    "name": "pseudonymize",
                    "email": "hash",
                    "phone": "mask",
                    "address": "redact",
                    "ip_address": "anonymize_ip"
                }
            
            # This is a placeholder implementation
            
            # Get the subject's data from various sources
            # In a real implementation, this would query the database
            # and apply the anonymization to each field
            
            # Placeholder for anonymization statistics
            stats = {
                "tables_processed": 0,
                "records_anonymized": 0,
                "fields_anonymized": 0,
                "anonymization_errors": 0
            }
            
            # Update the request to indicate anonymization was performed
            if request.notes:
                request.notes += f"\n---\n{datetime.utcnow().isoformat()}: Data anonymization performed"
            else:
                request.notes = f"Data anonymization performed at {datetime.utcnow().isoformat()}"
            
            request.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            return stats
            
        except exceptions.DataSubjectRequestNotFound:
            raise
        except Exception as e:
            self.db.rollback()
            raise exceptions.DataAnonymizationError(f"Failed to anonymize data: {str(e)}")
    
    def get_request_timeline(
        """Get Request Timeline."""
        self,
        request_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get Request Timeline."""
        """
        Get a timeline of events for a data subject rights request.
        
        Args:
            request_id: ID of the request
            
        Returns:
            A list of timeline events
            
        Raises:
            DataSubjectRequestNotFound: If no request exists with the given ID
        """
        request = self.get_request(request_id)
        
        timeline = []
        
        # Add request creation
        timeline.append({
            "timestamp": request.created_at,
            "event": "request_created",
            "details": {
                "request_type": request.request_type.value,
                "subject_type": request.subject_type.value,
                "subject_email": request.subject_email
            },
            "user_id": request.created_by
        })
        
        # Add status changes
        if request.verified_at:
            timeline.append({
                "timestamp": request.verified_at,
                "event": "identity_verified",
                "details": {
                    "verification_method": request.verification_method,
                    "verified_by": str(request.verified_by)
                },
                "user_id": request.verified_by
            })
        
        if request.assigned_to:
            timeline.append({
                "timestamp": request.updated_at,
                "event": "request_assigned",
                "details": {
                    "assigned_to": str(request.assigned_to)
                },
                "user_id": request.assigned_to
            })
        
        if request.status == models.DataSubjectRightsRequest.RequestStatus.COMPLETED and request.completed_at:
            timeline.append({
                "timestamp": request.completed_at,
                "event": "request_completed",
                "details": {
                    "completed_by": str(request.completed_by)
                },
                "user_id": request.completed_by
            })
        
        # Sort timeline by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        
        return timeline
