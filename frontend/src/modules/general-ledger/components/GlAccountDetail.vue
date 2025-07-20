<template>
  <div class="gl-account-detail">
    <!-- Account Header -->
    <div class="flex justify-content-between align-items-center mb-4">
      <h1>{{ pageTitle }}</h1>
      <div class="flex gap-2">
        <Button 
          label="Back" 
          icon="pi pi-arrow-left" 
          class="p-button-text" 
          @click="$router.go(-1)" 
        />
        <Button 
          v-if="!isNew"
          label="Print" 
          icon="pi pi-print" 
          class="p-button-text" 
          @click="handlePrint" 
        />
        <Button 
          v-if="!isNew"
          label="Export" 
          icon="pi pi-download" 
          class="p-button-text" 
          @click="handleExport" 
        />
        <Button 
          v-if="canDelete"
          label="Delete" 
          icon="pi pi-trash" 
          class="p-button-text p-button-danger" 
          @click="confirmDelete" 
        />
        <Button 
          label="Save" 
          icon="pi pi-save" 
          :loading="saving" 
          @click="saveAccount" 
        />
      </div>
    </div>

    <ProgressBar v-if="loading" mode="indeterminate" style="height: 6px" />

    <div v-else class="grid">
      <!-- Main Form -->
      <div class="col-12 md:col-8">
        <Card>
          <template #title>Account Information</template>
          <template #content>
            <form ref="formRef" @submit.prevent="saveAccount">
              <div class="grid">
                <!-- Account Number -->
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="accountNumber">Account Number <span class="text-red-500">*</span></label>
                    <InputText
                      id="accountNumber"
                      v-model="formData.accountNumber"
                      :class="{ 'p-invalid': v$.accountNumber.$error }"
                      :disabled="!isNew"
                      @blur="v$.accountNumber.$touch()"
                    />
                    <small v-if="v$.accountNumber.$error" class="p-error">
                      {{ v$.accountNumber.$errors[0]?.$message }}
                    </small>
                  </div>
                </div>

                <!-- Account Name -->
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="name">Account Name <span class="text-red-500">*</span></label>
                    <InputText
                      id="name"
                      v-model="formData.name"
                      :class="{ 'p-invalid': v$.name.$error }"
                      @blur="v$.name.$touch()"
                    />
                    <small v-if="v$.name.$error" class="p-error">
                      {{ v$.name.$errors[0]?.$message }}
                    </small>
                  </div>
                </div>

                <!-- Account Type -->
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="accountType">Account Type <span class="text-red-500">*</span></label>
                    <Dropdown
                      id="accountType"
                      v-model="formData.accountType"
                      :options="accountTypes"
                      option-label="label"
                      option-value="value"
                      :class="{ 'p-invalid': v$.accountType.$error }"
                      :loading="loading"
                      placeholder="Select Account Type"
                      @change="updateAccountType(formData.accountType)"
                    />
                    <small v-if="v$.accountType.$error" class="p-error">
                      {{ v$.accountType.$errors[0]?.$message }}
                    </small>
                  </div>
                </div>

                <!-- Account Category -->
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="accountCategory">Account Category <span class="text-red-500">*</span></label>
                    <Dropdown
                      id="accountCategory"
                      v-model="formData.accountCategory"
                      :options="accountCategories"
                      option-label="label"
                      option-value="value"
                      :class="{ 'p-invalid': v$.accountCategory.$error }"
                      :loading="loading"
                      placeholder="Select Account Category"
                    />
                    <small v-if="v$.accountCategory.$error" class="p-error">
                      {{ v$.accountCategory.$errors[0]?.$message }}
                    </small>
                  </div>
                </div>

                <!-- Parent Account -->
                <div class="col-12">
                  <div class="field">
                    <label for="parentAccount">Parent Account</label>
                    <Dropdown
                      id="parentAccount"
                      v-model="formData.parentAccountId"
                      :options="parentAccountOptions"
                      option-label="label"
                      option-value="value"
                      :loading="loadingAccounts"
                      :disabled="!formData.accountType"
                      placeholder="Select Parent Account"
                      :filter="true"
                      filter-placeholder="Search accounts..."
                      filter-input-auto-focus="true"
                      :show-clear="true"
                    />
                    <small v-if="v$.parentAccountId.$error" class="p-error">
                      {{ v$.parentAccountId.$errors[0]?.$message }}
                    </small>
                  </div>
                </div>

                <!-- Description -->
                <div class="col-12">
                  <div class="field">
                    <label for="description">Description</label>
                    <Textarea
                      id="description"
                      v-model="formData.description"
                      :auto-resize="true"
                      rows="3"
                    />
                  </div>
                </div>

                <!-- Currency and Status -->
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="currency">Currency <span class="text-red-500">*</span></label>
                    <Dropdown
                      id="currency"
                      v-model="formData.currency"
                      :options="currencies"
                      option-label="name"
                      option-value="code"
                      placeholder="Select Currency"
                      :loading="loadingCurrencies"
                    />
                  </div>
                </div>

                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="status">Status</label>
                    <Dropdown
                      id="status"
                      v-model="formData.status"
                      :options="accountStatuses"
                      option-label="label"
                      option-value="value"
                      placeholder="Select Status"
                    />
                  </div>
                </div>

                <!-- Toggle Options -->
                <div class="col-12 md:col-6">
                  <div class="field-checkbox">
                    <Checkbox
                      id="isDetailAccount"
                      v-model="formData.isDetailAccount"
                      :binary="true"
                    />
                    <label for="isDetailAccount">Is Detail Account (Allows Posting)</label>
                  </div>
                </div>

                <div class="col-12 md:col-6">
                  <div class="field-checkbox">
                    <Checkbox
                      id="isLocked"
                      v-model="formData.isLocked"
                      :binary="true"
                      :disabled="!formData.id"
                    />
                    <label for="isLocked">Lock Account (Prevent Modifications)</label>
                  </div>
                </div>

                <!-- Opening Balance -->
                <div v-if="isNew" class="col-12">
                  <div class="field">
                    <label for="openingBalance">Opening Balance</label>
                    <InputNumber
                      id="openingBalance"
                      v-model="formData.openingBalance"
                      mode="currency"
                      :currency="formData.currency || 'PKR'"
                      :min-fraction-digits="2"
                      :max-fraction-digits="4"
                    />
                  </div>
                </div>
              </div>
            </form>
          </template>
        </Card>

        <!-- Custom Fields Section -->
        <Card v-if="customFields.length > 0" class="mt-4">
          <template #title>Custom Fields</template>
          <template #content>
            <div class="grid">
              <div 
                v-for="field in customFields" 
                :key="field.id"
                class="col-12 md:col-6"
              >
                <div class="field">
                  <label :for="`custom-${field.id}`">
                    {{ field.name }}
                    <span v-if="field.required" class="text-red-500">*</span>
                  </label>
                  <InputText
                    v-if="field.type === 'text'"
                    :id="`custom-${field.id}`"
                    v-model="field.value"
                    :required="field.required"
                    class="w-full"
                  />
                  <Textarea
                    v-else-if="field.type === 'textarea'"
                    :id="`custom-${field.id}`"
                    v-model="field.value"
                    :required="field.required"
                    :auto-resize="true"
                    rows="3"
                    class="w-full"
                  />
                  <InputNumber
                    v-else-if="field.type === 'number'"
                    :id="`custom-${field.id}`"
                    v-model="field.value"
                    :required="field.required"
                    class="w-full"
                  />
                  <Checkbox
                    v-else-if="field.type === 'boolean'"
                    :id="`custom-${field.id}`"
                    v-model="field.value"
                    :binary="true"
                    :required="field.required"
                  />
                  <Calendar
                    v-else-if="field.type === 'date'"
                    :id="`custom-${field.id}`"
                    v-model="field.value"
                    :required="field.required"
                    class="w-full"
                    date-format="yy-mm-dd"
                    show-icon
                  />
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Sidebar -->
      <div class="col-12 md:col-4">
        <!-- Account Summary -->
        <Card class="mb-4">
          <template #title>Account Summary</template>
          <template #content>
            <div v-if="!isNew" class="flex flex-column gap-3">
              <div class="flex justify-content-between">
                <span class="font-medium">Account Number:</span>
                <span>{{ formData.accountNumber }}</span>
              </div>
              <div class="flex justify-content-between">
                <span class="font-medium">Type:</span>
                <Tag :value="formData.accountType" />
              </div>
              <div class="flex justify-content-between">
                <span class="font-medium">Status:</span>
                <Tag 
                  :value="formData.status" 
                  :severity="formData.status === 'active' ? 'success' : 'danger'"
                />
              </div>
              <div class="flex justify-content-between">
                <span class="font-medium">Created:</span>
                <span>{{ formatDate(new Date().toISOString()) }}</span>
              </div>
              <div class="flex justify-content-between">
                <span class="font-medium">Last Updated:</span>
                <span>{{ formatDate(new Date().toISOString()) }}</span>
              </div>
              <div class="flex justify-content-between">
                <span class="font-medium">Balance:</span>
                <span class="font-bold">
                  {{ formData.currency || 'PKR' }} {{ formData.openingBalance || '0.00' }}
                </span>
              </div>
            </div>
            <div v-else class="text-center p-4">
              <i class="pi pi-info-circle text-2xl mb-2"></i>
              <p>Account details will be displayed here after saving.</p>
            </div>
          </template>
        </Card>

        <!-- Activity Log -->
        <Card v-if="!isNew" class="mb-4">
          <template #title>
            <div class="flex align-items-center justify-content-between">
              <span>Recent Activity</span>
              <Button 
                icon="pi pi-refresh" 
                class="p-button-text p-button-sm" 
                :loading="loadingActivity"
                @click="loadActivityLogs"
              />
            </div>
          </template>
          <template #content>
            <div v-if="activityLogs.length > 0" class="flex flex-column gap-3">
              <div v-for="log in activityLogs" :key="log.id" class="border-bottom-1 surface-border pb-3">
                <div class="flex justify-content-between">
                  <span class="font-medium">{{ log.action }}</span>
                  <span class="text-500 text-sm">{{ formatDate(log.timestamp) }}</span>
                </div>
                <p class="text-sm mb-1">{{ log.details }}</p>
                <span class="text-500 text-xs">By {{ log.user }}</span>
              </div>
            </div>
            <div v-else class="text-center p-3">
              <p>No activity found</p>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Export Dialog -->
    <ReportExportDialog 
      ref="exportDialog"
      @export="handleExportConfirm"
    />

    <!-- Confirm Dialog -->
    <ConfirmDialog />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed, onMounted, PropType } from 'vue';
import { useRouter } from 'vue-router';
import { useVuelidate } from '@vuelidate/core';
import { required, maxLength, helpers } from '@vuelidate/validators';
import { useConfirm } from 'primevue/useconfirm';
import { useGlAccountStore } from '../store/gl-account.store';
import { useGlCategoryStore } from '../store/gl-category.store';
import { useNotification } from '@/shared/composables/useNotification';
import { formatDate } from '@/shared/utils/date-utils';
import ReportExportDialog from '@/shared/components/ReportExportDialog.vue';
import type { AxiosResponse } from 'axios';

// Import types and constants
import type { 
  GlAccount, 
  CreateGlAccountDto, 
  UpdateGlAccountDto,
  AccountType,
  AccountCategory,
  AccountStatus
} from '../types/gl-account';

import {
  ACCOUNT_TYPES,
  ACCOUNT_CATEGORIES,
  ACCOUNT_STATUS,
  ACCOUNT_TYPE_CATEGORIES,
  DEFAULT_GL_ACCOUNT,
  VALIDATION_MESSAGES
} from '../types/gl-account-constants';

// Type for form data
interface GlAccountFormData extends Omit<CreateGlAccountDto, 'id' | 'createdAt' | 'updatedAt'> {
  id?: string;
  parentAccount?: GlAccount | null;
  customFields?: Record<string, any>;
}

// Type for export formats
interface ExportFormat {
  label: string;
  value: string;
  icon: string;
}

// Type for dropdown options
interface DropdownOption {
  label: string;
  value: string;
}

// Import glAccountService for export functionality
import { glAccountService } from '../services/gl-account.service';

export default defineComponent({
  name: 'GlAccountDetail',
  components: {
    ReportExportDialog,
  },
  props: {
    id: {
      type: String,
      default: '',
    },
    parentAccountId: {
      type: String,
      default: null,
    },
    defaultAccountType: {
      type: String as PropType<AccountType>,
      default: ACCOUNT_TYPES.ASSET,
    },
  },
  setup(props, { emit }) {
    const router = useRouter();
    const glAccountStore = useGlAccountStore();
    const glCategoryStore = useGlCategoryStore();
    const confirm = useConfirm();
    const { showSuccess, showError } = useNotification();
    
    // Refs
    const isNew = computed(() => !props.id);
    const loading = ref(false);
    const saving = ref(false);
    const loadingAccounts = ref(false);
    const loadingCurrencies = ref(false);
    const loadingActivity = ref(false);
    const exportDialog = ref<InstanceType<typeof ReportExportDialog> | null>(null);
    const formRef = ref<HTMLFormElement | null>(null);

    // Form state
    const formData = reactive<GlAccountFormData>({
      ...DEFAULT_GL_ACCOUNT,
      accountType: props.defaultAccountType,
      parentAccountId: props.parentAccountId || null,
    });

    // Data options
    const currencies = ref([
      { code: 'PKR', name: 'Pakistani Rupee' },
      { code: 'USD', name: 'US Dollar' },
      { code: 'EUR', name: 'Euro' },
      { code: 'GBP', name: 'British Pound' },
      { code: 'AED', name: 'UAE Dirham' },
      { code: 'SAR', name: 'Saudi Riyal' },
    ]);

    const accountTypes = computed<DropdownOption[]>(() => 
      Object.entries(ACCOUNT_TYPES).map(([key, value]) => ({
        label: key.charAt(0).toUpperCase() + key.slice(1).toLowerCase(),
        value,
      }))
    );

    const accountStatuses = computed<DropdownOption[]>(() => 
      Object.entries(ACCOUNT_STATUS).map(([key, value]) => ({
        label: key.split('_').map(word => word.charAt(0) + word.slice(1).toLowerCase()).join(' '),
        value,
      }))
    );
    
    const accountCategories = computed<DropdownOption[]>(() => {
      const type = formData.accountType;
      const categories = ACCOUNT_TYPE_CATEGORIES[type] || [];
      
      return categories.map(category => {
        const key = Object.entries(ACCOUNT_CATEGORIES).find(([_, value]) => value === category)?.[0] || '';
        return {
          label: key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' '),
          value: category,
        };
      });
    });

    const parentAccountOptions = ref<Array<{ label: string; value: string; data: any }>>([]);
    const activityLogs = ref<Array<{ id: string; action: string; timestamp: string; user: string; details: string }>>([]);
    const customFields = ref<Array<{ id: string; name: string; type: string; value: any; required: boolean }>>([]);
    
    const exportFormats = ref<ExportFormat[]>([
      { label: 'PDF', value: 'pdf', icon: 'pi pi-file-pdf' },
      { label: 'Excel', value: 'xlsx', icon: 'pi pi-file-excel' },
      { label: 'CSV', value: 'csv', icon: 'pi pi-file' },
      { label: 'JSON', value: 'json', icon: 'pi pi-code' },
    ]);

    // Validation rules
    const rules = {
      accountNumber: { 
        required: helpers.withMessage(VALIDATION_MESSAGES.ACCOUNT_NUMBER_REQUIRED, required),
        maxLength: helpers.withMessage(VALIDATION_MESSAGES.ACCOUNT_NUMBER_LENGTH, maxLength(ACCOUNT_NUMBER_RULES.MAX_LENGTH)),
        validFormat: helpers.withMessage(
          VALIDATION_MESSAGES.ACCOUNT_NUMBER_INVALID,
          (value: string) => ACCOUNT_NUMBER_RULES.ALLOWED_CHARS.test(value)
        ),
      },
      name: { 
        required: helpers.withMessage(VALIDATION_MESSAGES.NAME_REQUIRED, required),
        maxLength: helpers.withMessage(VALIDATION_MESSAGES.NAME_LENGTH, maxLength(100)),
      },
      accountType: { 
        required: helpers.withMessage(VALIDATION_MESSAGES.ACCOUNT_TYPE_REQUIRED, required),
      },
      accountCategory: {
        required: helpers.withMessage(VALIDATION_MESSAGES.ACCOUNT_CATEGORY_REQUIRED, required),
        validCategory: helpers.withMessage(
          'Selected category is not valid for the account type',
          (value: string) => {
            const validCategories = ACCOUNT_TYPE_CATEGORIES[formData.accountType] || [];
            return validCategories.includes(value as AccountCategory);
          }
        ),
      },
      parentAccountId: {
        // Custom validator to prevent circular references
        isValidParent: helpers.withMessage(
          'Cannot select a descendant account as parent',
          (value: string | null) => {
            if (!value) return true;
            // Add logic to check for circular references
            return true;
          }
        ),
      },
    };

    const v$ = useVuelidate(rules, formData);

    // Methods
    const loadAccount = async () => {
      if (!props.id) return;
      
      loading.value = true;
      try {
        // Use fetchAccountById to get the account details
        const account = await glAccountStore.fetchAccountById(props.id);
        
        // Update form data with account details
        Object.assign(formData, {
          id: account.id,
          accountNumber: account.accountNumber,
          name: account.name,
          description: account.description,
          accountType: account.accountType,
          accountCategory: account.accountCategory,
          parentAccountId: account.parentAccountId,
          status: account.status,
          isDetailAccount: account.isDetailAccount,
          currency: account.currency,
          isLocked: account.isLocked,
          sortOrder: account.sortOrder,
          openingBalance: account.openingBalance,
          customFields: { ...account.customFields },
        });
        
        // Load parent account details if exists
        if (account.parentAccountId) {
          await loadParentAccount(account.parentAccountId);
        }
        
        // Load additional data if needed
        if (!isNew.value) {
          await Promise.all([
            loadActivityLogs(),
            loadCustomFields(),
          ]);
        }
      } catch (error) {
        console.error('Error loading account:', error);
        showError('Failed to load account details. Please try again.');
      } finally {
        loading.value = false;
      }
    };
    
    const loadParentAccount = async (parentId: string) => {
      if (!parentId) return;
      
      try {
        const parent = await glAccountStore.fetchAccountById(parentId);
        formData.parentAccount = parent;
      } catch (error) {
        console.warn('Failed to load parent account details:', error);
      }
    };
    
    const loadParentAccountOptions = async (query?: string) => {
      loadingAccounts.value = true;
      try {
        const filters = {
          isActive: true,
          searchTerm: query || '',
          excludeId: formData.id, // Exclude current account from parent options
        };
        
        const response = await glAccountStore.fetchAccounts(filters);
        
        // Format options for TreeSelect
        parentAccountOptions.value = response.data.map(account => ({
          label: `${account.accountNumber} - ${account.name}`,
          value: account.id,
          data: account,
        }));
      } catch (error) {
        console.error('Error loading parent accounts:', error);
        showError('Failed to load parent account options');
      } finally {
        loadingAccounts.value = false;
      }
    };
    
    const loadActivityLogs = async () => {
      if (!formData.id) return;
      
      loadingActivity.value = true;
      try {
        // TODO: Implement activity log fetching from API
        // This is a mock implementation
        activityLogs.value = [
          {
            id: '1',
            action: 'Created',
            timestamp: new Date().toISOString(),
            user: 'System',
            details: 'Account was created',
          },
        ];
      } catch (error) {
        console.error('Error loading activity logs:', error);
      } finally {
        loadingActivity.value = false;
      }
    };
    
    const loadCustomFields = async () => {
      if (!formData.id) return;
      
      try {
        // TODO: Implement custom fields fetching from API
        // This is a mock implementation
        customFields.value = [
          {
            id: 'tax_code',
            name: 'Tax Code',
            type: 'text',
            value: '',
            required: false,
          },
        ];
      } catch (error) {
        console.error('Error loading custom fields:', error);
      }
    };
    
    const saveAccount = async () => {
      // Validate form
      const isValid = await v$.value.$validate();
      if (!isValid) {
        showError('Please fix the validation errors before saving.');
        return false;
      }
      
      saving.value = true;
      try {
        let savedAccount: GlAccount;
        
        if (isNew.value) {
          // Create new account
          const createDto: CreateGlAccountDto = {
            ...formData,
            // Ensure we don't send undefined values
            parentAccountId: formData.parentAccountId || null,
            description: formData.description || '',
            customFields: formData.customFields || {},
          };
          
          savedAccount = await glAccountStore.createAccount(createDto);
          showSuccess('Account created successfully');
          
          // Redirect to edit page
          router.push({ 
            name: 'gl-account-detail', 
            params: { id: savedAccount.id } 
          });
        } else {
          // Update existing account
          if (!formData.id) throw new Error('Account ID is required for update');
          
          const updateDto: UpdateGlAccountDto = {
            ...formData,
            id: formData.id,
            // Ensure we don't send undefined values
            parentAccountId: formData.parentAccountId || null,
            description: formData.description || '',
            customFields: formData.customFields || {},
          };
          
          savedAccount = await glAccountStore.updateAccount(formData.id, updateDto);
          showSuccess('Account updated successfully');
        }
        
        // Reload the account to get fresh data
        await loadAccount();
        
        return true;
      } catch (error) {
        console.error('Error saving account:', error);
        showError(`Failed to save account: ${error.message || 'Unknown error'}`);
        return false;
      } finally {
        saving.value = false;
      }
    };
    
    const confirmDelete = () => {
      if (!formData.id) return;
      
      confirm.require({
        message: 'Are you sure you want to delete this account? This action cannot be undone.',
        header: 'Confirm Deletion',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        accept: () => deleteAccount(),
      });
    };
    
    const deleteAccount = async () => {
      if (!formData.id) return false;
      
      try {
        await glAccountStore.deleteAccount(formData.id);
        showSuccess('Account deleted successfully');
        
        // Navigate back to accounts list
        router.push({ name: 'gl-accounts' });
        return true;
      } catch (error) {
        console.error('Error deleting account:', error);
        showError(`Failed to delete account: ${error.message || 'Unknown error'}`);
        return false;
      }
    };
    
    const handlePrint = () => {
      window.print();
    };
    
    const handleExport = () => {
      if (!exportDialog.value) return;
      
      exportDialog.value.show({
        title: 'Export Account Data',
        formats: exportFormats.value,
      });
    };
    
    const handleExportConfirm = async (format: string) => {
      try {
        if (!formData.id) return;
        
        // Trigger export based on selected format
        let data: any;
        let filename = `gl-account-${formData.accountNumber}-${new Date().toISOString().split('T')[0]}`;
        
        switch (format) {
          case 'pdf':
            // TODO: Implement PDF export
            data = await glAccountService.exportAccountPdf(formData.id);
            filename += '.pdf';
            break;
            
          case 'xlsx':
            data = await glAccountService.exportAccountExcel(formData.id);
            filename += '.xlsx';
            break;
            
          case 'csv':
            data = await glAccountService.exportAccountCsv(formData.id);
            filename += '.csv';
            break;
            
          case 'json':
            data = await glAccountService.exportAccountJson(formData.id);
            filename += '.json';
            break;
            
          default:
            throw new Error(`Unsupported export format: ${format}`);
        }
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        
        // Cleanup
        if (link.parentNode) {
          link.parentNode.removeChild(link);
        }
        window.URL.revokeObjectURL(url);
        
        showSuccess(`Account data exported successfully as ${format.toUpperCase()}`);
      } catch (error) {
        console.error('Export error:', error);
        showError(`Failed to export account data: ${error.message || 'Unknown error'}`);
      }
    };
    
    const updateAccountType = (newType: AccountType) => {
      // Reset category if not valid for the new type
      if (formData.accountCategory && ACCOUNT_TYPE_CATEGORIES[newType]) {
        const validCategories = ACCOUNT_TYPE_CATEGORIES[newType];
        if (!validCategories.includes(formData.accountCategory as AccountCategory)) {
          formData.accountCategory = validCategories[0] || '';
        }
      }
      
      // Load parent accounts for the new type
      loadParentAccountOptions();
    };
    
    // Lifecycle hooks
    onMounted(async () => {
      await Promise.all([
        loadAccount(),
        loadParentAccountOptions(),
      ]);
    });
    
    // Computed properties
    const pageTitle = computed(() => {
      return isNew.value 
        ? 'New GL Account' 
        : `GL Account: ${formData.accountNumber} - ${formData.name}`;
    });
    
    const isFormDirty = computed(() => {
      return v$.value.$dirty;
    });
    
    const canEdit = computed(() => {
      return !formData.isLocked && !formData.isSystemAccount;
    });
    
    const canDelete = computed(() => {
      return !isNew.value && canEdit.value && !formData.isSystemAccount;
    });
    
    // Return template bindings
    return {
      // Refs
      loading,
      saving,
      loadingAccounts,
      loadingCurrencies,
      loadingActivity,
      exportDialog,
      formRef,
      
      // Data
      formData,
      currencies,
      accountTypes,
      accountStatuses,
      accountCategories,
      parentAccountOptions,
      activityLogs,
      customFields,
      exportFormats,
      
      // Computed
      isNew,
      pageTitle,
      isFormDirty,
      canEdit,
      canDelete,
      
      // Methods
      v$,
      saveAccount,
      confirmDelete,
      handlePrint,
      handleExport,
      handleExportConfirm,
      updateAccountType,
      loadParentAccountOptions,
      formatDate,
    };
        if (account) {
          const { 
            accountNumber,
            name,
            accountType,
            accountCategory,
            parentAccountId,
            currency,
            status,
            description,
            isDetailAccount,
            isSystemAccount,
            isLocked,
            level,
            sortOrder,
            openingBalance,
            currentBalance,
            yearToDateBalance,
            taxCode,
            costCenter,
            departmentId,
            projectCode,
            notes,
            tags,
            customFields
          } = account as GlAccount;
          
          // Assign values to formState individually to ensure type safety
          formState.accountNumber = accountNumber || '';
          formState.name = name || '';
          formState.accountType = accountType as AccountType;
          formState.accountCategory = accountCategory as AccountCategory;
          formState.parentAccountId = parentAccountId || null;
          formState.currency = currency || 'PKR';
          formState.status = status as AccountStatus;
          formState.description = description || '';
          formState.isDetailAccount = isDetailAccount || false;
          formState.isSystemAccount = isSystemAccount || false;
          formState.isLocked = isLocked || false;
          formState.level = level || 0;
          formState.sortOrder = sortOrder || 0;
          formState.openingBalance = openingBalance || 0;
          formState.currentBalance = currentBalance || 0;
          formState.yearToDateBalance = yearToDateBalance || 0;
          formState.balanceAsOf = new Date();
          formState.taxCode = taxCode || null;
          formState.costCenter = costCenter || null;
          formState.departmentId = departmentId || null;
          formState.projectCode = projectCode || null;
          formState.notes = notes || null;
          formState.tags = tags || [];
          formState.customFields = customFields || {};
          formData.taxCode = taxCode || null;
          formData.costCenter = costCenter || null;
          formData.departmentId = departmentId || null;
          formData.projectCode = projectCode || null;
          formData.notes = notes || null;
          formData.tags = tags || [];
          formData.customFields = customFields || {};
        }
      } catch (err: unknown) {
        const error = err as { response?: { status?: number } };
        showError('Failed to load GL Account');
        console.error('Error loading GL Account:', error);
        
        // Handle 404 error by redirecting to accounts list
        if (error?.response?.status === 404) {
          router.push({ name: 'gl-accounts' });
        }
      } finally {
        loading.value = false;
      }
    };

    const loadAccountCategories = async () => {
      try {
        const categories = await glCategoryStore.fetchCategories();
        accountCategories.value = categories.map((cat: { name: string; id: string }) => ({
          label: cat.name,
          value: cat.id,
        }));
      } catch (error) {
        console.error('Failed to load account categories', error);
      }
    };

    const loadParentAccounts = async () => {
      if (loadingAccounts.value) return;
      
      loadingAccounts.value = true;
      try {
        const filters: GlAccountFilters = {
          sortBy: 'accountNumber',
          sortOrder: 'asc',
          isDetailAccount: true,
          status: 'active'
        };
        
        const response = await glAccountStore.fetchAccounts(filters);
        
        parentAccountOptions.value = Array.isArray(response) 
          ? response.map((acc: GlAccount) => ({
              label: `${acc.accountNumber} - ${acc.name}`,
              value: acc.id,
              data: acc,
            }))
          : [];
      } catch (error) {
        console.error('Failed to load parent accounts', error);
      } finally {
        loadingAccounts.value = false;
      }
    };

    const loadCurrencies = async () => {
      loadingCurrencies.value = true;
      try {
        // Mock currency data since fetchCurrencies doesn't exist
        const mockCurrencies = [
          { code: 'USD', name: 'US Dollar' },
          { code: 'PKR', name: 'Pakistani Rupee' },
          { code: 'EUR', name: 'Euro' },
          { code: 'GBP', name: 'British Pound' },
          { code: 'AED', name: 'UAE Dirham' },
          { code: 'SAR', name: 'Saudi Riyal' },
        ];
        
        currencies.value = mockCurrencies;
      } catch (error) {
        console.error('Failed to load currencies', error);
      } finally {
        loadingCurrencies.value = false;
      }
    };

    // Activity logs functionality will be implemented in a future update
    // This is a no-op function to satisfy TypeScript
    const loadActivityLogs = (): Promise<void> => {
      return new Promise((resolve) => {
        // Implementation will be added later
        resolve();
      });
    };

    const loadCustomFields = async () => {
      try {
        // Fetch custom fields configuration from the API or settings
        // This is a mock implementation - replace with actual API call
        const fields = await new Promise<any[]>((resolve) => {
          setTimeout(() => {
            resolve([
              {
                id: 'costCenter',
                label: 'Cost Center',
                type: 'text',
                required: false,
              },
              {
                id: 'department',
                label: 'Department',
                type: 'dropdown',
                options: [
                  { label: 'Finance', value: 'finance' },
                  { label: 'HR', value: 'hr' },
                  { label: 'IT', value: 'it' },
                  { label: 'Operations', value: 'operations' },
                ],
                required: false,
              },
              {
                id: 'projectCode',
                label: 'Project Code',
                type: 'text',
                required: false,
              },
            ]);
          }, 300);
        });
        
        // Initialize custom fields in form data if not exists
        fields.forEach(field => {
          if (!formData.customFields[field.id]) {
            formData.customFields[field.id] = '';
          }
        });
        
        customFields.value = fields;
      } catch (error) {
        console.error('Failed to load custom fields', error);
        showError('Failed to load custom fields configuration', error);
      }
    };

    const getFieldComponent = (fieldType: string) => {
      switch (fieldType) {
        case 'dropdown':
          return 'Dropdown';
        case 'date':
          return 'Calendar';
        case 'boolean':
          return 'Checkbox';
        case 'number':
          return 'InputNumber';
        default:
          return 'InputText';
      }
    };

    const handleSubmit = async () => {
      const isValid = await v$.value.$validate();
      if (!isValid) return;
      
      saving.value = true;
      try {
        const accountData = {
          ...formData,
          accountCategory: formData.category as AccountCategory,
          customFields: formData.customFields || {},
        };
        
        if (isNew.value) {
          // For new accounts, create a CreateGlAccountDto
          const createDto: CreateGlAccountDto = {
            accountNumber: accountData.accountNumber,
            name: accountData.name,
            accountType: accountData.accountType,
            accountCategory: accountData.accountCategory,
            currency: accountData.currency || 'USD',
            description: accountData.description || undefined,
            parentAccountId: accountData.parentAccountId || undefined,
            status: accountData.status,
            isDetailAccount: accountData.isDetailAccount,
            sortOrder: accountData.sortOrder,
            openingBalance: accountData.openingBalance,
            taxCode: accountData.taxCode || undefined,
            costCenter: accountData.costCenter || undefined,
            departmentId: accountData.departmentId,
            projectCode: accountData.projectCode,
            notes: accountData.notes,
            tags: accountData.tags,
            customFields: accountData.customFields,
          };
          
          await glAccountStore.createAccount(createDto);
          showSuccess('GL Account created successfully');
        } else if (formData.id) {
          // For updates, create an UpdateGlAccountDto
          const updateDto: UpdateGlAccountDto = {
            id: formData.id!,
            name: accountData.name,
            description: accountData.description || undefined,
            status: accountData.status,
            isLocked: accountData.isLocked,
            sortOrder: accountData.sortOrder,
            taxCode: accountData.taxCode || undefined,
            costCenter: accountData.costCenter || undefined,
            departmentId: accountData.departmentId || undefined,
            projectCode: accountData.projectCode || undefined,
            notes: accountData.notes || undefined,
            tags: accountData.tags || undefined,
            customFields: accountData.customFields,
          };
          
          await glAccountStore.updateAccount(updateDto);
          showSuccess('GL Account updated successfully');
        }
        
        router.push({ name: 'gl-accounts' });
      } catch (error: any) {
        showError(error?.message || 'Failed to save GL Account');
      } finally {
        saving.value = false;
      }
    };

    const confirmDelete = () => {
      // Use the PrimeVue useConfirm composable
      const confirm = useConfirm();
      
      confirm.require({
        message: 'Are you sure you want to delete this account? This action cannot be undone. ' +
                 'This will also delete all child accounts and cannot be reversed.',
        header: 'Confirm Deletion',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        acceptLabel: 'Yes, delete it',
        rejectLabel: 'No, keep it',
        accept: handleDelete,
      });
    };

    const handleDelete = async () => {
      if (!props.id) return;
      
      try {
        await glAccountStore.deleteAccount(props.id);
        showSuccess('Account deleted successfully');
        // Navigate back to the accounts list with a success message
        router.push({ 
          name: 'gl-accounts',
          query: { deleted: 'true' }
        });
      } catch (error) {
        const errorData = (error as any)?.response?.data;
        const errorMessage = errorData?.message || 'Failed to delete account';
        
        // If the error is due to the account having child accounts
        if (errorData?.code === 'HAS_CHILD_ACCOUNTS') {
          // @ts-ignore - PrimeVue types issue
          confirm.require({
            message: 'This account has child accounts. Deleting it will also delete all child accounts. Do you want to proceed?',
            header: 'Confirm Deletion with Child Accounts',
            icon: 'pi pi-exclamation-triangle',
            acceptClass: 'p-button-danger',
            acceptLabel: 'Yes, delete all',
            rejectLabel: 'Cancel',
            accept: async () => {
              try {
                // Force delete with children
                await glAccountStore.deleteAccount(props.id, { force: true });
                showSuccess('Account and all child accounts deleted successfully');
                router.push({ 
                  name: 'gl-accounts',
                  query: { deleted: 'true' }
                });
              } catch (err) {
                const deleteError = err as any;
                const deleteErrorMessage = deleteError?.response?.data?.message || 
                                         'Failed to delete account with children';
                showError(deleteErrorMessage, err);
              }
            }
          });
        } else {
          showError(errorMessage, error);
        }
      }
    };

    const handleCancel = () => {
      router.go(-1);
    };

    const handlePrint = () => {
      window.print();
    };

    const handleExport = () => {
      exportDialog.value.show({
        title: 'Export Account Details',
        defaultFormat: 'pdf',
      });
    };

    const handleExportConfirm = async (format: string, options: any) => {
      if (!props.id) return;
      
      try {
        // Show loading state
        const loadingMessage = `Exporting to ${format.toUpperCase()}...`;
        const message = ref(loadingMessage);
        const loading = ref(true);
        
        // Use the PrimeVue useConfirm composable
        const confirm = useConfirm();
        
        // Show progress dialog
        confirm.require({
          header: 'Exporting Account Data',
          message: message.value,
          icon: 'pi pi-spin pi-spinner',
          closable: false,
          closeOnEscape: false,
          dismissableMask: false,
          footer: null,
        });

        // Call the export API
        try {
          // Add format-specific options
          const exportOptions = {
            format,
            includeChildren: options.includeChildren || false,
            includeTransactions: options.includeTransactions || false,
            dateRange: options.dateRange || {}
          };
          
          // Call the export API
          const result = await glAccountService.exportAccount(props.id, exportOptions);
          
          // Update UI to show success
          message.value = 'Export completed successfully!';
          loading.value = false;
          
          // Close the dialog after a short delay
          setTimeout(() => {
            // Show success message
            showSuccess('Export completed successfully');
            
            // Trigger file download
            if (result?.data) {
              const blob = new Blob([result.data], { type: result.headers['content-type'] });
              const url = window.URL.createObjectURL(blob);
              const contentDisposition = result.headers['content-disposition'];
              let filename = `account-${props.id}-${new Date().toISOString()}.${format}`;
              
              // Extract filename from content-disposition header if available
              if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename[^;=]*=((['"]).*?\2|[^;\n]*)/);
                if (filenameMatch && filenameMatch[1]) {
                  filename = filenameMatch[1].replace(/['"]/g, '');
                }
              }
              
              const link = document.createElement('a');
              link.href = url;
              link.setAttribute('download', filename);
              document.body.appendChild(link);
              link.click();
              link.remove();
              
              // Clean up the URL object
              window.URL.revokeObjectURL(url);
            }
          }, 1000);
        } catch (error) {
          progressDialog.close();
          const errorMessage = (error as any)?.response?.data?.message || 
                             'Failed to export account data';
          showError(errorMessage, error);
        }
      } catch (error) {
        console.error('Export error:', error);
        showError('Failed to initialize export', error);
      }
    };

    // Lifecycle hooks
    onMounted(async () => {
      try {
        await Promise.all([
          loadAccountCategories(),
          loadParentAccounts(),
          loadCurrencies(),
          loadCustomFields(),
          loadActivityLogs()
        ]);
        
        if (!isNew.value && props.id) {
          await loadAccount();
        }
      } catch (error) {
        console.error('Error initializing component:', error);
        showError('Failed to initialize component');
      }
    });

    return {
      // Refs
      formData,
      loading,
      saving,
      loadingAccounts,
      loadingCurrencies,
      loadingActivity,
      exportDialog,
      
      // Computed
      isNew,
      v$,
      
      // Data
      accountTypes,
      accountStatuses,
      accountCategories,
      parentAccountOptions,
      currencies,
      activityLogs,
      customFields,
      exportFormats,
      
      // Methods
      formatDate,
      getFieldComponent,
      handleSubmit,
      handleCancel,
      confirmDelete,
      handlePrint,
      handleExport,
      handleExportConfirm,
    };
  },
});
</script>

<style scoped>
.gl-account-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.required {
  color: var(--red-500);
}

:deep(.p-card) {
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1), 0 4px 5px 0 rgba(0, 0, 0, 0.1);
}

:deep(.p-tabview-panels) {
  padding: 1.25rem 0 0 0;
}

:deep(.p-field) {
  margin-bottom: 1.5rem;
}

:deep(.p-button) {
  min-width: 100px;
}

@media print {
  .p-tabview-nav,
  .p-card-footer {
    display: none !important;
  }
  
  .p-card {
    box-shadow: none !important;
    border: none !important;
  }
}
</style>
