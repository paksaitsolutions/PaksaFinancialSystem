import { api } from '@/utils/api';

export interface ComplianceReport {
  id: string;
  report_name: string;
  report_type: string;
  report_number: string;
  start_date: string;
  end_date: string;
  status: string;
  generated_at?: string;
  report_data?: Record<string, any>;
  file_path?: string;
  file_size?: string;
  requested_by: string;
  description?: string;
  created_at: string;
}

export interface ComplianceReportRequest {
  report_type: string;
  start_date: Date;
  end_date: Date;
  filters?: Record<string, any>;
  description?: string;
}

export interface CompliancePolicy {
  id: string;
  policy_name: string;
  policy_code: string;
  description?: string;
  requirements?: Record<string, any>;
  compliance_framework?: string;
  is_active: boolean;
  effective_date: string;
  review_date?: string;
  created_at: string;
  updated_at: string;
}

export interface CompliancePolicyRequest {
  policy_name: string;
  policy_code: string;
  description?: string;
  requirements?: Record<string, any>;
  compliance_framework?: string;
  effective_date: Date;
  review_date?: Date;
}

export interface ComplianceDashboard {
  total_reports: number;
  pending_reports: number;
  completed_reports: number;
  failed_reports: number;
  recent_reports: ComplianceReport[];
  active_policies: number;
  compliance_score: number;
}

export interface ReportType {
  code: string;
  name: string;
}

/**
 * Compliance Service
 * Provides methods to interact with the compliance API endpoints
 */
export default {
  /**
   * Generate a compliance report
   * @param reportRequest - Report generation request
   * @returns Promise with the generated report
   */
  async generateReport(reportRequest: ComplianceReportRequest) {
    const formattedRequest = {
      ...reportRequest,
      start_date: reportRequest.start_date.toISOString(),
      end_date: reportRequest.end_date.toISOString()
    };
    return api.post('/compliance/reports', formattedRequest);
  },

  /**
   * Get a compliance report by ID
   * @param reportId - Report ID
   * @returns Promise with the report details
   */
  async getReport(reportId: string) {
    return api.get(`/compliance/reports/${reportId}`);
  },

  /**
   * List compliance reports
   * @param filters - Filter options
   * @returns Promise with the list of reports
   */
  async listReports(filters: {
    report_type?: string;
    status?: string;
    skip?: number;
    limit?: number;
  } = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });

    return api.get(`/compliance/reports?${params.toString()}`);
  },

  /**
   * Get available report types
   * @returns Promise with available report types
   */
  async getReportTypes() {
    return api.get('/compliance/report-types');
  },

  /**
   * Create a compliance policy
   * @param policyRequest - Policy creation request
   * @returns Promise with the created policy
   */
  async createPolicy(policyRequest: CompliancePolicyRequest) {
    const formattedRequest = {
      ...policyRequest,
      effective_date: policyRequest.effective_date.toISOString(),
      review_date: policyRequest.review_date?.toISOString()
    };
    return api.post('/compliance/policies', formattedRequest);
  },

  /**
   * List compliance policies
   * @param activeOnly - Whether to show only active policies
   * @returns Promise with the list of policies
   */
  async listPolicies(activeOnly: boolean = true) {
    return api.get(`/compliance/policies?active_only=${activeOnly}`);
  },

  /**
   * Get compliance dashboard data
   * @returns Promise with dashboard data
   */
  async getDashboard() {
    return api.get('/compliance/dashboard');
  },

  /**
   * Utility functions for compliance
   */
  utils: {
    /**
     * Format report type for display
     */
    formatReportType(reportType: string): string {
      const typeMap: Record<string, string> = {
        'audit_trail': 'Audit Trail',
        'access_control': 'Access Control',
        'user_activity': 'User Activity',
        'security_assessment': 'Security Assessment',
        'sox_compliance': 'SOX Compliance',
        'data_retention': 'Data Retention',
        'financial_controls': 'Financial Controls'
      };
      
      return typeMap[reportType] || reportType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    /**
     * Get status color for UI
     */
    getStatusColor(status: string): string {
      const colorMap: Record<string, string> = {
        'pending': 'warning',
        'generating': 'info',
        'completed': 'success',
        'failed': 'error'
      };
      
      return colorMap[status] || 'grey';
    },

    /**
     * Format file size
     */
    formatFileSize(sizeStr?: string): string {
      if (!sizeStr) return 'N/A';
      
      const size = parseInt(sizeStr);
      if (size < 1024) return `${size} B`;
      if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
      if (size < 1024 * 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(1)} MB`;
      return `${(size / (1024 * 1024 * 1024)).toFixed(1)} GB`;
    },

    /**
     * Calculate compliance score color
     */
    getComplianceScoreColor(score: number): string {
      if (score >= 90) return 'success';
      if (score >= 70) return 'warning';
      return 'error';
    },

    /**
     * Format compliance framework
     */
    formatComplianceFramework(framework?: string): string {
      if (!framework) return 'General';
      
      const frameworkMap: Record<string, string> = {
        'sox': 'Sarbanes-Oxley Act',
        'pci_dss': 'PCI DSS',
        'gdpr': 'GDPR',
        'hipaa': 'HIPAA',
        'iso_27001': 'ISO 27001'
      };
      
      return frameworkMap[framework] || framework.toUpperCase();
    },

    /**
     * Get report type description
     */
    getReportTypeDescription(reportType: string): string {
      const descriptions: Record<string, string> = {
        'audit_trail': 'Comprehensive audit trail of all system activities',
        'access_control': 'User access patterns and authentication events',
        'user_activity': 'Detailed user activity and behavior analysis',
        'security_assessment': 'Security events and threat assessment',
        'sox_compliance': 'Financial controls and SOX compliance verification',
        'data_retention': 'Data retention policy compliance status',
        'financial_controls': 'Financial process controls and segregation of duties'
      };
      
      return descriptions[reportType] || 'Compliance report for regulatory requirements';
    },

    /**
     * Validate date range
     */
    validateDateRange(startDate: Date, endDate: Date): { valid: boolean; message?: string } {
      if (startDate >= endDate) {
        return { valid: false, message: 'End date must be after start date' };
      }
      
      const maxRange = 365; // days
      const daysDiff = (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24);
      
      if (daysDiff > maxRange) {
        return { valid: false, message: `Date range cannot exceed ${maxRange} days` };
      }
      
      return { valid: true };
    }
  }
};