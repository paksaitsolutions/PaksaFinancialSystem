import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useApi } from '@/composables/useApi';
import { useAuthStore } from '@/store/auth';

interface Attachment {
  id: string;
  tax_return_id: string;
  filename: string;
  description: string;
  document_type: string;
  file_size: number;
  mime_type: string;
  created_at: string;
  updated_at: string;
  download_url?: string;
}

export const useTaxAttachmentStore = defineStore('taxAttachment', () => {
  const api = useApi();
  const authStore = useAuthStore();
  
  const attachments = ref<Attachment[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  
  // Get all attachments for a tax return
  const fetchAttachments = async (taxReturnId: string) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await api.get(`/api/v1/tax/returns/${taxReturnId}/attachments`);
      attachments.value = response.data.map((attachment: any) => ({
        ...attachment,
        download_url: `${import.meta.env.VITE_API_BASE_URL}/api/v1/tax/attachments/${attachment.id}/download`
      }));
      
      return attachments.value;
    } catch (err: any) {
      console.error('Failed to fetch attachments:', err);
      error.value = err.response?.data?.detail || 'Failed to load attachments';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };
  
  // Upload a new attachment
  const uploadAttachment = async (taxReturnId: string, formData: FormData) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await api.post(
        `/api/v1/tax/returns/${taxReturnId}/attachments`, 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${authStore.accessToken}`
          }
        }
      );
      
      // Add the new attachment to the list
      attachments.value.unshift({
        ...response.data,
        download_url: `${import.meta.env.VITE_API_BASE_URL}/api/v1/tax/attachments/${response.data.id}/download`
      });
      
      return response.data;
    } catch (err: any) {
      console.error('Failed to upload attachment:', err);
      error.value = err.response?.data?.detail || 'Failed to upload attachment';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };
  
  // Download an attachment
  const downloadAttachment = async (attachmentId: string, filename: string) => {
    try {
      const response = await api.get(
        `/api/v1/tax/attachments/${attachmentId}/download`,
        { responseType: 'blob' }
      );
      
      // Create a temporary URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      
      // Create a temporary link element to trigger the download
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      if (link.parentNode) {
        link.parentNode.removeChild(link);
      }
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (err) {
      console.error('Failed to download attachment:', err);
      error.value = 'Failed to download attachment';
      throw err;
    }
  };
  
  // Delete an attachment
  const deleteAttachment = async (attachmentId: string) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      await api.delete(`/api/v1/tax/attachments/${attachmentId}`);
      
      // Remove the attachment from the list
      const index = attachments.value.findIndex(a => a.id === attachmentId);
      if (index !== -1) {
        attachments.value.splice(index, 1);
      }
      
      return true;
    } catch (err: any) {
      console.error('Failed to delete attachment:', err);
      error.value = err.response?.data?.detail || 'Failed to delete attachment';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };
  
  // Clear all attachments from the store
  const clearAttachments = () => {
    attachments.value = [];
    error.value = null;
  };
  
  return {
    // State
    attachments,
    isLoading,
    error,
    
    // Actions
    fetchAttachments,
    uploadAttachment,
    downloadAttachment,
    deleteAttachment,
    clearAttachments
  };
});

// Export the store as default
export default useTaxAttachmentStore;
