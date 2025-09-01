"""
Reconciliation API (cash-based)

Endpoints to start, track, and complete cash/bank reconciliations.
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Reconciliation, ReconciliationMatch, CashTransaction

router = APIRouter(prefix="/reconciliation", tags=["reconciliation"])


DEFAULT_TENANT_ID = "12345678-1234-5678-9012-123456789012"


class StartReconciliationRequest(BaseModel):
    account_id: str
    statement_date: str
    opening_balance: float
    closing_balance: float
    currency: Optional[str] = "USD"


@router.get("/status")
async def get_reconciliation_status(
    account_id: str = Query(...),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> Any:
    stmt = (
        select(Reconciliation)
        .where(
            and_(
                Reconciliation.account_id == account_id,
                Reconciliation.status != "completed",
            )
        )
        .order_by(desc(Reconciliation.created_at))
        .limit(1)
    )
    result = await db.execute(stmt)
    active = result.scalars().first()

    def serialize(rec: Reconciliation) -> dict:
        return {
            "id": str(rec.id),
            "account_id": str(rec.account_id),
            "statement_date": rec.statement_date,
            "opening_balance": float(rec.opening_balance or 0),
            "closing_balance": float(rec.closing_balance or 0),
            "currency": rec.currency or "USD",
            "status": rec.status,
        }

    return {"active_reconciliation": serialize(active) if active else None}


@router.post("/start")
async def start_reconciliation(
    payload: StartReconciliationRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    rec = Reconciliation(
        tenant_id=DEFAULT_TENANT_ID,
        account_id=payload.account_id,
        statement_date=payload.statement_date,
        opening_balance=payload.opening_balance,
        closing_balance=payload.closing_balance,
        currency=payload.currency or "USD",
        status="in_progress",
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return {"reconciliation": {
        "id": str(rec.id),
        "account_id": str(rec.account_id),
        "statement_date": rec.statement_date,
        "opening_balance": float(rec.opening_balance or 0),
        "closing_balance": float(rec.closing_balance or 0),
        "currency": rec.currency or "USD",
        "status": rec.status,
    }}


@router.get("/{reconciliation_id}/unreconciled")
async def get_unreconciled_transactions(
    reconciliation_id: str,
    account_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> Any:
    # All transactions for this account
    all_txn_stmt = select(CashTransaction).where(CashTransaction.cash_account_id == account_id)
    all_txn = (await db.execute(all_txn_stmt)).scalars().all()

    # Already matched in this reconciliation
    matched_stmt = select(ReconciliationMatch.cash_transaction_id).where(
        ReconciliationMatch.reconciliation_id == reconciliation_id
    )
    matched_ids = {str(row[0]) for row in await db.execute(matched_stmt)}

    # Build response list of unreconciled
    transactions = []
    for t in all_txn:
        tid = str(t.id)
        if tid in matched_ids:
            continue
        amt = float(t.amount or 0)
        transactions.append({
            "id": tid,
            "transaction_date": t.transaction_date,
            "reference": t.reference,
            "description": t.description,
            "amount": amt if t.transaction_type != "credit" else -abs(amt),
            "type": t.transaction_type or ("debit" if amt >= 0 else "credit"),
            "source_type": "cash_transaction",
            "source_id": tid,
        })
    return {"transactions": transactions}


class MatchItem(BaseModel):
    transaction_id: str
    statement_item_ids: Optional[List[str]] = None


class MatchRequest(BaseModel):
    matches: List[MatchItem]


@router.post("/match")
async def match_transactions(
    payload: MatchRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    if not payload.matches:
        return {"matched": 0}

    matched_count = 0
    for item in payload.matches:
        # Find transaction to derive account
        txn = (await db.execute(select(CashTransaction).where(CashTransaction.id == item.transaction_id))).scalars().first()
        if not txn:
            continue
        # Find an active reconciliation for this account
        rec_stmt = (
            select(Reconciliation)
            .where(and_(Reconciliation.account_id == txn.cash_account_id, Reconciliation.status == "in_progress"))
            .order_by(desc(Reconciliation.created_at))
            .limit(1)
        )
        rec = (await db.execute(rec_stmt)).scalars().first()
        if not rec:
            continue

        # Create or ignore duplicate match
        match = ReconciliationMatch(
            tenant_id=DEFAULT_TENANT_ID,
            reconciliation_id=rec.id,
            cash_transaction_id=txn.id,
        )
        db.add(match)
        try:
            await db.commit()
            matched_count += 1
        except Exception:
            # Likely unique constraint violation; rollback and continue
            await db.rollback()

    return {"matched": matched_count}


@router.post("/{reconciliation_id}/complete")
async def complete_reconciliation(
    reconciliation_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    rec = (await db.execute(select(Reconciliation).where(Reconciliation.id == reconciliation_id))).scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    rec.status = "completed"
    db.add(rec)
    await db.commit()
    return {"status": "completed"}


@router.post("/import")
async def import_bank_statement(
    account_id: str = Query(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> Any:
    # Placeholder: accept the upload; parsing not implemented here
    # In a real implementation, parse and stage statement items for matching.
    _ = account_id
    _ = db
    size = 0
    chunk = await file.read()
    size += len(chunk or b"")
    return {"imported": True, "filename": file.filename, "size": size}

