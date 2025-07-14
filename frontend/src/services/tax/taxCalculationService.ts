import { ref, computed } from 'vue';
import { useTaxPolicyStore } from '@/stores/tax/policy';
import { TaxPolicy, TaxRate, TaxExemption, TaxBracket } from '@/types/tax';
import { EmployeePayrollInfo, Payslip, PayRun } from '@/types/payroll';
import { formatCurrency } from '@/utils/formatting';

interface TaxCalculationResult {
  taxAmount: number;
  taxBreakdown: {
    [key: string]: number;
  };
  exemptions: {
    [key: string]: number;
  };
}

export class TaxCalculationService {
  private policyStore = useTaxPolicyStore();
  private currentPolicy = ref<TaxPolicy | null>(null);

  constructor() {
    // Watch for policy changes
    this.policyStore.$subscribe(() => {
      this.currentPolicy.value = this.policyStore.getCurrentPolicy();
    });
  }

  // Calculate tax for a single payslip
  calculatePayslipTax(payslip: Payslip): TaxCalculationResult {
    const policy = this.currentPolicy.value;
    if (!policy) {
      throw new Error('Tax policy not loaded');
    }

    const grossIncome = this.calculateGrossIncome(payslip);
    const applicableExemptions = this.calculateExemptions(payslip, policy);
    const taxableIncome = grossIncome - Object.values(applicableExemptions).reduce((a, b) => a + b, 0);

    return {
      taxAmount: this.calculateBracketedTax(taxableIncome, policy.tax_rates),
      taxBreakdown: this.calculateBracketBreakdown(taxableIncome, policy.tax_rates),
      exemptions: applicableExemptions
    };
  }

  // Calculate tax for an entire pay run
  calculatePayRunTax(payRun: PayRun): TaxCalculationResult {
    const policy = this.currentPolicy.value;
    if (!policy) {
      throw new Error('Tax policy not loaded');
    }

    const totalGrossIncome = payRun.payslips.reduce(
      (total, payslip) => total + this.calculateGrossIncome(payslip),
      0
    );

    // Calculate total exemptions (some may be per-employee, some per-payrun)
    const totalExemptions = this.calculatePayRunExemptions(payRun, policy);
    const taxableIncome = totalGrossIncome - Object.values(totalExemptions).reduce((a, b) => a + b, 0);

    return {
      taxAmount: this.calculateBracketedTax(taxableIncome, policy.tax_rates),
      taxBreakdown: this.calculateBracketBreakdown(taxableIncome, policy.tax_rates),
      exemptions: totalExemptions
    };
  }

  // Calculate year-to-date tax for an employee
  calculateYearToDateTax(employeeInfo: EmployeePayrollInfo): TaxCalculationResult {
    const policy = this.currentPolicy.value;
    if (!policy) {
      throw new Error('Tax policy not loaded');
    }

    const grossIncome = employeeInfo.year_to_date.gross_income;
    const applicableExemptions = this.calculateExemptionsForYTD(employeeInfo, policy);
    const taxableIncome = grossIncome - Object.values(applicableExemptions).reduce((a, b) => a + b, 0);

    return {
      taxAmount: this.calculateBracketedTax(taxableIncome, policy.tax_rates),
      taxBreakdown: this.calculateBracketBreakdown(taxableIncome, policy.tax_rates),
      exemptions: applicableExemptions
    };
  }

  private calculateGrossIncome(payslip: Payslip): number {
    return payslip.earnings.reduce((total, earning) => total + earning.amount, 0);
  }

  private calculateExemptions(payslip: Payslip, policy: TaxPolicy): { [key: string]: number } {
    const applicableExemptions: { [key: string]: number } = {};
    
    policy.tax_exemptions.forEach(exemption => {
      if (this.isExemptionApplicable(payslip, exemption)) {
        applicableExemptions[exemption.type] = exemption.amount;
      }
    });

    return applicableExemptions;
  }

  private calculatePayRunExemptions(payRun: PayRun, policy: TaxPolicy): { [key: string]: number } {
    const applicableExemptions: { [key: string]: number } = {};
    
    policy.tax_exemptions.forEach(exemption => {
      if (this.isPayRunExemptionApplicable(payRun, exemption)) {
        applicableExemptions[exemption.type] = exemption.amount;
      }
    });

    return applicableExemptions;
  }

  private calculateExemptionsForYTD(employeeInfo: EmployeePayrollInfo, policy: TaxPolicy): { [key: string]: number } {
    const applicableExemptions: { [key: string]: number } = {};
    
    policy.tax_exemptions.forEach(exemption => {
      if (this.isYTDExemptionApplicable(employeeInfo, exemption)) {
        applicableExemptions[exemption.type] = exemption.amount;
      }
    });

    return applicableExemptions;
  }

  private calculateBracketedTax(income: number, taxRates: TaxRate[]): number {
    let taxAmount = 0;
    let remainingIncome = income;

    taxRates.forEach(rate => {
      if (remainingIncome <= 0) return;

      const taxableAmount = Math.min(remainingIncome, rate.bracket.upper - rate.bracket.lower);
      taxAmount += taxableAmount * rate.rate;
      remainingIncome -= taxableAmount;
    });

    return taxAmount;
  }

  private calculateBracketBreakdown(income: number, taxRates: TaxRate[]): { [key: string]: number } {
    const breakdown: { [key: string]: number } = {};
    let remainingIncome = income;

    taxRates.forEach(rate => {
      if (remainingIncome <= 0) return;

      const bracketName = `${rate.bracket.lower}-${rate.bracket.upper}`;
      const taxableAmount = Math.min(remainingIncome, rate.bracket.upper - rate.bracket.lower);
      breakdown[bracketName] = taxableAmount * rate.rate;
      remainingIncome -= taxableAmount;
    });

    return breakdown;
  }

  private isExemptionApplicable(payslip: Payslip, exemption: TaxExemption): boolean {
    // Implement exemption eligibility logic based on employee category, income level, etc.
    return true; // Default implementation
  }

  private isPayRunExemptionApplicable(payRun: PayRun, exemption: TaxExemption): boolean {
    // Implement pay run-level exemption eligibility logic
    return true; // Default implementation
  }

  private isYTDExemptionApplicable(employeeInfo: EmployeePayrollInfo, exemption: TaxExemption): boolean {
    // Implement YTD exemption eligibility logic
    return true; // Default implementation
  }
}

// Export singleton instance
export const taxCalculationService = new TaxCalculationService();
