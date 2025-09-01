"""
Fixed Assets Module - Exceptions
"""
from typing import Optional
from uuid import UUID


class FixedAssetError(Exception):
    """Base exception for fixed assets module."""
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code or "fixed_asset_error"
        super().__init__(self.message)


class AssetNotFound(FixedAssetError):
    """Raised when an asset is not found."""
    def __init__(self, asset_id: UUID):
        self.asset_id = asset_id
        super().__init__(
            f"Asset with ID {asset_id} not found",
            code="asset_not_found"
        )


class AssetCategoryNotFound(FixedAssetError):
    """Raised when an asset category is not found."""
    def __init__(self, category_id: UUID):
        self.category_id = category_id
        super().__init__(
            f"Asset category with ID {category_id} not found",
            code="asset_category_not_found"
        )


class MaintenanceRecordNotFound(FixedAssetError):
    """Raised when a maintenance record is not found."""
    def __init__(self, record_id: UUID):
        self.record_id = record_id
        super().__init__(
            f"Maintenance record with ID {record_id} not found",
            code="maintenance_record_not_found"
        )


class DepreciationError(FixedAssetError):
    """Raised when there's an error with depreciation calculations."""
    def __init__(self, message: str, asset_id: Optional[UUID] = None):
        self.asset_id = asset_id
        super().__init__(
            message,
            code="depreciation_error"
        )


class AssetValidationError(FixedAssetError):
    """Raised when there's a validation error with asset data."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(
            message,
            code=f"validation_error.{field}" if field else "validation_error"
        )


class AssetInUseError(FixedAssetError):
    """Raised when trying to delete an asset that is in use."""
    def __init__(self, asset_id: UUID, usage: str):
        self.asset_id = asset_id
        self.usage = usage
        super().__init__(
            f"Cannot delete asset {asset_id} as it is being used in {usage}",
            code="asset_in_use"
        )


class AssetDisposalError(FixedAssetError):
    """Raised when there's an error disposing of an asset."""
    def __init__(self, asset_id: UUID, reason: str):
        self.asset_id = asset_id
        super().__init__(
            f"Cannot dispose of asset {asset_id}: {reason}",
            code="asset_disposal_error"
        )


class AssetTransferError(FixedAssetError):
    """Raised when there's an error transferring an asset."""
    def __init__(self, asset_id: UUID, reason: str):
        self.asset_id = asset_id
        super().__init__(
            f"Cannot transfer asset {asset_id}: {reason}",
            code="asset_transfer_error"
        )


class MaintenanceScheduleError(FixedAssetError):
    """Raised when there's an error with maintenance scheduling."""
    def __init__(self, asset_id: UUID, reason: str):
        self.asset_id = asset_id
        super().__init__(
            f"Maintenance scheduling error for asset {asset_id}: {reason}",
            code="maintenance_schedule_error"
        )


class AssetImportError(FixedAssetError):
    """Raised when there's an error importing assets."""
    def __init__(self, reason: str, row: Optional[int] = None):
        self.row = row
        super().__init__(
            f"Error importing assets{f' at row {row}' if row else ''}: {reason}",
            code="asset_import_error"
        )


class AssetExportError(FixedAssetError):
    """Raised when there's an error exporting assets."""
    def __init__(self, reason: str):
        super().__init__(
            f"Error exporting assets: {reason}",
            code="asset_export_error"
        )


class AssetDepreciationLockedError(FixedAssetError):
    """Raised when trying to modify an asset with locked depreciation."""
    def __init__(self, asset_id: UUID, period: str):
        self.asset_id = asset_id
        self.period = period
        super().__init__(
            f"Cannot modify asset {asset_id} - depreciation is locked for period {period}",
            code="asset_depreciation_locked"
        )
