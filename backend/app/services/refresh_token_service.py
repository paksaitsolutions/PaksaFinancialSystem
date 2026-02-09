"""Refresh token rotation and revocation persistence."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.security import SecurityManager
from app.models.core_models import RefreshToken


def issue_refresh_token(db: Session, user_id: str) -> str:
    token = SecurityManager.create_refresh_token({"sub": user_id})
    expires_at = datetime.utcnow() + timedelta(days=30)
    record = RefreshToken(
        user_id=user_id,
        token=token,
        issued_at=datetime.utcnow(),
        expires_at=expires_at,
    )
    db.add(record)
    try:
        db.commit()
    except (IntegrityError, OperationalError):
        db.rollback()
        return token
    return token


def rotate_refresh_token(db: Session, token: str) -> Dict[str, str]:
    record = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not record or record.revoked_at:
        raise ValueError("Invalid refresh token")
    if record.expires_at < datetime.utcnow():
        raise ValueError("Refresh token expired")

    new_token = SecurityManager.create_refresh_token({"sub": record.user_id})
    record.revoked_at = datetime.utcnow()
    record.replaced_by_token = new_token
    db.add(record)

    new_record = RefreshToken(
        user_id=record.user_id,
        token=new_token,
        issued_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db.add(new_record)
    try:
        db.commit()
    except (IntegrityError, OperationalError):
        db.rollback()
        raise ValueError("Refresh token storage unavailable")

    return {"refresh_token": new_token}


def revoke_refresh_token(db: Session, token: str) -> None:
    record = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if record and not record.revoked_at:
        record.revoked_at = datetime.utcnow()
        db.add(record)
        try:
            db.commit()
        except OperationalError:
            db.rollback()
