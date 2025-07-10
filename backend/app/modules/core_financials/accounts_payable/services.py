import uuid
from decimal import Decimal
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from . import models, schemas
from .exceptions import (
    BillNotFoundException,
    InvalidBillOperationException,
    InvalidPaymentOperationException,
    VendorNotFoundException,
)
from ..accounting.services import AccountService # For validating expense accounts

class VendorService:
    """Service for managing vendors."""
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_vendor(self, vendor_create: schemas.VendorCreate) -> models.Vendor:
        new_vendor = models.Vendor(**vendor_create.dict())
        self.db.add(new_vendor)
        await self.db.commit()
        await self.db.refresh(new_vendor)
        return new_vendor

    async def get_vendor_by_id(self, vendor_id: uuid.UUID) -> models.Vendor:
        vendor = await self.db.get(models.Vendor, vendor_id)
        if not vendor:
            raise VendorNotFoundException(str(vendor_id))
        return vendor

class BillService:
    """Service for managing bills."""
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.account_service = AccountService(db_session)

    async def create_bill(self, bill_create: schemas.BillCreate) -> models.Bill:
        # Ensure vendor exists
        await VendorService(self.db).get_vendor_by_id(bill_create.vendor_id)

        total_amount = Decimal(0)
        line_items_data = []
        for item in bill_create.line_items:
            # Ensure expense account exists
            await self.account_service.get_account_by_id(item.account_id)
            line_total = item.quantity * item.unit_price
            total_amount += line_total
            line_items_data.append({**item.dict(), "total_price": line_total})

        new_bill = models.Bill(
            **bill_create.dict(exclude={"line_items"}), total_amount=total_amount
        )
        self.db.add(new_bill)
        await self.db.flush() # Get ID for line items

        for line_data in line_items_data:
            new_line = models.BillLineItem(**line_data, bill_id=new_bill.id)
            self.db.add(new_line)

        await self.db.commit()
        await self.db.refresh(new_bill)
        return new_bill

    async def get_bill_by_id(self, bill_id: uuid.UUID) -> models.Bill:
        result = await self.db.execute(
            select(models.Bill)
            .options(joinedload(models.Bill.line_items), joinedload(models.Bill.vendor))
            .where(models.Bill.id == bill_id)
        )
        bill = result.scalars().first()
        if not bill:
            raise BillNotFoundException(str(bill_id))
        return bill

class PaymentService:
    """Service for managing payments to vendors."""
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.bill_service = BillService(db_session)

    async def create_payment(self, payment_create: schemas.PaymentCreate) -> models.Payment:
        total_allocated = sum(alloc.amount_allocated for alloc in payment_create.allocations)
        if total_allocated > payment_create.amount:
            raise InvalidPaymentOperationException("Total allocated amount exceeds payment amount.")

        # Ensure vendor exists
        await VendorService(self.db).get_vendor_by_id(payment_create.vendor_id)

        new_payment = models.Payment(**payment_create.dict(exclude={"allocations"}))
        self.db.add(new_payment)
        await self.db.flush()

        for alloc_data in payment_create.allocations:
            bill = await self.bill_service.get_bill_by_id(alloc_data.bill_id)
            if bill.vendor_id != new_payment.vendor_id:
                raise InvalidPaymentOperationException("Cannot allocate payment to a bill from a different vendor.")
            
            bill.amount_paid += alloc_data.amount_allocated
            if bill.amount_paid > bill.total_amount:
                raise InvalidPaymentOperationException(f"Overpayment on bill {bill.id}.")
            
            if bill.amount_paid == bill.total_amount:
                bill.status = models.BillStatus.PAID
            else:
                bill.status = models.BillStatus.PARTIALLY_PAID

            new_allocation = models.PaymentAllocation(
                **alloc_data.dict(), payment_id=new_payment.id
            )
            self.db.add(new_allocation)

        new_payment.status = models.PaymentStatus.PAID # Assuming direct payment
        await self.db.commit()
        await self.db.refresh(new_payment)
        return new_payment
