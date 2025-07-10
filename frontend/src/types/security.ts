export interface SecurityEvent {
  id: string;
  eventType: string;
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical';
  source: string;
  description: string;
  timestamp: string;
  userId?: string;
  username?: string;
  ipAddress?: string;
  userAgent?: string;
  location?: string;
  details?: Record<string, unknown>;
  resolved: boolean;
  resolvedAt?: string;
  resolvedBy?: string;
  createdAt: string;
  updatedAt: string;
}

export interface SecurityEventFilter {
  skip?: number;
  limit?: number;
  orderBy?: string;
  orderDesc?: boolean;
  eventType?: string;
  severity?: string;
  source?: string;
  resolved?: boolean;
  ipAddress?: string;
  userId?: string;
  startDate?: string;
  endDate?: string;
  searchQuery?: string;
}

export interface SecurityEventResponse {
  items: SecurityEvent[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface SecurityEventStats {
  total: number;
  bySeverity: Record<string, number>;
  byType: Record<string, number>;
  bySource: Record<string, number>;
  byStatus: {
    resolved: number;
    unresolved: number;
  };
  timeline: Array<{
    date: string;
    count: number;
  }>;
}
