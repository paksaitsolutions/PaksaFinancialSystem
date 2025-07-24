"""
Benefits models for the Payroll module.
"""
from datetime import date, datetime
from sqlalchemy import Column, Date, Enum, ForeignKey, Numeric, String, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.db.base import Base
from app.modules.core_financials.payroll.models.base import PayrollBase


class BenefitPlan(PayrollBase, Base):
    """Benefit plan model for different types of employee benefits."""
    __tablename__ = "payroll_benefit_plans"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # Plan identification
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    plan_code = Column(String(50), unique=True, index=True, nullable=False)
    
    # Plan type
    benefit_type = Column(
        Enum('HEALTH_INSURANCE', 'DENTAL_INSURANCE', 'VISION_INSURANCE', 
             'LIFE_INSURANCE', 'DISABILITY_INSURANCE', 'RETIREMENT', 'FLEX_SPENDING',
             'TRANSPORTATION', 'MEAL_ALLOWANCE', 'EDUCATION', 'CHILD_CARE', 'OTHER',
             name='benefit_type_enum'),
        nullable=False
    )
    
    # Coverage details
    coverage_type = Column(
        Enum('EMPLOYEE_ONLY', 'EMPLOYEE_PLUS_ONE', 'EMPLOYEE_PLUS_FAMILY', 
             'CUSTOM', 'OTHER', name='coverage_type_enum'),
        nullable=False
    )
    
    # Cost structure
    cost_calculation = Column(
        Enum('FIXED_AMOUNT', 'PERCENTAGE_OF_SALARY', 'PER_EMPLOYEE', 
             'PER_DEPENDENT', 'TIERED', 'OTHER', name='cost_calculation_enum'),
        nullable=False
    )
    
    # Employer contribution
    employer_contribution_type = Column(
        Enum('FIXED_AMOUNT', 'PERCENTAGE', 'TIERED', 'NONE', name='contribution_type_enum'),
        default='NONE',
        nullable=False
    )
    employer_contribution_value = Column(Numeric(10, 4), nullable=True)
    
    # Employee contribution
    employee_contribution_type = Column(
        Enum('FIXED_AMOUNT', 'PERCENTAGE', 'TIERED', 'NONE', name='contribution_type_enum'),
        default='NONE',
        nullable=False
    )
    employee_contribution_value = Column(Numeric(10, 4), nullable=True)
    
    # Plan dates
    effective_date = Column(Date, nullable=False, index=True)
    renewal_date = Column(Date, nullable=True, index=True)
    termination_date = Column(Date, nullable=True, index=True)
    
    # Plan limits
    annual_maximum = Column(Numeric(15, 2), nullable=True)
    lifetime_maximum = Column(Numeric(15, 2), nullable=True)
    
    # Tax implications
    is_pretax = Column(Boolean, default=False, nullable=False)  # For Section 125 plans
    is_taxable = Column(Boolean, default=False, nullable=False)  # If benefit is taxable income
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    enrollments = relationship("EmployeeBenefit", back_populates="benefit_plan")
    
    def __repr__(self):
        return f"<BenefitPlan {self.plan_code}: {self.name}>"
    
    @property
    def is_currently_active(self):
        """Check if the benefit plan is currently active."""
        today = date.today()
        if not self.is_active:
            return False
        if self.effective_date > today:
            return False
        if self.termination_date and self.termination_date < today:
            return False
        return True


class EmployeeBenefit(PayrollBase, Base):
    """Employee enrollment in a benefit plan."""
    __tablename__ = "payroll_employee_benefits"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    # References
    employee_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_employees.id'), 
        nullable=False,
        index=True
    )
    benefit_plan_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('payroll_benefit_plans.id'), 
        nullable=False,
        index=True
    )
    
    # Enrollment details
    enrollment_date = Column(Date, nullable=False, index=True)
    coverage_start_date = Column(Date, nullable=False, index=True)
    coverage_end_date = Column(Date, nullable=True, index=True)
    
    # Coverage level
    coverage_level = Column(
        Enum('EMPLOYEE_ONLY', 'EMPLOYEE_PLUS_ONE', 'EMPLOYEE_PLUS_FAMILY', 
             'CUSTOM', 'OTHER', name='coverage_level_enum'),
        nullable=False
    )
    
    # Dependents covered (if any)
    dependents_covered = Column(Integer, default=0, nullable=False)
    
    # Cost and contributions
    employer_contribution = Column(Numeric(15, 2), default=0, nullable=False)
    employee_contribution = Column(Numeric(15, 2), default=0, nullable=False)
    total_cost = Column(Numeric(15, 2), nullable=False)
    
    # Payment frequency (how often the premium is paid)
    payment_frequency = Column(
        Enum('WEEKLY', 'BI_WEEKLY', 'SEMI_MONTHLY', 'MONTHLY', 'QUARTERLY', 'ANNUALLY',
             name='payment_frequency_enum'),
        default='MONTHLY',
        nullable=False
    )
    
    # Benefit limits and usage
    annual_maximum = Column(Numeric(15, 2), nullable=True)
    lifetime_maximum = Column(Numeric(15, 2), nullable=True)
    amount_used_ytd = Column(Numeric(15, 2), default=0, nullable=False)
    amount_used_lifetime = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Status
    status = Column(
        Enum('ACTIVE', 'PENDING', 'TERMINATED', 'SUSPENDED', 'COBRA', 'OTHER',
             name='benefit_status_enum'),
        default='ACTIVE',
        nullable=False,
        index=True
    )
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", backref="benefits")
    benefit_plan = relationship("BenefitPlan", back_populates="enrollments")
    
    def __repr__(self):
        return f"<EmployeeBenefit {self.benefit_plan.name} for Employee {self.employee_id}>"
    
    @property
    def is_currently_active(self):
        """Check if the benefit enrollment is currently active."""
        today = date.today()
        if self.status != 'ACTIVE':
            return False
        if self.coverage_start_date > today:
            return False
        if self.coverage_end_date and self.coverage_end_date < today:
            return False
        return True
    
    def calculate_contributions(self, employee_salary=None):
        """Calculate employer and employee contributions based on the benefit plan."""
        plan = self.benefit_plan
        
        # Calculate total cost
        if plan.cost_calculation == 'FIXED_AMOUNT':
            self.total_cost = plan.employer_contribution_value or 0
        elif plan.cost_calculation == 'PERCENTAGE_OF_SALARY' and employee_salary is not None:
            self.total_cost = (employee_salary * (plan.employer_contribution_value or 0) / 100).quantize(Decimal('0.01'))
        # Add other cost calculation methods as needed
        
        # Calculate employer contribution
        if plan.employer_contribution_type == 'FIXED_AMOUNT':
            self.employer_contribution = plan.employer_contribution_value or 0
        elif plan.employer_contribution_type == 'PERCENTAGE':
            self.employer_contribution = (self.total_cost * (plan.employer_contribution_value or 0) / 100).quantize(Decimal('0.01'))
        else:
            self.employer_contribution = Decimal('0.00')
        
        # Calculate employee contribution
        if plan.employee_contribution_type == 'FIXED_AMOUNT':
            self.employee_contribution = plan.employee_contribution_value or 0
        elif plan.employee_contribution_type == 'PERCENTAGE':
            self.employee_contribution = (self.total_cost * (plan.employee_contribution_value or 0) / 100).quantize(Decimal('0.01'))
        else:
            self.employee_contribution = self.total_cost - self.employer_contribution
        
        # Ensure total cost equals employer + employee contributions
        self.total_cost = (self.employer_contribution + self.employee_contribution).quantize(Decimal('0.01'))
