<template>
  <div class="tax-attachment-list">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-medium">Tax Return Attachments</h3>
      <Button 
        icon="pi pi-plus" 
        label="Add Attachment" 
        @click="showUploadDialog = true"
        size="small"
      />
    </div>

    <!-- Upload Dialog -->
    <Dialog 
      v-model:visible="showUploadDialog" 
      header="Upload Attachment" 
      :modal="true"
      :style="{ width: '500px' }"
    >
      <div class="p-fluid">
        <div class="field">
          <label for="file">File</label>
          <FileUpload 
            id="file"
            ref="fileUpload"
            :auto="true"
            mode="basic"
            :multiple="false"
            :maxFileSize="maxFileSize"
            :accept="allowedFileTypes"
            :chooseLabel="$t('common.chooseFile') || 'Choose'"
            :class="{'p-invalid': errors.file}"
            @select="onFileSelect"
          />
          <small class="p-error" v-if="errors.file">{{ errors.file }}</small>
        </div>

        <div class="field">
          <label for="description">Description</label>
          <InputText 
            id="description" 
            v-model="attachment.description" 
            :class="{'p-invalid': errors.description}"
            placeholder="Enter a description for this attachment"
          />
          <small class="p-error" v-if="errors.description">{{ errors.description }}</small>
        </div>

        <div class="field">
          <label for="documentType">Document Type</label>
          <Dropdown
            id="documentType"
            v-model="attachment.document_type"
            :options="documentTypes"
            optionLabel="label"
            optionValue="value"
            placeholder="Select document type"
            :class="{'p-invalid': errors.document_type}"
          />
          <small class="p-error" v-if="errors.document_type">{{ errors.document_type }}</small>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="closeUploadDialog"
        />
        <Button 
          label="Upload" 
          icon="pi pi-upload" 
          :loading="isUploading"
          @click="uploadAttachment"
        />
      </template>
    </Dialog>

    <!-- Attachments List -->
    <div v-if="attachments.length > 0" class="mt-4">
      <DataTable 
        :value="attachments" 
        :paginator="true" 
        :rows="10"
        :loading="isLoading"
        responsiveLayout="scroll"
      >
        <Column field="filename" header="File Name" :sortable="true">
          <template #body="{ data }">
            <a href="#" @click="downloadAttachment(data)" class="text-primary">
              <i :class="getFileIcon(data.filename) + ' mr-2'"></i>
              {{ data.filename }}
            </a>
          </template>
        </Column>
        <Column field="description" header="Description" :sortable="true" />
        <Column field="document_type" header="Type" :sortable="true">
          <template #body="{ data }">
            <Tag :value="formatDocumentType(data.document_type)" :severity="getDocumentTypeSeverity(data.document_type)" />
          </template>
        </Column>
        <Column field="file_size" header="Size" :sortable="true">
          <template #body="{ data }">
            {{ formatFileSize(data.file_size) }}
          </template>
        </Column>
        <Column field="created_at" header="Uploaded" :sortable="true">
          <template #body="{ data }">
            {{ formatDate(data.created_at) }}
          </template>
        </Column>
        <Column header="Actions" style="width: 10rem">
          <template #body="{ data }">
            <Button 
              icon="pi pi-download" 
              class="p-button-rounded p-button-text p-button-sm"
              @click="downloadAttachment(data)"
              v-tooltip.top="'Download'"
            />
            <Button 
              icon="pi pi-trash" 
              class="p-button-rounded p-button-text p-button-sm p-button-danger"
              @click="confirmDelete(data)"
              v-tooltip.top="'Delete'"
            />
          </template>
        </Column>
      </DataTable>
    </div>
    
    <div v-else class="p-4 text-center border-round border-1 surface-border">
      <p class="text-600">No attachments found</p>
      <Button 
        label="Upload Your First Attachment" 
        icon="pi pi-upload" 
        class="mt-2"
        @click="showUploadDialog = true"
      />
    </div>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';
import { useTaxAttachmentStore } from '../store/tax-attachment';
import { storeToRefs } from 'pinia';

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
}

export default defineComponent({
  name: 'TaxAttachmentList',
  props: {
    taxReturnId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const { t } = useI18n();
    const confirm = useConfirm();
    const toast = useToast();
    const taxAttachmentStore = useTaxAttachmentStore();
    const { attachments, isLoading } = storeToRefs(taxAttachmentStore);
    
    const showUploadDialog = ref(false);
    const isUploading = ref(false);
    const fileUpload = ref();
    
    const attachment = ref({
      tax_return_id: props.taxReturnId,
      file: null as File | null,
      description: '',
      document_type: ''
    });
    
    const errors = ref({
      file: '',
      description: '',
      document_type: ''
    });
    
    const maxFileSize = 10 * 1024 * 1024; // 10MB
    const allowedFileTypes = '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png';
    
    const documentTypes = [
      { label: 'Tax Return', value: 'tax_return' },
      { label: 'Receipt', value: 'receipt' },
      { label: 'Invoice', value: 'invoice' },
      { label: 'Statement', value: 'statement' },
      { label: 'Correspondence', value: 'correspondence' },
      { label: 'Other', value: 'other' }
    ];
    
    // Load attachments when component mounts
    onMounted(async () => {
      await loadAttachments();
    });
    
    // Watch for tax return ID changes
    // watch(() => props.taxReturnId, async (newVal) => {
    //   if (newVal) {
    //     await loadAttachments();
    //   }
    // });
    
    const loadAttachments = async () => {
      try {
        await taxAttachmentStore.fetchAttachments(props.taxReturnId);
      } catch (error) {
        console.error('Error loading attachments:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load attachments',
          life: 5000
        });
      }
    };
    
    const onFileSelect = (event: any) => {
      if (event.files && event.files.length > 0) {
        attachment.value.file = event.files[0];
        // Auto-fill description from filename if empty
        if (!attachment.value.description) {
          attachment.value.description = attachment.value.file.name
            .replace(/\.[^/.]+$/, '') // Remove extension
            .replace(/[_-]/g, ' ') // Replace underscores and hyphens with spaces
            .replace(/\b\w/g, l => l.toUpperCase()); // Capitalize first letter of each word
        }
      }
    };
    
    const validate = () => {
      let isValid = true;
      errors.value = { file: '', description: '', document_type: '' };
      
      if (!attachment.value.file) {
        errors.value.file = 'Please select a file';
        isValid = false;
      } else if (attachment.value.file.size > maxFileSize) {
        errors.value.file = `File size must be less than ${maxFileSize / (1024 * 1024)}MB`;
        isValid = false;
      }
      
      if (!attachment.value.description?.trim()) {
        errors.value.description = 'Description is required';
        isValid = false;
      }
      
      if (!attachment.value.document_type) {
        errors.value.document_type = 'Document type is required';
        isValid = false;
      }
      
      return isValid;
    };
    
    const uploadAttachment = async () => {
      if (!validate()) return;
      
      isUploading.value = true;
      
      try {
        const formData = new FormData();
        formData.append('file', attachment.value.file as Blob);
        formData.append('description', attachment.value.description);
        formData.append('document_type', attachment.value.document_type);
        
        await taxAttachmentStore.uploadAttachment(props.taxReturnId, formData);
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Attachment uploaded successfully',
          life: 3000
        });
        
        closeUploadDialog();
        await loadAttachments();
      } catch (error) {
        console.error('Error uploading attachment:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to upload attachment',
          life: 5000
        });
      } finally {
        isUploading.value = false;
      }
    };
    
    const downloadAttachment = async (attachment: Attachment) => {
      try {
        await taxAttachmentStore.downloadAttachment(attachment.id, attachment.filename);
      } catch (error) {
        console.error('Error downloading attachment:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to download attachment',
          life: 5000
        });
      }
    };
    
    const confirmDelete = (attachment: Attachment) => {
      confirm.require({
        message: `Are you sure you want to delete "${attachment.filename}"?`,
        header: 'Confirm Delete',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Delete',
        acceptClass: 'p-button-danger',
        accept: () => deleteAttachment(attachment.id)
      });
    };
    
    const deleteAttachment = async (id: string) => {
      try {
        await taxAttachmentStore.deleteAttachment(id);
        await loadAttachments();
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Attachment deleted successfully',
          life: 3000
        });
      } catch (error) {
        console.error('Error deleting attachment:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete attachment',
          life: 5000
        });
      }
    };
    
    const closeUploadDialog = () => {
      showUploadDialog.value = false;
      resetForm();
      if (fileUpload.value) {
        fileUpload.value.clear();
      }
    };
    
    const resetForm = () => {
      attachment.value = {
        tax_return_id: props.taxReturnId,
        file: null,
        description: '',
        document_type: ''
      };
      errors.value = { file: '', description: '', document_type: '' };
    };
    
    const getFileIcon = (filename: string) => {
      const extension = filename.split('.').pop()?.toLowerCase();
      
      switch (extension) {
        case 'pdf':
          return 'pi pi-file-pdf text-red-500';
        case 'doc':
        case 'docx':
          return 'pi pi-file-word text-blue-500';
        case 'xls':
        case 'xlsx':
          return 'pi pi-file-excel text-green-500';
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
          return 'pi pi-image text-amber-500';
        default:
          return 'pi pi-file text-gray-500';
      }
    };
    
    const formatDocumentType = (type: string) => {
      const docType = documentTypes.find(t => t.value === type);
      return docType ? docType.label : type;
    };
    
    const getDocumentTypeSeverity = (type: string) => {
      switch (type) {
        case 'tax_return':
          return 'primary';
        case 'receipt':
          return 'success';
        case 'invoice':
          return 'info';
        case 'statement':
          return 'warning';
        default:
          return 'contrast';
      }
    };
    
    const formatFileSize = (bytes: number) => {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleDateString();
    };
    
    return {
      showUploadDialog,
      isUploading,
      attachment,
      errors,
      attachments,
      isLoading,
      maxFileSize,
      allowedFileTypes,
      documentTypes,
      fileUpload,
      onFileSelect,
      uploadAttachment,
      downloadAttachment,
      confirmDelete,
      closeUploadDialog,
      getFileIcon,
      formatDocumentType,
      getDocumentTypeSeverity,
      formatFileSize,
      formatDate
    };
  }
});
</script>

<style scoped>
.tax-attachment-list {
  width: 100%;
}

:deep(.p-fileupload-choose) {
  width: 100%;
}

:deep(.p-fileupload-filename) {
  word-break: break-all;
}
</style>
