"""
CRUD operations for Accounts Receivable module.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Type, TypeVar, Union, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, or_, func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.core.database import Base
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ValidationException,
    ForbiddenException,
)
from app.models.accounts_receivable import Invoice, InvoiceItem, PaymentReceipt, InvoiceStatus, PaymentMethod
from app.schemas.accounts_receivable import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceItemCreate,
    PaymentReceiptCreate,
    PaymentReceiptUpdate,
)
from app.schemas.base import BaseSchema
from .base_ap import CRUDBase

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)

class CRUDInvoice(CRUDBase[Invoice, InvoiceCreate, InvoiceUpdate]):
    """CRUD operations for Invoice model."""
    
    async def get_by_number(
        self, db: AsyncSession, *, invoice_number: str
    ) -> Optional[Invoice]:
        """Get an invoice by its number."""
        result = await db.execute(
            select(self.model)
            .options(
                selectinload(Invoice.items),
                selectinload(Invoice.payments),
                joinedload(Invoice.customer),
            )
            .filter(self.model.invoice_number == invoice_number)
        )
        return result.scalars().first()

# Initialize the CRUD operations
invoice = CRUDInvoice(Invoice)

class CRUDPaymentReceipt(CRUDBase[PaymentReceipt, PaymentReceiptCreate, PaymentReceiptUpdate]):
    """CRUD operations for PaymentReceipt model."""
    
    async def get_by_receipt_number(
        self, db: AsyncSession, *, receipt_number: str
    ) -> Optional[PaymentReceipt]:
        """Get a payment receipt by its number."""
        result = await db.execute(
            select(self.model)
            .options(
                joinedload(PaymentReceipt.invoice),
                joinedload(PaymentReceipt.customer),
            )
            .filter(self.model.receipt_number == receipt_number)
        )
        return result.scalars().first()

# Initialize the CRUD operations
payment_receipt = CRUDPaymentReceipt(PaymentReceipt)