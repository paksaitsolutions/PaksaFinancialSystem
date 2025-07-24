import { api } from '@/utils/api';

export interface PasswordPolicy {
  id: string;
  name: string;
  description?: string;
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
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PasswordValidation {
  valid: boolean;
  errors: string[];
  policy: {
    min_length: number;
    max_length: number;
    require_uppercase: boolean;
    require_lowercase: boolean;
    require_numbers: boolean;
    require_special_chars: boolean;
  };
}

export interface PasswordChangeRequest {
  old_password: string;
  new_password: string;
}

export interface PasswordChangeResponse {
  success: boolean;
  message: string;
}

export interface AccountLockStatus {
  locked: boolean;
  failed_attempts: number;
  max_attempts: number;
  unlock_time?: string;
  remaining_attempts: number;
}

export interface PasswordExpiryStatus {
  expired: boolean;
  expires_at?: string;
  days_until_expiry?: number;
}

/**
 * Password Service
 * Provides methods to interact with the password policy API endpoints
 */
export default {
  /**
   * Get the active password policy
   * @returns Promise with the password policy
   */
  async getPasswordPolicy() {
    return api.get('/password/policy');
  },

  /**
   * Validate a password against the active policy
   * @param password - Password to validate
   * @returns Promise with validation results
   */
  async validatePassword(password: string) {
    return api.post('/password/validate', { password });
  },

  /**
   * Change user password
   * @param passwordChange - Password change request
   * @returns Promise with change results
   */
  async changePassword(passwordChange: PasswordChangeRequest) {
    return api.post('/password/change', passwordChange);
  },

  /**
   * Get account lock status
   * @returns Promise with lock status
   */
  async getLockStatus() {
    return api.get('/password/lock-status');
  },

  /**
   * Unlock a user account
   * @param userId - User ID to unlock
   * @returns Promise with unlock result
   */
  async unlockAccount(userId: string) {
    return api.post(`/password/unlock-account/${userId}`);
  },

  /**
   * Get password expiry status
   * @returns Promise with expiry status
   */
  async getExpiryStatus() {
    return api.get('/password/expiry-status');
  },

  /**
   * Generate password strength indicator
   * @param password - Password to check
   * @param policy - Password policy
   * @returns Strength score and feedback
   */
  generatePasswordStrength(password: string, policy: PasswordPolicy) {
    let score = 0;
    const feedback = [];

    // Length check
    if (password.length >= policy.min_length) {
      score += 20;
    } else {
      feedback.push(`Password must be at least ${policy.min_length} characters`);
    }

    // Character type checks
    if (policy.require_uppercase && /[A-Z]/.test(password)) {
      score += 20;
    } else if (policy.require_uppercase) {
      feedback.push('Add uppercase letters');
    }

    if (policy.require_lowercase && /[a-z]/.test(password)) {
      score += 20;
    } else if (policy.require_lowercase) {
      feedback.push('Add lowercase letters');
    }

    if (policy.require_numbers && /\d/.test(password)) {
      score += 20;
    } else if (policy.require_numbers) {
      feedback.push('Add numbers');
    }

    if (policy.require_special_chars && /[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      score += 20;
    } else if (policy.require_special_chars) {
      feedback.push('Add special characters');
    }

    // Determine strength level
    let strength = 'Very Weak';
    let color = 'error';

    if (score >= 80) {
      strength = 'Strong';
      color = 'success';
    } else if (score >= 60) {
      strength = 'Good';
      color = 'warning';
    } else if (score >= 40) {
      strength = 'Fair';
      color = 'orange';
    } else if (score >= 20) {
      strength = 'Weak';
      color = 'error';
    }

    return {
      score,
      strength,
      color,
      feedback
    };
  }
};