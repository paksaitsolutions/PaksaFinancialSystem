from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.finance.tax_transaction import (
    TaxTransaction, 
    TaxTransactionStatus,
    TaxTransactionType,
    TaxTransactionComponent
)
from app.schemas.tax import (
    TaxTransactionCreate,
    TaxTransactionUpdate,
    TaxTransactionInDB,
    TaxTransactionComponentCreate,
    TaxTransactionComponentInDB
)
from app.core.exceptions import NotFoundException, ValidationException
from app.core.db.session import with_db_session
from app.core.auth import get_current_user

class TaxTransactionService:
    """Service for handling tax transaction operations"""
    
    @with_db_session
    def create_transaction(
        self,
        db: Session,
        transaction_data: TaxTransactionCreate,
        current_user_id: UUID
    ) -> TaxTransactionInDB:
        """Create a new tax transaction with components"""
        # Validate transaction data
        self._validate_transaction_data(transaction_data)
        
        # Create base transaction
        transaction_dict = transaction_data.dict(exclude={"components"})
        transaction = TaxTransaction(
            **transaction_dict,
            created_by=current_user_id,
            status=TaxTransactionStatus.DRAFT
        )
        
        # Add components
        components = []
        for comp_data in transaction_data.components:
            component = TaxTransactionComponent(
                **comp_data.dict(),
                transaction=transaction
            )
            components.append(component)
        
        # Calculate totals if not provided
        if not transaction.tax_amount or not transaction.total_amount:
            self._calculate_totals(transaction, components)
        
        # Save to database
        db.add(transaction)
        db.add_all(components)
        db.commit()
        db.refresh(transaction)
        
        return TaxTransactionInDB.from_orm(transaction)
    
    @with_db_session
    def update_transaction(
        self,
        db: Session,
        transaction_id: UUID,
        update_data: TaxTransactionUpdate,
        current_user_id: UUID
    ) -> TaxTransactionInDB:
        """Update an existing tax transaction"""
        transaction = db.query(TaxTransaction).get(transaction_id)
        if not transaction:
            raise NotFoundException("Tax transaction not found")
            
        if transaction.status != TaxTransactionStatus.DRAFT:
            raise ValidationException("Only draft transactions can be modified")
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True, exclude={"components"})
        for field, value in update_dict.items():
            setattr(transaction, field, value)
        
        # Update components if provided
        if update_data.components is not None:
            # Delete existing components
            db.query(TaxTransactionComponent).filter(
                TaxTransactionComponent.transaction_id == transaction_id
            ).delete()
            
            # Add updated components
            components = []
            for comp_data in update_data.components:
                component = TaxTransactionComponent(
                    **comp_data.dict(),
                    transaction_id=transaction_id
                )
                components.append(component)
            
            db.add_all(components)
            
            # Recalculate totals
            self._calculate_totals(transaction, components)
        
        transaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(transaction)
        
        return TaxTransactionInDB.from_orm(transaction)
    
    @with_db_session
    def get_transaction(
        self,
        db: Session,
        transaction_id: UUID
    ) -> TaxTransactionInDB:
        """Retrieve a tax transaction by ID"""
        transaction = db.query(TaxTransaction).get(transaction_id)
        if not transaction:
            raise NotFoundException("Tax transaction not found")
        return TaxTransactionInDB.from_orm(transaction)
    
    @with_db_session
    def list_transactions(
        self,
        db: Session,
        company_id: UUID,
        status: Optional[TaxTransactionStatus] = None,
        transaction_type: Optional[TaxTransactionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaxTransactionInDB]:
        """List tax transactions with filtering and pagination"""
        query = db.query(TaxTransaction).filter(
            TaxTransaction.company_id == company_id,
            TaxTransaction.deleted_at.is_(None)
        )
        
        if status:
            query = query.filter(TaxTransaction.status == status)
        if transaction_type:
            query = query.filter(TaxTransaction.transaction_type == transaction_type)
        if start_date:
            query = query.filter(TaxTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(TaxTransaction.transaction_date <= end_date)
            
        transactions = query.offset(skip).limit(limit).all()
        return [TaxTransactionInDB.from_orm(t) for t in transactions]
    
    @with_db_session
    def post_transaction(
        self,
        db: Session,
        transaction_id: UUID,
        current_user_id: UUID
    ) -> TaxTransactionInDB:
        """Post a draft transaction to make it final"""
        transaction = db.query(TaxTransaction).get(transaction_id)
        if not transaction:
            raise NotFoundException("Tax transaction not found")
            
        if transaction.status != TaxTransactionStatus.DRAFT:
            raise ValidationException("Only draft transactions can be posted")
        
        # Additional validation can be added here
        
        # Update status and post
        transaction.status = TaxTransactionStatus.POSTED
        transaction.posted_by = current_user_id
        transaction.posted_at = datetime.utcnow()
        
        db.commit()
        db.refresh(transaction)
        
        # TODO: Trigger any post-posting actions (e.g., GL posting)
        
        return TaxTransactionInDB.from_orm(transaction)
    
    @with_db_session
    def void_transaction(
        self,
        db: Session,
        transaction_id: UUID,
        reason: str,
        current_user_id: UUID
    ) -> TaxTransactionInDB:
        """Void a posted transaction"""
        transaction = db.query(TaxTransaction).get(transaction_id)
        if not transaction:
            raise NotFoundException("Tax transaction not found")
            
        if transaction.status != TaxTransactionStatus.POSTED:
            raise ValidationException("Only posted transactions can be voided")
        
        # Create reversal transaction
        reversal = TaxTransaction(
            transaction_date=datetime.utcnow(),
            document_number=f"VOID-{transaction.document_number}",
            reference_number=transaction.document_number,
            company_id=transaction.company_id,
            tax_type=transaction.tax_type,
            tax_rate_id=transaction.tax_rate_id,
            taxable_amount=transaction.taxable_amount * -1,
            tax_amount=transaction.tax_amount * -1,
            total_amount=transaction.total_amount * -1,
            jurisdiction_code=transaction.jurisdiction_code,
            tax_jurisdiction_id=transaction.tax_jurisdiction_id,
            status=TaxTransactionStatus.POSTED,
            transaction_type=transaction.transaction_type,
            source_document_type="tax_transaction",
            source_document_id=transaction.id,
            created_by=current_user_id,
            posted_by=current_user_id,
            posted_at=datetime.utcnow(),
            notes=f"Void of transaction {transaction.document_number}: {reason}"
        )
        
        # Update original transaction
        transaction.status = TaxTransactionStatus.VOIDED
        transaction.notes = f"{transaction.notes or ''}\nVoided on {datetime.utcnow()}: {reason}"
        
        # Save changes
        db.add(reversal)
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return TaxTransactionInDB.from_orm(transaction)
    
    def _validate_transaction_data(self, data: TaxTransactionCreate) -> None:
        """Validate transaction data before creation"""
        if not data.components:
            raise ValidationException("At least one tax component is required")
            
        # Validate that component amounts match transaction totals
        total_taxable = sum(c.taxable_amount for c in data.components)
        total_tax = sum(c.tax_amount for c in data.components)
        
        if data.taxable_amount is not None and abs(total_taxable - data.taxable_amount) > 0.01:
            raise ValidationException("Sum of component taxable amounts does not match transaction total")
            
        if data.tax_amount is not None and abs(total_tax - data.tax_amount) > 0.01:
            raise ValidationException("Sum of component tax amounts does not match transaction total")
    
    def _calculate_totals(
        self, 
        transaction: TaxTransaction, 
        components: List[TaxTransactionComponent]
    ) -> None:
        """Calculate and update transaction totals from components"""
        transaction.taxable_amount = sum(c.taxable_amount for c in components)
        transaction.tax_amount = sum(c.tax_amount for c in components)
        transaction.total_amount = transaction.taxable_amount + transaction.tax_amount


# Singleton instance
tax_transaction_service = TaxTransactionService()
