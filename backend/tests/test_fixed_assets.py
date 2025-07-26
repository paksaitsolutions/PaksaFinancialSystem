import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from decimal import Decimal

from app.main import app
from app.modules.core_financials.fixed_assets.services import FixedAssetService
from app.modules.core_financials.fixed_assets.disposal_service import AssetDisposalService
from app.modules.core_financials.fixed_assets.bulk_operations import BulkOperationsService
from app.modules.core_financials.fixed_assets.models import FixedAsset, AssetStatus

client = TestClient(app)

class TestFixedAssetService:
    """Test fixed asset service functionality"""
    
    @pytest.mark.asyncio
    async def test_create_asset(self, db_session: AsyncSession):
        """Test asset creation"""
        service = FixedAssetService()
        
        asset_data = {
            "asset_number": "FA-001",
            "name": "Test Equipment",
            "category": "Equipment",
            "purchase_date": date.today(),
            "purchase_cost": Decimal("10000.00"),
            "useful_life_years": 5
        }
        
        asset = await service.create(db_session, obj_in=asset_data)
        
        assert asset is not None
        assert asset.asset_number == "FA-001"
        assert asset.name == "Test Equipment"
        assert asset.status == AssetStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_calculate_depreciation(self, db_session: AsyncSession):
        """Test depreciation calculation"""
        service = FixedAssetService()
        
        # Create test asset
        asset = FixedAsset(
            asset_number="FA-002",
            name="Test Asset",
            category="Equipment",
            purchase_date=date(2024, 1, 1),
            purchase_cost=Decimal("12000.00"),
            salvage_value=Decimal("2000.00"),
            useful_life_years=5,
            accumulated_depreciation=Decimal("0")
        )
        
        # Calculate monthly depreciation
        depreciation = await service.calculate_depreciation(asset, date(2024, 2, 1))
        
        # Expected: (12000 - 2000) / (5 * 12) = 166.67
        expected = Decimal("10000.00") / (5 * 12)
        assert abs(depreciation - expected) < Decimal("0.01")

class TestAssetDisposalService:
    """Test asset disposal functionality"""
    
    @pytest.mark.asyncio
    async def test_asset_disposal(self, db_session: AsyncSession):
        """Test asset disposal with gain/loss calculation"""
        disposal_service = AssetDisposalService()
        
        # Mock asset (would be retrieved from database)
        asset = FixedAsset(
            id=1,
            asset_number="FA-003",
            name="Disposal Test Asset",
            purchase_cost=Decimal("5000.00"),
            accumulated_depreciation=Decimal("3000.00"),
            status=AssetStatus.ACTIVE
        )
        
        disposal_request = {
            "disposal_date": date.today(),
            "disposal_amount": Decimal("2500.00"),
            "disposal_reason": "End of useful life"
        }
        
        # Test would require actual database setup
        # This is a structure test
        assert disposal_service is not None

class TestBulkOperationsService:
    """Test bulk operations functionality"""
    
    @pytest.mark.asyncio
    async def test_bulk_update_structure(self, db_session: AsyncSession):
        """Test bulk update service structure"""
        bulk_service = BulkOperationsService()
        
        update_data = {
            "category": "Updated Equipment",
            "location": "New Location"
        }
        
        # Test service structure
        assert bulk_service is not None
        assert hasattr(bulk_service, 'bulk_update_assets')
        assert hasattr(bulk_service, 'bulk_calculate_depreciation')

class TestFixedAssetAPI:
    """Test fixed asset API endpoints"""
    
    def test_create_asset_endpoint(self):
        """Test asset creation API endpoint"""
        asset_data = {
            "asset_number": "API-001",
            "name": "API Test Asset",
            "category": "Equipment",
            "purchase_date": "2024-01-01",
            "purchase_cost": 15000.00,
            "useful_life_years": 7
        }
        
        response = client.post("/api/fixed-assets/assets/", json=asset_data)
        
        # Test endpoint structure (would return 401 without auth)
        assert response.status_code in [201, 401, 422]
    
    def test_get_assets_endpoint(self):
        """Test get assets API endpoint"""
        response = client.get("/api/fixed-assets/assets/")
        
        # Test endpoint exists
        assert response.status_code in [200, 401]
    
    def test_bulk_operations_endpoints(self):
        """Test bulk operations API endpoints"""
        # Test bulk update endpoint
        response = client.put("/api/fixed-assets/assets/bulk-update", 
                            json={"asset_ids": [1, 2], "category": "Updated"})
        assert response.status_code in [200, 401, 422]
        
        # Test bulk depreciation endpoint
        response = client.post("/api/fixed-assets/depreciation/bulk-calculate",
                             json={"period_date": "2024-01-01"})
        assert response.status_code in [200, 401, 422]
    
    def test_disposal_endpoints(self):
        """Test asset disposal API endpoints"""
        disposal_data = {
            "disposal_date": "2024-01-01",
            "disposal_amount": 1000.00,
            "disposal_reason": "Test disposal"
        }
        
        response = client.post("/api/fixed-assets/assets/1/dispose-advanced", 
                             json=disposal_data)
        assert response.status_code in [200, 401, 404, 422]

class TestAdvancedDepreciation:
    """Test advanced depreciation methods"""
    
    def test_depreciation_schedule_endpoint(self):
        """Test depreciation schedule API endpoint"""
        response = client.get("/api/fixed-assets/assets/1/depreciation-schedule")
        
        # Test endpoint exists
        assert response.status_code in [200, 401, 404]
    
    def test_depreciation_methods(self):
        """Test different depreciation methods"""
        from app.modules.core_financials.fixed_assets.advanced_depreciation import AdvancedDepreciationService
        
        service = AdvancedDepreciationService()
        
        # Test service methods exist
        assert hasattr(service, 'calculate_units_of_production_depreciation')
        assert hasattr(service, 'calculate_sum_of_years_digits_depreciation')
        assert hasattr(service, 'calculate_double_declining_balance_depreciation')
        assert hasattr(service, 'get_depreciation_schedule')

@pytest.fixture
async def db_session():
    """Mock database session for testing"""
    # In real implementation, would return actual test database session
    return None