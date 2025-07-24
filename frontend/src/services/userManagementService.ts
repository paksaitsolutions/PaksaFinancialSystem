import { api } from '@/utils/api';

export interface LoginHistory {
  id: string;
  user_id: string;
  company_id: string;
  login_time: string;
  logout_time?: string;
  session_duration?: number;
  login_method: string;
  success: boolean;
  failure_reason?: string;
  ip_address?: string;
  user_agent?: string;
  location?: string;
  device_type?: string;
}

export interface UserActivity {
  id: string;
  user_id: string;
  company_id: string;
  activity_type: string;
  action: string;
  description?: string;
  resource_type?: string;
  resource_id?: string;
  ip_address?: string;
  user_agent?: string;
  request_method?: string;
  request_path?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface PasswordPolicy {
  id: string;
  company_id: string;
  min_length: number;
  max_length: number;
  require_uppercase: boolean;
  require_lowercase: boolean;
  require_numbers: boolean;
  require_special_chars: boolean;
  password_history_count: number;
  password_expiry_days: number;
  max_failed_attempts: number;
  lockout_duration_minutes: number;
  reset_token_expiry_hours: number;
  require_security_questions: boolean;
}

export interface CrossCompanyAccess {
  id: string;
  user_id: string;
  source_company_id: string;
  target_company_id: string;
  access_type: string;
  permissions?: Record<string, any>;
  is_active: boolean;
  expires_at?: string;
  approved_by: string;
  approval_reason?: string;
  created_at: string;
}

/**
 * Enhanced User Management Service
 */
export default {
  /**
   * Get login history for a user
   */
  async getLoginHistory(userId: string, companyId?: string, limit: number = 100) {
    const params = new URLSearchParams();
    if (companyId) params.append('company_id', companyId);
    params.append('limit', limit.toString());

    return api.get(`/user-management/${userId}/login-history?${params.toString()}`);
  },

  /**
   * Get user activities
   */
  async getUserActivities(userId: string, companyId?: string, activityType?: string, limit: number = 100) {
    const params = new URLSearchParams();
    if (companyId) params.append('company_id', companyId);
    if (activityType) params.append('activity_type', activityType);
    params.append('limit', limit.toString());

    return api.get(`/user-management/${userId}/activities?${params.toString()}`);
  },

  /**
   * Create password policy for a company
   */
  async createPasswordPolicy(companyId: string, policyData: Partial<PasswordPolicy>) {
    return api.post(`/user-management/companies/${companyId}/password-policy`, policyData);
  },

  /**
   * Grant cross-company access
   */
  async grantCrossCompanyAccess(userId: string, targetCompanyId: string, accessType: string = 'read_only') {
    return api.post(`/user-management/${userId}/cross-company-access`, {
      target_company_id: targetCompanyId,
      access_type: accessType
    });
  },

  /**
   * Utility functions
   */
  utils: {
    /**
     * Format login method for display
     */
    formatLoginMethod(method: string): string {
      const methodMap: Record<string, string> = {
        'email_password': 'Email & Password',
        'oauth_google': 'Google OAuth',
        'oauth_microsoft': 'Microsoft OAuth',
        'saml_sso': 'SAML SSO'
      };
      
      return methodMap[method] || method.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    /**
     * Format activity type
     */
    formatActivityType(type: string): string {
      const typeMap: Record<string, string> = {
        'login': 'Login',
        'logout': 'Logout',
        'password_change': 'Password Change',
        'profile_update': 'Profile Update',
        'permission_change': 'Permission Change',
        'data_access': 'Data Access',
        'data_modify': 'Data Modification',
        'system_action': 'System Action'
      };
      
      return typeMap[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    /**
     * Get activity type color
     */
    getActivityTypeColor(type: string): string {
      const colorMap: Record<string, string> = {
        'login': 'success',
        'logout': 'info',
        'password_change': 'warning',
        'profile_update': 'info',
        'permission_change': 'warning',
        'data_access': 'primary',
        'data_modify': 'warning',
        'system_action': 'secondary'
      };
      
      return colorMap[type] || 'grey';
    },

    /**
     * Format session duration
     */
    formatSessionDuration(seconds: number): string {
      if (seconds < 60) return `${seconds}s`;
      
      const minutes = Math.floor(seconds / 60);
      if (minutes < 60) return `${minutes}m`;
      
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      
      if (hours < 24) {
        return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
      }
      
      const days = Math.floor(hours / 24);
      const remainingHours = hours % 24;
      
      return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
    },

    /**
     * Validate password against policy
     */
    validatePassword(password: string, policy: PasswordPolicy): { valid: boolean; errors: string[] } {
      const errors: string[] = [];
      
      if (password.length < policy.min_length) {
        errors.push(`Password must be at least ${policy.min_length} characters long`);
      }
      
      if (password.length > policy.max_length) {
        errors.push(`Password must be no more than ${policy.max_length} characters long`);
      }
      
      if (policy.require_uppercase && !/[A-Z]/.test(password)) {
        errors.push('Password must contain at least one uppercase letter');
      }
      
      if (policy.require_lowercase && !/[a-z]/.test(password)) {
        errors.push('Password must contain at least one lowercase letter');
      }
      
      if (policy.require_numbers && !/\d/.test(password)) {
        errors.push('Password must contain at least one number');
      }
      
      if (policy.require_special_chars && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        errors.push('Password must contain at least one special character');
      }
      
      return {
        valid: errors.length === 0,
        errors
      };
    },

    /**
     * Get access type display name
     */
    formatAccessType(type: string): string {
      const typeMap: Record<string, string> = {
        'read_only': 'Read Only',
        'read_write': 'Read & Write',
        'admin': 'Administrator',
        'limited': 'Limited Access'
      };
      
      return typeMap[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    /**
     * Get access type color
     */
    getAccessTypeColor(type: string): string {
      const colorMap: Record<string, string> = {
        'read_only': 'info',
        'read_write': 'warning',
        'admin': 'error',
        'limited': 'secondary'
      };
      
      return colorMap[type] || 'grey';
    }
  }
};