"""
Base model for all payroll-related models.
"""
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, DateTime, String, Boolean
from datetime import datetime


class PayrollBase:
    """Base class for all payroll models with common fields."""
    
    @declared_attr
    def __tablename__(cls):
        """
        Generate table name automatically from class name.
        Converts CamelCase class name to snake_case table name with 'payroll_' prefix.
        """
        import re
        # Convert CamelCase to snake_case
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        return f'payroll_{name}s'
    
    # Common audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(50), nullable=True)
    updated_by = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __repr__(self):
        """String representation of the model."""
        return f"<{self.__class__.__name__} {getattr(self, 'id', '')}>"
