import { api } from '@/utils/api';

export interface Backup {
  id: string;
  backup_name: string;
  backup_type: string;
  file_path?: string;
  file_size?: number;
  compression_type?: string;
  status: string;
  started_at?: string;
  completed_at?: string;
  tables_included?: string[];
  error_message?: string;
  checksum?: string;
  initiated_by: string;
  created_at: string;
}

export interface BackupRequest {
  backup_name: string;
  backup_type?: string;
  tables?: string[];
}

export interface RestoreOperation {
  id: string;
  restore_name: string;
  backup_id: string;
  restore_point?: string;
  tables_to_restore?: string[];
  overwrite_existing: boolean;
  status: string;
  started_at?: string;
  completed_at?: string;
  records_restored?: number;
  error_message?: string;
  initiated_by: string;
  created_at: string;
}

export interface RestoreRequest {
  restore_name: string;
  backup_id: string;
  tables_to_restore?: string[];
  overwrite_existing?: boolean;
}

export interface BackupSchedule {
  id: string;
  schedule_name: string;
  backup_type: string;
  cron_expression: string;
  is_active: boolean;
  retention_days: number;
  compression_enabled: boolean;
  last_run?: string;
  next_run?: string;
  created_at: string;
  updated_at: string;
}

export interface BackupScheduleRequest {
  schedule_name: string;
  backup_type?: string;
  cron_expression: string;
  retention_days?: number;
  compression_enabled?: boolean;
}

export interface BackupDashboard {
  total_backups: number;
  successful_backups: number;
  failed_backups: number;
  total_storage_mb: number;
  recent_backups: Backup[];
  active_schedules: number;
  last_backup_date?: string;
}

/**
 * Backup Service
 * Provides methods to interact with the backup and restore API endpoints
 */
export default {
  /**
   * Create a database backup
   * @param backupRequest - Backup creation request
   * @returns Promise with the created backup
   */
  async createBackup(backupRequest: BackupRequest) {
    return api.post('/backup/backups', backupRequest);
  },

  /**
   * List database backups
   * @param limit - Maximum number of backups to return
   * @returns Promise with the list of backups
   */
  async listBackups(limit: number = 100) {
    return api.get(`/backup/backups?limit=${limit}`);
  },

  /**
   * Get a backup by ID
   * @param backupId - Backup ID
   * @returns Promise with the backup details
   */
  async getBackup(backupId: string) {
    return api.get(`/backup/backups/${backupId}`);
  },

  /**
   * Restore from a backup
   * @param restoreRequest - Restore operation request
   * @returns Promise with the restore operation
   */
  async restoreBackup(restoreRequest: RestoreRequest) {
    return api.post('/backup/restore', restoreRequest);
  },

  /**
   * List restore operations
   * @param limit - Maximum number of operations to return
   * @returns Promise with the list of restore operations
   */
  async listRestoreOperations(limit: number = 100) {
    return api.get(`/backup/restore-operations?limit=${limit}`);
  },

  /**
   * Create a backup schedule
   * @param scheduleRequest - Schedule creation request
   * @returns Promise with the created schedule
   */
  async createSchedule(scheduleRequest: BackupScheduleRequest) {
    return api.post('/backup/schedules', scheduleRequest);
  },

  /**
   * List backup schedules
   * @param activeOnly - Whether to show only active schedules
   * @returns Promise with the list of schedules
   */
  async listSchedules(activeOnly: boolean = true) {
    return api.get(`/backup/schedules?active_only=${activeOnly}`);
  },

  /**
   * Clean up old backups
   * @param retentionDays - Number of days to retain backups
   * @returns Promise with cleanup result
   */
  async cleanupOldBackups(retentionDays: number = 30) {
    return api.post(`/backup/cleanup?retention_days=${retentionDays}`);
  },

  /**
   * Get backup dashboard data
   * @returns Promise with dashboard data
   */
  async getDashboard() {
    return api.get('/backup/dashboard');
  },

  /**
   * Utility functions for backup operations
   */
  utils: {
    /**
     * Format backup type for display
     */
    formatBackupType(type: string): string {
      const typeMap: Record<string, string> = {
        'full': 'Full Backup',
        'incremental': 'Incremental Backup',
        'differential': 'Differential Backup'
      };
      
      return typeMap[type] || type.charAt(0).toUpperCase() + type.slice(1);
    },

    /**
     * Get status color for UI
     */
    getStatusColor(status: string): string {
      const colorMap: Record<string, string> = {
        'pending': 'warning',
        'running': 'info',
        'completed': 'success',
        'failed': 'error'
      };
      
      return colorMap[status] || 'grey';
    },

    /**
     * Format file size
     */
    formatFileSize(bytes?: number): string {
      if (!bytes) return 'N/A';
      
      if (bytes < 1024) return `${bytes} B`;
      if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
      if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
    },

    /**
     * Calculate backup duration
     */
    calculateDuration(startedAt?: string, completedAt?: string): string {
      if (!startedAt || !completedAt) return 'N/A';
      
      const start = new Date(startedAt);
      const end = new Date(completedAt);
      const duration = end.getTime() - start.getTime();
      
      const seconds = Math.floor(duration / 1000);
      const minutes = Math.floor(seconds / 60);
      const hours = Math.floor(minutes / 60);
      
      if (hours > 0) {
        return `${hours}h ${minutes % 60}m`;
      } else if (minutes > 0) {
        return `${minutes}m ${seconds % 60}s`;
      } else {
        return `${seconds}s`;
      }
    },

    /**
     * Validate cron expression
     */
    validateCronExpression(expression: string): { valid: boolean; message?: string } {
      // Basic cron validation (5 fields: minute hour day month weekday)
      const parts = expression.trim().split(/\s+/);
      
      if (parts.length !== 5) {
        return { valid: false, message: 'Cron expression must have 5 fields' };
      }
      
      // Basic field validation
      const ranges = [
        { min: 0, max: 59 }, // minute
        { min: 0, max: 23 }, // hour
        { min: 1, max: 31 }, // day
        { min: 1, max: 12 }, // month
        { min: 0, max: 7 }   // weekday
      ];
      
      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        if (part === '*' || part === '?') continue;
        
        // Check for numeric values
        if (/^\d+$/.test(part)) {
          const num = parseInt(part);
          if (num < ranges[i].min || num > ranges[i].max) {
            return { valid: false, message: `Field ${i + 1} out of range` };
          }
        }
      }
      
      return { valid: true };
    },

    /**
     * Get common cron expressions
     */
    getCommonCronExpressions(): Array<{ label: string; expression: string }> {
      return [
        { label: 'Daily at midnight', expression: '0 0 * * *' },
        { label: 'Daily at 2 AM', expression: '0 2 * * *' },
        { label: 'Weekly on Sunday at 2 AM', expression: '0 2 * * 0' },
        { label: 'Monthly on 1st at 2 AM', expression: '0 2 1 * *' },
        { label: 'Every 6 hours', expression: '0 */6 * * *' },
        { label: 'Every 12 hours', expression: '0 */12 * * *' }
      ];
    },

    /**
     * Calculate success rate
     */
    calculateSuccessRate(successful: number, total: number): number {
      if (total === 0) return 0;
      return Math.round((successful / total) * 100);
    },

    /**
     * Get backup type recommendation
     */
    getBackupTypeRecommendation(lastBackupType?: string, daysSinceLastFull?: number): string {
      if (!lastBackupType || daysSinceLastFull === undefined || daysSinceLastFull >= 7) {
        return 'full';
      } else if (daysSinceLastFull >= 1) {
        return 'incremental';
      } else {
        return 'differential';
      }
    },

    /**
     * Estimate backup time
     */
    estimateBackupTime(backupType: string, dataSize: number): string {
      // Rough estimates based on backup type and data size
      const baseTime = dataSize / (1024 * 1024); // MB
      
      let multiplier = 1;
      switch (backupType) {
        case 'full':
          multiplier = 1;
          break;
        case 'incremental':
          multiplier = 0.3;
          break;
        case 'differential':
          multiplier = 0.6;
          break;
      }
      
      const estimatedMinutes = Math.ceil(baseTime * multiplier * 0.1);
      
      if (estimatedMinutes < 1) {
        return '< 1 minute';
      } else if (estimatedMinutes < 60) {
        return `~${estimatedMinutes} minutes`;
      } else {
        const hours = Math.floor(estimatedMinutes / 60);
        const minutes = estimatedMinutes % 60;
        return `~${hours}h ${minutes}m`;
      }
    }
  }
};