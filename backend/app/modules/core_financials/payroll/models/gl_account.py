"""
GL Account model for the Payroll module.
"""
from datetime import date
from decimal import Decimal
from sqlalchemy import Column, String, Text, Boolean, Date, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.core.database import Base
from app.modules.core_financials.payroll.models.base import PayrollBase


class GLAccount(PayrollBase, Base):
    """General Ledger Account model for payroll transactions."""
    __tablename__ = "payroll_gl_accounts"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Account identification
    account_number = Column(String(50), unique=True, index=True, nullable=False)
    account_name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Account classification
    account_type = Column(
        Enum('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE', name='gl_account_type_enum'),
        nullable=False,
        index=True
    )
    
    # Account category (more specific classification)
    category = Column(String(50), nullable=True, index=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_contra = Column(Boolean, default=False, nullable=False)  # For contra-accounts
    
    # Parent-child relationship for hierarchical accounts
    parent_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_gl_accounts.id'), 
        nullable=True,
        index=True
    )
    
    # Level in the account hierarchy (1 = top level, 2 = sub-account, etc.)
    level = Column(Integer, default=1, nullable=False)
    
    # Account balance information
    current_balance = Column(Numeric(20, 2), default=0, nullable=False)
    balance_as_of = Column(Date, nullable=True)
    
    # Budget information
    budget_amount = Column(Numeric(20, 2), nullable=True)
    budget_year = Column(Integer, nullable=True)
    
    # Tax information
    is_tax_related = Column(Boolean, default=False, nullable=False)
    tax_code = Column(String(20), nullable=True)
    
    # Reconciliation information
    requires_reconciliation = Column(Boolean, default=False, nullable=False)
    last_reconciled = Column(Date, nullable=True)
    
    # Custom fields and metadata
    custom_fields = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    parent = relationship("GLAccount", remote_side=[id], back_populates="children")
    children = relationship("GLAccount", back_populates="parent")
    
    # Add relationships to all models that reference this one
    earning_codes = relationship("EarningCode", back_populates="gl_account")
    deduction_codes = relationship("DeductionCode", back_populates="gl_account")
    tax_codes_employee = relationship(
        "TaxCode", 
        foreign_keys="[TaxCode.employee_liability_account_id]",
        back_populates="employee_liability_account"
    )
    tax_codes_employer = relationship(
        "TaxCode", 
        foreign_keys="[TaxCode.employer_liability_account_id]",
        back_populates="employer_liability_account"
    )
    benefit_plans_employee = relationship(
        "BenefitPlan", 
        foreign_keys="[BenefitPlan.employee_contra_account_id]",
        back_populates="employee_contra_account"
    )
    benefit_plans_employer = relationship(
        "BenefitPlan", 
        foreign_keys="[BenefitPlan.employer_contra_account_id]",
        back_populates="employer_contra_account"
    )
    
    def __repr__(self):
        return f"<GLAccount {self.account_number}: {self.account_name}>"
    
    @property
    def full_account_name(self):
        """Return the full account name including parent accounts."""
        if self.parent:
            return f"{self.parent.full_account_name}:{self.account_name}"
        return self.account_name
    
    @property
    def full_account_number(self):
        """Return the full account number including parent accounts."""
        if self.parent:
            return f"{self.parent.full_account_number}.{self.account_number}"
        return self.account_number
    
    @property
    def is_debit_balance(self):
        """Determine if this account type normally has a debit balance."""
        return self.account_type in ['ASSET', 'EXPENSE']
    
    @property
    def is_credit_balance(self):
        """Determine if this account type normally has a credit balance."""
        return self.account_type in ['LIABILITY', 'EQUITY', 'REVENUE']
    
    @property
    def balance_type(self):
        """Return 'debit' or 'credit' based on the account type."""
        return 'debit' if self.is_debit_balance else 'credit'
    
    @property
    def formatted_balance(self):
        """Return the balance with the appropriate sign based on account type."""
        if self.is_debit_balance:
            return self.current_balance
        return -self.current_balance if self.current_balance else Decimal('0')
    
    def update_balance(self, amount, is_debit):
        """Update the account balance based on a transaction.
        
        Args:
            amount (Decimal): The amount of the transaction
            is_debit (bool): Whether this is a debit to the account
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        try:
            if (is_debit and self.is_debit_balance) or (not is_debit and not self.is_debit_balance):
                # Increase the balance
                self.current_balance += amount
            else:
                # Decrease the balance
                self.current_balance -= amount
            return True
        except Exception as e:
            # Log the error
            return False
