import { api } from '@/utils/api';

export interface DataRetentionPolicy {
  id: string;
  policy_name: string;
  policy_code: string;
  table_name: string;
  data_category: string;
  retention_period_days: number;
  retention_action: string;
  description?: string;
  legal_basis?: string;
  conditions?: Record<string, any>;
  status: string;
  last_executed?: string;
  next_execution?: string;
  created_at: string;
  updated_at: string;
}

export interface DataRetentionPolicyRequest {
  policy_name: string;
  policy_code: string;
  table_name: string;
  data_category: string;
  retention_period_days: number;
  retention_action?: string;
  description?: string;
  legal_basis?: string;
  conditions?: Record<string, any>;
}

export interface RetentionExecution {
  id: string;
  policy_id: string;
  execution_date: string;
  records_processed: number;
  records_deleted: number;
  records_archived: number;
  records_anonymized: number;
  status: string;
  error_message?: string;
  execution_time_seconds?: number;
}

export interface RetentionDashboard {
  total_policies: number;
  active_policies: number;
  policies_due: number;
  recent_executions: RetentionExecution[];
  total_records_processed: number;
  storage_saved_mb: number;
}

/**
 * Data Retention Service
 * Provides methods to interact with the data retention API endpoints
 */
export default {
  /**
   * Create a data retention policy
   * @param policyRequest - Policy creation request
   * @returns Promise with the created policy
   */
  async createPolicy(policyRequest: DataRetentionPolicyRequest) {
    return api.post('/retention/policies', policyRequest);
  },

  /**
   * List data retention policies
   * @param activeOnly - Whether to show only active policies
   * @returns Promise with the list of policies
   */
  async listPolicies(activeOnly: boolean = true) {
    return api.get(`/retention/policies?active_only=${activeOnly}`);
  },

  /**
   * Execute a specific retention policy
   * @param policyId - Policy ID to execute
   * @returns Promise with execution result
   */
  async executePolicy(policyId: string) {
    return api.post(`/retention/policies/${policyId}/execute`);
  },

  /**
   * Execute all due retention policies
   * @returns Promise with execution results
   */
  async executeAllPolicies() {
    return api.post('/retention/execute-all');
  },

  /**
   * Get retention execution history
   * @param policyId - Optional policy ID filter
   * @param limit - Maximum number of records
   * @returns Promise with execution history
   */
  async getExecutionHistory(policyId?: string, limit: number = 100) {
    const params = new URLSearchParams();
    if (policyId) params.append('policy_id', policyId);
    params.append('limit', limit.toString());

    return api.get(`/retention/executions?${params.toString()}`);
  },

  /**
   * Initialize default retention policies
   * @returns Promise with initialization result
   */
  async initializeDefaultPolicies() {
    return api.post('/retention/initialize');
  },

  /**
   * Get retention dashboard data
   * @returns Promise with dashboard data
   */
  async getDashboard() {
    return api.get('/retention/dashboard');
  },

  /**
   * Utility functions for data retention
   */
  utils: {
    /**
     * Format retention action for display
     */
    formatRetentionAction(action: string): string {
      const actionMap: Record<string, string> = {
        'delete': 'Delete',
        'archive': 'Archive',
        'anonymize': 'Anonymize'
      };
      
      return actionMap[action] || action.charAt(0).toUpperCase() + action.slice(1);
    },

    /**
     * Get action color for UI
     */
    getActionColor(action: string): string {
      const colorMap: Record<string, string> = {
        'delete': 'error',
        'archive': 'warning',
        'anonymize': 'info'
      };
      
      return colorMap[action] || 'grey';
    },

    /**
     * Format retention period for display
     */
    formatRetentionPeriod(days: number): string {
      if (days < 30) {
        return `${days} days`;
      } else if (days < 365) {
        const months = Math.round(days / 30);
        return `${months} month${months > 1 ? 's' : ''}`;
      } else {
        const years = Math.round(days / 365);
        return `${years} year${years > 1 ? 's' : ''}`;
      }
    },

    /**
     * Get status color for UI
     */
    getStatusColor(status: string): string {
      const colorMap: Record<string, string> = {
        'active': 'success',
        'inactive': 'warning',
        'suspended': 'error',
        'completed': 'success',
        'failed': 'error',
        'running': 'info'
      };
      
      return colorMap[status] || 'grey';
    },

    /**
     * Format data category for display
     */
    formatDataCategory(category: string): string {
      return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    /**
     * Calculate next execution time
     */
    getNextExecutionTime(lastExecuted?: string, periodDays: number = 1): Date {
      const base = lastExecuted ? new Date(lastExecuted) : new Date();
      return new Date(base.getTime() + (periodDays * 24 * 60 * 60 * 1000));
    },

    /**
     * Check if policy is due for execution
     */
    isPolicyDue(nextExecution?: string): boolean {
      if (!nextExecution) return false;
      return new Date(nextExecution) <= new Date();
    },

    /**
     * Format execution summary
     */
    formatExecutionSummary(execution: RetentionExecution): string {
      const { records_processed, records_deleted, records_archived, records_anonymized } = execution;
      
      if (records_deleted > 0) {
        return `Deleted ${records_deleted} of ${records_processed} records`;
      } else if (records_archived > 0) {
        return `Archived ${records_archived} of ${records_processed} records`;
      } else if (records_anonymized > 0) {
        return `Anonymized ${records_anonymized} of ${records_processed} records`;
      } else {
        return `Processed ${records_processed} records`;
      }
    },

    /**
     * Validate retention period
     */
    validateRetentionPeriod(days: number, dataCategory: string): { valid: boolean; message?: string } {
      if (days < 1) {
        return { valid: false, message: 'Retention period must be at least 1 day' };
      }
      
      // Category-specific validation
      const categoryLimits: Record<string, { min: number; max: number }> = {
        'audit': { min: 2555, max: 3650 }, // 7-10 years for audit data
        'financial': { min: 2555, max: 3650 }, // 7-10 years for financial data
        'session': { min: 1, max: 90 }, // 1-90 days for session data
        'security': { min: 30, max: 365 }, // 30 days to 1 year for security data
        'personal': { min: 30, max: 2555 } // 30 days to 7 years for personal data
      };
      
      const limits = categoryLimits[dataCategory];
      if (limits) {
        if (days < limits.min) {
          return { 
            valid: false, 
            message: `${this.formatDataCategory(dataCategory)} data must be retained for at least ${this.formatRetentionPeriod(limits.min)}` 
          };
        }
        if (days > limits.max) {
          return { 
            valid: false, 
            message: `${this.formatDataCategory(dataCategory)} data retention cannot exceed ${this.formatRetentionPeriod(limits.max)}` 
          };
        }
      }
      
      return { valid: true };
    },

    /**
     * Get recommended retention periods by data category
     */
    getRecommendedRetention(dataCategory: string): number[] {
      const recommendations: Record<string, number[]> = {
        'audit': [2555, 3650], // 7, 10 years
        'financial': [2555, 3650], // 7, 10 years
        'session': [7, 30, 90], // 1 week, 1 month, 3 months
        'security': [90, 180, 365], // 3 months, 6 months, 1 year
        'personal': [365, 1095, 2555], // 1 year, 3 years, 7 years
        'operational': [30, 90, 365] // 1 month, 3 months, 1 year
      };
      
      return recommendations[dataCategory] || [30, 90, 365];
    }
  }
};