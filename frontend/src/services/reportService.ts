import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useAuthStore } from '@/stores/auth';
import api from '@/services/api';
import type { 
  Report, 
  ReportCategory, 
  ReportExecution, 
  ReportSchedule,
  ReportSubscription,
  ReportFavorite,
  ReportComment
} from '@/types/reports';

const toast = useToast();
const authStore = useAuthStore();

// Reports
const reports = ref<Report[]>([]);
const loading = ref(false);
const error = ref<Error | null>(null);

// Fetch all reports
export const fetchReports = async (): Promise<Report[]> => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await api.get('/reports');
    reports.value = response.data;
    return reports.value;
  } catch (err) {
    error.value = err as Error;
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to fetch reports',
      life: 3000,
    });
    throw err;
  } finally {
    loading.value = false;
  }
};

// Get report by ID
export const getReportById = async (id: string): Promise<Report> => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await api.get(`/reports/${id}`);
    return response.data;
  } catch (err) {
    error.value = err as Error;
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to fetch report',
      life: 3000,
    });
    throw err;
  } finally {
    loading.value = false;
  }
};

// Create a new report
export const createReport = async (report: Partial<Report>): Promise<Report> => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await api.post('/reports', {
      ...report,
      createdBy: authStore.user?.id,
      modifiedBy: authStore.user?.id,
    });
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Report created successfully',
      life: 3000,
    });
    
    return response.data;
  } catch (err) {
    error.value = err as Error;
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to create report',
      life: 3000,
    });
    throw err;
  } finally {
    loading.value = false;
  }
};

// Update an existing report
export const updateReport = async (id: string, report: Partial<Report>): Promise<Report> => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await api.put(`/reports/${id}`, {
      ...report,
      modifiedBy: authStore.user?.id,
    });
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Report updated successfully',
      life: 3000,
    });
    
    return response.data;
  } catch (err) {
    error.value = err as Error;
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to update report',
      life: 3000,
    });
    throw err;
  } finally {
    loading.value = false;
  }
};

// Delete a report
export const deleteReport = async (id: string): Promise<void> => {
  loading.value = true;
  error.value = null;
  
  try {
    await api.delete(`/reports/${id}`);
    
    // Remove from local state
    const index = reports.value.findIndex(r => r.id === id);
    if (index !== -1) {
      reports.value.splice(index, 1);
    }
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Report deleted successfully',
      life: 3000,
    });
  } catch (err) {
    error.value = err as Error;
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete report',
      life: 3000,
    });
    throw err;
  } finally {
    loading.value = false;
  }
};

// Run a report
export const runReport = async (id: string, params: Record<string, any> = {}): Promise<ReportExecution> => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await api.post(`/reports/${id}/run`, params);
    
    // Update last run time in local state
    const report = reports.value.find(r => r.id === id);
    if (report) {
      report.lastRun = new Date().toISOString();
    }
    
    return response.data;
  } catch (err) {
    error.value = err as Error;
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to run report',
      life: 3000,
    });
    throw err;
  } finally {
    loading.value = false;
  }
};

// Export a report
export const exportReport = async (
  id: string, 
  format: 'pdf' | 'excel' | 'csv' | 'json', 
  options: Record<string, any> = {}
): Promise<void> => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await api.post(
      `/reports/${id}/export`,
      { format, ...options },
      { responseType: 'blob' }
    );
    
    // Create a download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `report_${id}_${new Date().toISOString().split('T')[0]}.${format}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `Report exported as ${format.toUpperCase()}`,
      life: 3000,
    });
  } catch (err) {
    error.value = err as Error;
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `Failed to export report as ${format.toUpperCase()}`,
      life: 3000,
    });
    throw err;
  } finally {
    loading.value = false;
  }
};

// Report Categories
export const fetchReportCategories = async (): Promise<ReportCategory[]> => {
  try {
    const response = await api.get('/report-categories');
    return response.data;
  } catch (err) {
    console.error('Failed to fetch report categories:', err);
    return [];
  }
};

// Favorites
export const fetchFavoriteReports = async (userId: string): Promise<ReportFavorite[]> => {
  try {
    const response = await api.get(`/users/${userId}/favorite-reports`);
    return response.data;
  } catch (err) {
    console.error('Failed to fetch favorite reports:', err);
    return [];
  }
};

export const addToFavorites = async (userId: string, reportId: string): Promise<ReportFavorite> => {
  try {
    const response = await api.post(`/users/${userId}/favorite-reports`, { reportId });
    return response.data;
  } catch (err) {
    console.error('Failed to add to favorites:', err);
    throw err;
  }
};

export const removeFromFavorites = async (userId: string, reportId: string): Promise<void> => {
  try {
    await api.delete(`/users/${userId}/favorite-reports/${reportId}`);
  } catch (err) {
    console.error('Failed to remove from favorites:', err);
    throw err;
  }
};

// Recent Reports
export const fetchRecentReports = async (userId: string, limit = 5): Promise<Report[]> => {
  try {
    const response = await api.get(`/users/${userId}/recent-reports?limit=${limit}`);
    return response.data;
  } catch (err) {
    console.error('Failed to fetch recent reports:', err);
    return [];
  }
};

// Report Schedules
export const fetchReportSchedules = async (reportId: string): Promise<ReportSchedule[]> => {
  try {
    const response = await api.get(`/reports/${reportId}/schedules`);
    return response.data;
  } catch (err) {
    console.error('Failed to fetch report schedules:', err);
    return [];
  }
};

export const createReportSchedule = async (
  reportId: string, 
  schedule: Partial<ReportSchedule>
): Promise<ReportSchedule> => {
  try {
    const response = await api.post(`/reports/${reportId}/schedules`, {
      ...schedule,
      createdBy: authStore.user?.id,
      modifiedBy: authStore.user?.id,
    });
    return response.data;
  } catch (err) {
    console.error('Failed to create report schedule:', err);
    throw err;
  }
};

// Report Subscriptions
export const fetchReportSubscriptions = async (reportId: string): Promise<ReportSubscription[]> => {
  try {
    const response = await api.get(`/reports/${reportId}/subscriptions`);
    return response.data;
  } catch (err) {
    console.error('Failed to fetch report subscriptions:', err);
    return [];
  }
};

export const subscribeToReport = async (
  reportId: string, 
  subscription: Partial<ReportSubscription>
): Promise<ReportSubscription> => {
  try {
    const response = await api.post(`/reports/${reportId}/subscriptions`, {
      ...subscription,
      userId: authStore.user?.id,
    });
    return response.data;
  } catch (err) {
    console.error('Failed to subscribe to report:', err);
    throw err;
  }
};

// Report Comments
export const fetchReportComments = async (reportId: string): Promise<ReportComment[]> => {
  try {
    const response = await api.get(`/reports/${reportId}/comments`);
    return response.data;
  } catch (err) {
    console.error('Failed to fetch report comments:', err);
    return [];
  }
};

export const addReportComment = async (
  reportId: string, 
  content: string,
  parentId?: string
): Promise<ReportComment> => {
  try {
    const response = await api.post(`/reports/${reportId}/comments`, {
      content,
      parentId,
      userId: authStore.user?.id,
      userName: authStore.user?.name,
      userAvatar: authStore.user?.avatar,
    });
    return response.data;
  } catch (err) {
    console.error('Failed to add comment:', err);
    throw err;
  }
};

export const updateReportComment = async (
  reportId: string,
  commentId: string,
  content: string
): Promise<ReportComment> => {
  try {
    const response = await api.put(`/reports/${reportId}/comments/${commentId}`, {
      content,
      modified: new Date().toISOString(),
    });
    return response.data;
  } catch (err) {
    console.error('Failed to update comment:', err);
    throw err;
  }
};

export const deleteReportComment = async (reportId: string, commentId: string): Promise<void> => {
  try {
    await api.delete(`/reports/${reportId}/comments/${commentId}`);
  } catch (err) {
    console.error('Failed to delete comment:', err);
    throw err;
  }
};

export default {
  // Reports
  reports,
  loading,
  error,
  fetchReports,
  getReportById,
  createReport,
  updateReport,
  deleteReport,
  runReport,
  exportReport,
  
  // Categories
  fetchReportCategories,
  
  // Favorites
  fetchFavoriteReports,
  addToFavorites,
  removeFromFavorites,
  
  // Recent
  fetchRecentReports,
  
  // Schedules
  fetchReportSchedules,
  createReportSchedule,
  
  // Subscriptions
  fetchReportSubscriptions,
  subscribeToReport,
  
  // Comments
  fetchReportComments,
  addReportComment,
  updateReportComment,
  deleteReportComment,
};