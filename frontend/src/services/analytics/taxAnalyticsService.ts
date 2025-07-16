import { useTaxPolicyStore } from '@/stores/tax/policy';
import { usePayrollStore } from '@/stores/payroll';
import { useAIStore } from '@/stores/ai';
import { formatCurrency, formatDate } from '@/utils/formatters';

export class TaxAnalyticsService {
  private taxPolicyStore = useTaxPolicyStore();
  private payrollStore = usePayrollStore();
  private aiStore = useAIStore();

  async generateTaxInsights(payRunId: string): Promise<{ insights: string; recommendations: string }> {
    try {
      const payRun = await this.payrollStore.getPayRunById(payRunId);
      const taxPolicy = await this.taxPolicyStore.getCurrentPolicy();
      
      const prompt = this.generateInsightsPrompt(payRun, taxPolicy);
      const response = await this.aiStore.generateInsights(prompt);
      
      return {
        insights: response.insights,
        recommendations: response.recommendations
      };
    } catch (error) {
      console.error('Error generating tax insights:', error);
      throw error;
    }
  }

  async analyzeTaxTrends(period: string): Promise<{ trends: any; analysis: string }> {
    try {
      const payRuns = await this.payrollStore.getPayRunsByPeriod(period);
      const taxPolicy = await this.taxPolicyStore.getCurrentPolicy();
      
      const analysisData = this.calculateTaxMetrics(payRuns);
      const prompt = this.generateTrendsPrompt(analysisData, taxPolicy);
      
      const response = await this.aiStore.generateAnalysis(prompt);
      
      return {
        trends: analysisData,
        analysis: response.analysis
      };
    } catch (error) {
      console.error('Error analyzing tax trends:', error);
      throw error;
    }
  }

  private calculateTaxMetrics(payRuns: any[]): any {
    const metrics = {
      totalTax: 0,
      avgTaxPerEmployee: 0,
      exemptionUsage: {},
      jurisdictionalBreakdown: {},
      complianceRate: 0
    };

    payRuns.forEach(run => {
      metrics.totalTax += run.taxAmount || 0;
      
      if (run.payslips && run.payslips.length > 0) {
        metrics.avgTaxPerEmployee += (run.taxAmount || 0) / run.payslips.length;
      }
      
      // Calculate exemption usage
      if (run.exemptions) {
        Object.entries(run.exemptions).forEach(([type, amount]) => {
          if (!metrics.exemptionUsage[type]) {
            metrics.exemptionUsage[type] = 0;
          }
          metrics.exemptionUsage[type] += amount;
        });
      }
    });

    metrics.avgTaxPerEmployee = metrics.avgTaxPerEmployee / payRuns.length;
    
    return metrics;
  }

  private generateInsightsPrompt(payRun: any, taxPolicy: any): string {
    return `Analyze the tax implications of this pay run:
    Pay Run Details:
    - Period: ${formatDate(payRun.periodStart)} to ${formatDate(payRun.periodEnd)}
    - Total Employees: ${payRun.payslips.length}
    - Total Tax Amount: ${formatCurrency(payRun.taxAmount)}
    - Tax Breakdown: ${JSON.stringify(payRun.taxBreakdown)}
    
    Current Tax Policy:
    ${JSON.stringify(taxPolicy)}
    
    Provide insights on tax compliance, potential optimizations, and areas of concern.`;
  }

  private generateTrendsPrompt(metrics: any, taxPolicy: any): string {
    return `Analyze the tax trends based on these metrics:
    Metrics:
    ${JSON.stringify(metrics)}
    
    Current Tax Policy:
    ${JSON.stringify(taxPolicy)}
    
    Provide a detailed analysis of tax trends, compliance patterns, and recommendations for optimization.`;
  }
}

export const taxAnalyticsService = new TaxAnalyticsService();
