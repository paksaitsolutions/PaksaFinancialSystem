from .payroll_processing import (
    PayrollStatusEnum,
    PayrollRunCreate,
    PayrollRunUpdate,
    PayrollRunResponse,
    PayslipCreate,
    PayslipResponse,
    PayrollCalculationRequest,
    PayrollSummary
)

# Aliases for backward compatibility
PayPeriod = PayrollRunResponse
PayPeriodCreate = PayrollRunCreate
PayRun = PayrollRunResponse
PayRunCreate = PayrollRunCreate
PayRunWithDetails = PayrollRunResponse
Payslip = PayslipResponse
PayslipWithDetails = PayslipResponse
YearToDateSummary = PayrollSummary