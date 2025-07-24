import pytest
from unittest.mock import AsyncMock, MagicMock
from app.modules.core_financials.fixed_assets.services import FixedAssetService
from app.modules.core_financials.budget.services import BudgetService
from app.services.tenant_service import TenantService
from decimal import Decimal
from datetime import date

class TestFixedAssetService:
    @pytest.fixture
    def asset_service(self):
        return FixedAssetService()
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    async def test_calculate_depreciation_straight_line(self, asset_service, mock_db):
        # Mock asset
        asset = MagicMock()
        asset.purchase_cost = Decimal('1000.00')
        asset.salvage_value = Decimal('100.00')
        asset.useful_life_years = 5
        asset.depreciation_method = 'straight_line'
        asset.status = 'active'
        asset.purchase_date = date(2023, 1, 1)
        asset.accumulated_depreciation = Decimal('0.00')
        
        # Test calculation
        depreciation = await asset_service.calculate_depreciation(asset, date(2023, 2, 1))
        expected_monthly = Decimal('900.00') / (5 * 12)  # (1000-100) / 60 months
        
        assert depreciation == expected_monthly

class TestBudgetService:
    @pytest.fixture
    def budget_service(self):
        return BudgetService()
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    async def test_approve_budget(self, budget_service, mock_db):
        # Mock budget
        budget = MagicMock()
        budget.id = 1
        budget.status = "PENDING_APPROVAL"
        
        # Mock service methods
        budget_service.get = AsyncMock(return_value=budget)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Test approval
        result = await budget_service.approve_budget(mock_db, 1, "Approved by manager")
        
        assert result.status == "APPROVED"
        assert result.approval_notes == "Approved by manager"

class TestTenantService:
    @pytest.fixture
    def tenant_service(self):
        return TenantService()
    
    async def test_create_tenant(self, tenant_service):
        company_data = {
            'name': 'Test Company',
            'email': 'test@company.com',
            'industry': 'Technology'
        }
        
        # Mock database operations
        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Mock setup methods
        tenant_service._setup_tenant_database = AsyncMock()
        
        result = await tenant_service.create_tenant(mock_db, company_data)
        
        assert result.name == 'Test Company'
        assert result.email == 'test@company.com'
        assert result.status == 'active'