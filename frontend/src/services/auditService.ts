import { api } from '@/utils/api';

export interface AuditLog {
  id: string;
  user_id?: string;
  session_id?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  endpoint?: string;
  method?: string;
  ip_address?: string;
  user_agent?: string;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  description?: string;
  metadata?: Record<string, any>;
  timestamp: string;
}

export interface AuditLogRequest {
  action: string;
  resource_type: string;
  resource_id?: string;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  description?: string;
  metadata?: Record<string, any>;
}

export interface AuditStatistics {
  total_logs: number;
  active_users: number;
  actions: Record<string, number>;
  resources: Record<string, number>;
  period_days: number;
}

export interface AuditConfig {
  id: string;
  name: string;
  description?: string;
  log_read_operations: string;
  log_failed_attempts: string;
  retention_days: string;
  excluded_resources?: string[];
  sensitive_resources?: string[];
  is_active: string;
  created_at: string;
  updated_at: string;
}

export interface UserActivity {
  user_id: string;
  logs: AuditLog[];
  total_actions: number;
  period_days: number;
}

export interface ResourceHistory {
  resource_type: string;
  resource_id: string;
  logs: AuditLog[];
  total_changes: number;
}

/**
 * Audit Service
 * Provides methods to interact with the audit logging API endpoints
 */
export default {
  /**
   * Create an audit log entry
   * @param logRequest - Audit log data
   * @returns Promise with the created audit log
   */
  async createAuditLog(logRequest: AuditLogRequest) {
    return api.post('/audit/log', logRequest);
  },

  /**
   * Get audit logs with optional filters
   * @param filters - Filter options
   * @returns Promise with the list of audit logs
   */
  async getAuditLogs(filters: {
    user_id?: string;
    resource_type?: string;
    action?: string;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  } = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });

    return api.get(`/audit/logs?${params.toString()}`);
  },

  /**
   * Get user activity
   * @param userId - User ID
   * @param days - Number of days to look back
   * @returns Promise with user activity
   */
  async getUserActivity(userId: string, days: number = 30) {
    return api.get(`/audit/user/${userId}/activity?days=${days}`);
  },

  /**
   * Get resource history
   * @param resourceType - Resource type
   * @param resourceId - Resource ID
   * @returns Promise with resource history
   */
  async getResourceHistory(resourceType: string, resourceId: string) {
    return api.get(`/audit/resource/${resourceType}/${resourceId}/history`);
  },

  /**
   * Get audit statistics
   * @param days - Number of days to analyze
   * @returns Promise with audit statistics
   */
  async getAuditStatistics(days: number = 30) {
    return api.get(`/audit/statistics?days=${days}`);
  },

  /**
   * Get audit configuration
   * @returns Promise with audit configuration
   */
  async getAuditConfig() {
    return api.get('/audit/config');
  },

  /**
   * Clean up old audit logs
   * @returns Promise with cleanup result
   */
  async cleanupOldLogs() {
    return api.post('/audit/cleanup');
  },

  /**
   * Utility functions for audit logging
   */
  utils: {
    /**
     * Format action for display
     */
    formatAction(action: string): string {
      const actionMap: Record<string, string> = {
        create: 'Created',
        read: 'Viewed',
        update: 'Updated',
        delete: 'Deleted',
        login: 'Logged In',
        logout: 'Logged Out',
        export: 'Exported',
        import: 'Imported',
        approve: 'Approved',
        reject: 'Rejected'
      };
      
      return actionMap[action] || action.charAt(0).toUpperCase() + action.slice(1);
    },

    /**
     * Format resource type for display
     */
    formatResourceType(resourceType: string): string {
      return resourceType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    /**
     * Get action color for UI
     */
    getActionColor(action: string): string {
      const colorMap: Record<string, string> = {
        create: 'success',
        read: 'info',
        update: 'warning',
        delete: 'error',
        login: 'primary',
        logout: 'secondary',
        export: 'purple',
        import: 'orange',
        approve: 'green',
        reject: 'red'
      };
      
      return colorMap[action] || 'grey';
    },

    /**
     * Format timestamp for display
     */
    formatTimestamp(timestamp: string): string {
      return new Date(timestamp).toLocaleString();
    },

    /**
     * Check if values contain sensitive data
     */
    hasSensitiveData(values: Record<string, any>): boolean {
      if (!values) return false;
      
      const sensitiveFields = [
        'password', 'token', 'secret', 'key', 'ssn', 'credit_card'
      ];
      
      return Object.keys(values).some(key => 
        sensitiveFields.some(field => key.toLowerCase().includes(field))
      );
    },

    /**
     * Get summary of changes
     */
    getChangesSummary(oldValues: Record<string, any>, newValues: Record<string, any>): string[] {
      const changes: string[] = [];
      
      if (!oldValues || !newValues) return changes;
      
      Object.keys(newValues).forEach(key => {
        if (oldValues[key] !== newValues[key]) {
          changes.push(`${key}: ${oldValues[key]} → ${newValues[key]}`);
        }
      });
      
      return changes;
    }
  }
};