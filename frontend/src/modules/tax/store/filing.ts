import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { TaxFilingService } from '@/modules/tax/services/taxFilingService';
import type { 
  TaxFiling, 
  TaxFilingCreate, 
  TaxFilingUpdate, 
  TaxFilingFilter, 
  TaxFilingStats, 
  TaxFilingCalendarEvent,
  TaxReturnAttachment
} from '@/modules/tax/types/taxFiling';
import { useToast } from 'primevue/usetoast';

export const useTaxFilingStore = defineStore('taxFiling', () => {
  // State
  const filings = ref<TaxFiling[]>([]);
  const currentFiling = ref<TaxFiling | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const stats = ref<TaxFilingStats | null>(null);
  const calendarEvents = ref<TaxFilingCalendarEvent[]>([]);
  const pagination = ref({
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 1,
  });

  // Getters
  const upcomingFilings = computed(() => {
    const today = new Date();
    return filings.value.filter(
      (filing) => new Date(filing.due_date) >= today && filing.status !== 'filed'
    ).sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime());
  });

  const overdueFilings = computed(() => {
    const today = new Date();
    return filings.value.filter(
      (filing) => new Date(filing.due_date) < today && filing.status !== 'filed'
    ).sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime());
  });

  const recentFilings = computed(() => {
    return [...filings.value]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5);
  });
  
  // Get file icon based on file type
  const getFileIcon = (fileName: string): string => {
    const extension = fileName.split('.').pop()?.toLowerCase() || '';
    
    const iconMap: Record<string, string> = {
      // Documents
      'pdf': 'pi pi-file-pdf',
      'doc': 'pi pi-file-word',
      'docx': 'pi pi-file-word',
      'xls': 'pi pi-file-excel',
      'xlsx': 'pi pi-file-excel',
      'ppt': 'pi pi-file-powerpoint',
      'pptx': 'pi pi-file-powerpoint',
      'txt': 'pi pi-file',
      'csv': 'pi pi-file-csv',
      // Images
      'jpg': 'pi pi-image',
      'jpeg': 'pi pi-image',
      'png': 'pi pi-image',
      'gif': 'pi pi-image',
      'svg': 'pi pi-image',
      // Archives
      'zip': 'pi pi-file-archive',
      'rar': 'pi pi-file-archive',
      '7z': 'pi pi-file-archive',
      'tar': 'pi pi-file-archive',
      'gz': 'pi pi-file-archive',
    };
    
    return iconMap[extension] || 'pi pi-file';
  };
  
  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  // Actions
  const fetchFilings = async (filter: TaxFilingFilter = {}, page = 1, limit = 10) => {
    const authStore = useAuthStore();
    loading.value = true;
    error.value = null;
    
    try {
      // Ensure user is authenticated
      await authStore.checkAuth();
      
      // Add company ID to filter if not provided
      const companyFilter = { 
        company_id: authStore.currentUser?.company_id,
        ...filter 
      };
      
      const response = await TaxFilingService.getFilings({ 
        ...companyFilter, 
        page, 
        limit 
      });
      
      filings.value = response.data;
      pagination.value = {
        page: response.page,
        limit: response.limit,
        total: response.total,
        totalPages: Math.ceil(response.total / response.limit),
      };
      return response;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to fetch tax filings';
      error.value = errorMessage;
      console.error('Error fetching tax filings:', err);
      throw new Error(errorMessage);
    } finally {
      loading.value = false;
    }
  };

  const fetchFilingById = async (id: string) => {
    loading.value = true;
    error.value = null;
    try {
      currentFiling.value = await TaxFilingService.getFilingById(id);
      return currentFiling.value;
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch tax filing';
      console.error(`Error fetching tax filing ${id}:`, err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const uploadAttachment = async (file: File, attachmentType: string) => {
    const authStore = useAuthStore();
    const toast = useToast();
    
    try {
      // Ensure user is authenticated
      await authStore.checkAuth();
      
      // Step 1: Get pre-signed URL for upload
      const uploadData = {
        file_name: file.name,
        file_type: file.type,
        file_size: file.size,
        attachment_type: attachmentType
      };
      
      const { uploadUrl, attachmentId } = await TaxFilingService.getUploadUrl(uploadData);
      
      // Step 2: Upload file to pre-signed URL
      const uploadResponse = await fetch(uploadUrl, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type,
          'Content-Length': file.size.toString(),
        },
      });
      
      if (!uploadResponse.ok) {
        throw new Error('Failed to upload file');
      }
      
      return { attachmentId };
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to upload attachment';
      toast.add({
        severity: 'error',
        summary: 'Upload Failed',
        detail: errorMessage,
        life: 5000
      });
      console.error('Error uploading attachment:', err);
      throw new Error(errorMessage);
    }
  };
  
  const confirmAttachment = async (attachmentId: string, filingId: string) => {
    try {
      return await TaxFilingService.confirmAttachmentUpload(attachmentId, filingId);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to confirm attachment';
      console.error('Error confirming attachment:', err);
      throw new Error(errorMessage);
    }
  };
  
  const deleteAttachment = async (attachmentId: string) => {
    try {
      await TaxFilingService.deleteAttachment(attachmentId);
      // Remove attachment from current filing if it exists
      if (currentFiling.value) {
        currentFiling.value.attachments = currentFiling.value.attachments?.filter(
          (a: TaxReturnAttachment) => a.id !== attachmentId
        );
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to delete attachment';
      console.error('Error deleting attachment:', err);
      throw new Error(errorMessage);
    }
  };

  const createFiling = async (filingData: TaxFilingCreate, attachments: File[] = []) => {
    const authStore = useAuthStore();
    const toast = useToast();
    
    loading.value = true;
    error.value = null;
    
    try {
      // Ensure user is authenticated
      await authStore.checkAuth();
      
      // Add company ID and created by info
      const filingWithCompany = {
        ...filingData,
        company_id: authStore.currentUser?.company_id,
        created_by: authStore.currentUser?.id,
      };
      
      // Create the filing
      const newFiling = await TaxFilingService.createFiling(filingWithCompany);
      
      // Handle file uploads if any
      if (attachments && attachments.length > 0) {
        const uploadPromises = attachments.map(file => 
          uploadAttachment(file, 'supporting_document')
            .then(({ attachmentId }) => 
              confirmAttachment(attachmentId, newFiling.id)
            )
        );
        
        // Wait for all uploads to complete
        await Promise.all(uploadPromises);
        
        // Refresh the filing to get updated attachments
        const updatedFiling = await TaxFilingService.getFilingById(newFiling.id);
        filings.value.unshift(updatedFiling);
        return updatedFiling;
      }
      
      filings.value.unshift(newFiling);
      return newFiling;
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to create tax filing';
      error.value = errorMessage;
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: errorMessage,
        life: 5000
      });
      console.error('Error creating tax filing:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const updateFiling = async (id: string, updates: TaxFilingUpdate, newAttachments: File[] = []) => {
    const authStore = useAuthStore();
    const toast = useToast();
    
    loading.value = true;
    error.value = null;
    
    try {
      // Ensure user is authenticated
      await authStore.checkAuth();
      
      // Add updated by info
      const updatesWithUser = {
        ...updates,
        updated_by: authStore.currentUser?.id,
      };
      
      // Update the filing
      const updatedFiling = await TaxFilingService.updateFiling(id, updatesWithUser);
      
      // Handle new file uploads if any
      if (newAttachments && newAttachments.length > 0) {
        const uploadPromises = newAttachments.map(file => 
          uploadAttachment(file, 'supporting_document')
            .then(({ attachmentId }) => 
              confirmAttachment(attachmentId, id)
            )
        );
        
        // Wait for all uploads to complete
        await Promise.all(uploadPromises);
        
        // Refresh the filing to get updated attachments
        const refreshedFiling = await TaxFilingService.getFilingById(id);
        updatedFiling.attachments = refreshedFiling.attachments;
      }
      
      // Update local state
      const index = filings.value.findIndex(f => f.id === id);
      if (index !== -1) {
        filings.value[index] = updatedFiling;
      }
      if (currentFiling.value?.id === id) {
        currentFiling.value = updatedFiling;
      }
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Tax filing updated successfully',
        life: 3000
      });
      
      return updatedFiling;
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to update tax filing';
      error.value = errorMessage;
      toast.add({
        severity: 'error',
        summary: 'Update Failed',
        detail: errorMessage,
        life: 5000
      });
      console.error(`Error updating tax filing ${id}:`, err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const submitFiling = async (id: string) => {
    const authStore = useAuthStore();
    const toast = useToast();
    
    loading.value = true;
    error.value = null;
    
    try {
      // Ensure user is authenticated
      await authStore.checkAuth();
      
      // Submit the filing
      const submittedFiling = await TaxFilingService.submitFiling(id);
      
      // Update local state
      const index = filings.value.findIndex(f => f.id === id);
      if (index !== -1) {
        filings.value[index] = submittedFiling;
      }
      if (currentFiling.value?.id === id) {
        currentFiling.value = submittedFiling;
      }
      
      toast.add({
        severity: 'success',
        summary: 'Submitted',
        detail: 'Tax filing submitted successfully',
        life: 5000
      });
      
      return submittedFiling;
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to submit tax filing';
      error.value = errorMessage;
      toast.add({
        severity: 'error',
        summary: 'Submission Failed',
        detail: errorMessage,
        life: 5000
      });
      console.error(`Error submitting tax filing ${id}:`, err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchFilingStats = async (params?: { 
    start_date?: string; 
    end_date?: string; 
    tax_type?: string;
  }) => {
    loading.value = true;
    error.value = null;
    try {
      stats.value = await TaxFilingService.getFilingStats(params);
      return stats.value;
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch filing statistics';
      console.error('Error fetching filing stats:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchFilingCalendar = async (startDate: string, endDate: string, jurisdictionCode?: string) => {
    loading.value = true;
    error.value = null;
    try {
      calendarEvents.value = await TaxFilingService.getFilingCalendar({
        start_date: startDate,
        end_date: endDate,
        jurisdiction_code: jurisdictionCode,
      });
      return calendarEvents.value;
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch filing calendar';
      console.error('Error fetching filing calendar:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const downloadFiling = async (filingId: string, format: 'pdf' | 'excel' | 'csv' = 'pdf') => {
    try {
      const blob = await TaxFilingService.downloadFiling(filingId, format);
      
      // Create a download link and trigger it
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `tax-filing-${filingId}.${format}`);
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      if (link.parentNode) {
        link.parentNode.removeChild(link);
      }
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to download filing';
      console.error(`Error downloading filing ${filingId}:`, err);
      throw err;
    }
  };

  // Reset store state
  const reset = () => {
    filings.value = [];
    currentFiling.value = null;
    loading.value = false;
    error.value = null;
    stats.value = null;
    calendarEvents.value = [];
    pagination.value = {
      page: 1,
      limit: 10,
      total: 0,
      totalPages: 1,
    };
  };

  return {
    // State
    filings,
    currentFiling,
    loading,
    error,
    stats,
    calendarEvents,
    pagination,
    
    // Getters
    upcomingFilings,
    overdueFilings,
    recentFilings,
    getFileIcon,
    formatFileSize,
    
    // Actions
    fetchFilings,
    fetchFilingById,
    createFiling,
    updateFiling,
    submitFiling,
    fetchFilingStats,
    fetchFilingCalendar,
    downloadFiling,
    uploadAttachment,
    deleteAttachment,
    confirmAttachment,
    reset,
  };
});
