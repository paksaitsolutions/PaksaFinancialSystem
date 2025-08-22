<template>
  <div class="tax-filing-form">
    <form @submit.prevent="handleSubmit">
      <div class="grid">
        <!-- Basic Information -->
        <div class="col-12 md:col-6">
          <div class="card p-fluid">
            <h3>Basic Information</h3>
            
            <!-- Tax Type -->
            <div class="field">
              <label for="taxType">Tax Type <span class="required">*</span></label>
              <Dropdown
                id="taxType"
                v-model="formData.tax_type"
                :options="taxTypes"
                optionLabel="name"
                optionValue="code"
                placeholder="Select Tax Type"
                :class="{ 'p-invalid': errors.tax_type }"
              />
              <small v-if="errors.tax_type" class="p-error">{{ errors.tax_type[0] }}</small>
            </div>

            <!-- Jurisdiction -->
            <div class="field">
              <label for="jurisdiction">Jurisdiction <span class="required">*</span></label>
              <Dropdown
                id="jurisdiction"
                v-model="formData.jurisdiction_id"
                :options="jurisdictions"
                optionLabel="name"
                optionValue="id"
                placeholder="Select Jurisdiction"
                :class="{ 'p-invalid': errors.jurisdiction_id }"
                :loading="loadingJurisdictions"
                :filter="true"
              >
                <template #value="slotProps">
                  <div v-if="slotProps.value">
                    {{ getJurisdictionName(slotProps.value) }}
                  </div>
                  <span v-else>
                    {{ slotProps.placeholder }}
                  </span>
                </template>
                <template #option="slotProps">
                  <div>{{ slotProps.option.name }} ({{ slotProps.option.code }})</div>
                </template>
              </Dropdown>
              <small v-if="errors.jurisdiction_id" class="p-error">{{ errors.jurisdiction_id[0] }}</small>
            </div>

            <!-- Tax Period -->
            <div class="field">
              <label for="taxPeriod">Tax Period <span class="required">*</span></label>
              <Dropdown
                id="taxPeriod"
                v-model="formData.tax_period_id"
                :options="taxPeriods"
                optionLabel="name"
                optionValue="id"
                placeholder="Select Tax Period"
                :class="{ 'p-invalid': errors.tax_period_id }"
                :loading="loadingPeriods"
              >
                <template #value="slotProps">
                  <div v-if="slotProps.value">
                    {{ getPeriodName(slotProps.value) }}
              <small v-if="errors.tax_period_id" class="p-error">{{ errors.tax_period_id[0] }}</small>
            </div>

            <!-- Due Date -->
            <div class="field">
              <label for="dueDate">Due Date <span class="required">*</span></label>
              <Calendar
                id="dueDate"
                v-model="formData.due_date"
                :minDate="new Date()"
                dateFormat="yy-mm-dd"
                :showIcon="true"
                :class="{ 'p-invalid': errors.due_date }"
                :disabled="submitting"
              />
              <small v-if="errors.due_date" class="p-error">{{ errors.due_date[0] }}</small>
            </div>
          </div>

          <!-- Financial Information -->
          <div class="col-12 md:col-6">
            <div class="card p-fluid">
              <h3>Financial Information</h3>
              
              <!-- Currency -->
              <div class="field">
                <label for="currency">Currency <span class="required">*</span></label>
                <Dropdown
                  id="currency"
                  v-model="formData.currency"
                  :options="currencies"
                  optionLabel="name"
                  optionValue="code"
                  placeholder="Select Currency"
                  :class="{ 'p-invalid': errors.currency }"
                  :disabled="submitting"
                />
                <small v-if="errors.currency" class="p-error">{{ errors.currency[0] }}</small>
              </div>

              <!-- Tax Amount -->
              <div class="field">
                <label for="taxAmount">Tax Amount <span class="required">*</span></label>
                <InputNumber
                  id="taxAmount"
                  v-model="formData.tax_amount"
                  mode="currency"
                  :currency="formData.currency || 'USD'"
                  :minFractionDigits="2"
                  :maxFractionDigits="2"
                  :min="0"
                  :class="{ 'p-invalid': errors.tax_amount }"
                  :disabled="submitting || autoCalculate"
                />
                <small v-if="errors.tax_amount" class="p-error">{{ errors.tax_amount[0] }}</small>
              </div>

              <!-- Penalty Amount -->
              <div class="field">
                <label for="penaltyAmount">Penalty Amount</label>
                <InputNumber
                  id="penaltyAmount"
                  v-model="formData.penalty_amount"
                  mode="currency"
                  :currency="formData.currency || 'USD'"
                  :minFractionDigits="2"
                  :maxFractionDigits="2"
                  :min="0"
                  :class="{ 'p-invalid': errors.penalty_amount }"
                  :disabled="submitting"
                />
                <small v-if="errors.penalty_amount" class="p-error">{{ errors.penalty_amount[0] }}</small>
              </div>

              <!-- Interest Amount -->
              <div class="field">
                <label for="interestAmount">Interest Amount</label>
                <InputNumber
                  id="interestAmount"
                  v-model="formData.interest_amount"
                  mode="currency"
                  :currency="formData.currency || 'USD'"
                  :minFractionDigits="2"
                  :maxFractionDigits="2"
                  :min="0"
                  :class="{ 'p-invalid': errors.interest_amount }"
                  :disabled="submitting"
                />
                <small v-if="errors.interest_amount" class="p-error">{{ errors.interest_amount[0] }}</small>
              </div>

              <!-- Total Amount (Calculated) -->
              <div class="field">
                <label>Total Amount</label>
                <div class="p-inputgroup">
                  <span class="p-inputgroup-addon">
                    {{ getCurrencySymbol(formData.currency) }}
                  </span>
                  <InputText 
                    :value="formatCurrency(totalAmount, formData.currency)" 
                    disabled 
                    class="font-bold"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Notes & Attachments -->
          <div class="col-12">
            <div class="card">
              <h3>Notes & Attachments</h3>
              
              <!-- Notes -->
              <div class="field">
                <label for="notes">Notes</label>
                <Textarea
                  id="notes"
                  v-model="formData.notes"
                  :autoResize="true"
                  rows="3"
                  :disabled="submitting"
                />
                <small v-if="errors.notes" class="p-error">{{ errors.notes[0] }}</small>
              </div>

              <!-- Attachments -->
              <div class="field">
                <label>Attachments</label>
                <FileUpload 
                  mode="basic"
                  :multiple="true"
                  :auto="true"
                  :customUpload="true"
                  :maxFileSize="10000000"
                  :invalidFileSizeMessageSummary="'Invalid file size'"
                  invalidFileSizeMessageDetail="Maximum upload file size is 10MB"
                  :invalidFileTypeMessageSummary="'Invalid file type'"
                  invalidFileTypeMessageDetail="Invalid file type. Please upload a valid file."
                  :chooseLabel="$t('common.chooseFile')"
                  @select="onFileSelect"
                  class="w-full"
                >
                  <template #empty>
                    <div class="flex flex-column align-items-center">
                      <i class="pi pi-cloud-upload text-4xl text-500 mb-2"></i>
                      <p class="text-500">Drag and drop files here or click to browse</p>
                      <small class="text-500">Maximum file size: 10MB</small>
                    </div>
                  </template>
                </FileUpload>
                
                <!-- Uploaded Files -->
                <div v-if="attachments.length > 0" class="mt-3">
                  <div v-for="(file, index) in attachments" :key="index" class="p-3 border-round border-1 surface-border mb-2">
                    <div class="flex justify-content-between align-items-center">
                      <div class="flex align-items-center">
                        <i :class="getFileIcon(file.name)" class="mr-2"></i>
                        <span class="font-medium">{{ file.name }}</span>
                        <span class="text-500 ml-2">({{ formatFileSize(file.size) }})</span>
                      </div>
                      <Button 
                        icon="pi pi-times" 
                        class="p-button-text p-button-danger p-button-rounded p-button-sm" 
                        @click="removeAttachment(index)"
                      />
                    </div>
                    <ProgressBar 
                      v-if="file.progress < 100" 
                      :value="file.progress" 
                      class="mt-2"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="flex justify-content-end gap-2 mt-4">
          <Button 
            label="Cancel" 
            icon="pi pi-times" 
            class="p-button-text" 
            @click="$emit('cancel')" 
          />
          <Button 
            type="submit" 
            :label="isEditing ? 'Update' : 'Create'"
            :loading="submitting"
            :disabled="submitting"
          />
        </div>
      </div>
    </form>
  </div>
</div>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useTaxFilingStore } from '../store/filing';
import { useAuthStore } from '@/stores/auth';
import type { TaxFiling, TaxFilingCreate, TaxFilingAttachment } from '../types/filing';

const props = defineProps({
  filingId: {
    type: String,
    default: null
  },
  companyId: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['saved', 'cancel']);

// Services and Stores
const taxFilingStore = useTaxFilingStore();
const authStore = useAuthStore();
const toast = useToast();
const confirm = useConfirm();
const router = useRouter();

// State
interface TaxFilingFormData {
  company_id: string;
  tax_type: string;
  tax_period_id: string;
  jurisdiction_id: string;
  due_date: Date | null;
  currency: string;
  tax_amount: number;
  penalty_amount: number;
  interest_amount: number;
  notes: string;
}

const formData = ref<TaxFilingFormData>({
  company_id: props.companyId,
  tax_type: '',
  tax_period_id: '',
  jurisdiction_id: '',
  due_date: new Date(),
  currency: 'USD',
  tax_amount: 0,
  penalty_amount: 0,
  interest_amount: 0,
  notes: ''
});

const errors = ref<Record<string, string[]>>({});
const submitting = ref(false);
const isEditing = computed(() => !!props.filingId);

// Tax types
const taxTypes = ref([
  { code: 'income', name: 'Income Tax' },
  { code: 'sales', name: 'Sales Tax' },
  { code: 'vat', name: 'Value Added Tax (VAT)' },
  { code: 'withholding', name: 'Withholding Tax' },
  { code: 'property', name: 'Property Tax' },
  { code: 'excise', name: 'Excise Tax' },
  { code: 'customs', name: 'Customs Duty' },
]);

// Jurisdictions - will be loaded from API
interface Jurisdiction {
  id: string;
  name: string;
  code: string;
}

// Tax period interface
interface TaxPeriod {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
}

const jurisdictions = ref<Jurisdiction[]>([]);
const taxPeriods = ref<TaxPeriod[]>([]);

// Currencies
const currencies = ref([
  { code: 'USD', name: 'US Dollar', symbol: '$' },
  { code: 'PKR', name: 'Pakistani Rupee', symbol: '₨' },
  { code: 'SAR', name: 'Saudi Riyal', symbol: '﷼' },
  { code: 'AED', name: 'UAE Dirham', symbol: 'د.إ' },
  { code: 'EUR', name: 'Euro', symbol: '€' },
  { code: 'GBP', name: 'British Pound', symbol: '£' },
]);

// Load jurisdictions from API
const loadJurisdictions = async () => {
  try {
    loadingJurisdictions.value = true;
    // Replace with actual API call
    // const response = await fetch('/api/v1/tax/jurisdictions');
    // jurisdictions.value = await response.json();
    
    // Mock data for now
    jurisdictions.value = [
      { id: 'pk', name: 'Pakistan', code: 'PK' },
      { id: 'ksa', name: 'Saudi Arabia', code: 'KSA' },
      { id: 'uae', name: 'United Arab Emirates', code: 'UAE' },
      { id: 'us', name: 'United States', code: 'US' },
      { id: 'uk', name: 'United Kingdom', code: 'UK' },
    ];
  } catch (error) {
    console.error('Error loading jurisdictions:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load jurisdictions',
      life: 5000
    });
  } finally {
    loadingJurisdictions.value = false;
  }
};

// Load tax periods from API
const loadTaxPeriods = async () => {
  try {
    loadingPeriods.value = true;
    // Replace with actual API call
    // const response = await fetch('/api/v1/tax/periods');
    // taxPeriods.value = await response.json();
    
    // Mock data for now
    taxPeriods.value = [
      { id: '2023-q1', name: 'Q1 2023', start_date: '2023-01-01', end_date: '2023-03-31' },
      { id: '2023-q2', name: 'Q2 2023', start_date: '2023-04-01', end_date: '2023-06-30' },
      { id: '2023-q3', name: 'Q3 2023', start_date: '2023-07-01', end_date: '2023-09-30' },
      { id: '2023-q4', name: 'Q4 2023', start_date: '2023-10-01', end_date: '2023-12-31' },
      { id: '2024-q1', name: 'Q1 2024', start_date: '2024-01-01', end_date: '2024-03-31' },
    ];
  } catch (error) {
    console.error('Error loading tax periods:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load tax periods',
      life: 5000
    });
  } finally {
    loadingPeriods.value = false;
  }
};

// Ensure consistent typing with the imported TaxFilingAttachment type
type Attachment = Omit<TaxFilingAttachment, 'id' | 'file_name' | 'file_size' | 'file_type' | 'file_url'> & {
  id?: string;
  name: string;
  size: number;
  type: string;
  file?: File;
  progress: number;
  url?: string;
  attachment_type: 'supporting_document' | 'tax_return' | 'receipt' | 'other';
};

const attachments = ref<Attachment[]>([]);

const loadingJurisdictions = ref(false);
const loadingPeriods = ref(false);
const autoCalculate = ref(false);

// Computed
const totalAmount = computed(() => {
  const tax = formData.value.tax_amount || 0;
  const penalty = formData.value.penalty_amount || 0;
  const interest = formData.value.interest_amount || 0;
  return tax + penalty + interest;
});

const minDueDate = computed(() => {
  if (!formData.value.tax_period_id) return null;
  const period = taxPeriods.value.find(p => p.id === formData.value.tax_period_id);
  return period ? new Date(period.end_date) : null;
});

const maxDueDate = computed(() => {
  if (!formData.value.tax_period_id) return null;
  const period = taxPeriods.value.find(p => p.id === formData.value.tax_period_id);
  if (!period) return null;
  const dueDate = new Date(period.end_date);
  dueDate.setMonth(dueDate.getMonth() + 1); // 1 month after period end
  return dueDate;
});

// Methods
const getJurisdictionName = (id: string) => {
  const jurisdiction = jurisdictions.value.find(j => j.id === id);
  return jurisdiction ? `${jurisdiction.name} (${jurisdiction.code})` : '';
};

const getPeriodName = (id: string) => {
  const period = taxPeriods.value.find(p => p.id === id);
  return period ? `${period.name} (${formatDateRange(period)})` : '';
};

const getCurrencyName = (code: string) => {
  const currency = currencies.value.find(c => c.code === code);
  return currency ? `${currency.name} (${currency.symbol || currency.code})` : '';
};

const getCurrencySymbol = (code: string) => {
  const currency = currencies.value.find(c => c.code === code);
  return currency ? (currency.symbol || currency.code) : code;
};

const formatDateRange = (period: { start_date: string; end_date: string }) => {
  if (!period) return '';
  const start = new Date(period.start_date).toLocaleDateString();
  const end = new Date(period.end_date).toLocaleDateString();
  return `${start} - ${end}`;
};

const formatCurrency = (amount: number, currencyCode: string) => {
  if (amount === null || amount === undefined) return '';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currencyCode || 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
};

const getFileIcon = (fileName: string) => {
  const extension = fileName.split('.').pop()?.toLowerCase();
  switch (extension) {
    case 'pdf': return 'pi pi-file-pdf text-red-500';
    case 'doc':
    case 'docx': return 'pi pi-file-word text-blue-500';
    case 'xls':
    case 'xlsx': return 'pi pi-file-excel text-green-500';
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif': return 'pi pi-image text-purple-500';
    case 'zip':
    case 'rar':
    case '7z': return 'pi pi-file-archive text-amber-500';
    default: return 'pi pi-file text-gray-500';
  }
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const onFileSelect = async (event: { files: File[] }) => {
  if (!event?.files?.length) return;
  
  // Filter out files that are too large (10MB max)
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  const validFiles = event.files.filter(file => file.size <= MAX_FILE_SIZE);
  
  // Show error for files that are too large
  const oversizedFiles = event.files.filter(file => file.size > MAX_FILE_SIZE);
  if (oversizedFiles.length > 0) {
    const fileList = oversizedFiles.map(f => f.name).join(', ');
    toast.add({
      severity: 'warn',
      summary: 'File too large',
      detail: `The following files exceed the 10MB limit: ${fileList}`,
      life: 5000
    });
  }
  
  // Process valid files
  for (const file of validFiles) {
    // Check if file already exists
    if (attachments.value.some(a => a.name === file.name && a.size === file.size)) {
      toast.add({
        severity: 'warn',
        summary: 'File already added',
        detail: `The file ${file.name} has already been added.`,
        life: 3000
      });
      continue;
    }
    
    try {
      // Create a new attachment object
      const attachment = {
        id: undefined as string | undefined,
        name: file.name,
        size: file.size,
        type: file.type,
        file,
        progress: 0,
        attachment_type: 'supporting_document' as const,
        description: '',
        url: undefined as string | undefined
      };
      
      // Add to attachments array
      const index = attachments.value.push(attachment) - 1;
      
      // If this is an edit, upload the file immediately
      if (isEditing.value && props.filingId) {
        try {
          // Show upload in progress
          attachment.progress = 10;
          
          // Upload the file
          const { attachmentId } = await taxFilingStore.uploadAttachment(file, 'supporting_document');
          
          // Update attachment with ID from server
          attachment.id = attachmentId;
          attachment.progress = 50;
          
          // Confirm the attachment with the filing
          await taxFilingStore.confirmAttachment(attachmentId, props.filingId);
          
          // Update progress
          attachment.progress = 100;
          
          toast.add({
            severity: 'success',
            summary: 'Upload Complete',
            detail: `${file.name} has been uploaded successfully.`,
            life: 3000
          });
          
        } catch (error) {
          console.error('Error uploading file:', error);
          attachment.progress = -1; // Mark as failed
          
          toast.add({
            severity: 'error',
            summary: 'Upload Failed',
            detail: `Failed to upload ${file.name}. Please try again.`,
            life: 5000
          });
        }
      }
      
    } catch (error) {
      console.error('Error processing file:', file.name, error);
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: `Failed to process ${file.name}. Please try again.`,
        life: 5000
      });
    }
  }
};

const removeAttachment = async (index: number) => {
  const attachment = attachments.value[index];
  
  // If the attachment has an ID, it means it's already been saved to the server
  if (attachment.id) {
    try {
      await taxFilingStore.deleteAttachment(attachment.id);
      toast.add({
        severity: 'success',
        summary: 'Removed',
        detail: `${attachment.name} has been removed.`,
        life: 3000
      });
    } catch (error) {
      console.error('Error deleting attachment:', error);
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: `Failed to remove ${attachment.name}. Please try again.`,
        life: 5000
      });
      return; // Don't remove from UI if deletion failed
    }
  }
  
  // Remove from the attachments array
  attachments.value.splice(index, 1);
};

const validateForm = (): boolean => {
  const newErrors: Record<string, string[]> = {};
  
  if (!formData.value.tax_type) {
    newErrors.tax_type = ['Tax type is required'];
  }
  
  if (!formData.value.jurisdiction_id) {
    newErrors.jurisdiction_id = ['Jurisdiction is required'];
  }
  
  if (!formData.value.tax_period_id) {
    newErrors.tax_period_id = ['Tax period is required'];
  }
  
  if (!formData.value.due_date) {
    newErrors.due_date = ['Due date is required'];
  } else if (minDueDate.value && new Date(formData.value.due_date) < minDueDate.value) {
    newErrors.due_date = [`Due date cannot be before ${minDueDate.value.toLocaleDateString()}`];
  } else if (maxDueDate.value && new Date(formData.value.due_date) > maxDueDate.value) {
    newErrors.due_date = [`Due date cannot be after ${maxDueDate.value.toLocaleDateString()}`];
  }
  
  if (!formData.value.currency) {
    newErrors.currency = ['Currency is required'];
  }
  
  if (!formData.value.tax_amount || formData.value.tax_amount <= 0) {
    newErrors.tax_amount = ['Tax amount must be greater than 0'];
  }
  
  errors.value = newErrors;
  return Object.keys(newErrors).length === 0;
};

const handleSubmit = async () => {
  if (!validateForm()) {
    // Show the first error message to the user
    const firstError = Object.values(errors.value)[0]?.[0] || 'Please fill in all required fields correctly.';
    toast.add({
      severity: 'error',
      summary: 'Validation Error',
      detail: firstError,
      life: 5000
    });
    return;
  }
  
  submitting.value = true;
  
  try {
    // Get files to upload (new attachments)
    const filesToUpload = attachments.value
      .filter(a => a.file && !a.id)
      .map(a => a.file as File);
    
    // Prepare the payload
    const payload: TaxFilingCreate = {
      ...formData.value,
      total_amount: totalAmount.value,
      notes: formData.value.notes || undefined
    };
    
    let result: TaxFiling;
    
    if (isEditing.value && props.filingId) {
      // Update existing filing
      result = await taxFilingStore.updateFiling(
        props.filingId,
        payload,
        filesToUpload
      );
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Tax filing updated successfully',
        life: 3000
      });
    } else {
      // Create new filing
      result = await taxFilingStore.createFiling(
        payload,
        filesToUpload
      );
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Tax filing created successfully',
        life: 3000
      });
    }
    
    // Emit saved event with the result
    emit('saved', result);
    
  } catch (error: any) {
    console.error('Error saving tax filing:', error);
    
    if (error.response?.data?.errors) {
      // Handle validation errors
      errors.value = error.response.data.errors;
      
      toast.add({
        severity: 'error',
        summary: 'Validation Error',
        detail: 'Please check the form for errors.',
        life: 5000
      });
    } else {
      // Handle other errors
      const errorMessage = error.response?.data?.message || 'Failed to save tax filing. Please try again.';
      
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: errorMessage,
        life: 5000
      });
    }
    
    // Re-throw the error to be handled by the parent component if needed
    throw error;
  } finally {
    submitting.value = false;
  }
};

const loadFiling = async (id: string) => {
  try {
    // Fetch the filing from the store
    const filing = await taxFilingStore.fetchFilingById(id);
    
    if (!filing) {
      throw new Error('Filing not found');
    }
    
    // Update form data with proper type safety
    formData.value = {
      company_id: filing.company_id,
      tax_type: filing.tax_type,
      tax_period_id: filing.tax_period_id,
      jurisdiction_id: filing.jurisdiction_id,
      due_date: filing.due_date ? new Date(filing.due_date) : null,
      currency: filing.currency || 'USD',
      tax_amount: filing.tax_amount || 0,
      penalty_amount: filing.penalty_amount || 0,
      interest_amount: filing.interest_amount || 0,
      notes: filing.notes || ''
    };
    
    // Clear existing attachments
    attachments.value = [];
    
    // Safely handle attachments with proper typing
    const filingAttachments = Array.isArray((filing as any).attachments) 
      ? (filing as any).attachments 
      : [];
      
    if (filingAttachments.length > 0) {
      attachments.value = filingAttachments.map((a: Partial<TaxFilingAttachment>) => {
        const attachment: Attachment = {
          id: a.id,
          name: a.file_name || 'Unknown File',
          size: a.file_size || 0,
          type: a.file_type || 'application/octet-stream',
          url: a.file_url,
          progress: 100,
          attachment_type: (a.attachment_type as Attachment['attachment_type']) || 'supporting_document',
          description: a.description || ''
        };
        return attachment;
      });
    }
    
  } catch (error) {
    console.error('Error loading tax filing:', error);
    
    const errorMessage = error instanceof Error ? error.message : 'Failed to load tax filing';
    
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage,
      life: 5000
    });
    
    // Emit cancel to close the form or handle the error in the parent
    emit('cancel');
    
    // Re-throw the error to be handled by the parent component if needed
    throw error;
  }
};

// Lifecycle hooks
onMounted(async () => {
  try {
    // Load initial data
    await Promise.all([
      loadJurisdictions(),
      loadTaxPeriods()
    ]);
    
    // Load filing data if in edit mode
    if (props.filingId) {
      try {
        await loadFiling(props.filingId);
      } catch (error) {
        // Error is already handled in loadFiling
        console.error('Error in loadFiling:', error);
      }
    }
  } catch (error) {
    console.error('Error initializing form:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to initialize form. Please refresh the page and try again.',
      life: 5000
    });
  }
});

// Watch for changes to auto-calculate tax if needed
watch(
  () => [formData.value.tax_type, formData.value.jurisdiction_id, formData.value.tax_period_id], 
  async ([taxType, jurisdictionId, periodId]) => {
    if (autoCalculate.value && taxType && jurisdictionId && periodId) {
      try {
        // Here you would typically call an API to calculate the tax
        // For now, we'll just set a mock value
        formData.value = {
          ...formData.value,
          tax_amount: Math.random() * 10000
        };
      } catch (error) {
        console.error('Error calculating tax:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to calculate tax. Please enter the amount manually.',
          life: 5000
        });
      }
    }
  },
  { deep: true }
);
</script>

<style scoped>
.tax-filing-form {
  max-width: 1200px;
  margin: 0 auto;
}

.required {
  color: var(--red-500);
  font-weight: bold;
}

:deep(.p-card) {
  margin-bottom: 1.5rem;
}

:deep(.p-card .p-card-title) {
  font-size: 1.25rem;
  margin-bottom: 1rem;
  color: var(--primary-color);
}

:deep(.p-field) {
  margin-bottom: 1.25rem;
}

:deep(.p-inputtext),
:deep(.p-dropdown),
:deep(.p-calendar),
:deep(.p-inputnumber) {
  width: 100%;
}

:deep(.p-fileupload) {
  border: 1px dashed var(--surface-300);
  border-radius: 4px;
  padding: 1.5rem;
  background: var(--surface-50);
  transition: all 0.3s;
}

:deep(.p-fileupload:hover) {
  border-color: var(--primary-color);
  background: var(--surface-0);
}

:deep(.p-fileupload .p-button) {
  margin-right: 0.5rem;
}

:deep(.p-fileupload-file) {
  align-items: center;
  padding: 0.75rem;
  border-radius: 4px;
  background: var(--surface-0);
  border: 1px solid var(--surface-200);
  margin-bottom: 0.5rem;
}

:deep(.p-fileupload-file-thumbnail) {
  font-size: 1.5rem;
  margin-right: 0.75rem;
}

:deep(.p-fileupload-file-actions) {
  margin-left: auto;
}

:deep(.p-progressbar) {
  height: 6px;
  margin-top: 0.5rem;
  border-radius: 3px;
}

:deep(.p-progressbar .p-progressbar-value) {
  background: var(--primary-color);
}

:deep(.p-fileupload-file-size) {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  margin-left: 0.5rem;
}

:deep(.p-fileupload-file-badge) {
  display: none;
}

:deep(.p-fileupload-file-actions .p-button) {
  color: var(--text-color-secondary);
  background: transparent;
  border: none;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  transition: all 0.2s;
}

:deep(.p-fileupload-file-actions .p-button:hover) {
  background: var(--surface-100);
  color: var(--primary-color);
}

:deep(.p-fileupload-file-actions .p-button:focus) {
  box-shadow: none;
}

:deep(.p-fileupload-file-actions .p-button.p-button-danger) {
  color: var(--red-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-danger:hover) {
  background: var(--red-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-success) {
  color: var(--green-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-success:hover) {
  background: var(--green-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-warning) {
  color: var(--yellow-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-warning:hover) {
  background: var(--yellow-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-info) {
  color: var(--blue-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-info:hover) {
  background: var(--blue-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-help) {
  color: var(--purple-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-help:hover) {
  background: var(--purple-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-secondary) {
  color: var(--surface-600);
}

:deep(.p-fileupload-file-actions .p-button.p-button-secondary:hover) {
  background: var(--surface-100);
}

:deep(.p-fileupload-file-actions .p-button.p-button-success) {
  color: var(--green-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-success:hover) {
  background: var(--green-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-warning) {
  color: var(--yellow-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-warning:hover) {
  background: var(--yellow-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-danger) {
  color: var(--red-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-danger:hover) {
  background: var(--red-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-info) {
  color: var(--blue-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-info:hover) {
  background: var(--blue-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-help) {
  color: var(--purple-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-help:hover) {
  background: var(--purple-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-secondary) {
  color: var(--surface-600);
}

:deep(.p-fileupload-file-actions .p-button.p-button-secondary:hover) {
  background: var(--surface-100);
}

:deep(.p-fileupload-file-actions .p-button.p-button-success) {
  color: var(--green-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-success:hover) {
  background: var(--green-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-warning) {
  color: var(--yellow-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-warning:hover) {
  background: var(--yellow-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-danger) {
  color: var(--red-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-danger:hover) {
  background: var(--red-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-info) {
  color: var(--blue-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-info:hover) {
  background: var(--blue-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-help) {
  color: var(--purple-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-help:hover) {
  background: var(--purple-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-secondary) {
  color: var(--surface-600);
}

:deep(.p-fileupload-file-actions .p-button.p-button-secondary:hover) {
  background: var(--surface-100);
}

:deep(.p-fileupload-file-actions .p-button.p-button-success) {
  color: var(--green-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-success:hover) {
  background: var(--green-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-warning) {
  color: var(--yellow-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-warning:hover) {
  background: var(--yellow-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-danger) {
  color: var(--red-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-danger:hover) {
  background: var(--red-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-info) {
  color: var(--blue-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-info:hover) {
  background: var(--blue-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-help) {
  color: var(--purple-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-help:hover) {
  background: var(--purple-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-secondary) {
  color: var(--surface-600);
}

:deep(.p-fileupload-file-actions .p-button.p-button-secondary:hover) {
  background: var(--surface-100);
}

:deep(.p-fileupload-file-actions .p-button.p-button-success) {
  color: var(--green-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-success:hover) {
  background: var(--green-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-warning) {
  color: var(--yellow-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-warning:hover) {
  background: var(--yellow-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-danger) {
  color: var(--red-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-danger:hover) {
  background: var(--red-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-info) {
  color: var(--blue-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-info:hover) {
  background: var(--blue-50);
}

:deep(.p-fileupload-file-actions .p-button.p-button-help) {
  color: var(--purple-500);
}

:deep(.p-fileupload-file-actions .p-button.p-button-help:hover) {
  background: var(--purple-50);
}
