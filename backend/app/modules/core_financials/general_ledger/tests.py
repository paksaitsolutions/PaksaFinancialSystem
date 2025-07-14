"""
Tests for General Ledger module.
"""
import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.core_financials.general_ledger.models import Account, AccountType
from app.modules.core_financials.general_ledger.services import AccountService, JournalEntryService
from app.modules.core_financials.general_ledger.schemas import AccountCreate, JournalEntryCreate, JournalEntryLineCreate

@pytest.fixture
async def account_service():
    return AccountService()

@pytest.fixture
async def journal_service():
    return JournalEntryService()

@pytest.mark.asyncio
async def test_create_account(account_service: AccountService, db_session: AsyncSession):
    """Test creating a new account."""
    account_data = AccountCreate(
        account_code="1000",
        account_name="Cash",
        account_type=AccountType.ASSET,
        description="Main cash account"
    )
    
    account = await account_service.create(db_session, obj_in=account_data)
    
    assert account.account_code == "1000"
    assert account.account_name == "Cash"
    assert account.account_type == AccountType.ASSET
    assert account.is_active is True

@pytest.mark.asyncio
async def test_get_account_by_code(account_service: AccountService, db_session: AsyncSession):
    """Test retrieving account by code."""
    # Create account first
    account_data = AccountCreate(
        account_code="2000",
        account_name="Accounts Payable",
        account_type=AccountType.LIABILITY
    )
    created_account = await account_service.create(db_session, obj_in=account_data)
    
    # Retrieve by code
    found_account = await account_service.get_by_code(db_session, "2000")
    
    assert found_account is not None
    assert found_account.id == created_account.id
    assert found_account.account_code == "2000"

@pytest.mark.asyncio
async def test_create_journal_entry(journal_service: JournalEntryService, db_session: AsyncSession):
    """Test creating a journal entry."""
    # Create accounts first
    account_service = AccountService()
    cash_account = await account_service.create(db_session, obj_in=AccountCreate(
        account_code="1000", account_name="Cash", account_type=AccountType.ASSET
    ))
    revenue_account = await account_service.create(db_session, obj_in=AccountCreate(
        account_code="4000", account_name="Revenue", account_type=AccountType.REVENUE
    ))
    
    # Create journal entry
    entry_data = JournalEntryCreate(
        entry_date=date.today(),
        description="Test journal entry",
        lines=[
            JournalEntryLineCreate(
                account_id=cash_account.id,
                debit_amount=Decimal("1000.00"),
                credit_amount=Decimal("0.00")
            ),
            JournalEntryLineCreate(
                account_id=revenue_account.id,
                debit_amount=Decimal("0.00"),
                credit_amount=Decimal("1000.00")
            )
        ]
    )
    
    journal_entry = await journal_service.create_journal_entry(db_session, entry_data=entry_data)
    
    assert journal_entry.total_debit == Decimal("1000.00")
    assert journal_entry.total_credit == Decimal("1000.00")
    assert len(journal_entry.lines) == 2
    assert journal_entry.status == "draft"

@pytest.mark.asyncio
async def test_unbalanced_journal_entry_fails(journal_service: JournalEntryService, db_session: AsyncSession):
    """Test that unbalanced journal entries are rejected."""
    account_service = AccountService()
    cash_account = await account_service.create(db_session, obj_in=AccountCreate(
        account_code="1000", account_name="Cash", account_type=AccountType.ASSET
    ))
    
    # Create unbalanced entry
    entry_data = JournalEntryCreate(
        entry_date=date.today(),
        description="Unbalanced entry",
        lines=[
            JournalEntryLineCreate(
                account_id=cash_account.id,
                debit_amount=Decimal("1000.00"),
                credit_amount=Decimal("0.00")
            )
        ]
    )
    
    with pytest.raises(ValueError, match="Total debits must equal total credits"):
        await journal_service.create_journal_entry(db_session, entry_data=entry_data)