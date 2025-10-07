"""
Payroll models package.

This package contains all the database models for the Payroll module.
"""

# Import base model first
from .base import PayrollBase

# Import all models
from .gl_account import GLAccount
# from .payroll_codes import (
#     EarningCode,
#     DeductionCode,
#     TaxCode,
#     BenefitPlan,
#     PayPeriod
# )

# Import other models
# from .employee import Employee
from .payroll_processing import PayrollRun, PayrollItem
# from .department import Department
# from .payslip import Payslip
# from .tax_filing import TaxFiling

# Export all models
__all__ = [
    'PayrollBase',
    'GLAccount',
    # 'EarningCode',
    # 'DeductionCode',
    # 'TaxCode',
    # 'BenefitPlan',
    # 'PayPeriod',
    # 'Employee',
    'PayrollRun',
    'PayrollItem',
    # 'Department'
]
