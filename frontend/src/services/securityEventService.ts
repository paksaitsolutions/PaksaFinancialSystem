import { apiClient } from '@/utils/apiClient';
import type { AxiosError } from 'axios';

// Types
export interface SecurityEvent {
  id: string;
  eventType: string;
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical';
  source: string;
  description: string;
  userId?: string;
  username?: string;
  ipAddress?: string;
  userAgent?: string;
  resourceType?: string;
  resourceId?: string;
  details: Record<string, unknown>;
  metadata: Record<string, unknown>;
  resolved: boolean;
  resolvedAt?: string;
  resolvedBy?: string;
  resolvedReason?: string;
  createdAt: string;
  updatedAt: string;
}

export interface SecurityEventListResponse {
  items: SecurityEvent[];
  total: number;
  skip: number;
  limit: number;
}

export interface SecurityEventFilter {
  eventType?: string;
  severity?: 'info' | 'low' | 'medium' | 'high' | 'critical';
  startDate?: string;
  endDate?: string;
  source?: string;
  resolved?: boolean;
  ipAddress?: string;
  userId?: string;
  skip?: number;
  limit?: number;
  orderBy?: string;
  orderDesc?: boolean;
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

export const securityEventService = {
  // List security events with filtering and pagination
  async getEvents(filters: SecurityEventFilter = {}): Promise<SecurityEventListResponse> {
    try {
      const params = {
        ...filters,
        skip: filters.skip || 0,
        limit: filters.limit || 10,
        order_by: filters.orderBy || 'createdAt',
        order_desc: filters.orderDesc !== false, // Default to true if not specified
      };

      // Remove undefined values
      Object.keys(params).forEach(key => params[key] === undefined && delete params[key]);

      return await apiClient.get<SecurityEventListResponse>('/security/events', { params });
    } catch (error) {
      console.error('Error fetching security events:', error);
      return handleApiError(error);
    }
  },

  // Get a single security event by ID
  async getEvent(eventId: string): Promise<SecurityEvent> {
    try {
      return await apiClient.get<SecurityEvent>(`/security/events/${eventId}`);
    } catch (error) {
      console.error(`Error fetching security event ${eventId}:`, error);
      return handleApiError(error);
    }
  },

  // Mark an event as resolved
  async resolveEvent(eventId: string, reason: string): Promise<SecurityEvent> {
    try {
      return await apiClient.patch<SecurityEvent>(`/security/events/${eventId}/resolve`, { reason });
    } catch (error) {
      console.error(`Error resolving security event ${eventId}:`, error);
      return handleApiError(error);
    }
  },

  // Get security events summary (for charts/analytics)
  async getEventsSummary(options: {
    groupBy: 'hour' | 'day' | 'week' | 'month';
    startDate?: string;
    endDate?: string;
    eventType?: string;
    severity?: string;
    source?: string;
  }) {
    try {
      const params = { ...options };
      Object.keys(params).forEach(key => params[key] === undefined && delete params[key]);
      
      return await apiClient.get('/security/events/summary', { params });
    } catch (error) {
      console.error('Error fetching security events summary:', error);
      return handleApiError(error);
    }
  },

  // Get security alerts
  async getAlerts(filters: {
    status?: 'open' | 'acknowledged' | 'resolved';
    severity?: string;
    startDate?: string;
    endDate?: string;
    skip?: number;
    limit?: number;
  } = {}) {
    try {
      const params = {
        ...filters,
        skip: filters.skip || 0,
        limit: filters.limit || 10,
      };

      Object.keys(params).forEach(key => params[key] === undefined && delete params[key]);
      
      return await apiClient.get('/security/alerts', { params });
    } catch (error) {
      console.error('Error fetching security alerts:', error);
      return handleApiError(error);
    }
  },

  // Acknowledge a security alert
  async acknowledgeAlert(alertId: string): Promise<void> {
    try {
      await apiClient.post(`/security/alerts/${alertId}/acknowledge`);
    } catch (error) {
      console.error(`Error acknowledging alert ${alertId}:`, error);
      return handleApiError(error);
    }
  },
};

export default securityEventService;
