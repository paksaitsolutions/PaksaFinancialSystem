from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, Integer, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.models.user import User  # Assuming User model exists

class PurchaseRequisition(Base):
    """
    Purchase Requisition model for tracking purchase requests before they become purchase orders.
    """
    __tablename__ = 'purchase_requisitions'

    id = Column(Integer, primary_key=True, index=True)
    requisition_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    requisition_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    required_date = Column(DateTime, nullable=True)
    status = Column(Enum('draft', 'submitted', 'approved', 'rejected', 'converted_to_po', name='requisition_status'), 
                   default='draft', nullable=False)
    priority = Column(Enum('low', 'medium', 'high', 'urgent', name='requisition_priority'), 
                     default='medium', nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    notes = Column(Text, nullable=True)
    metadata_ = Column('metadata', JSON, nullable=True)
    
    # Relationships
    requester_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    requester = relationship("User", back_populates="purchase_requisitions")
    
    approver_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    approver = relationship("User", foreign_keys=[approver_id])
    
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)  # Assuming Department model exists
    
    items = relationship("RequisitionItem", back_populates="requisition", 
                        cascade="all, delete-orphan")
    
    # Audit fields
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    updated_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    
    def __repr__(self):
        return f"<PurchaseRequisition {self.requisition_number}>"


class RequisitionItem(Base):
    """
    Individual line items for a purchase requisition.
    """
    __tablename__ = 'requisition_items'
    
    id = Column(Integer, primary_key=True, index=True)
    requisition_id = Column(Integer, ForeignKey('purchase_requisitions.id', ondelete='CASCADE'), 
                          nullable=False)
    item_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Float, nullable=False, default=1.0)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    
    # Links to inventory/catalog if available
    item_code = Column(String(100), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)  # Assuming Category model exists
    
    # Project/GL account tracking
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)  # Assuming Project model exists
    gl_account_id = Column(Integer, ForeignKey('gl_accounts.id'), nullable=True)  # Assuming GLAccount model exists
    
    # Status tracking
    status = Column(Enum('pending', 'approved', 'rejected', 'ordered', 'received', 'cancelled', 
                        name='requisition_item_status'), default='pending', nullable=False)
    
    # Relationships
    requisition = relationship("PurchaseRequisition", back_populates="items")
    
    # Audit fields
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<RequisitionItem {self.id} - {self.item_name}>"
