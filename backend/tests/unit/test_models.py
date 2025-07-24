import pytest
from app.modules.core_financials.fixed_assets.models import FixedAsset, DepreciationEntry
from app.modules.core_financials.budget.models import Budget, BudgetLineItem
from decimal import Decimal
from datetime import date

class TestFixedAssetModel:
    def test_create_fixed_asset(self, test_tenant):
        asset = FixedAsset(
            tenant_id=test_tenant,
            asset_number="FA-001",
            name="Test Asset",
            category="IT Equipment",
            purchase_date=date.today(),
            purchase_cost=Decimal('1000.00'),
            useful_life_years=5
        )
        
        assert asset.asset_number == "FA-001"
        assert asset.name == "Test Asset"
        assert asset.purchase_cost == Decimal('1000.00')
        assert asset.tenant_id == test_tenant

    def test_depreciation_calculation(self, test_tenant):
        asset = FixedAsset(
            tenant_id=test_tenant,
            asset_number="FA-002",
            name="Depreciable Asset",
            category="Equipment",
            purchase_date=date.today(),
            purchase_cost=Decimal('1200.00'),
            salvage_value=Decimal('200.00'),
            useful_life_years=5
        )
        
        # Test straight-line depreciation
        annual_depreciation = (asset.purchase_cost - asset.salvage_value) / asset.useful_life_years
        assert annual_depreciation == Decimal('200.00')

class TestBudgetModel:
    def test_create_budget(self, test_tenant):
        budget = Budget(
            tenant_id=test_tenant,
            name="Test Budget",
            amount=Decimal('10000.00'),
            type="OPERATIONAL",
            start_date=date.today(),
            end_date=date(2024, 12, 31)
        )
        
        assert budget.name == "Test Budget"
        assert budget.amount == Decimal('10000.00')
        assert budget.type == "OPERATIONAL"
        assert budget.tenant_id == test_tenant

    def test_budget_line_items(self, test_tenant):
        budget = Budget(
            tenant_id=test_tenant,
            name="Budget with Items",
            amount=Decimal('5000.00'),
            type="PROJECT",
            start_date=date.today(),
            end_date=date(2024, 12, 31)
        )
        
        line_item = BudgetLineItem(
            tenant_id=test_tenant,
            category="Personnel",
            description="Staff costs",
            amount=Decimal('3000.00')
        )
        
        assert line_item.category == "Personnel"
        assert line_item.amount == Decimal('3000.00')
        assert line_item.tenant_id == test_tenant