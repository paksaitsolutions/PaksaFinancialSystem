"""
Minimal reconciliation models integrated with app.core.database Base.

This implementation reconciles CashAccount transactions with bank statements.
"""
from sqlalchemy import Column, String, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class Reconciliation(BaseModel):
    __tablename__ = "reconciliations"

    tenant_id = Column(GUID(), nullable=False, index=True)
    # Link to cash/bank account being reconciled
    account_id = Column(GUID(), ForeignKey("cash_accounts.id"), nullable=False, index=True)

    # Statement info
    statement_date = Column(String(10), nullable=False)
    opening_balance = Column(Numeric(15, 2), nullable=False)
    closing_balance = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")

    status = Column(String(20), nullable=False, default="in_progress")  # in_progress, completed

    # Relationships
    account = relationship("CashAccount")
    matches = relationship("ReconciliationMatch", back_populates="reconciliation", cascade="all, delete-orphan")


class ReconciliationMatch(BaseModel):
    __tablename__ = "reconciliation_matches"

    tenant_id = Column(GUID(), nullable=False, index=True)
    reconciliation_id = Column(GUID(), ForeignKey("reconciliations.id", ondelete="CASCADE"), nullable=False, index=True)
    cash_transaction_id = Column(GUID(), ForeignKey("cash_transactions.id", ondelete="CASCADE"), nullable=False, index=True)

    reconciliation = relationship("Reconciliation", back_populates="matches")
    transaction = relationship("CashTransaction")

    __table_args__ = (
        UniqueConstraint("reconciliation_id", "cash_transaction_id", name="uq_recon_txn_unique"),
    )

