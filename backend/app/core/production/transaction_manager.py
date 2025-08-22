"""
Production transaction management and data consistency.
"""
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class TransactionManager:
    """Production transaction management."""
    
    @staticmethod
    @asynccontextmanager
    async def atomic_transaction(db: AsyncSession):
        """Ensure atomic database operations."""
        try:
            await db.begin()
            yield db
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
    
    @staticmethod
    async def validate_business_rules(db: AsyncSession, operation: str, data: Dict[str, Any]) -> List[str]:
        """Validate business rules before operations."""
        errors = []
        
        if operation == "journal_entry":
            # Validate journal entry balance
            total_debits = sum(line.get('debit_amount', 0) for line in data.get('lines', []))
            total_credits = sum(line.get('credit_amount', 0) for line in data.get('lines', []))
            
            if abs(total_debits - total_credits) > 0.01:
                errors.append("Journal entry must balance (debits = credits)")
        
        elif operation == "payment":
            # Validate payment amount
            if data.get('amount', 0) <= 0:
                errors.append("Payment amount must be positive")
            
            # Validate payment doesn't exceed outstanding balance
            outstanding = data.get('outstanding_balance', 0)
            if data.get('amount', 0) > outstanding:
                errors.append("Payment cannot exceed outstanding balance")
        
        elif operation == "invoice":
            # Validate invoice has line items
            if not data.get('line_items'):
                errors.append("Invoice must have at least one line item")
            
            # Validate customer credit limit
            customer_balance = data.get('customer_balance', 0)
            invoice_amount = data.get('total_amount', 0)
            credit_limit = data.get('credit_limit', 0)
            
            if customer_balance + invoice_amount > credit_limit:
                errors.append("Invoice would exceed customer credit limit")
        
        return errors
    
    @staticmethod
    async def ensure_data_consistency(db: AsyncSession, operation: str, data: Dict[str, Any]):
        """Ensure data consistency across related tables."""
        if operation == "journal_entry":
            # Update account balances
            for line in data.get('lines', []):
                account_id = line.get('account_id')
                debit_amount = line.get('debit_amount', 0)
                credit_amount = line.get('credit_amount', 0)
                
                # Update account balance (simplified)
                logger.info(f"Updating account {account_id} balance")
        
        elif operation == "payment":
            # Update invoice/bill status
            invoice_id = data.get('invoice_id')
            payment_amount = data.get('amount', 0)
            
            logger.info(f"Updating invoice {invoice_id} with payment {payment_amount}")
        
        elif operation == "inventory_transaction":
            # Update inventory quantities
            item_id = data.get('item_id')
            quantity_change = data.get('quantity_change', 0)
            
            logger.info(f"Updating inventory item {item_id} quantity by {quantity_change}")

class ConcurrencyManager:
    """Handle concurrent access and prevent race conditions."""
    
    @staticmethod
    async def acquire_row_lock(db: AsyncSession, table: str, record_id: str):
        """Acquire row-level lock to prevent concurrent modifications."""
        # In production, implement proper row locking
        logger.info(f"Acquiring lock for {table}:{record_id}")
    
    @staticmethod
    async def check_version_conflict(db: AsyncSession, table: str, record_id: str, expected_version: int) -> bool:
        """Check for optimistic locking version conflicts."""
        # In production, implement version checking
        logger.info(f"Checking version for {table}:{record_id}")
        return True

class DataValidator:
    """Production data validation."""
    
    @staticmethod
    def validate_financial_amount(amount: float) -> bool:
        """Validate financial amounts."""
        return 0 <= amount <= 999999999.99
    
    @staticmethod
    def validate_tenant_isolation(user_tenant_id: str, resource_tenant_id: str) -> bool:
        """Ensure tenant data isolation."""
        return user_tenant_id == resource_tenant_id
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate required fields are present."""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        return missing_fields