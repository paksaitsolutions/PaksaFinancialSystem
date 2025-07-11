def test_fixed_asset_model():
    from .models import FixedAsset
    asset = FixedAsset(id=1, name='Laptop', category='IT', purchase_date='2025-01-01', cost=1500.0, depreciation=300.0)
    assert asset.name == 'Laptop'
    assert asset.category == 'IT'
    assert asset.cost == 1500.0

def test_maintenance_record_model():
    from .models import MaintenanceRecord
    record = MaintenanceRecord(id=1, asset_id=1, date='2025-02-01', description='Annual Service', cost=100.0)
    assert record.description == 'Annual Service'
    assert record.cost == 100.0
