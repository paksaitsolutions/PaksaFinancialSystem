"""
Fixed Assets models for the financial system.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, 
    CheckConstraint, 
    Column, 
    Date, 
    DateTime, 
    Enum as SQLEnum, 
    ForeignKey, 
    Integer,
    Numeric, 
    String, 
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from core.database import Base


class AssetStatus(str, Enum):
    """Status of a fixed asset."""
    ACTIVE = 'active'  # In use and being depreciated
    IDLE = 'idle'  # Not in use but available
    UNDER_MAINTENANCE = 'under_maintenance'  # Being repaired or maintained
    DISPOSED = 'disposed'  # Sold, scrapped, or otherwise disposed of
    LOST_OR_STOLEN = 'lost_or_stolen'  # Missing or stolen
    IN_TRANSIT = 'in_transit'  # Being moved between locations
    LEASED = 'leased'  # Leased to another party
    RETIRED = 'retired'  # No longer in use but still owned


class AssetCondition(str, Enum):
    """Physical condition of a fixed asset."""
    NEW = 'new'  # Brand new, never used
    EXCELLENT = 'excellent'  # Like new, minimal wear
    GOOD = 'good'  # Normal wear and tear
    FAIR = 'fair'  # Noticeable wear, may need maintenance
    POOR = 'poor'  # Significant wear, needs maintenance or replacement
    UNUSABLE = 'unusable'  # Not functional, requires repair or disposal


class DepreciationMethod(str, Enum):
    """Methods for calculating asset depreciation."""
    STRAIGHT_LINE = 'straight_line'  # Equal amounts each period
    DOUBLE_DECLINING = 'double_declining'  # Accelerated depreciation
    SUM_OF_YEARS = 'sum_of_years'  # Accelerated depreciation
    UNITS_OF_PRODUCTION = 'units_of_production'  # Based on usage
    TAX = 'tax'  # Tax-specific depreciation (e.g., MACRS, Section 179)
    NONE = 'none'  # Land or assets not depreciated


class AssetCategory(Base):
    """Categories for classifying fixed assets."""
    __tablename__ = 'asset_category'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Default accounting settings
    default_asset_account_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('account.id'))
    default_depreciation_expense_account_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('account.id'))
    default_accumulated_depreciation_account_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('account.id'))
    default_gain_loss_account_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('account.id'))
    default_depreciation_method: Mapped[DepreciationMethod] = mapped_column(
        SQLEnum(DepreciationMethod), 
        default=DepreciationMethod.STRAIGHT_LINE,
        nullable=False,
    )
    default_useful_life_years: Mapped[Optional[int]]  # Default useful life in years
    
    # Relationships
    assets: Mapped[List['Asset']] = relationship('Asset', back_populates='category')
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    def __repr__(self) -> str:
        return f'<AssetCategory {self.name}>'


class Asset(Base):
    """Fixed asset model for tracking company assets."""
    __tablename__ = 'asset'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    asset_number: Mapped[Optional[str]] = mapped_column(String(50), unique=True)  # Internal asset ID
    serial_number: Mapped[Optional[str]] = mapped_column(String(100))  # Manufacturer's serial number
    barcode: Mapped[Optional[str]] = mapped_column(String(100), unique=True)  # Barcode/UPC
    
    # Asset details
    description: Mapped[Optional[str]] = mapped_column(Text)
    model: Mapped[Optional[str]] = mapped_column(String(100))  # Model name/number
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    purchase_order: Mapped[Optional[str]] = mapped_column(String(50))  # PO number
    
    # Acquisition details
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    purchase_cost: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False, default=0)
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)  # Actual price paid
    sales_tax: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    installation_cost: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    other_costs: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    
    # Depreciation details
    depreciation_method: Mapped[DepreciationMethod] = mapped_column(
        SQLEnum(DepreciationMethod), 
        default=DepreciationMethod.STRAIGHT_LINE,
        nullable=False,
    )
    useful_life_years: Mapped[Optional[int]]  # In years
    useful_life_units: Mapped[Optional[int]]  # For units of production method
    salvage_value: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    start_depreciation_date: Mapped[Optional[date]]  # When depreciation begins
    
    # Current status
    status: Mapped[AssetStatus] = mapped_column(
        SQLEnum(AssetStatus), 
        default=AssetStatus.ACTIVE,
        nullable=False,
    )
    condition: Mapped[Optional[AssetCondition]] = mapped_column(SQLEnum(AssetCondition))
    location: Mapped[Optional[str]] = mapped_column(String(200))  # Physical location
    
    # Insurance
    insured: Mapped[bool] = mapped_column(Boolean, default=False)
    insurance_policy_number: Mapped[Optional[str]] = mapped_column(String(100))
    insurance_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(19, 4))
    insurance_expiry: Mapped[Optional[date]]
    
    # Warranty
    under_warranty: Mapped[bool] = mapped_column(Boolean, default=False)
    warranty_expiry: Mapped[Optional[date]]
    warranty_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Disposal
    disposed_date: Mapped[Optional[date]]
    disposal_method: Mapped[Optional[str]] = mapped_column(String(50))  # Sold, scrapped, donated, etc.
    disposal_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(19, 4))  # Proceeds from disposal
    disposal_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    category_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('asset_category.id'), nullable=False)
    category: Mapped[AssetCategory] = relationship('AssetCategory', back_populates='assets')
    
    # Accounting integration
    asset_account_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('account.id'))
    accumulated_depreciation_account_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('account.id'))
    depreciation_expense_account_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('account.id'))
    gain_loss_account_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('account.id'))
    
    # Journal entries
    acquisition_journal_entry_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('journal_entry.id'))
    disposal_journal_entry_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('journal_entry.id'))
    
    # Maintenance and history
    maintenance_records: Mapped[List['MaintenanceRecord']] = relationship('MaintenanceRecord', back_populates='asset')
    depreciation_schedules: Mapped[List['DepreciationSchedule']] = relationship('DepreciationSchedule', back_populates='asset')
    asset_transfers: Mapped[List['AssetTransfer']] = relationship('AssetTransfer', back_populates='asset')
    
    # Metadata
    tags: Mapped[Optional[List[str]]] = mapped_column(JSONB)  # For categorization and filtering
    custom_fields: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    # Computed properties
    @property
    def total_cost(self) -> Decimal:
        """Calculate the total capitalized cost of the asset."""
        return (
            self.purchase_price + 
            self.sales_tax + 
            self.shipping_cost + 
            self.installation_cost + 
            self.other_costs
        )
    
    @property
    def current_book_value(self) -> Decimal:
        """Calculate the current book value (cost - accumulated depreciation)."""
        if not self.depreciation_schedules:
            return self.total_cost
        
        latest_schedule = max(
            self.depreciation_schedules, 
            key=lambda x: x.end_date if x.end_date else date.min
        )
        return latest_step.book_value
    
    @property
    def accumulated_depreciation(self) -> Decimal:
        """Calculate total accumulated depreciation to date."""
        return self.total_cost - self.current_book_value
    
    def __repr__(self) -> str:
        return f'<Asset {self.name} ({self.asset_number or "No ID"})>'


class MaintenanceRecord(Base):
    """Maintenance and service records for fixed assets."""
    __tablename__ = 'maintenance_record'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Maintenance details
    maintenance_date: Mapped[date] = mapped_column(Date, nullable=False)
    maintenance_type: Mapped[str] = mapped_column(String(50))  # e.g., 'Preventive', 'Corrective', 'Inspection'
    summary: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Service provider
    service_provider: Mapped[Optional[str]] = mapped_column(String(100))
    service_contact: Mapped[Optional[str]] = mapped_column(String(100))
    service_phone: Mapped[Optional[str]] = mapped_column(String(20))
    service_email: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Cost and parts
    labor_cost: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    parts_cost: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=0)
    
    # Dates
    start_time: Mapped[Optional[datetime]]
    end_time: Mapped[Optional[datetime]]
    next_maintenance_date: Mapped[Optional[date]]
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default='completed')  # scheduled, in_progress, completed, cancelled
    
    # Asset relationship
    asset_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('asset.id'), nullable=False)
    asset: Mapped[Asset] = relationship('Asset', back_populates='maintenance_records')
    
    # Accounting integration
    expense_account_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('account.id'))
    journal_entry_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('journal_entry.id'))
    
    # Attachments and documents
    document_reference: Mapped[Optional[str]] = mapped_column(String(200))  # Path to document
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    def __repr__(self) -> str:
        return f'<MaintenanceRecord {self.maintenance_date} - {self.summary}>'


class DepreciationSchedule(Base):
    """Depreciation schedule for fixed assets."""
    __tablename__ = 'depreciation_schedule'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Period information
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    period: Mapped[int] = mapped_column(Integer, nullable=False)  # Month number or period number
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Depreciation amounts
    depreciation_amount: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    accumulated_depreciation: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    book_value: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)
    
    # Status
    is_posted: Mapped[bool] = mapped_column(Boolean, default=False)
    posted_date: Mapped[Optional[date]]
    
    # Asset relationship
    asset_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('asset.id'), nullable=False)
    asset: Mapped[Asset] = relationship('Asset', back_populates='depreciation_schedules')
    
    # Accounting integration
    journal_entry_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('journal_entry.id'))
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    def __repr__(self) -> str:
        return f'<DepreciationSchedule {self.asset_id} - {self.fiscal_year}-{self.period}>'


class AssetTransfer(Base):
    """Asset transfer history between locations or departments."""
    __tablename__ = 'asset_transfer'
    
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Transfer details
    transfer_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    transfer_reason: Mapped[Optional[str]] = mapped_column(String(200))
    transfer_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Location information
    from_location: Mapped[Optional[str]] = mapped_column(String(200))
    to_location: Mapped[Optional[str]] = mapped_column(String(200), nullable=False)
    
    # Department/Cost center
    from_department: Mapped[Optional[str]] = mapped_column(String(100))
    to_department: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Asset relationship
    asset_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('asset.id'), nullable=False)
    asset: Mapped[Asset] = relationship('Asset', back_populates='asset_transfers')
    
    # Responsible parties
    transferred_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    received_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    # Created by/updated by
    created_by_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey('user.id'))
    
    def __repr__(self) -> str:
        return f'<AssetTransfer {self.asset_id} to {self.to_location}>'
