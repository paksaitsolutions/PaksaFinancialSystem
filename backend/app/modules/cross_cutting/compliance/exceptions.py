"""
Paksa Financial System - Compliance & Security Exceptions
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

Custom exceptions for the Compliance & Security module.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import status
from pydantic import BaseModel

from app.core.exceptions import AppException, ErrorCode


class ComplianceException(AppException):
    """Base exception for compliance-related errors"""
    pass


class AuditLogError(ComplianceException):
    """Raised when there's an error with audit logging"""
    error_code = ErrorCode.AUDIT_LOG_ERROR
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class AuditLogNotFound(ComplianceException):
    """Raised when an audit log entry is not found"""
    error_code = ErrorCode.RESOURCE_NOT_FOUND
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, log_id: UUID):
        super().__init__(f"Audit log with ID '{log_id}' not found")
        self.log_id = log_id


class DataSubjectRequestError(ComplianceException):
    """Raised when there's an error with a data subject request"""
    error_code = ErrorCode.DATA_SUBJECT_REQUEST_ERROR
    status_code = status.HTTP_400_BAD_REQUEST


class DataSubjectRequestNotFound(ComplianceException):
    """Raised when a data subject request is not found"""
    error_code = ErrorCode.RESOURCE_NOT_FOUND
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, request_id: UUID):
        super().__init__(f"Data subject request with ID '{request_id}' not found")
        self.request_id = request_id


class DataSubjectVerificationFailed(ComplianceException):
    """Raised when data subject verification fails"""
    error_code = ErrorCode.VERIFICATION_FAILED
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, reason: str):
        super().__init__(f"Data subject verification failed: {reason}")
        self.reason = reason


class DataExportError(ComplianceException):
    """Raised when there's an error exporting data"""
    error_code = ErrorCode.DATA_EXPORT_ERROR
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}


class DataExportNotFound(ComplianceException):
    """Raised when a data export is not found"""
    error_code = ErrorCode.RESOURCE_NOT_FOUND
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, export_id: UUID):
        super().__init__(f"Data export with ID '{export_id}' not found")
        self.export_id = export_id


class SecurityPolicyError(ComplianceException):
    """Raised when there's an error with a security policy"""
    error_code = ErrorCode.SECURITY_POLICY_ERROR
    status_code = status.HTTP_400_BAD_REQUEST


class SecurityPolicyNotFound(ComplianceException):
    """Raised when a security policy is not found"""
    error_code = ErrorCode.RESOURCE_NOT_FOUND
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, policy_id: Optional[UUID] = None, name: Optional[str] = None):
        if policy_id:
            message = f"Security policy with ID '{policy_id}' not found"
        elif name:
            message = f"Security policy with name '{name}' not found"
        else:
            message = "Security policy not found"
        super().__init__(message)
        self.policy_id = policy_id
        self.name = name


class EncryptionError(ComplianceException):
    """Raised when there's an error with encryption/decryption"""
    error_code = ErrorCode.ENCRYPTION_ERROR
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class EncryptionKeyError(ComplianceException):
    """Raised when there's an error with an encryption key"""
    error_code = ErrorCode.ENCRYPTION_KEY_ERROR
    status_code = status.HTTP_400_BAD_REQUEST


class EncryptionKeyNotFound(ComplianceException):
    """Raised when an encryption key is not found"""
    error_code = ErrorCode.RESOURCE_NOT_FOUND
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, key_id: Optional[UUID] = None, name: Optional[str] = None):
        if key_id:
            message = f"Encryption key with ID '{key_id}' not found"
        elif name:
            message = f"Encryption key with name '{name}' not found"
        else:
            message = "Encryption key not found"
        super().__init__(message)
        self.key_id = key_id
        self.name = name


class SecurityEventError(ComplianceException):
    """Raised when there's an error with a security event"""
    error_code = ErrorCode.SECURITY_EVENT_ERROR
    status_code = status.HTTP_400_BAD_REQUEST


class SecurityEventNotFound(ComplianceException):
    """Raised when a security event is not found"""
    error_code = ErrorCode.RESOURCE_NOT_FOUND
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, event_id: UUID):
        super().__init__(f"Security event with ID '{event_id}' not found")
        self.event_id = event_id


class AccessDenied(ComplianceException):
    """Raised when access to a resource is denied"""
    error_code = ErrorCode.ACCESS_DENIED
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, resource_type: str, resource_id: Optional[UUID] = None):
        if resource_id:
            message = f"Access denied to {resource_type} with ID '{resource_id}'"
        else:
            message = f"Access denied to {resource_type}"
        super().__init__(message)
        self.resource_type = resource_type
        self.resource_id = resource_id


class RateLimitExceeded(ComplianceException):
    """Raised when a rate limit is exceeded"""
    error_code = ErrorCode.RATE_LIMIT_EXCEEDED
    status_code = status.HTTP_429_TOO_MANY_REQUESTS

    def __init__(self, retry_after: int):
        super().__init__("Rate limit exceeded")
        self.retry_after = retry_after
        self.headers = {"Retry-After": str(retry_after)}


class DataRetentionError(ComplianceException):
    """Raised when there's an error with data retention"""
    error_code = ErrorCode.DATA_RETENTION_ERROR
    status_code = status.HTTP_400_BAD_REQUEST


class DataAnonymizationError(ComplianceException):
    """Raised when there's an error with data anonymization"""
    error_code = ErrorCode.DATA_ANONYMIZATION_ERROR
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ConsentError(ComplianceException):
    """Raised when there's an error with consent management"""
    error_code = ErrorCode.CONSENT_ERROR
    status_code = status.HTTP_400_BAD_REQUEST


class ConsentNotFound(ComplianceException):
    """Raised when a consent record is not found"""
    error_code = ErrorCode.RESOURCE_NOT_FOUND
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, consent_id: UUID):
        super().__init__(f"Consent record with ID '{consent_id}' not found")
        self.consent_id = consent_id
