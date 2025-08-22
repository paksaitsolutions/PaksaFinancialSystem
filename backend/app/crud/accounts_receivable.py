<<<<<<< HEAD:backend/crud/accounts_receivable.py
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

from core.database import Base
from core.exceptions import (
    BadRequestException,
    NotFoundException,
    ValidationException,
    ForbiddenException,
)
from models.accounts_receivable import Invoice, InvoiceItem, PaymentReceipt, InvoiceStatus, PaymentMethod
from schemas.accounts_receivable import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceItemCreate,
    PaymentReceiptCreate,
    PaymentReceiptUpdate,
)
from schemas.base import BaseSchema
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
        
    async def create_with_items(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: InvoiceCreate, 
        created_by_id: UUID
    ) -> Invoice:
        """
        Create a new invoice with line items.
        
        Args:
            db: Database session
            obj_in: Invoice creation data
            created_by_id: ID of the user creating the invoice
            
        Returns:
            The created invoice with items
            
        Raises:
            NotFoundException: If customer or product not found
            BadRequestException: If validation fails
        """
        from crud import customer as customer_crud
        from crud import product as product_crud
        
        # Verify customer exists
        customer = await customer_crud.customer.get(db, id=obj_in.customer_id)
        if not customer:
            raise NotFoundException(detail=f"Customer with ID {obj_in.customer_id} not found")
        
        # Calculate invoice totals
        subtotal = Decimal('0.00')
        tax_amount = Decimal('0.00')
        discount_amount = Decimal('0.00')
        
        # Validate and prepare items
        db_items = []
        for item in obj_in.items:
            # Verify product exists if specified
            if item.product_id:
                product = await product_crud.product.get(db, id=item.product_id)
                if not product:
                    raise NotFoundException(detail=f"Product with ID {item.product_id} not found")
            
            # Calculate item amounts
            item_total = item.quantity * item.unit_price
            item_discount = item_total * (item.discount_percent / 100)
            item_subtotal = item_total - item_discount
            item_tax = item_subtotal * (item.tax_rate / 100)
            
            # Update running totals
            subtotal += item_subtotal
            discount_amount += item_discount
            tax_amount += item_tax
            
            # Prepare item for database
            db_item = InvoiceItem(
                **item.dict(exclude={"id"}, exclude_unset=True),
                amount=item_subtotal + item_tax,
            )
            db_items.append(db_item)
        
        total_amount = subtotal + tax_amount
        
        # Generate invoice number (format: INV-YYYYMMDD-XXXXX)
        today = datetime.now(timezone.utc).date()
        invoice_count = await db.execute(
            select(func.count(Invoice.id))
            .where(func.date(Invoice.created_at) == today)
        )
        invoice_number = f"INV-{today.strftime('%Y%m%d')}-{invoice_count.scalar() + 1:05d}"
        
        # Create invoice
        db_invoice = Invoice(
            **obj_in.dict(exclude={"items"}, exclude_unset=True),
            invoice_number=invoice_number,
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            amount_paid=Decimal('0.00'),
            balance_due=total_amount,
            status=InvoiceStatus.DRAFT,
            created_by_id=created_by_id,
            updated_by_id=created_by_id,
        )
        
        # Add items to invoice
        db_invoice.items = db_items
        
        # Save to database
        db.add(db_invoice)
        await db.commit()
        await db.refresh(db_invoice)
        
        return db_invoice
    
    async def get_overdue_invoices(
        self, db: AsyncSession, *, as_of: datetime = None
    ) -> List[Invoice]:
        """Get all overdue invoices as of a specific date."""
        if as_of is None:
            as_of = datetime.now(timezone.utc)
            
        result = await db.execute(
            select(self.model)
            .where(
                and_(
                    self.model.status.in_([
                        InvoiceStatus.SENT,
                        InvoiceStatus.PARTIALLY_PAID,
                        InvoiceStatus.OVERDUE
                    ]),
                    self.model.due_date < as_of.date(),
                    self.model.balance_due > 0
                )
            )
            .options(
                selectinload(Invoice.items),
                joinedload(Invoice.customer),
            )
            .order_by(self.model.due_date)
        )
        return result.scalars().all()

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
=======
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
from models.accounts_receivable import Invoice, InvoiceItem, PaymentReceipt, InvoiceStatus, PaymentMethod
from schemas.accounts_receivable import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceItemCreate,
    PaymentReceiptCreate,
    PaymentReceiptUpdate,
)
from schemas.base import BaseSchema
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
        
    async def create_with_items(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: InvoiceCreate, 
        created_by_id: UUID
    ) -> Invoice:
        """
        Create a new invoice with line items.
        
        Args:
            db: Database session
            obj_in: Invoice creation data
            created_by_id: ID of the user creating the invoice
            
        Returns:
            The created invoice with items
            
        Raises:
            NotFoundException: If customer or product not found
            BadRequestException: If validation fails
        """
        from crud import customer as customer_crud
        from crud import product as product_crud
        
        # Verify customer exists
        customer = await customer_crud.customer.get(db, id=obj_in.customer_id)
        if not customer:
            raise NotFoundException(detail=f"Customer with ID {obj_in.customer_id} not found")
        
        # Calculate invoice totals
        subtotal = Decimal('0.00')
        tax_amount = Decimal('0.00')
        discount_amount = Decimal('0.00')
        
        # Validate and prepare items
        db_items = []
        for item in obj_in.items:
            # Verify product exists if specified
            if item.product_id:
                product = await product_crud.product.get(db, id=item.product_id)
                if not product:
                    raise NotFoundException(detail=f"Product with ID {item.product_id} not found")
            
            # Calculate item amounts
            item_total = item.quantity * item.unit_price
            item_discount = item_total * (item.discount_percent / 100)
            item_subtotal = item_total - item_discount
            item_tax = item_subtotal * (item.tax_rate / 100)
            
            # Update running totals
            subtotal += item_subtotal
            discount_amount += item_discount
            tax_amount += item_tax
            
            # Prepare item for database
            db_item = InvoiceItem(
                **item.dict(exclude={"id"}, exclude_unset=True),
                amount=item_subtotal + item_tax,
            )
            db_items.append(db_item)
        
        total_amount = subtotal + tax_amount
        
        # Generate invoice number (format: INV-YYYYMMDD-XXXXX)
        today = datetime.now(timezone.utc).date()
        invoice_count = await db.execute(
            select(func.count(Invoice.id))
            .where(func.date(Invoice.created_at) == today)
        )
        invoice_number = f"INV-{today.strftime('%Y%m%d')}-{invoice_count.scalar() + 1:05d}"
        
        # Create invoice
        db_invoice = Invoice(
            **obj_in.dict(exclude={"items"}, exclude_unset=True),
            invoice_number=invoice_number,
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            amount_paid=Decimal('0.00'),
            balance_due=total_amount,
            status=InvoiceStatus.DRAFT,
            created_by_id=created_by_id,
            updated_by_id=created_by_id,
        )
        
        # Add items to invoice
        db_invoice.items = db_items
        
        # Save to database
        db.add(db_invoice)
        await db.commit()
        await db.refresh(db_invoice)
        
        return db_invoice
    
    async def get_overdue_invoices(
        self, db: AsyncSession, *, as_of: datetime = None
    ) -> List[Invoice]:
        """Get all overdue invoices as of a specific date."""
        if as_of is None:
            as_of = datetime.now(timezone.utc)
            
        result = await db.execute(
            select(self.model)
            .where(
                and_(
                    self.model.status.in_([
                        InvoiceStatus.SENT,
                        InvoiceStatus.PARTIALLY_PAID,
                        InvoiceStatus.OVERDUE
                    ]),
                    self.model.due_date < as_of.date(),
                    self.model.balance_due > 0
                )
            )
            .options(
                selectinload(Invoice.items),
                joinedload(Invoice.customer),
            )
            .order_by(self.model.due_date)
        )
        return result.scalars().all()

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
>>>>>>> e96df7278ce4216131b6c65d411c0723f4de7f91:backend/app/crud/accounts_receivable.py
