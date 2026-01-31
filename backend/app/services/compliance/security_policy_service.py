"""
Paksa Financial System - Security Policy Service
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

Service for managing security policies and configurations.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
import json

from .. import models, schemas, exceptions
from ...core.config import settings
from ...core.database import Base
from sqlalchemy import and_, or_, desc, func, update
from sqlalchemy.orm import Session
from uuid import UUID, uuid4

from app.core.security import get_password_hash, verify_password






class SecurityPolicyService:
    """
    Service for managing security policies and configurations.
    
    This service handles the creation, management, and enforcement of
    security policies across the application.
    """
    
    def __init__(self, db: Session):
        """  Init  ."""
        self.db = db
    
    def create_policy(
        """Create Policy."""
        self,
        policy_data: schemas.SecurityPolicyCreate,
        created_by: UUID
    ) -> models.SecurityPolicy:
        """Create Policy."""
        """
        Create a new security policy.
        
        Args:
            policy_data: The policy data
            created_by: ID of the user creating the policy
            
        Returns:
            The created security policy
            
        Raises:
            SecurityPolicyError: If there's an error creating the policy
        """
        try:
            # Check if a policy with the same name already exists
            existing = self.db.query(models.SecurityPolicy).filter(
                models.SecurityPolicy.name == policy_data.name
            ).first()
            
            if existing:
                raise exceptions.SecurityPolicyError(
                    f"A policy with the name '{policy_data.name}' already exists"
                )
            
            # Create the policy
            db_policy = models.SecurityPolicy(
                id=uuid4(),
                name=policy_data.name,
                description=policy_data.description,
                is_enabled=policy_data.is_enabled,
                config=policy_data.config or {},
                created_by=created_by,
                updated_by=created_by,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(db_policy)
            self.db.commit()
            self.db.refresh(db_policy)
            
            return db_policy
            
        except exceptions.SecurityPolicyError:
            raise
        except Exception as e:
            self.db.rollback()
            raise exceptions.SecurityPolicyError(f"Failed to create policy: {str(e)}")
    
    def get_policy(
        """Get Policy."""
        self,
        policy_id: Optional[UUID] = None,
        name: Optional[str] = None
    ) -> models.SecurityPolicy:
        """Get Policy."""
        """
        Retrieve a security policy by ID or name.
        
        Args:
            policy_id: ID of the policy to retrieve
            name: Name of the policy to retrieve
            
        Returns:
            The requested security policy
            
        Raises:
            SecurityPolicyNotFound: If no policy exists with the given ID or name
        """
        if not policy_id and not name:
            raise ValueError("Either policy_id or name must be provided")
        
        query = self.db.query(models.SecurityPolicy)
        
        if policy_id:
            query = query.filter(models.SecurityPolicy.id == policy_id)
        elif name:
            query = query.filter(models.SecurityPolicy.name == name)
        
        policy = query.first()
        
        if not policy:
            if policy_id:
                raise exceptions.SecurityPolicyNotFound(policy_id=policy_id)
            else:
                raise exceptions.SecurityPolicyNotFound(name=name)
        
        return policy
    
    def list_policies(
        """List Policies."""
        self,
        is_enabled: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "name",
        order_desc: bool = False
    ) -> Tuple[List[models.SecurityPolicy], int]:
        """List Policies."""
        """
        List security policies with filtering and pagination.
        
        Args:
            is_enabled: Filter by enabled status
            search: Search term to filter by name or description
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_desc: Whether to sort in descending order
            
        Returns:
            A tuple containing:
                - List of security policies
                - Total count of matching policies
        """
        query = self.db.query(models.SecurityPolicy)
        
        # Apply filters
        if is_enabled is not None:
            query = query.filter(models.SecurityPolicy.is_enabled == is_enabled)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.SecurityPolicy.name.ilike(search_term),
                    models.SecurityPolicy.description.ilike(search_term)
                )
            )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply ordering
        order_field = getattr(models.SecurityPolicy, order_by, models.SecurityPolicy.name)
        if order_desc:
            order_field = order_field.desc()
        query = query.order_by(order_field)
        
        # Apply pagination
        policies = query.offset(skip).limit(limit).all()
        
        return policies, total
    
    def update_policy(
        """Update Policy."""
        self,
        policy_id: UUID,
        policy_data: schemas.SecurityPolicyUpdate,
        updated_by: UUID
    ) -> models.SecurityPolicy:
        """Update Policy."""
        """
        Update a security policy.
        
        Args:
            policy_id: ID of the policy to update
            policy_data: The updated policy data
            updated_by: ID of the user updating the policy
            
        Returns:
            The updated security policy
            
        Raises:
            SecurityPolicyNotFound: If no policy exists with the given ID
            SecurityPolicyError: If there's an error updating the policy
        """
        try:
            policy = self.get_policy(policy_id=policy_id)
            
            # Update fields if provided
            if policy_data.description is not None:
                policy.description = policy_data.description
            
            if policy_data.is_enabled is not None:
                policy.is_enabled = policy_data.is_enabled
            
            if policy_data.config is not None:
                # Merge the config dictionaries
                policy.config = {**policy.config, **policy_data.config}
            
            # Update timestamps and updated_by
            policy.updated_at = datetime.utcnow()
            policy.updated_by = updated_by
            
            self.db.commit()
            self.db.refresh(policy)
            
            return policy
            
        except exceptions.SecurityPolicyNotFound:
            raise
        except Exception as e:
            self.db.rollback()
            raise exceptions.SecurityPolicyError(f"Failed to update policy: {str(e)}")
    
    def delete_policy(self, policy_id: UUID) -> None:
        """Delete Policy."""
        """
        Delete a security policy.
        
        Args:
            policy_id: ID of the policy to delete
            
        Raises:
            SecurityPolicyNotFound: If no policy exists with the given ID
            SecurityPolicyError: If there's an error deleting the policy
        """
        try:
            policy = self.get_policy(policy_id=policy_id)
            
            # Prevent deletion of system-required policies
            if policy.name in ["password_policy", "mfa_policy"]:
                raise exceptions.SecurityPolicyError(
                    f"Cannot delete system-required policy: {policy.name}"
                )
            
            self.db.delete(policy)
            self.db.commit()
            
        except exceptions.SecurityPolicyNotFound:
            raise
        except exceptions.SecurityPolicyError:
            raise
        except Exception as e:
            self.db.rollback()
            raise exceptions.SecurityPolicyError(f"Failed to delete policy: {str(e)}")
    
    def get_policy_config(
        """Get Policy Config."""
        self,
        policy_name: str,
        default_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get Policy Config."""
        """
        Get the configuration for a security policy by name.
        
        Args:
            policy_name: Name of the policy
            default_config: Default configuration to return if policy not found
            
        Returns:
            The policy configuration, or default_config if policy not found
        """
        try:
            policy = self.get_policy(name=policy_name)
            if policy and policy.is_enabled:
                return policy.config
            return default_config or {}
        except exceptions.SecurityPolicyNotFound:
            return default_config or {}
    
    def get_password_policy(self) -> Dict[str, Any]:
        """Get Password Policy."""
        """
        Get the current password policy configuration.
        
        Returns:
            The password policy configuration
        """
        default_policy = {
            "min_length": 12,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digits": True,
            "require_special_chars": True,
            "max_age_days": 90,
            "history_size": 5,
            "max_attempts": 5,
            "lockout_minutes": 30
        }
        
        return self.get_policy_config("password_policy", default_policy)
    
    def get_mfa_policy(self) -> Dict[str, Any]:
        """Get Mfa Policy."""
        """
        Get the current MFA policy configuration.
        
        Returns:
            The MFA policy configuration
        """
        default_policy = {
            "enabled": True,
            "required": False,
            "methods": ["totp", "sms", "email"],
            "default_method": "totp",
            "remember_days": 30,
            "max_attempts": 3
        }
        
        return self.get_policy_config("mfa_policy", default_policy)
    
    def get_login_policy(self) -> Dict[str, Any]:
        """Get Login Policy."""
        """
        Get the current login policy configuration.
        
        Returns:
            The login policy configuration
        """
        default_policy = {
            "max_attempts": 5,
            "lockout_minutes": 15,
            "ip_whitelist": [],
            "ip_blacklist": [],
            "require_verified_email": True,
            "require_verified_phone": False,
            "session_timeout_minutes": 1440,  # 24 hours
            "inactivity_timeout_minutes": 30
        }
        
        return self.get_policy_config("login_policy", default_policy)
    
    def get_audit_policy(self) -> Dict[str, Any]:
        """Get Audit Policy."""
        """
        Get the current audit policy configuration.
        
        Returns:
            The audit policy configuration
        """
        default_policy = {
            "enabled": True,
            "retention_days": 365,
            "log_failed_logins": True,
            "log_password_changes": True,
            "log_profile_updates": True,
            "log_security_events": True,
            "log_sensitive_operations": True,
            "alert_on_critical_events": True
        }
        
        return self.get_policy_config("audit_policy", default_policy)
    
    def get_data_retention_policy(self) -> Dict[str, Any]:
        """Get Data Retention Policy."""
        """
        Get the current data retention policy configuration.
        
        Returns:
            The data retention policy configuration
        """
        default_policy = {
            "enabled": True,
            "retention_periods": {
                "user_data": 365,  # days
                "audit_logs": 365,
                "security_events": 365,
                "system_logs": 90,
                "backups": 30,
                "temporary_files": 7
            },
            "auto_delete": True,
            "archive_before_delete": True,
            "notify_before_deletion": True,
            "notification_days_before": 30
        }
        
        return self.get_policy_config("data_retention_policy", default_policy)
    
    def get_privacy_policy(self) -> Dict[str, Any]:
        """Get Privacy Policy."""
        """
        Get the current privacy policy configuration.
        
        Returns:
            The privacy policy configuration
        """
        default_policy = {
            "data_collection_notice": True,
            "cookie_consent": True,
            "cookie_max_age_days": 365,
            "third_party_sharing": {
                "enabled": True,
                "require_consent": True,
                "partners": []
            },
            "right_to_be_forgotten": True,
            "data_portability": True,
            "contact_email": "privacy@example.com",
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return self.get_policy_config("privacy_policy", default_policy)
    
    def get_api_security_policy(self) -> Dict[str, Any]:
        """Get Api Security Policy."""
        """
        Get the current API security policy configuration.
        
        Returns:
            The API security policy configuration
        """
        default_policy = {
            "enabled": True,
            "rate_limiting": {
                "enabled": True,
                "max_requests_per_minute": 100,
                "max_requests_per_hour": 1000,
                "max_requests_per_day": 10000
            },
            "cors": {
                "enabled": True,
                "allowed_origins": ["*"],
                "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allowed_headers": ["Content-Type", "Authorization"],
                "allow_credentials": True,
                "max_age_seconds": 600
            },
            "authentication": {
                "require_authentication": True,
                "token_expiration_minutes": 1440,  # 24 hours
                "refresh_token_expiration_days": 30,
                "api_key_expiration_days": 90
            },
            "security_headers": {
                "strict_transport_security": True,
                "x_content_type_options": "nosniff",
                "x_frame_options": "DENY",
                "x_xss_protection": "1; mode=block",
                "content_security_policy": "default-src 'self'"
            }
        }
        
        return self.get_policy_config("api_security_policy", default_policy)
    
    def get_notification_policy(self) -> Dict[str, Any]:
        """Get Notification Policy."""
        """
        Get the current notification policy configuration.
        
        Returns:
            The notification policy configuration
        """
        default_policy = {
            "enabled": True,
            "default_provider": "email",
            "providers": {
                "email": {
                    "enabled": True,
                    "from_email": "noreply@example.com",
                    "from_name": "Paksa Financial System"
                },
                "sms": {
                    "enabled": False,
                    "from_number": None,
                    "provider": None
                },
                "push": {
                    "enabled": False,
                    "providers": []
                }
            },
            "templates": {
                "password_reset": {
                    "subject": "Password Reset Request",
                    "template": "password_reset.html"
                },
                "account_verification": {
                    "subject": "Verify Your Account",
                    "template": "account_verification.html"
                },
                "security_alert": {
                    "subject": "Security Alert",
                    "template": "security_alert.html"
                }
            }
        }
        
        return self.get_policy_config("notification_policy", default_policy)
    
    def get_backup_policy(self) -> Dict[str, Any]:
        """Get Backup Policy."""
        """
        Get the current backup policy configuration.
        
        Returns:
            The backup policy configuration
        """
        default_policy = {
            "enabled": True,
            "schedule": {
                "frequency": "daily",  # daily, weekly, monthly
                "time": "02:00",  # 2 AM
                "day_of_week": 0,  # 0 = Monday, 6 = Sunday
                "day_of_month": 1
            },
            "retention": {
                "keep_daily": 7,
                "keep_weekly": 4,
                "keep_monthly": 12,
                "keep_yearly": 5,
                "max_backups": 30
            },
            "storage": {
                "type": "local",  # local, s3, azure, gcp
                "path": "/var/backups/paksa",
                "encrypt": True,
                "compression": "gzip"
            },
            "notifications": {
                "on_success": True,
                "on_failure": True,
                "email_recipients": ["admin@example.com"]
            }
        }
        
        return self.get_policy_config("backup_policy", default_policy)
    
    def get_compliance_policy(self) -> Dict[str, Any]:
        """Get Compliance Policy."""
        """
        Get the current compliance policy configuration.
        
        Returns:
            The compliance policy configuration
        """
        default_policy = {
            "gdpr": {
                "enabled": True,
                "data_protection_officer": {
                    "name": "",
                    "email": "dpo@example.com",
                    "phone": ""
                },
                "data_retention": {
                    "default_retention_days": 365,
                    "user_data_retention_days": 365,
                    "log_retention_days": 90,
                    "backup_retention_days": 30
                },
                "rights_enforcement": {
                    "right_to_access": True,
                    "right_to_rectification": True,
                    "right_to_erasure": True,
                    "right_to_restrict_processing": True,
                    "right_to_data_portability": True,
                    "right_to_object": True,
                    "right_not_to_be_subject_to_automated_decision_making": True
                },
                "data_breach_notification": {
                    "notify_within_hours": 72,
                    "notify_authorities": True,
                    "notify_affected_users": True
                }
            },
            "ccpa": {
                "enabled": True,
                "do_not_sell_personal_information": True,
                "verification_required": True,
                "financial_incentive_notice": True
            },
            "hipaa": {
                "enabled": False,
                "baa_required": True,
                "encryption_required": True,
                "audit_logging_required": True
            },
            "pci_dss": {
                "enabled": False,
                "saq_type": "D",
                "external_vulnerability_scans": False,
                "internal_vulnerability_scans": False
            },
            "sox": {
                "enabled": False,
                "financial_reporting_controls": False,
                "change_management_controls": False,
                "access_controls": False
            }
        }
        
        return self.get_policy_config("compliance_policy", default_policy)
    
    def get_security_headers_policy(self) -> Dict[str, Any]:
        """Get Security Headers Policy."""
        """
        Get the current security headers policy configuration.
        
        Returns:
            The security headers policy configuration
        """
        default_policy = {
            "strict_transport_security": {
                "enabled": True,
                "max_age_seconds": 31536000,  # 1 year
                "include_subdomains": True,
                "preload": True
            },
            "x_content_type_options": {
                "enabled": True,
                "value": "nosniff"
            },
            "x_frame_options": {
                "enabled": True,
                "value": "DENY"
            },
            "x_xss_protection": {
                "enabled": True,
                "value": "1; mode=block"
            },
            "content_security_policy": {
                "enabled": True,
                "value": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self';"
            },
            "referrer_policy": {
                "enabled": True,
                "value": "strict-origin-when-cross-origin"
            },
            "permissions_policy": {
                "enabled": True,
                "value": "geolocation=(), microphone=(), camera=()"
            },
            "feature_policy": {
                "enabled": False,
                "value": "geolocation 'none'; microphone 'none'; camera 'none'"
            },
            "expect_ct": {
                "enabled": False,
                "max_age_seconds": 86400,
                "enforce": False,
                "report_uri": ""
            },
            "report_to": {
                "enabled": False,
                "groups": [
                    {
                        "name": "default",
                        "max_age": 10886400,
                        "endpoints": [{"url": "/reporting"}],
                        "include_subdomains": True
                    }
                ]
            },
            "permissions_policy_directive": {
                "enabled": True,
                "directives": {
                    "accelerometer": [],
                    "ambient-light-sensor": [],
                    "autoplay": [],
                    "battery": [],
                    "camera": [],
                    "display-capture": [],
                    "document-domain": [],
                    "encrypted-media": [],
                    "execution-while-not-rendered": [],
                    "execution-while-out-of-viewport": [],
                    "fullscreen": [],
                    "geolocation": [],
                    "gyroscope": [],
                    "magnetometer": [],
                    "microphone": [],
                    "midi": [],
                    "navigation-override": [],
                    "payment": [],
                    "picture-in-picture": [],
                    "publickey-credentials": [],
                    "sync-xhr": [],
                    "usb": [],
                    "web-share": [],
                    "xr-spatial-tracking": []
                }
            }
        }
        
        return self.get_policy_config("security_headers_policy", default_policy)
