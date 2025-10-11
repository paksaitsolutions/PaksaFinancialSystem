from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

# Import only unified models to ensure they are registered with SQLAlchemy
from app.models.core_models import *
from app.models.ai_bi_models import *
from app.models.user import User
from app.models.role import Role, Permission, RolePermission, UserPermission