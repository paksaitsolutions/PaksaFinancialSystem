"""
Tax models for compliance and reporting.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, Numeric, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel, GUID

class ComplianceCheck(BaseModel):
    """Model for compliance check records."""
    __tablename__ = "compliance_checks"
    
    check_id = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(20), nullable=False)  # passed, failed, warning, pending
    entity_id = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    check_type = Column(String(50), nullable=False)  # transaction, customer, vendor, report, document
    passed_rules = Column(JSON, default=list)
    failed_rules = Column(JSON, default=list)
    warnings = Column(JSON, default=list)
    check_metadata = Column(JSON, default=dict)
    next_check = Column(DateTime, nullable=True)
    created_by = Column(GUID, nullable=True)

class ComplianceRule(BaseModel):
    """Model for compliance rules."""
    __tablename__ = "compliance_rules"
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    check_type = Column(String(50), nullable=False)
    jurisdiction = Column(String(10), nullable=False)
    entity_types = Column(JSON, default=list)  # List of entity types this rule applies to
    severity = Column(String(20), nullable=False, default='medium')  # low, medium, high, critical
    rule_config = Column(JSON, default=dict)  # Rule configuration and parameters
    is_active = Column(Boolean, default=True)
    created_by = Column(GUID, nullable=True)
    updated_by = Column(GUID, nullable=True)

class ComplianceAlert(BaseModel):
    """Model for compliance alerts."""
    __tablename__ = "compliance_alerts"
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    status = Column(String(20), nullable=False, default='open')  # open, acknowledged, resolved
    check_id = Column(String(100), nullable=True)
    entity_id = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    details = Column(JSON, default=dict)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(GUID, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_by = Column(GUID, nullable=True)

class TaxTransaction(BaseModel):
    """Model for tax transactions."""
    __tablename__ = "tax_transactions"
    
    transaction_id = Column(String(100), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # sale, purchase, payment, etc.
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0)
    jurisdiction = Column(String(10), nullable=False)
    from_party = Column(String(200), nullable=True)
    to_party = Column(String(200), nullable=True)
    status = Column(String(20), nullable=False, default='pending')
    transaction_metadata = Column(JSON, default=dict)
    created_by = Column(GUID, nullable=True)

class TaxRateCompliance(BaseModel):
    """Model for tax rates compliance."""
    __tablename__ = "tax_rates_compliance"
    
    tax_type = Column(String(50), nullable=False)  # sales, vat, gst, income, etc.
    jurisdiction = Column(String(10), nullable=False)
    rate = Column(Numeric(5, 4), nullable=False)  # Tax rate as decimal (e.g., 0.0825 for 8.25%)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(GUID, nullable=True)
    updated_by = Column(GUID, nullable=True)

class TaxJurisdictionCompliance(BaseModel):
    """Model for tax jurisdictions compliance."""
    __tablename__ = "tax_jurisdictions_compliance"
    
    name = Column(String(200), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    country = Column(String(2), nullable=False)  # ISO country code
    state = Column(String(10), nullable=True)  # State/province code
    tax_types = Column(JSON, default=list)  # List of tax types applicable
    compliance_requirements = Column(JSON, default=list)  # List of compliance requirements
    filing_frequency = Column(String(20), nullable=False, default='monthly')
    next_filing_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(GUID, nullable=True)
    updated_by = Column(GUID, nullable=True)

class TaxFilingCompliance(BaseModel):
    """Model for tax filings compliance."""
    __tablename__ = "tax_filings_compliance"
    
    filing_reference = Column(String(100), unique=True, nullable=False)
    tax_type = Column(String(50), nullable=False)
    jurisdiction_code = Column(String(10), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    filing_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default='draft')  # draft, prepared, submitted, accepted, rejected, paid
    total_amount = Column(Numeric(15, 2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default='USD')
    filing_data = Column(JSON, default=dict)
    submission_reference = Column(String(100), nullable=True)
    created_by = Column(GUID, nullable=True)
    updated_by = Column(GUID, nullable=True)

class TaxExemptionCompliance(BaseModel):
    """Model for tax exemptions compliance."""
    __tablename__ = "tax_exemptions_compliance"
    
    exemption_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    tax_types = Column(JSON, default=list)  # Tax types this exemption applies to
    jurisdictions = Column(JSON, default=list)  # Jurisdictions where this exemption is valid
    certificate_required = Column(Boolean, default=False)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    company_id = Column(GUID, nullable=True)  # If company-specific
    created_by = Column(GUID, nullable=True)
    updated_by = Column(GUID, nullable=True)

class TaxExemptionCertificate(BaseModel):
    """Model for tax exemption certificates."""
    __tablename__ = "tax_exemption_certificates"
    
    certificate_number = Column(String(100), unique=True, nullable=False)
    customer_id = Column(GUID, nullable=True)
    customer_tax_id = Column(String(50), nullable=True)
    customer_name = Column(String(200), nullable=False)
    exemption_type = Column(String(50), nullable=False)
    issuing_jurisdiction = Column(String(10), nullable=False)
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    tax_codes = Column(JSON, default=list)  # Tax codes this certificate covers
    jurisdictions = Column(JSON, default=list)  # Jurisdictions where valid
    document_reference = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_valid = Column(Boolean, default=True)
    created_by = Column(GUID, nullable=True)
    updated_by = Column(GUID, nullable=True)

class ComplianceSchedule(BaseModel):
    """Model for scheduled compliance checks."""
    __tablename__ = "compliance_schedules"
    
    name = Column(String(200), nullable=False)
    check_type = Column(String(50), nullable=False)
    entity_id = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    jurisdiction = Column(String(10), nullable=False)
    frequency = Column(String(20), nullable=False)  # hourly, daily, weekly, monthly
    next_run = Column(DateTime, nullable=False)
    last_run = Column(DateTime, nullable=True)
    rules = Column(JSON, default=list)  # List of rule IDs to apply
    is_active = Column(Boolean, default=True)
    created_by = Column(GUID, nullable=True)
    updated_by = Column(GUID, nullable=True)

class ComplianceSettings(BaseModel):
    """Model for compliance settings."""
    __tablename__ = "compliance_settings"
    
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False)  # System settings vs user settings
    company_id = Column(GUID, nullable=True)  # Company-specific settings
    user_id = Column(GUID, nullable=True)  # User-specific settings
    created_by = Column(GUID, nullable=True)
    updated_by = Column(GUID, nullable=True)