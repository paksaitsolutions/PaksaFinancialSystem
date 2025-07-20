import { computed } from 'vue';
import { PayrollRecord, PayrollDeduction } from '../services/payrollApiService';

export const usePayrollCalculations = () => {
  /**
   * Calculate total deductions for a payroll record
   */
  const calculateTotalDeductions = (deductions: PayrollDeduction[]): number => {
    if (!deductions || !deductions.length) return 0;
    return deductions.reduce((sum, deduction) => sum + Number(deduction.amount), 0);
  };

  /**
   * Calculate net pay from gross pay and total deductions
   */
  const calculateNetPay = (grossPay: number, totalDeductions: number): number => {
    return Math.max(0, grossPay - totalDeductions);
  };

  /**
   * Format currency with proper localization
   */
  const formatCurrency = (amount: number, currency: string = 'USD'): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  /**
   * Calculate tax withholding based on tax brackets
   */
  const calculateTaxWithholding = (
    grossPay: number,
    taxBrackets: Array<{ min: number; max?: number; rate: number }>,
    annualSalary: boolean = false
  ): number => {
    let taxableIncome = annualSalary ? grossPay : grossPay * 26; // Convert to annual if bi-weekly
    let tax = 0;

    for (const bracket of taxBrackets) {
      if (bracket.max && taxableIncome > bracket.max) {
        tax += (bracket.max - (bracket.min - 1)) * bracket.rate;
      } else if (taxableIncome > bracket.min) {
        tax += (taxableIncome - (bracket.min - 1)) * bracket.rate;
        break;
      }
    }

    return annualSalary ? tax / 26 : tax; // Convert back to bi-weekly if needed
  };

  /**
   * Calculate FICA (Social Security and Medicare) taxes
   */
  const calculateFICATaxes = (grossPay: number, year: number = new Date().getFullYear()) => {
    // Social Security tax (6.2% up to wage base limit)
    const SOCIAL_SECURITY_RATE = 0.062;
    const SOCIAL_SECURITY_WAGE_BASE = 147000; // 2023, update for current year
    
    // Medicare tax (1.45% + 0.9% for high earners)
    const MEDICARE_RATE = 0.0145;
    const ADDITIONAL_MEDICARE_RATE = 0.009;
    const ADDITIONAL_MEDICARE_THRESHOLD = 200000; // For single filers, adjust for other statuses

    // Calculate Social Security tax
    const socialSecurityTax = Math.min(
      grossPay * SOCIAL_SECURITY_RATE,
      (SOCIAL_SECURITY_WAGE_BASE / 26) * SOCIAL_SECURITY_RATE
    );

    // Calculate Medicare tax
    let medicareTax = grossPay * MEDICARE_RATE;
    if (grossPay * 26 > ADDITIONAL_MEDICARE_THRESHOLD) {
      medicareTax += (grossPay - (ADDITIONAL_MEDICARE_THRESHOLD / 26)) * ADDITIONAL_MEDICARE_RATE;
    }

    return {
      socialSecurity: socialSecurityTax,
      medicare: medicareTax,
      total: socialSecurityTax + medicareTax
    };
  };

  /**
   * Calculate year-to-date (YTD) totals for an employee
   */
  const calculateYtdTotals = (payrollRecords: PayrollRecord[], employeeId: number) => {
    const employeeRecords = payrollRecords.filter(
      record => record.employee_id === employeeId && record.status === 'paid'
    );

    return employeeRecords.reduce(
      (totals, record) => ({
        grossPay: totals.grossPay + (Number(record.gross_pay) || 0),
        totalTaxes: totals.totalTaxes + (calculateTotalDeductions(record.deductions || []) || 0),
        netPay: totals.netPay + (Number(record.net_pay) || 0),
        count: totals.count + 1
      }),
      { grossPay: 0, totalTaxes: 0, netPay: 0, count: 0 }
    );
  };

  /**
   * Generate a payroll summary for reporting
   */
  const generatePayrollSummary = (payrollRecord: PayrollRecord) => {
    if (!payrollRecord) return null;

    const deductions = payrollRecord.deductions || [];
    const totalDeductions = calculateTotalDeductions(deductions);
    const netPay = calculateNetPay(Number(payrollRecord.gross_pay), totalDeductions);

    // Group deductions by type
    const deductionsByType = deductions.reduce((groups, deduction) => {
      const type = deduction.deduction_type;
      if (!groups[type]) {
        groups[type] = 0;
      }
      groups[type] += Number(deduction.amount);
      return groups;
    }, {} as Record<string, number>);

    return {
      grossPay: Number(payrollRecord.gross_pay),
      totalDeductions,
      netPay,
      deductionsByType,
      payPeriod: {
        start: payrollRecord.pay_period_start,
        end: payrollRecord.pay_period_end,
        payDate: payrollRecord.pay_date
      },
      status: payrollRecord.status,
      employee: payrollRecord.employee
    };
  };

  return {
    calculateTotalDeductions,
    calculateNetPay,
    formatCurrency,
    calculateTaxWithholding,
    calculateFICATaxes,
    calculateYtdTotals,
    generatePayrollSummary
  };
};

export default usePayrollCalculations;
