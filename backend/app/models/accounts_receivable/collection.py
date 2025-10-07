from sqlalchemy import Column, String, Text, DateTime, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class Collection(Base):
    __tablename__ = "ar_collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), nullable=False)
    collection_date = Column(DateTime(timezone=True), default=func.now())
    amount_due = Column(Numeric(15, 2), nullable=False)
    amount_collected = Column(Numeric(15, 2), default=0)
    days_overdue = Column(String(20))
    status = Column(String(50), default="pending")  # pending, in_progress, collected, written_off
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    collection_method = Column(String(50))  # email, phone, letter, legal
    notes = Column(Text)
    assigned_to = Column(UUID(as_uuid=True))
    next_action_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)


class CollectionActivity(Base):
    __tablename__ = "ar_collection_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("ar_collections.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # call, email, letter, payment, note
    activity_date = Column(DateTime(timezone=True), default=func.now())
    description = Column(Text)
    amount = Column(Numeric(15, 2))
    performed_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    collection = relationship("Collection", backref="activities")