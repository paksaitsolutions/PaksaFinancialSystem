import { api } from '@/utils/api';

export interface UserSession {
  id: string;
  session_token: string;
  user_id: string;
  ip_address?: string;
  user_agent?: string;
  device_info?: string;
  created_at: string;
  last_activity: string;
  expires_at: string;
  status: string;
  terminated_at?: string;
  termination_reason?: string;
}

export interface SessionValidation {
  valid: boolean;
  reason?: string;
  user_id?: string;
  expires_at?: string;
}

export interface SessionConfig {
  id: string;
  name: string;
  description?: string;
  session_timeout_minutes: number;
  max_concurrent_sessions: number;
  remember_me_duration_days: number;
  require_fresh_login_minutes: number;
  auto_logout_on_idle: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SessionCreateRequest {
  user_id: string;
  ip_address?: string;
  user_agent?: string;
  remember_me?: boolean;
}

/**
 * Session Service
 * Provides methods to interact with the session management API endpoints
 */
export default {
  /**
   * Create a new session
   * @param sessionData - Session creation data
   * @returns Promise with the created session
   */
  async createSession(sessionData: SessionCreateRequest) {
    return api.post('/session/create', sessionData);
  },

  /**
   * Validate a session token
   * @param sessionToken - Session token to validate
   * @returns Promise with validation results
   */
  async validateSession(sessionToken: string) {
    return api.get(`/session/validate/${sessionToken}`);
  },

  /**
   * Extend session expiration
   * @param sessionToken - Session token
   * @param durationMinutes - Extension duration in minutes
   * @returns Promise with updated session
   */
  async extendSession(sessionToken: string, durationMinutes?: number) {
    return api.post(`/session/extend/${sessionToken}`, {
      duration_minutes: durationMinutes
    });
  },

  /**
   * Terminate a specific session
   * @param sessionToken - Session token to terminate
   * @param reason - Termination reason
   * @returns Promise with termination result
   */
  async terminateSession(sessionToken: string, reason: string = 'User logout') {
    return api.post(`/session/terminate/${sessionToken}`, { reason });
  },

  /**
   * Get all sessions for a user
   * @param userId - User ID
   * @param activeOnly - Whether to return only active sessions
   * @returns Promise with user sessions
   */
  async getUserSessions(userId: string, activeOnly: boolean = true) {
    return api.get(`/session/user/${userId}?active_only=${activeOnly}`);
  },

  /**
   * Terminate all sessions for a user
   * @param userId - User ID
   * @param exceptSession - Session to keep active
   * @param reason - Termination reason
   * @returns Promise with termination result
   */
  async terminateUserSessions(userId: string, exceptSession?: string, reason: string = 'Admin action') {
    const params = new URLSearchParams();
    if (exceptSession) params.append('except_session', exceptSession);
    params.append('reason', reason);

    return api.post(`/session/terminate-user/${userId}?${params.toString()}`);
  },

  /**
   * Clean up expired sessions
   * @returns Promise with cleanup result
   */
  async cleanupExpiredSessions() {
    return api.post('/session/cleanup');
  },

  /**
   * Get session configuration
   * @returns Promise with session configuration
   */
  async getSessionConfig() {
    return api.get('/session/config');
  },

  /**
   * Check if fresh login is required
   * @param sessionToken - Session token
   * @returns Promise with fresh login requirement
   */
  async checkFreshLoginRequired(sessionToken: string) {
    return api.get(`/session/fresh-login-required/${sessionToken}`);
  },

  /**
   * Session management utilities
   */
  utils: {
    /**
     * Get session token from localStorage
     */
    getSessionToken(): string | null {
      return localStorage.getItem('session_token');
    },

    /**
     * Set session token in localStorage
     */
    setSessionToken(token: string): void {
      localStorage.setItem('session_token', token);
    },

    /**
     * Remove session token from localStorage
     */
    removeSessionToken(): void {
      localStorage.removeItem('session_token');
    },

    /**
     * Check if session is expired
     */
    isSessionExpired(expiresAt: string): boolean {
      return new Date() > new Date(expiresAt);
    },

    /**
     * Get time until session expires
     */
    getTimeUntilExpiry(expiresAt: string): number {
      return new Date(expiresAt).getTime() - new Date().getTime();
    },

    /**
     * Format session duration
     */
    formatSessionDuration(createdAt: string, expiresAt: string): string {
      const created = new Date(createdAt);
      const expires = new Date(expiresAt);
      const duration = expires.getTime() - created.getTime();
      
      const hours = Math.floor(duration / (1000 * 60 * 60));
      const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
      
      if (hours > 0) {
        return `${hours}h ${minutes}m`;
      }
      return `${minutes}m`;
    }
  }
};