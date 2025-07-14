def test_bank_account_model():
    from .models import BankAccount
    account = BankAccount(id=1, name='Main Account', number='123456', balance=10000.0)
    assert account.name == 'Main Account'
    assert account.number == '123456'
    assert account.balance == 10000.0

def test_cash_transaction_model():
    from .models import CashTransaction
    transaction = CashTransaction(id=1, account_id=1, date='2025-01-01', amount=500.0, type='Deposit')
    assert transaction.amount == 500.0
    assert transaction.type == 'Deposit'
