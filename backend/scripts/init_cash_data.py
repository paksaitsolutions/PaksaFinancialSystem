import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.cash_management import BankAccount, BankTransaction, TransactionType, TransactionStatus, AccountType
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

def init_cash_data():
    db = SessionLocal()
    try:
        # Create sample bank accounts
        accounts = [
            BankAccount(
                id=uuid.uuid4(),
                name="Main Checking Account",
                account_number="****1234",
                account_type=AccountType.CHECKING,
                bank_name="First National Bank",
                routing_number="123456789",
                current_balance=Decimal("25000.00"),
                available_balance=Decimal("25000.00"),
                is_active=True
            ),
            BankAccount(
                id=uuid.uuid4(),
                name="Business Savings",
                account_number="****5678",
                account_type=AccountType.SAVINGS,
                bank_name="First National Bank",
                routing_number="123456789",
                current_balance=Decimal("50000.00"),
                available_balance=Decimal("50000.00"),
                is_active=True
            ),
            BankAccount(
                id=uuid.uuid4(),
                name="Payroll Account",
                account_number="****9012",
                account_type=AccountType.CHECKING,
                bank_name="Community Bank",
                routing_number="987654321",
                current_balance=Decimal("15000.00"),
                available_balance=Decimal("15000.00"),
                is_active=True
            )
        ]
        
        for account in accounts:
            db.add(account)
        
        db.commit()
        
        # Create sample transactions
        main_account = accounts[0]
        transactions = [
            BankTransaction(
                account_id=main_account.id,
                transaction_date=datetime.now() - timedelta(days=5),
                transaction_type=TransactionType.DEPOSIT,
                status=TransactionStatus.POSTED,
                amount=Decimal("5000.00"),
                reference_number="DEP001",
                memo="Customer payment received",
                payee="ABC Corporation",
                payment_method="Wire Transfer"
            ),
            BankTransaction(
                account_id=main_account.id,
                transaction_date=datetime.now() - timedelta(days=3),
                transaction_type=TransactionType.WITHDRAWAL,
                status=TransactionStatus.POSTED,
                amount=Decimal("1200.00"),
                reference_number="CHK001",
                memo="Office supplies",
                payee="Office Depot",
                payment_method="Check"
            ),
            BankTransaction(
                account_id=main_account.id,
                transaction_date=datetime.now() - timedelta(days=1),
                transaction_type=TransactionType.PAYMENT,
                status=TransactionStatus.PENDING,
                amount=Decimal("800.00"),
                reference_number="ACH001",
                memo="Utility payment",
                payee="Electric Company",
                payment_method="ACH"
            )
        ]
        
        for transaction in transactions:
            db.add(transaction)
        
        db.commit()
        print("Cash management sample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_cash_data()