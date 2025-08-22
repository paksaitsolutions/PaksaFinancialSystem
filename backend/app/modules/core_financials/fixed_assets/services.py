<<<<<<< HEAD
"""
Fixed Assets Module - Services
"""
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict, Any, Tuple, Union
from uuid import UUID, uuid4

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, text, update, case, cast, Date, Integer, Numeric

from app.core.exceptions import NotFoundError, ValidationError, BusinessRuleError
from app.core.database import Base
from . import models, schemas
from ..accounting.models import GLAccount, JournalEntry, JournalEntryLine, AccountType
from ..accounting.schemas import JournalEntryCreate, JournalEntryLineCreate


class FixedAssetService:
    """Service class for fixed assets operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Asset Category Methods
    def create_asset_category(self, category: schemas.AssetCategoryCreate, user_id: UUID) -> models.AssetCategory:
        """Create a new asset category."""
        # Check if category with same name already exists
        existing = self.db.query(models.AssetCategory).filter(
            func.lower(models.AssetCategory.name) == func.lower(category.name)
        ).first()
        
        if existing:
            raise ValidationError(f"Asset category with name '{category.name}' already exists")
        
        # Create new category
        db_category = models.AssetCategory(
            **category.dict(exclude={"metadata"}),
            id=uuid4(),
            created_by_id=user_id,
            updated_by_id=user_id,
            metadata=category.metadata or {}
        )
        
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def get_asset_category(self, category_id: UUID) -> models.AssetCategory:
        """Get an asset category by ID."""
        category = self.db.query(models.AssetCategory).get(category_id)
        if not category:
            raise NotFoundError(f"Asset category with ID {category_id} not found")
        return category
    
    def list_asset_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> Tuple[List[models.AssetCategory], int]:
        """List asset categories with optional search and pagination."""
        query = self.db.query(models.AssetCategory)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.AssetCategory.name.ilike(search_term),
                    models.AssetCategory.description.ilike(search_term)
                )
            )
        
        total = query.count()
        categories = query.order_by(models.AssetCategory.name).offset(skip).limit(limit).all()
        
        return categories, total
    
    def update_asset_category(
        self, 
        category_id: UUID, 
        category_update: schemas.AssetCategoryUpdate, 
        user_id: UUID
    ) -> models.AssetCategory:
        """Update an asset category."""
        db_category = self.get_asset_category(category_id)
        
        # Check if name is being changed and if it's already in use
        if category_update.name and category_update.name.lower() != db_category.name.lower():
            existing = self.db.query(models.AssetCategory).filter(
                func.lower(models.AssetCategory.name) == category_update.name.lower(),
                models.AssetCategory.id != category_id
            ).first()
            
            if existing:
                raise ValidationError(f"Asset category with name '{category_update.name}' already exists")
        
        # Update fields
        update_data = category_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        db_category.updated_by_id = user_id
        db_category.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def delete_asset_category(self, category_id: UUID) -> None:
        """Delete an asset category."""
        db_category = self.get_asset_category(category_id)
        
        # Check if category is in use
        asset_count = self.db.query(models.Asset).filter(
            models.Asset.category_id == category_id
        ).count()
        
        if asset_count > 0:
            raise BusinessRuleError(
                f"Cannot delete category with {asset_count} associated assets. "
                "Reassign or delete the assets first."
            )
        
        self.db.delete(db_category)
        self.db.commit()
    
    # Asset Methods
    def create_asset(self, asset: schemas.AssetCreate, user_id: UUID) -> models.Asset:
        """Create a new fixed asset."""
        # Validate category exists
        category = self.get_asset_category(asset.category_id)
        
        # Set default values from category if not provided
        if not hasattr(asset, 'depreciation_method') or not asset.depreciation_method:
            asset.depreciation_method = category.default_depreciation_method
        
        if not hasattr(asset, 'useful_life_years') or not asset.useful_life_years:
            asset.useful_life_years = category.default_useful_life_years
        
        # Set default accounts from category if not provided
        if not hasattr(asset, 'asset_account_id') or not asset.asset_account_id:
            asset.asset_account_id = category.default_asset_account_id
        
        if not hasattr(asset, 'depreciation_expense_account_id') or not asset.depreciation_expense_account_id:
            asset.depreciation_expense_account_id = category.default_depreciation_expense_account_id
            
        if not hasattr(asset, 'accumulated_depreciation_account_id') or not asset.accumulated_depreciation_account_id:
            asset.accumulated_depreciation_account_id = category.default_accumulated_depreciation_account_id
            
        if not hasattr(asset, 'gain_loss_account_id') or not asset.gain_loss_account_id:
            asset.gain_loss_account_id = category.default_gain_loss_account_id
        
        # Calculate total cost
        total_cost = (
            (asset.purchase_price or Decimal('0')) +
            (asset.sales_tax or Decimal('0')) +
            (asset.shipping_cost or Decimal('0')) +
            (asset.installation_cost or Decimal('0')) +
            (asset.other_costs or Decimal('0'))
        )
        
        # Create asset
        db_asset = models.Asset(
            **asset.dict(
                exclude={"metadata", "purchase_price", "sales_tax", "shipping_cost", "installation_cost", "other_costs"},
                exclude_unset=True
            ),
            id=uuid4(),
            purchase_cost=total_cost,
            created_by_id=user_id,
            updated_by_id=user_id,
            metadata=asset.metadata or {}
        )
        
        # Create acquisition journal entry if accounting integration is enabled
        if all([
            db_asset.asset_account_id,
            db_asset.depreciation_expense_account_id,
            db_asset.accumulated_depreciation_account_id
        ]):
            self._create_asset_acquisition_entry(db_asset, user_id)
        
        # Generate depreciation schedule
        if db_asset.depreciation_method != schemas.DepreciationMethod.NONE and db_asset.useful_life_years:
            self._generate_depreciation_schedule(db_asset, user_id)
        
        self.db.add(db_asset)
        self.db.commit()
        self.db.refresh(db_asset)
        return db_asset
    
    def get_asset(self, asset_id: UUID, include_details: bool = False) -> models.Asset:
        """Get a fixed asset by ID with optional related data."""
        query = self.db.query(models.Asset)
        
        if include_details:
            query = query.options(
                joinedload(models.Asset.category),
                joinedload(models.Asset.maintenance_records),
                joinedload(models.Asset.depreciation_schedules),
                joinedload(models.Asset.asset_transfers)
            )
        
        asset = query.get(asset_id)
        
        if not asset:
            raise NotFoundError(f"Asset with ID {asset_id} not found")
            
        return asset
    
    def list_assets(
        self,
        category_id: Optional[UUID] = None,
        status: Optional[schemas.AssetStatus] = None,
        location: Optional[str] = None,
        department: Optional[str] = None,
        acquired_after: Optional[date] = None,
        acquired_before: Optional[date] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[models.Asset], int]:
        """List fixed assets with filtering and pagination."""
        query = self.db.query(models.Asset)
        
        # Apply filters
        if category_id:
            query = query.filter(models.Asset.category_id == category_id)
            
        if status:
            query = query.filter(models.Asset.status == status)
            
        if location:
            query = query.filter(models.Asset.location.ilike(f"%{location}%"))
            
        if department:
            query = query.filter(models.Asset.department.ilike(f"%{department}%"))
            
        if acquired_after:
            query = query.filter(models.Asset.purchase_date >= acquired_after)
            
        if acquired_before:
            query = query.filter(models.Asset.purchase_date <= acquired_before)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.Asset.name.ilike(search_term),
                    models.Asset.asset_number.ilike(search_term),
                    models.Asset.serial_number.ilike(search_term),
                    models.Asset.description.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        assets = query.order_by(models.Asset.purchase_date.desc()).offset(skip).limit(limit).all()
        
        return assets, total
    
    def update_asset(
        self, 
        asset_id: UUID, 
        asset_update: schemas.AssetUpdate, 
        user_id: UUID
    ) -> models.Asset:
        """Update a fixed asset."""
        db_asset = self.get_asset(asset_id)
        
        # Check if asset is disposed
        if db_asset.status == schemas.AssetStatus.DISPOSED:
            raise BusinessRuleError("Cannot update a disposed asset")
        
        # Update fields
        update_data = asset_update.dict(exclude_unset=True)
        
        # Handle status changes
        if 'status' in update_data and update_data['status'] != db_asset.status:
            new_status = update_data['status']
            
            # Handle asset disposal
            if new_status == schemas.AssetStatus.DISPOSED:
                if 'disposed_date' not in update_data:
                    update_data['disposed_date'] = date.today()
                
                # Create disposal journal entry if accounting integration is enabled
                if all([
                    db_asset.asset_account_id,
                    db_asset.accumulated_depreciation_account_id,
                    db_asset.gain_loss_account_id
                ]):
                    self._create_asset_disposal_entry(db_asset, user_id)
        
        # Update the asset
        for field, value in update_data.items():
            setattr(db_asset, field, value)
        
        db_asset.updated_by_id = user_id
        db_asset.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_asset)
        return db_asset
    
    def delete_asset(self, asset_id: UUID) -> None:
        """Delete a fixed asset."""
        db_asset = self.get_asset(asset_id)
        
        # Check if asset has transactions
        has_transactions = (
            self.db.query(models.DepreciationSchedule)
            .filter(models.DepreciationSchedule.asset_id == asset_id)
            .first() is not None
        )
        
        if has_transactions:
            raise BusinessRuleError(
                "Cannot delete an asset with associated transactions. "
                "Consider marking it as disposed instead."
            )
        
        # Delete related records
        self.db.query(models.MaintenanceRecord).filter(
            models.MaintenanceRecord.asset_id == asset_id
        ).delete(synchronize_session=False)
        
        self.db.query(models.DepreciationSchedule).filter(
            models.DepreciationSchedule.asset_id == asset_id
        ).delete(synchronize_session=False)
        
        self.db.query(models.AssetTransfer).filter(
            models.AssetTransfer.asset_id == asset_id
        ).delete(synchronize_session=False)
        
        # Delete the asset
        self.db.delete(db_asset)
        self.db.commit()
    
    # Maintenance Record Methods
    def create_maintenance_record(
        self, 
        record: schemas.MaintenanceRecordCreate, 
        user_id: UUID
    ) -> models.MaintenanceRecord:
        """Create a new maintenance record for an asset."""
        # Validate asset exists
        asset = self.get_asset(record.asset_id)
        
        # Calculate total cost
        total_cost = (record.labor_cost or Decimal('0')) + (record.parts_cost or Decimal('0'))
        
        # Create maintenance record
        db_record = models.MaintenanceRecord(
            **record.dict(exclude={"metadata"}, exclude_unset=True),
            id=uuid4(),
            total_cost=total_cost,
            created_by_id=user_id,
            updated_by_id=user_id,
            metadata=record.metadata or {}
        )
        
        # Create journal entry for maintenance cost if accounting integration is enabled
        if all([
            asset.asset_account_id,
            record.expense_account_id
        ]):
            self._create_maintenance_journal_entry(asset, db_record, user_id)
        
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record
    
    def get_maintenance_record(self, record_id: UUID) -> models.MaintenanceRecord:
        """Get a maintenance record by ID."""
        record = self.db.query(models.MaintenanceRecord).get(record_id)
        if not record:
            raise NotFoundError(f"Maintenance record with ID {record_id} not found")
        return record
    
    def list_maintenance_records(
        self,
        asset_id: Optional[UUID] = None,
        maintenance_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[models.MaintenanceRecord], int]:
        """List maintenance records with filtering and pagination."""
        query = self.db.query(models.MaintenanceRecord)
        
        # Apply filters
        if asset_id:
            query = query.filter(models.MaintenanceRecord.asset_id == asset_id)
            
        if maintenance_type:
            query = query.filter(models.MaintenanceRecord.maintenance_type == maintenance_type)
            
        if start_date:
            query = query.filter(models.MaintenanceRecord.maintenance_date >= start_date)
            
        if end_date:
            query = query.filter(models.MaintenanceRecord.maintenance_date <= end_date)
            
        if status:
            query = query.filter(models.MaintenanceRecord.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        records = query.order_by(
            models.MaintenanceRecord.maintenance_date.desc()
        ).offset(skip).limit(limit).all()
        
        return records, total
    
    def update_maintenance_record(
        self, 
        record_id: UUID, 
        record_update: schemas.MaintenanceRecordUpdate, 
        user_id: UUID
    ) -> models.MaintenanceRecord:
        """Update a maintenance record."""
        db_record = self.get_maintenance_record(record_id)
        
        # Update fields
        update_data = record_update.dict(exclude_unset=True)
        
        # Recalculate total cost if labor_cost or parts_cost are updated
        if 'labor_cost' in update_data or 'parts_cost' in update_data:
            labor_cost = update_data.get('labor_cost', db_record.labor_cost or Decimal('0'))
            parts_cost = update_data.get('parts_cost', db_record.parts_cost or Decimal('0'))
            update_data['total_cost'] = labor_cost + parts_cost
        
        for field, value in update_data.items():
            setattr(db_record, field, value)
        
        db_record.updated_by_id = user_id
        db_record.updated_at = datetime.utcnow()
        
        # TODO: Update journal entry if accounting integration is enabled
        
        self.db.commit()
        self.db.refresh(db_record)
        return db_record
    
    def delete_maintenance_record(self, record_id: UUID) -> None:
        """Delete a maintenance record."""
        db_record = self.get_maintenance_record(record_id)
        
        # TODO: Reverse journal entry if accounting integration is enabled
        
        self.db.delete(db_record)
        self.db.commit()
    
    # Depreciation Methods
    def calculate_depreciation(
        self,
        asset: models.Asset,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate depreciation for an asset up to the specified date.
        
        Args:
            asset: The asset to calculate depreciation for
            as_of_date: Date to calculate depreciation up to (defaults to today)
            
        Returns:
            Dict containing depreciation details
        """
        if not as_of_date:
            as_of_date = date.today()
        
        if asset.depreciation_method == schemas.DepreciationMethod.NONE or not asset.useful_life_years:
            return {
                'depreciation_method': asset.depreciation_method,
                'useful_life_years': asset.useful_life_years,
                'months_depreciated': 0,
                'months_remaining': 0,
                'depreciation_to_date': Decimal('0'),
                'current_book_value': asset.purchase_cost,
                'depreciation_expense': Decimal('0')
            }
        
        # Get the depreciation start date (either the asset's start date or purchase date)
        start_date = asset.start_depreciation_date or asset.purchase_date
        
        # Calculate months between dates
        months_since_purchase = (as_of_date.year - start_date.year) * 12 + (as_of_date.month - start_date.month)
        months_since_purchase = max(0, months_since_purchase)  # Ensure not negative
        
        total_months = asset.useful_life_years * 12
        months_depreciated = min(months_since_purchase, total_months)
        months_remaining = max(0, total_months - months_depreciated)
        
        # Calculate depreciation amounts based on method
        if asset.depreciation_method == schemas.DepreciationMethod.STRAIGHT_LINE:
            monthly_depreciation = (asset.purchase_cost - asset.salvage_value) / total_months
            depreciation_to_date = monthly_depreciation * months_depreciated
            current_book_value = max(asset.salvage_value, asset.purchase_cost - depreciation_to_date)
            
            # Current period depreciation (last month)
            current_month_depreciation = (
                monthly_depreciation 
                if months_depreciated > 0 and months_depreciated <= total_months 
                else Decimal('0')
            )
            
        elif asset.depreciation_method == schemas.DepreciationMethod.DOUBLE_DECLINING:
            # Double declining balance method
            book_value = asset.purchase_cost
            remaining_life = total_months
            depreciation_to_date = Decimal('0')
            
            for _ in range(months_depreciated):
                if remaining_life <= 0:
                    break
                    
                # Calculate monthly rate (double the straight-line rate)
                monthly_rate = (2 / total_months) / 100
                monthly_depreciation = book_value * monthly_rate
                
                # Ensure we don't depreciate below salvage value
                if book_value - monthly_depreciation < asset.salvage_value:
                    monthly_depreciation = book_value - asset.salvage_value
                
                depreciation_to_date += monthly_depreciation
                book_value -= monthly_depreciation
                remaining_life -= 1
            
            current_book_value = max(asset.salvage_value, asset.purchase_cost - depreciation_to_date)
            
            # For current period, we'd need to calculate just the current month's depreciation
            # This is a simplification - in practice, you'd want to track each period separately
            if months_depreciated > 0 and months_depreciated <= total_months:
                temp_book_value = asset.purchase_cost
                for _ in range(months_depreciated - 1):
                    if temp_book_value <= asset.salvage_value:
                        break
                    monthly_rate = (2 / total_months) / 100
                    monthly_depreciation = temp_book_value * monthly_rate
                    if temp_book_value - monthly_depreciation < asset.salvage_value:
                        monthly_depreciation = temp_book_value - asset.salvage_value
                    temp_book_value -= monthly_depreciation
                
                current_month_depreciation = min(
                    temp_book_value - asset.salvage_value,
                    temp_book_value * (2 / total_months) / 100
                )
                if current_month_depreciation < 0:
                    current_month_depreciation = Decimal('0')
            else:
                current_month_depreciation = Decimal('0')
                
        else:
            # For simplicity, default to straight-line if method not implemented
            monthly_depreciation = (asset.purchase_cost - asset.salvage_value) / total_months
            depreciation_to_date = monthly_depreciation * months_depreciated
            current_book_value = max(asset.salvage_value, asset.purchase_cost - depreciation_to_date)
            current_month_depreciation = monthly_depreciation if months_depreciated > 0 else Decimal('0')
        
        return {
            'depreciation_method': asset.depreciation_method,
            'useful_life_years': asset.useful_life_years,
            'months_depreciated': months_depreciated,
            'months_remaining': months_remaining,
            'depreciation_to_date': depreciation_to_date.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            'current_book_value': current_book_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            'depreciation_expense': current_month_depreciation.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        }
    
    def generate_depreciation_schedule(
        self,
        asset_id: UUID,
        user_id: UUID
    ) -> List[models.DepreciationSchedule]:
        """Generate or regenerate the depreciation schedule for an asset."""
        asset = self.get_asset(asset_id)
        
        if asset.depreciation_method == schemas.DepreciationMethod.NONE or not asset.useful_life_years:
            return []
        
        # Delete existing schedule if it exists
        self.db.query(models.DepreciationSchedule).filter(
            models.DepreciationSchedule.asset_id == asset_id
        ).delete(synchronize_session=False)
        
        # Generate new schedule
        start_date = asset.start_depreciation_date or asset.purchase_date
        total_months = asset.useful_life_years * 12
        
        schedules = []
        accumulated_depreciation = Decimal('0')
        
        for month in range(1, total_months + 1):
            period_date = start_date + timedelta(days=30 * month)  # Approximate month
            fiscal_year = period_date.year
            period = (period_date.month - 1) // 3 + 1  # Quarter (1-4)
            
            # Calculate depreciation for this period
            dep_calc = self.calculate_depreciation(
                asset,
                period_date
            )
            
            period_depreciation = dep_calc['depreciation_to_date'] - accumulated_depreciation
            accumulated_depreciation = dep_calc['depreciation_to_date']
            
            # Create schedule entry
            schedule = models.DepreciationSchedule(
                id=uuid4(),
                asset_id=asset_id,
                fiscal_year=fiscal_year,
                period=period,
                start_date=period_date.replace(day=1),
                end_date=(period_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1),
                depreciation_amount=period_depreciation,
                accumulated_depreciation=accumulated_depreciation,
                book_value=dep_calc['current_book_value'],
                is_posted=False,
                created_by_id=user_id,
                updated_by_id=user_id
            )
            
            schedules.append(schedule)
        
        # Bulk insert the schedule
        self.db.bulk_save_objects(schedules)
        self.db.commit()
        
        return schedules
    
    def post_depreciation(
        self,
        period_date: date,
        user_id: UUID,
        asset_ids: Optional[List[UUID]] = None
    ) -> List[models.DepreciationSchedule]:
        """
        Post depreciation for a specific period.
        
        Args:
            period_date: The end date of the period to post depreciation for
            user_id: ID of the user posting the depreciation
            asset_ids: Optional list of asset IDs to post depreciation for
            
        Returns:
            List of created depreciation schedules
        """
        # Find assets that need depreciation
        query = self.db.query(models.Asset).filter(
            models.Asset.depreciation_method != schemas.DepreciationMethod.NONE,
            models.Asset.status == schemas.AssetStatus.ACTIVE,
            or_(
                models.Asset.disposed_date.is_(None),
                models.Asset.disposed_date > period_date
            )
        )
        
        if asset_ids:
            query = query.filter(models.Asset.id.in_(asset_ids))
        
        assets = query.all()
        posted_schedules = []
        
        for asset in assets:
            # Find or create depreciation schedule for this period
            schedule = self.db.query(models.DepreciationSchedule).filter(
                models.DepreciationSchedule.asset_id == asset.id,
                models.DepreciationSchedule.start_date <= period_date,
                models.DepreciationSchedule.end_date >= period_date
            ).first()
            
            if not schedule:
                # Generate schedule if it doesn't exist
                self._generate_depreciation_schedule(asset, user_id)
                schedule = self.db.query(models.DepreciationSchedule).filter(
                    models.DepreciationSchedule.asset_id == asset.id,
                    models.DepreciationSchedule.start_date <= period_date,
                    models.DepreciationSchedule.end_date >= period_date
                ).first()
                
                if not schedule:
                    continue  # Skip if still no schedule
            
            # Skip if already posted
            if schedule.is_posted:
                continue
            
            # Create journal entry for depreciation
            if all([
                asset.asset_account_id,
                asset.accumulated_depreciation_account_id,
                asset.depreciation_expense_account_id
            ]):
                self._create_depreciation_journal_entry(asset, schedule, user_id)
            
            # Mark as posted
            schedule.is_posted = True
            schedule.posted_date = date.today()
            schedule.updated_by_id = user_id
            schedule.updated_at = datetime.utcnow()
            
            self.db.add(schedule)
            posted_schedules.append(schedule)
        
        self.db.commit()
        return posted_schedules
    
    # Helper Methods
    def _create_asset_acquisition_entry(
        self,
        asset: models.Asset,
        user_id: UUID
    ) -> None:
        """Create journal entry for asset acquisition."""
        # This is a placeholder - in a real implementation, you would create a journal entry
        # that debits the asset account and credits the appropriate liability or cash account
        pass
    
    def _create_asset_disposal_entry(
        self,
        asset: models.Asset,
        user_id: UUID
    ) -> None:
        """Create journal entry for asset disposal."""
        # This is a placeholder - in a real implementation, you would create a journal entry
        # that removes the asset and accumulated depreciation, and records any gain or loss
        pass
    
    def _create_depreciation_journal_entry(
        self,
        asset: models.Asset,
        schedule: models.DepreciationSchedule,
        user_id: UUID
    ) -> None:
        """Create journal entry for depreciation expense."""
        # This is a placeholder - in a real implementation, you would create a journal entry
        # that debits depreciation expense and credits accumulated depreciation
        pass
    
    def _create_maintenance_journal_entry(
        self,
        asset: models.Asset,
        record: models.MaintenanceRecord,
        user_id: UUID
    ) -> None:
        """Create journal entry for maintenance expense."""
        # This is a placeholder - in a real implementation, you would create a journal entry
        # that debits maintenance expense and credits cash or accounts payable
        pass
    
    def _generate_depreciation_schedule(
        self,
        asset: models.Asset,
        user_id: UUID
    ) -> List[models.DepreciationSchedule]:
        """Internal method to generate depreciation schedule for an asset."""
        # This is a helper method called by other methods to generate the schedule
        # The actual implementation would be similar to the calculate_depreciation method
        # but would create DepreciationSchedule records instead of just calculating values
        return []


# Service factory function
def get_fixed_asset_service(db: Session) -> FixedAssetService:
    """Dependency function to get a FixedAssetService instance."""
    return FixedAssetService(db)
=======
from typing import List, Optional
from decimal import Decimal
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.crud.base import CRUDBase
from .models import FixedAsset, DepreciationEntry, MaintenanceRecord, AssetCategory, AssetStatus, DepreciationMethod
from .schemas import (
    FixedAssetCreate, FixedAssetUpdate, DepreciationEntryCreate, 
    MaintenanceRecordCreate, MaintenanceRecordUpdate, AssetCategoryCreate,
    AssetDisposalRequest, AssetReport
)

class FixedAssetService(CRUDBase[FixedAsset, FixedAssetCreate, FixedAssetUpdate]):
    def __init__(self):
        super().__init__(FixedAsset)
    
    async def get_by_asset_number(self, db: AsyncSession, asset_number: str) -> Optional[FixedAsset]:
        result = await db.execute(select(FixedAsset).where(FixedAsset.asset_number == asset_number))
        return result.scalar_one_or_none()
    
    async def get_assets_by_category(self, db: AsyncSession, category: str) -> List[FixedAsset]:
        result = await db.execute(
            select(FixedAsset).where(
                and_(FixedAsset.category == category, FixedAsset.is_active == True)
            )
        )
        return result.scalars().all()
    
    async def get_assets_by_status(self, db: AsyncSession, status: AssetStatus) -> List[FixedAsset]:
        result = await db.execute(
            select(FixedAsset).where(
                and_(FixedAsset.status == status, FixedAsset.is_active == True)
            )
        )
        return result.scalars().all()
    
    async def calculate_depreciation(self, asset: FixedAsset, period_date: date) -> Decimal:
        """Calculate depreciation for a specific period"""
        if asset.status != AssetStatus.ACTIVE:
            return Decimal('0')
        
        months_since_purchase = (period_date.year - asset.purchase_date.year) * 12 + \
                               (period_date.month - asset.purchase_date.month)
        
        if months_since_purchase <= 0:
            return Decimal('0')
        
        depreciable_amount = asset.purchase_cost - asset.salvage_value
        
        if asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
            monthly_depreciation = depreciable_amount / (asset.useful_life_years * 12)
            return monthly_depreciation
        
        elif asset.depreciation_method == DepreciationMethod.DECLINING_BALANCE:
            # Double declining balance method
            rate = Decimal('2') / asset.useful_life_years
            current_book_value = asset.purchase_cost - asset.accumulated_depreciation
            annual_depreciation = current_book_value * rate
            monthly_depreciation = annual_depreciation / 12
            
            # Ensure we don't depreciate below salvage value
            remaining_depreciable = current_book_value - asset.salvage_value
            return min(monthly_depreciation, remaining_depreciable)
        
        return Decimal('0')
    
    async def create_depreciation_entry(
        self, 
        db: AsyncSession, 
        asset_id: int, 
        period_date: date
    ) -> Optional[DepreciationEntry]:
        """Create a depreciation entry for an asset"""
        asset = await self.get(db, asset_id)
        if not asset:
            return None
        
        depreciation_amount = await self.calculate_depreciation(asset, period_date)
        if depreciation_amount <= 0:
            return None
        
        new_accumulated = asset.accumulated_depreciation + depreciation_amount
        book_value = asset.purchase_cost - new_accumulated
        
        # Create depreciation entry
        entry = DepreciationEntry(
            asset_id=asset_id,
            period_date=period_date,
            depreciation_amount=depreciation_amount,
            accumulated_depreciation=new_accumulated,
            book_value=book_value
        )
        
        db.add(entry)
        
        # Update asset's accumulated depreciation
        asset.accumulated_depreciation = new_accumulated
        db.add(asset)
        
        await db.commit()
        await db.refresh(entry)
        return entry
    
    async def dispose_asset(
        self, 
        db: AsyncSession, 
        asset_id: int, 
        disposal_request: AssetDisposalRequest
    ) -> Optional[FixedAsset]:
        """Dispose of an asset"""
        asset = await self.get(db, asset_id)
        if not asset:
            return None
        
        asset.status = AssetStatus.DISPOSED
        asset.disposal_date = disposal_request.disposal_date
        asset.disposal_amount = disposal_request.disposal_amount
        asset.disposal_reason = disposal_request.disposal_reason
        
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        return asset
    
    async def get_asset_report(self, db: AsyncSession) -> AssetReport:
        """Generate asset summary report"""
        # Get total counts and values
        result = await db.execute(
            select(
                func.count(FixedAsset.id).label('total_assets'),
                func.sum(FixedAsset.purchase_cost).label('total_cost'),
                func.sum(FixedAsset.accumulated_depreciation).label('total_accumulated_depreciation')
            ).where(FixedAsset.is_active == True)
        )
        
        totals = result.first()
        total_cost = totals.total_cost or Decimal('0')
        total_accumulated = totals.total_accumulated_depreciation or Decimal('0')
        
        # Assets by category
        category_result = await db.execute(
            select(
                FixedAsset.category,
                func.count(FixedAsset.id).label('count'),
                func.sum(FixedAsset.purchase_cost).label('total_cost')
            ).where(FixedAsset.is_active == True)
            .group_by(FixedAsset.category)
        )
        
        assets_by_category = [
            {
                'category': row.category,
                'count': row.count,
                'total_cost': float(row.total_cost or 0)
            }
            for row in category_result
        ]
        
        # Assets by status
        status_result = await db.execute(
            select(
                FixedAsset.status,
                func.count(FixedAsset.id).label('count')
            ).where(FixedAsset.is_active == True)
            .group_by(FixedAsset.status)
        )
        
        assets_by_status = [
            {
                'status': row.status.value,
                'count': row.count
            }
            for row in status_result
        ]
        
        return AssetReport(
            total_assets=totals.total_assets or 0,
            total_cost=total_cost,
            total_accumulated_depreciation=total_accumulated,
            total_book_value=total_cost - total_accumulated,
            assets_by_category=assets_by_category,
            assets_by_status=assets_by_status
        )

class MaintenanceService(CRUDBase[MaintenanceRecord, MaintenanceRecordCreate, MaintenanceRecordUpdate]):
    def __init__(self):
        super().__init__(MaintenanceRecord)
    
    async def get_by_asset(self, db: AsyncSession, asset_id: int) -> List[MaintenanceRecord]:
        result = await db.execute(
            select(MaintenanceRecord)
            .where(MaintenanceRecord.asset_id == asset_id)
            .order_by(MaintenanceRecord.scheduled_date.desc())
        )
        return result.scalars().all()
    
    async def get_upcoming_maintenance(self, db: AsyncSession, days_ahead: int = 30) -> List[MaintenanceRecord]:
        future_date = date.today() + relativedelta(days=days_ahead)
        result = await db.execute(
            select(MaintenanceRecord)
            .where(
                and_(
                    MaintenanceRecord.scheduled_date <= future_date,
                    MaintenanceRecord.scheduled_date >= date.today(),
                    MaintenanceRecord.status == 'scheduled'
                )
            )
            .order_by(MaintenanceRecord.scheduled_date)
        )
        return result.scalars().all()

class AssetCategoryService(CRUDBase[AssetCategory, AssetCategoryCreate, None]):
    def __init__(self):
        super().__init__(AssetCategory)
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[AssetCategory]:
        result = await db.execute(select(AssetCategory).where(AssetCategory.name == name))
        return result.scalar_one_or_none()
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91
