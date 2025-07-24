import { api } from '@/utils/api';

export interface EncryptedUserProfile {
  id: string;
  user_id: string;
  ssn?: string;
  phone_number?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  bank_account_number?: string;
  routing_number?: string;
  tax_id?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
}

export interface EncryptedUserProfileCreate {
  ssn?: string;
  phone_number?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  bank_account_number?: string;
  routing_number?: string;
  tax_id?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
}

export interface EncryptionStatus {
  encryption_enabled: boolean;
  key_configured: boolean;
  encrypted_user_profiles: number;
  encryption_algorithm: string;
  key_derivation: string;
}

/**
 * Encryption Service
 * Provides methods to interact with the encryption API endpoints
 */
export default {
  /**
   * Create or update encrypted user profile
   * @param userId - User ID
   * @param profile - Profile data to encrypt
   * @returns Promise with the encrypted profile
   */
  async createUserProfile(userId: string, profile: EncryptedUserProfileCreate) {
    return api.post(`/encryption/user-profile/${userId}`, profile);
  },

  /**
   * Get encrypted user profile (automatically decrypted)
   * @param userId - User ID
   * @returns Promise with the decrypted profile
   */
  async getUserProfile(userId: string) {
    return api.get(`/encryption/user-profile/${userId}`);
  },

  /**
   * Get encryption status and statistics
   * @returns Promise with encryption status
   */
  async getEncryptionStatus() {
    return api.get('/encryption/status');
  },

  /**
   * Encrypt arbitrary data
   * @param data - Data to encrypt
   * @returns Promise with encrypted data
   */
  async encryptData(data: string) {
    return api.post('/encryption/encrypt', { data });
  },

  /**
   * Decrypt data
   * @param encryptedData - Encrypted data to decrypt
   * @returns Promise with decrypted data
   */
  async decryptData(encryptedData: string) {
    return api.post('/encryption/decrypt', { encrypted_data: encryptedData });
  },

  /**
   * Utility functions for encryption
   */
  utils: {
    /**
     * Check if field contains sensitive data
     */
    isSensitiveField(fieldName: string): boolean {
      const sensitiveFields = [
        'ssn', 'social_security_number', 'phone_number', 'bank_account',
        'routing_number', 'tax_id', 'credit_card', 'password'
      ];
      
      return sensitiveFields.some(field => 
        fieldName.toLowerCase().includes(field)
      );
    },

    /**
     * Mask sensitive data for display
     */
    maskSensitiveData(value: string, fieldType: string): string {
      if (!value) return '';
      
      switch (fieldType.toLowerCase()) {
        case 'ssn':
        case 'social_security_number':
          return `***-**-${value.slice(-4)}`;
        
        case 'phone_number':
          return `***-***-${value.slice(-4)}`;
        
        case 'bank_account':
        case 'bank_account_number':
          return `****${value.slice(-4)}`;
        
        case 'credit_card':
          return `****-****-****-${value.slice(-4)}`;
        
        default:
          return `****${value.slice(-4)}`;
      }
    },

    /**
     * Format field name for display
     */
    formatFieldName(fieldName: string): string {
      return fieldName
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
    },

    /**
     * Get encryption status color for UI
     */
    getEncryptionStatusColor(status: EncryptionStatus): string {
      if (!status.encryption_enabled) return 'error';
      if (!status.key_configured) return 'warning';
      return 'success';
    },

    /**
     * Get encryption status message
     */
    getEncryptionStatusMessage(status: EncryptionStatus): string {
      if (!status.encryption_enabled) {
        return 'Encryption is disabled';
      }
      if (!status.key_configured) {
        return 'Encryption key not configured';
      }
      return `Encryption active with ${status.encryption_algorithm}`;
    },

    /**
     * Validate sensitive data format
     */
    validateSensitiveData(value: string, fieldType: string): { valid: boolean; message?: string } {
      if (!value) return { valid: true };
      
      switch (fieldType.toLowerCase()) {
        case 'ssn':
        case 'social_security_number':
          const ssnRegex = /^\d{3}-?\d{2}-?\d{4}$/;
          return {
            valid: ssnRegex.test(value.replace(/-/g, '')),
            message: 'SSN must be in format XXX-XX-XXXX'
          };
        
        case 'phone_number':
          const phoneRegex = /^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$/;
          return {
            valid: phoneRegex.test(value),
            message: 'Phone number must be in valid format'
          };
        
        case 'zip_code':
          const zipRegex = /^\d{5}(-\d{4})?$/;
          return {
            valid: zipRegex.test(value),
            message: 'ZIP code must be in format XXXXX or XXXXX-XXXX'
          };
        
        default:
          return { valid: true };
      }
    }
  }
};