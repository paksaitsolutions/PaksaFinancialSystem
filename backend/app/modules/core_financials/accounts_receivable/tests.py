def test_customer_model():
    from .models import Customer
    customer = Customer(id=1, name='Test Customer', contact='test@example.com')
    assert customer.name == 'Test Customer'
    assert customer.contact == 'test@example.com'

def test_ar_invoice_model():
    from .models import ARInvoice
    invoice = ARInvoice(id=1, customer_id=1, date='2025-01-01', amount=1000.0, status='Unpaid')
    assert invoice.amount == 1000.0
    assert invoice.status == 'Unpaid'
