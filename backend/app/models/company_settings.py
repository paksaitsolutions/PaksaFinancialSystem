from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class CompanySettings(Base):
    __tablename__ = "company_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False, unique=True)
    invoice_template = Column(String, nullable=True)
    branding = Column(JSON, nullable=True)
    default_currency = Column(String, nullable=True)
    tax_rates = Column(JSON, nullable=True)
    language = Column(String, nullable=True)
    payment_methods = Column(JSON, nullable=True)
    document_numbering = Column(JSON, nullable=True)
    custom_fields = Column(JSON, nullable=True)
    notifications = Column(JSON, nullable=True)
    integrations = Column(JSON, nullable=True)
    feature_toggles = Column(JSON, nullable=True)
    data_retention_policy = Column(String, nullable=True)

    company = relationship("Company", back_populates="settings")
