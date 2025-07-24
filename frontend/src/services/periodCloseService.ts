import { api } from '@/utils/api';
import { format } from 'date-fns';

export interface AccountingPeriod {
  id: string;
  period_name: string;
  period_type: 'monthly' | 'quarterly' | 'yearly';
  start_date: string;
  end_date: string;
  status: 'open' | 'closing' | 'closed' | 'reopened';
  closed_by?: string;
  closed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface PeriodCloseTask {
  id: string;
  period_close_id: string;
  task_name: string;
  task_description?: string;
  task_order: number;
  is_required: boolean;
  is_automated: boolean;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped';
  started_at?: string;
  completed_at?: string;
  assigned_to?: string;
  completed_by?: string;
  result_message?: string;
  error_message?: string;
  created_at: string;
}

export interface PeriodClose {
  id: string;
  close_number: string;
  period_id: string;
  close_type: 'monthly' | 'quarterly' | 'yearly';
  status: 'open' | 'closing' | 'closed' | 'reopened';
  initiated_at: string;
  completed_at?: string;
  initiated_by: string;
  completed_by?: string;
  notes?: string;
  period: AccountingPeriod;
  close_tasks: PeriodCloseTask[];
  created_at: string;
}

export interface AccountingPeriodCreate {
  period_name: string;
  period_type: string;
  start_date: Date;
  end_date: Date;
}

/**
 * Period Close Service
 * Provides methods to interact with the period close API endpoints
 */
export default {
  /**
   * Create a new accounting period
   * @param period - Period data
   * @returns Promise with the created period
   */
  async createAccountingPeriod(period: AccountingPeriodCreate) {
    const formattedPeriod = {
      ...period,
      start_date: format(period.start_date, 'yyyy-MM-dd'),
      end_date: format(period.end_date, 'yyyy-MM-dd')
    };
    return api.post('/period-close/periods', formattedPeriod);
  },

  /**
   * List accounting periods
   * @param options - Filter options
   * @returns Promise with the list of periods
   */
  async listAccountingPeriods(options = {
    skip: 0,
    limit: 100
  }) {
    const params = new URLSearchParams({
      skip: options.skip.toString(),
      limit: options.limit.toString()
    });

    return api.get(`/period-close/periods?${params.toString()}`);
  },

  /**
   * Initiate period close
   * @param periodId - Period ID
   * @returns Promise with the period close
   */
  async initiatePeriodClose(periodId: string) {
    return api.post(`/period-close/periods/${periodId}/close`);
  },

  /**
   * List period closes
   * @param options - Filter options
   * @returns Promise with the list of closes
   */
  async listPeriodCloses(options = {
    skip: 0,
    limit: 100
  }) {
    const params = new URLSearchParams({
      skip: options.skip.toString(),
      limit: options.limit.toString()
    });

    return api.get(`/period-close/closes?${params.toString()}`);
  },

  /**
   * Execute a close task
   * @param taskId - Task ID
   * @returns Promise with the task result
   */
  async executeCloseTask(taskId: string) {
    return api.post(`/period-close/tasks/${taskId}/execute`);
  },

  /**
   * Complete period close
   * @param closeId - Close ID
   * @returns Promise with the completed close
   */
  async completePeriodClose(closeId: string) {
    return api.post(`/period-close/closes/${closeId}/complete`);
  }
};