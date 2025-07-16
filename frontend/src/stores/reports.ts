import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import * as reportService from '@/services/reportService';
import type { 
  Report, 
  ReportCategory, 
  ReportExecution, 
  ReportSchedule,
  ReportSubscription,
  ReportFavorite,
  ReportComment
} from '@/types/reports';

export const useReportsStore = defineStore('reports', () => {
  const authStore = useAuthStore();
  
  // State
  const reports = ref<Report[]>([]);
  const categories = ref<ReportCategory[]>([]);
  const favorites = ref<ReportFavorite[]>([]);
  const recentReports = ref<Report[]>([]);
  const loading = ref(false);
  const error = ref<Error | null>(null);
  const selectedReport = ref<Report | null>(null);
  const reportExecutions = ref<Record<string, ReportExecution[]>>({});
  const reportSchedules = ref<Record<string, ReportSchedule[]>>({});
  const reportSubscriptions = ref<Record<string, ReportSubscription[]>>({});
  const reportComments = ref<Record<string, ReportComment[]>>({});
  
  // Getters
  const favoriteReports = computed<Report[]>(() => {
    return reports.value.filter(report => 
      favorites.value.some(fav => fav.reportId === report.id)
    );
  });
  
  const recentReportIds = computed<Set<string>>(() => {
    return new Set(recentReports.value.map(r => r.id));
  });
  
  const reportsByCategory = computed<Record<string, Report[]>>(() => {
    const result: Record<string, Report[]> = {};
    
    // Initialize with all categories
    categories.value.forEach(category => {
      result[category.id] = [];
    });
    
    // Add uncategorized reports
    result['uncategorized'] = [];
    
    // Group reports by category
    reports.value.forEach(report => {
      if (report.categoryId && result[report.categoryId]) {
        result[report.categoryId].push(report);
      } else {
        result['uncategorized'].push(report);
      }
    });
    
    return result;
  });
  
  // Actions
  const fetchReports = async () => {
    loading.value = true;
    error.value = null;
    try {
      reports.value = await reportService.fetchReports();
    } catch (err) {
      error.value = err as Error;
      console.error('Failed to fetch reports:', err);
    } finally {
      loading.value = false;
    }
  };
  
  const fetchReportById = async (id: string) => {
    loading.value = true;
    error.value = null;
    try {
      selectedReport.value = await reportService.getReportById(id);
      return selectedReport.value;
    } catch (err) {
      error.value = err as Error;
      console.error(`Failed to fetch report ${id}:`, err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const createReport = async (reportData: Partial<Report>) => {
    loading.value = true;
    error.value = null;
    try {
      const newReport = await reportService.createReport(reportData);
      reports.value.push(newReport);
      return newReport;
    } catch (err) {
      error.value = err as Error;
      console.error('Failed to create report:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const updateReport = async (id: string, reportData: Partial<Report>) => {
    loading.value = true;
    error.value = null;
    try {
      const updatedReport = await reportService.updateReport(id, reportData);
      
      // Update in reports array
      const index = reports.value.findIndex(r => r.id === id);
      if (index !== -1) {
        reports.value[index] = { ...reports.value[index], ...updatedReport };
      }
      
      // Update selected report if it's the one being updated
      if (selectedReport.value?.id === id) {
        selectedReport.value = { ...selectedReport.value, ...updatedReport };
      }
      
      return updatedReport;
    } catch (err) {
      error.value = err as Error;
      console.error(`Failed to update report ${id}:`, err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const deleteReport = async (id: string) => {
    loading.value = true;
    error.value = null;
    try {
      await reportService.deleteReport(id);
      
      // Remove from reports array
      const index = reports.value.findIndex(r => r.id === id);
      if (index !== -1) {
        reports.value.splice(index, 1);
      }
      
      // Clear selected report if it's the one being deleted
      if (selectedReport.value?.id === id) {
        selectedReport.value = null;
      }
    } catch (err) {
      error.value = err as Error;
      console.error(`Failed to delete report ${id}:`, err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const runReport = async (id: string, params: Record<string, any> = {}) => {
    loading.value = true;
    error.value = null;
    try {
      const execution = await reportService.runReport(id, params);
      
      // Update report's last run time
      const report = reports.value.find(r => r.id === id);
      if (report) {
        report.lastRun = new Date().toISOString();
      }
      
      // Add to executions
      if (!reportExecutions.value[id]) {
        reportExecutions.value[id] = [];
      }
      reportExecutions.value[id].unshift(execution);
      
      // Add to recent reports if not already there
      if (!recentReportIds.value.has(id)) {
        const report = reports.value.find(r => r.id === id);
        if (report) {
          recentReports.value.unshift(report);
          // Keep only the last 10 recent reports
          if (recentReports.value.length > 10) {
            recentReports.value.pop();
          }
        }
      }
      
      return execution;
    } catch (err) {
      error.value = err as Error;
      console.error(`Failed to run report ${id}:`, err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const exportReport = async (
    id: string, 
    format: 'pdf' | 'excel' | 'csv' | 'json', 
    options: Record<string, any> = {}
  ) => {
    loading.value = true;
    error.value = null;
    try {
      await reportService.exportReport(id, format, options);
    } catch (err) {
      error.value = err as Error;
      console.error(`Failed to export report ${id} as ${format}:`, err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // Categories
  const fetchCategories = async () => {
    try {
      categories.value = await reportService.fetchReportCategories();
    } catch (err) {
      console.error('Failed to fetch report categories:', err);
    }
  };
  
  // Favorites
  const fetchFavorites = async () => {
    if (!authStore.user?.id) return;
    
    try {
      favorites.value = await reportService.fetchFavoriteReports(authStore.user.id);
    } catch (err) {
      console.error('Failed to fetch favorite reports:', err);
    }
  };
  
  const toggleFavorite = async (reportId: string) => {
    if (!authStore.user?.id) return;
    
    try {
      const isFavorite = favorites.value.some(fav => fav.reportId === reportId);
      
      if (isFavorite) {
        await reportService.removeFromFavorites(authStore.user.id, reportId);
        favorites.value = favorites.value.filter(fav => fav.reportId !== reportId);
      } else {
        const favorite = await reportService.addToFavorites(authStore.user.id, reportId);
        favorites.value.push(favorite);
      }
      
      return !isFavorite;
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
      throw err;
    }
  };
  
  // Recent Reports
  const fetchRecentReports = async () => {
    if (!authStore.user?.id) return;
    
    try {
      recentReports.value = await reportService.fetchRecentReports(authStore.user.id);
    } catch (err) {
      console.error('Failed to fetch recent reports:', err);
    }
  };
  
  // Schedules
  const fetchReportSchedules = async (reportId: string) => {
    try {
      const schedules = await reportService.fetchReportSchedules(reportId);
      reportSchedules.value[reportId] = schedules;
      return schedules;
    } catch (err) {
      console.error(`Failed to fetch schedules for report ${reportId}:`, err);
      throw err;
    }
  };
  
  const createReportSchedule = async (reportId: string, schedule: Partial<ReportSchedule>) => {
    try {
      const newSchedule = await reportService.createReportSchedule(reportId, schedule);
      
      if (!reportSchedules.value[reportId]) {
        reportSchedules.value[reportId] = [];
      }
      
      reportSchedules.value[reportId].push(newSchedule);
      return newSchedule;
    } catch (err) {
      console.error(`Failed to create schedule for report ${reportId}:`, err);
      throw err;
    }
  };
  
  // Subscriptions
  const fetchReportSubscriptions = async (reportId: string) => {
    try {
      const subscriptions = await reportService.fetchReportSubscriptions(reportId);
      reportSubscriptions.value[reportId] = subscriptions;
      return subscriptions;
    } catch (err) {
      console.error(`Failed to fetch subscriptions for report ${reportId}:`, err);
      throw err;
    }
  };
  
  const subscribeToReport = async (reportId: string, subscription: Partial<ReportSubscription>) => {
    try {
      const newSubscription = await reportService.subscribeToReport(reportId, subscription);
      
      if (!reportSubscriptions.value[reportId]) {
        reportSubscriptions.value[reportId] = [];
      }
      
      // Check if already subscribed and update, otherwise add new
      const existingIndex = reportSubscriptions.value[reportId].findIndex(
        sub => sub.userId === newSubscription.userId
      );
      
      if (existingIndex !== -1) {
        reportSubscriptions.value[reportId][existingIndex] = newSubscription;
      } else {
        reportSubscriptions.value[reportId].push(newSubscription);
      }
      
      return newSubscription;
    } catch (err) {
      console.error(`Failed to subscribe to report ${reportId}:`, err);
      throw err;
    }
  };
  
  // Comments
  const fetchReportComments = async (reportId: string) => {
    try {
      const comments = await reportService.fetchReportComments(reportId);
      reportComments.value[reportId] = comments;
      return comments;
    } catch (err) {
      console.error(`Failed to fetch comments for report ${reportId}:`, err);
      throw err;
    }
  };
  
  const addComment = async (reportId: string, content: string, parentId?: string) => {
    try {
      const newComment = await reportService.addReportComment(reportId, content, parentId);
      
      if (!reportComments.value[reportId]) {
        reportComments.value[reportId] = [];
      }
      
      if (parentId) {
        // Add as a reply
        const parentComment = reportComments.value[reportId].find(c => c.id === parentId);
        if (parentComment) {
          if (!parentComment.replies) {
            parentComment.replies = [];
          }
          parentComment.replies.push(newComment);
        }
      } else {
        // Add as a top-level comment
        reportComments.value[reportId].push(newComment);
      }
      
      return newComment;
    } catch (err) {
      console.error('Failed to add comment:', err);
      throw err;
    }
  };
  
  const updateComment = async (reportId: string, commentId: string, content: string) => {
    try {
      const updatedComment = await reportService.updateReportComment(reportId, commentId, content);
      
      // Update in comments array
      const updateInArray = (comments: ReportComment[]): boolean => {
        for (let i = 0; i < comments.length; i++) {
          if (comments[i].id === commentId) {
            comments[i] = { ...comments[i], ...updatedComment };
            return true;
          }
          
          if (comments[i].replies) {
            if (updateInArray(comments[i].replies!)) {
              return true;
            }
          }
        }
        return false;
      };
      
      if (reportComments.value[reportId]) {
        updateInArray(reportComments.value[reportId]);
      }
      
      return updatedComment;
    } catch (err) {
      console.error(`Failed to update comment ${commentId}:`, err);
      throw err;
    }
  };
  
  const deleteComment = async (reportId: string, commentId: string) => {
    try {
      await reportService.deleteReportComment(reportId, commentId);
      
      // Remove from comments array
      const removeFromArray = (comments: ReportComment[]): boolean => {
        for (let i = 0; i < comments.length; i++) {
          if (comments[i].id === commentId) {
            comments.splice(i, 1);
            return true;
          }
          
          if (comments[i].replies) {
            if (removeFromArray(comments[i].replies!)) {
              return true;
            }
          }
        }
        return false;
      };
      
      if (reportComments.value[reportId]) {
        removeFromArray(reportComments.value[reportId]);
      }
    } catch (err) {
      console.error(`Failed to delete comment ${commentId}:`, err);
      throw err;
    }
  };
  
  // Initialize
  const initialize = async () => {
    await Promise.all([
      fetchReports(),
      fetchCategories(),
    ]);
    
    if (authStore.isAuthenticated) {
      await Promise.all([
        fetchFavorites(),
        fetchRecentReports(),
      ]);
    }
  };
  
  // Watch for auth changes
  watch(() => authStore.isAuthenticated, (isAuthenticated) => {
    if (isAuthenticated) {
      fetchFavorites();
      fetchRecentReports();
    } else {
      favorites.value = [];
      recentReports.value = [];
    }
  });
  
  return {
    // State
    reports,
    categories,
    favorites,
    recentReports,
    loading,
    error,
    selectedReport,
    reportExecutions,
    reportSchedules,
    reportSubscriptions,
    reportComments,
    
    // Getters
    favoriteReports,
    recentReportIds,
    reportsByCategory,
    
    // Actions
    initialize,
    fetchReports,
    fetchReportById,
    createReport,
    updateReport,
    deleteReport,
    runReport,
    exportReport,
    fetchCategories,
    fetchFavorites,
    toggleFavorite,
    fetchRecentReports,
    fetchReportSchedules,
    createReportSchedule,
    fetchReportSubscriptions,
    subscribeToReport,
    fetchReportComments,
    addComment,
    updateComment,
    deleteComment,
  };
});
