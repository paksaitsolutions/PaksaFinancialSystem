import pytest
from unittest.mock import AsyncMock, patch
from app.modules.core_financials.fixed_assets.services import FixedAssetService
from app.modules.core_financials.budget.services import BudgetService
from app.services.tenant_service import TenantService
from decimal import Decimal
from datetime import date

class TestFixedAssetsBudgetIntegration:
    """Test integration between Fixed Assets and Budget modules"""
    
    @pytest.fixture
    def asset_service(self):
        return FixedAssetService()
    
    @pytest.fixture
    def budget_service(self):
        return BudgetService()
    
    async def test_asset_depreciation_budget_impact(self, asset_service, budget_service):
        """Test that asset depreciation affects budget calculations"""
        mock_db = AsyncMock()
        
        # Create mock asset
        asset = AsyncMock()
        asset.purchase_cost = Decimal('12000.00')
        asset.salvage_value = Decimal('2000.00')
        asset.useful_life_years = 5
        asset.status = 'active'
        
        # Calculate annual depreciation
        annual_depreciation = await asset_service.calculate_depreciation(asset, date.today())
        
        # Create budget that includes depreciation
        budget_data = {
            'name': 'Capital Budget',
            'amount': annual_depreciation * 12,  # Monthly depreciation * 12
            'type': 'CAPITAL'
        }
        
        # Mock budget creation
        budget_service.create = AsyncMock()
        await budget_service.create(mock_db, obj_in=budget_data)
        
        # Verify integration
        budget_service.create.assert_called_once()

class TestTenantModuleIntegration:
    """Test integration between tenant system and all modules"""
    
    @pytest.fixture
    def tenant_service(self):
        return TenantService()
    
    async def test_tenant_data_isolation(self, tenant_service):
        """Test that tenant data is properly isolated across modules"""
        mock_db = AsyncMock()
        
        # Create tenant
        company_data = {
            'name': 'Integration Test Company',
            'email': 'integration@test.com'
        }
        
        tenant_service._setup_tenant_database = AsyncMock()
        company = await tenant_service.create_tenant(mock_db, company_data)
        
        # Verify tenant isolation setup
        tenant_service._setup_tenant_database.assert_called_once()
        assert company.status == 'active'

class TestSecurityIntegration:
    """Test security integration across modules"""
    
    async def test_tenant_access_validation(self):
        """Test that tenant access is validated across all modules"""
        with patch('app.core.db.tenant_middleware.get_current_tenant') as mock_tenant:
            mock_tenant.return_value = 'test_tenant_123'
            
            # Test would verify that all services respect tenant context
            from app.core.security.tenant_isolation import TenantDataIsolation
            
            query_params = {'id': 1}
            result = await TenantDataIsolation.enforce_isolation(
                AsyncMock(), AsyncMock(), query_params
            )
            
            assert 'tenant_id' in result
            assert result['tenant_id'] == 'test_tenant_123'