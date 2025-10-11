"""
Department model for organizational structure.
"""
from sqlalchemy import Column, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.db.base import Base

class Department(Base):
    """
    Department model representing organizational departments.
    """
    __tablename__ = "departments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(20), unique=True, nullable=True)
    description = Column(Text, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=True)
    cost_center = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    parent = relationship("Department", remote_side="Department.id", backref="sub_departments")
    employees = relationship("Employee", back_populates="department")
    manager = relationship("Employee", foreign_keys=[manager_id])
    
    def __repr__(self):
        return f"<Department {self.code}: {self.name}>"
