import { apiClient } from '@/utils/apiClient';
import type { AxiosError } from 'axios';

// Types
export interface EncryptionKey {
  id: string;
  name: string;
  algorithm: string;
  keySize: number;
  status: 'active' | 'inactive' | 'expired' | 'compromised';
  createdAt: string;
  expiresAt: string | null;
  keyMaterial?: string;
}

export interface EncryptionLog {
  id: string;
  timestamp: string;
  action: string;
  keyName: string;
  status: 'success' | 'failed' | 'warning';
  initiatedBy: string;
}

export interface Settings {
  keyRotationInterval: number;
  autoRotate: boolean;
  encryptionLevel: string;
  requireMfa: boolean;
}

interface GenerateKeyRequest {
  name: string;
  algorithm: string;
  keySize: number;
  expiresAt?: string | null;
}

interface ImportKeyRequest {
  name: string;
  keyMaterial: string;
  password?: string;
}

// Helper to handle API errors
const handleApiError = (error: unknown): never => {
  if ((error as AxiosError)?.isAxiosError) {
    const axiosError = error as AxiosError<{ message?: string }>;
    const errorMessage = (axiosError.response?.data as any)?.message || axiosError.message;
    throw new Error(errorMessage || 'An unknown error occurred');
  }
  throw error instanceof Error ? error : new Error('An unknown error occurred');
};

export const encryptionService = {
  // Key Management
  async getKeys(): Promise<EncryptionKey[]> {
    try {
      return await apiClient.get<EncryptionKey[]>('/encryption/keys');
    } catch (error) {
      console.error('Error fetching encryption keys:', error);
      return handleApiError(error);
    }
  },

  async generateKey(data: GenerateKeyRequest): Promise<EncryptionKey> {
    try {
      return await apiClient.post<EncryptionKey>('/encryption/keys/generate', data);
    } catch (error) {
      console.error('Error generating encryption key:', error);
      return handleApiError(error);
    }
  },

  async importKey(data: ImportKeyRequest): Promise<EncryptionKey> {
    try {
      return await apiClient.post<EncryptionKey>('/encryption/keys/import', data);
    } catch (error) {
      console.error('Error importing encryption key:', error);
      return handleApiError(error);
    }
  },

  async rotateKey(keyId: string): Promise<EncryptionKey> {
    try {
      return await apiClient.post<EncryptionKey>(`/encryption/keys/${keyId}/rotate`, {});
    } catch (error) {
      console.error('Error rotating encryption key:', error);
      return handleApiError(error);
    }
  },

  async updateKeyStatus(keyId: string, status: 'active' | 'inactive'): Promise<EncryptionKey> {
    try {
      return await apiClient.patch<EncryptionKey>(`/encryption/keys/${keyId}/status`, { status });
    } catch (error) {
      console.error('Error updating key status:', error);
      return handleApiError(error);
    }
  },

  async deleteKey(keyId: string): Promise<void> {
    try {
      await apiClient.delete(`/encryption/keys/${keyId}`);
    } catch (error) {
      console.error('Error deleting encryption key:', error);
      return handleApiError(error);
    }
  },

  // Logs
  async getLogs(): Promise<EncryptionLog[]> {
    try {
      return await apiClient.get<EncryptionLog[]>('/encryption/logs');
    } catch (error) {
      console.error('Error fetching encryption logs:', error);
      return handleApiError(error);
    }
  },

  // Settings
  async getSettings(): Promise<Settings> {
    try {
      return await apiClient.get<Settings>('/encryption/settings');
    } catch (error) {
      console.error('Error fetching encryption settings:', error);
      // Return default settings if API fails
      return {
        keyRotationInterval: 90,
        autoRotate: true,
        encryptionLevel: 'high',
        requireMfa: true
      };
    }
  },

  async updateSettings(settings: Partial<Settings>): Promise<Settings> {
    try {
      return await apiClient.patch<Settings>('/encryption/settings', settings);
    } catch (error) {
      console.error('Error updating encryption settings:', error);
      return handleApiError(error);
      };
    }
  }
};

export default encryptionService;
