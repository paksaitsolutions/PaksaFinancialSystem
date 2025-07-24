export interface Report {
  id: string;
  name: string;
  description: string;
  route: string;
  icon: string;
  category: string;
  categoryId?: string;
  lastRun?: string;
  favorite?: boolean;
  is_favorite?: boolean;
  tags?: string[];
}

export interface CompanyReport {
  id: string;
  company_id: string;
  report_name: string;
  report_type: string;
  period_start: string;
  period_end: string;
  filters?: Record<string, any>;
  status: string;
  generated_at?: string;
  file_path?: string;
  file_format?: string;
  report_data?: Record<string, any>;
  generated_by: string;
  description?: string;
  created_at: string;
}

export interface ReportTemplate {
  id: string;
  company_id: string;
  template_name: string;
  report_type: string;
  template_config: Record<string, any>;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
}

export interface ReportSchedule {
  id: string;
  company_id: string;
  schedule_name: string;
  report_type: string;
  cron_expression: string;
  is_active: boolean;
  report_config?: Record<string, any>;
  email_recipients?: string[];
  last_run?: string;
  next_run?: string;
  created_at: string;
}

export interface ReportCategory {
  id: string;
  name: string;
  icon: string;
  count: number;
  reports?: Report[];
}

export interface ReportExportFormat {
  value: string;
  label: string;
  icon: string;
}