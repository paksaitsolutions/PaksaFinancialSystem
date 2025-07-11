def test_vendor_model():
    from .models import Vendor
    vendor = Vendor(id=1, name='Test Vendor', contact='test@example.com')
    assert vendor.name == 'Test Vendor'
    assert vendor.contact == 'test@example.com'

def test_invoice_model():
    from .models import Invoice
    invoice = Invoice(id=1, vendor_id=1, date='2025-01-01', amount=500.0, status='Pending')
    assert invoice.amount == 500.0
    assert invoice.status == 'Pending'
