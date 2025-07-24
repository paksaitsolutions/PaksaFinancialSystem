import { api } from '@/utils/api';

export interface TenantAuthConfig {
  id: string;
  company_id: string;
  custom_login_url?: string;
  company_code_required: boolean;
  session_timeout_minutes: number;
  remember_me_enabled: boolean;
  remember_me_duration_days: number;
  concurrent_sessions_limit: number;
  password_reset_enabled: boolean;
  password_reset_expiry_hours: number;
  custom_reset_template?: string;
  oauth_providers?: Record<string, any>;
  saml_config?: Record<string, any>;
  login_logo_url?: string;
  login_background_url?: string;
  brand_colors?: Record<string, string>;
  created_at: string;
  updated_at: string;
}

export interface TenantLoginRequest {
  email: string;
  password: string;
  company_code?: string;
  remember_me?: boolean;
}

export interface TenantLoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  company_id: string;
  company_name: string;
  redirect_url?: string;
}

export interface TenantSession {
  id: string;
  session_token: string;
  user_id: string;
  company_id: string;
  login_method: string;
  ip_address?: string;
  user_agent?: string;
  expires_at: string;
  last_activity: string;
  remember_me: boolean;
  status: string;
  created_at: string;
}

export interface OAuthProvider {
  id: string;
  company_id: string;
  provider_name: string;
  client_id: string;
  redirect_uri: string;
  scopes?: string[];
  is_active: boolean;
  auto_create_users: boolean;
  default_role?: string;
  created_at: string;
}

/**
 * Tenant Authentication Service
 * Provides methods for multi-tenant authentication operations
 */
export default {
  /**
   * Create authentication configuration for a company
   * @param companyId - Company ID
   * @param config - Auth configuration
   * @returns Promise with created config
   */
  async createAuthConfig(companyId: string, config: Partial<TenantAuthConfig>) {
    return api.post(`/tenant-auth/config/${companyId}`, config);
  },

  /**
   * Get authentication configuration for a company
   * @param companyId - Company ID
   * @returns Promise with auth config
   */
  async getAuthConfig(companyId: string) {
    return api.get(`/tenant-auth/config/${companyId}`);
  },

  /**
   * Login with tenant context
   * @param loginData - Login credentials
   * @returns Promise with login response
   */
  async login(loginData: TenantLoginRequest) {
    return api.post('/tenant-auth/login', loginData);
  },

  /**
   * Logout and terminate session
   * @param sessionToken - Session token
   * @returns Promise with logout response
   */
  async logout(sessionToken: string) {
    return api.post('/tenant-auth/logout', { session_token: sessionToken });
  },

  /**
   * Get active sessions for a user
   * @param userId - User ID
   * @param companyId - Company ID
   * @returns Promise with sessions list
   */
  async getUserSessions(userId: string, companyId: string) {
    return api.get(`/tenant-auth/sessions/${userId}?company_id=${companyId}`);
  },

  /**
   * Terminate all sessions for a user
   * @param userId - User ID
   * @param companyId - Company ID
   * @param exceptCurrent - Keep current session active
   * @returns Promise with termination response
   */
  async terminateAllSessions(userId: string, companyId: string, exceptCurrent: boolean = true) {
    return api.delete(`/tenant-auth/sessions/${userId}/terminate-all?company_id=${companyId}&except_current=${exceptCurrent}`);
  },

  /**
   * Request password reset
   * @param email - User email
   * @param companyCode - Company code (optional)
   * @returns Promise with reset response
   */
  async requestPasswordReset(email: string, companyCode?: string) {
    return api.post('/tenant-auth/password-reset', {
      email,
      company_code: companyCode
    });
  },

  /**
   * Confirm password reset
   * @param token - Reset token
   * @param newPassword - New password
   * @returns Promise with confirmation response
   */
  async confirmPasswordReset(token: string, newPassword: string) {
    return api.post('/tenant-auth/password-reset/confirm', {
      token,
      new_password: newPassword
    });
  },

  /**
   * Create OAuth provider configuration
   * @param companyId - Company ID
   * @param providerData - OAuth provider data
   * @returns Promise with created provider
   */
  async createOAuthProvider(companyId: string, providerData: Partial<OAuthProvider>) {
    return api.post(`/tenant-auth/oauth/${companyId}`, providerData);
  },

  /**
   * Get OAuth providers for a company
   * @param companyId - Company ID
   * @param activeOnly - Show only active providers
   * @returns Promise with providers list
   */
  async getOAuthProviders(companyId: string, activeOnly: boolean = true) {
    return api.get(`/tenant-auth/oauth/${companyId}?active_only=${activeOnly}`);
  },

  /**
   * Get companies available to a user
   * @param userId - User ID
   * @returns Promise with companies list
   */
  async getUserCompanies(userId: string) {
    return api.get(`/tenant-auth/companies/${userId}`);
  },

  /**
   * Get login attempts for monitoring
   * @param companyId - Company ID (optional)
   * @param email - Email filter (optional)
   * @param limit - Results limit
   * @returns Promise with login attempts
   */
  async getLoginAttempts(companyId?: string, email?: string, limit: number = 100) {
    const params = new URLSearchParams();
    if (companyId) params.append('company_id', companyId);
    if (email) params.append('email', email);
    params.append('limit', limit.toString());

    return api.get(`/tenant-auth/login-attempts?${params.toString()}`);
  },

  /**
   * Clean up expired sessions
   * @returns Promise with cleanup response
   */
  async cleanupExpiredSessions() {
    return api.post('/tenant-auth/cleanup-sessions');
  },

  /**
   * Utility functions for tenant authentication
   */
  utils: {
    /**
     * Get login URL for a company
     */
    getLoginUrl(companyCode?: string): string {
      const baseUrl = '/login';
      return companyCode ? `${baseUrl}?company=${companyCode}` : baseUrl;
    },

    /**
     * Format session status
     */
    formatSessionStatus(status: string): string {
      const statusMap: Record<string, string> = {
        'active': 'Active',
        'expired': 'Expired',
        'terminated': 'Terminated'
      };
      
      return statusMap[status] || status.charAt(0).toUpperCase() + status.slice(1);
    },

    /**
     * Get status color for UI
     */
    getStatusColor(status: string): string {
      const colorMap: Record<string, string> = {
        'active': 'success',
        'expired': 'warning',
        'terminated': 'error'
      };
      
      return colorMap[status] || 'grey';
    },

    /**
     * Format login method
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
     * Check if session is expiring soon
     */
    isSessionExpiringSoon(expiresAt: string, thresholdMinutes: number = 5): boolean {
      const expiryTime = new Date(expiresAt).getTime();
      const now = new Date().getTime();
      const threshold = thresholdMinutes * 60 * 1000;
      
      return (expiryTime - now) <= threshold;
    },

    /**
     * Get time until session expires
     */
    getTimeUntilExpiry(expiresAt: string): string {
      const expiryTime = new Date(expiresAt).getTime();
      const now = new Date().getTime();
      const diff = expiryTime - now;
      
      if (diff <= 0) return 'Expired';
      
      const minutes = Math.floor(diff / (1000 * 60));
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);
      
      if (days > 0) return `${days}d ${hours % 24}h`;
      if (hours > 0) return `${hours}h ${minutes % 60}m`;
      return `${minutes}m`;
    },

    /**
     * Validate company code format
     */
    validateCompanyCode(code: string): { valid: boolean; message?: string } {
      if (!code) {
        return { valid: false, message: 'Company code is required' };
      }
      
      if (code.length < 2 || code.length > 20) {
        return { valid: false, message: 'Company code must be 2-20 characters' };
      }
      
      if (!/^[A-Za-z0-9-_]+$/.test(code)) {
        return { valid: false, message: 'Company code can only contain letters, numbers, hyphens, and underscores' };
      }
      
      return { valid: true };
    },

    /**
     * Get OAuth provider icon
     */
    getOAuthProviderIcon(provider: string): string {
      const iconMap: Record<string, string> = {
        'google': 'mdi-google',
        'microsoft': 'mdi-microsoft',
        'github': 'mdi-github',
        'linkedin': 'mdi-linkedin'
      };
      
      return iconMap[provider.toLowerCase()] || 'mdi-account-circle';
    },

    /**
     * Generate secure session token
     */
    generateSessionToken(): string {
      const array = new Uint8Array(32);
      crypto.getRandomValues(array);
      return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }
  }
};