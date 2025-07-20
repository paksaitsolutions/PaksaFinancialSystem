<template>
  <div class="gl-account-detail">
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <div>
            <span v-if="isNew">New GL Account</span>
            <span v-else>GL Account: {{ account.accountNumber }} - {{ account.name }}</span>
          </div>
          <div>
            <Button 
              v-if="!isNew" 
              icon="pi pi-print" 
              class="p-button-text p-button-rounded p-button-plain" 
              @click="handlePrint"
              v-tooltip.top="'Print Account Details'"
            />
            <Button 
              icon="pi pi-file-export" 
              class="p-button-text p-button-rounded p-button-plain" 
              @click="handleExport"
              v-tooltip.top="'Export Account Data'"
            />
          </div>
        </div>
      </template>

      <TabView>
        <TabPanel header="Account Information">
          <div class="p-fluid grid">
            <div class="field col-12 md:col-6">
              <label for="accountNumber">Account Number <span class="required">*</span></label>
              <InputText 
                id="accountNumber" 
                v-model="formData.accountNumber" 
                :class="{ 'p-invalid': v$.accountNumber.$error }"
                :disabled="!isNew"
              />
              <small v-if="v$.accountNumber.$error" class="p-error">
                {{ v$.accountNumber.$errors[0].$message }}
              </small>
            </div>

            <div class="field col-12 md:col-6">
              <label for="name">Account Name <span class="required">*</span></label>
              <InputText 
                id="name" 
                v-model="formData.name" 
                :class="{ 'p-invalid': v$.name.$error }"
              />
              <small v-if="v$.name.$error" class="p-error">
                {{ v$.name.$errors[0].$message }}
              </small>
            </div>

            <div class="field col-12 md:col-6">
              <label for="accountType">Account Type <span class="required">*</span></label>
              <Dropdown
                id="accountType"
                v-model="formData.accountType"
                :options="accountTypes"
                optionLabel="label"
                optionValue="value"
                :class="{ 'p-invalid': v$.accountType.$error }"
                :disabled="!isNew"
              />
              <small v-if="v$.accountType.$error" class="p-error">
                {{ v$.accountType.$errors[0].$message }}
              </small>
            </div>

            <div class="field col-12 md:col-6">
              <label for="category">Category</label>
              <Dropdown
                id="category"
                v-model="formData.category"
                :options="accountCategories"
                optionLabel="label"
                optionValue="value"
              />
            </div>

            <div class="field col-12 md:col-6">
              <label for="parentAccount">Parent Account</label>
              <TreeSelect
                v-model="formData.parentAccountId"
                :options="parentAccountOptions"
                placeholder="Select Parent Account"
                :loading="loadingAccounts"
                :class="{ 'p-invalid': v$.parentAccountId.$error }"
                :disabled="!isNew"
              />
              <small v-if="v$.parentAccountId.$error" class="p-error">
                {{ v$.parentAccountId.$errors[0].$message }}
              </small>
            </div>

            <div class="field col-12 md:col-6">
              <label for="currency">Currency</label>
              <Dropdown
                id="currency"
                v-model="formData.currency"
                :options="currencies"
                optionLabel="name"
                optionValue="code"
                :loading="loadingCurrencies"
              />
            </div>

            <div class="field col-12 md:col-6">
              <label for="status">Status</label>
              <Dropdown
                id="status"
                v-model="formData.status"
                :options="accountStatuses"
                optionLabel="label"
                optionValue="value"
              />
            </div>

            <div class="field col-12">
              <label for="description">Description</label>
              <Textarea id="description" v-model="formData.description" rows="3" />
            </div>

            <div class="field col-12 md:col-6">
              <div class="flex align-items-center">
                <Checkbox 
                  id="isTaxRelevant" 
                  v-model="formData.isTaxRelevant" 
                  :binary="true"
                />
                <label for="isTaxRelevant" class="ml-2">Tax Relevant</label>
              </div>
            </div>

            <div class="field col-12 md:col-6">
              <div class="flex align-items-center">
                <Checkbox 
                  id="isReconcilable" 
                  v-model="formData.isReconcilable" 
                  :binary="true"
                />
                <label for="isReconcilable" class="ml-2">Reconcilable</label>
              </div>
            </div>
          </div>
        </TabPanel>

        <TabPanel header="Advanced Settings" v-if="!isNew">
          <div class="p-fluid grid">
            <div class="field col-12 md:col-6">
              <label for="openingBalance">Opening Balance</label>
              <InputNumber
                id="openingBalance"
                v-model="formData.openingBalance"
                mode="currency"
                :currency="formData.currency || 'USD'"
                :minFractionDigits="2"
                :maxFractionDigits="4"
                :disabled="!isNew"
              />
            </div>

            <div class="field col-12 md:col-6">
              <label for="asOfDate">Balance As Of</label>
              <Calendar
                id="asOfDate"
                v-model="formData.balanceAsOf"
                :showIcon="true"
                :disabled="!isNew"
              />
            </div>

            <div class="field col-12">
              <h4>Custom Fields</h4>
              <div class="grid">
                <div 
                  v-for="field in customFields" 
                  :key="field.id" 
                  class="field col-12 md:col-6"
                >
                  <component
                    :is="getFieldComponent(field.type)"
                    v-model="formData.customFields[field.id]"
                    :id="`custom-${field.id}`"
                    :label="field.label"
                    :options="field.options"
                    :required="field.required"
                  />
                </div>
              </div>
            </div>
          </div>
        </TabPanel>

        <TabPanel header="Activity" v-if="!isNew">
          <DataTable
            :value="activityLogs"
            :loading="loadingActivity"
            :paginator="true"
            :rows="10"
            :rowsPerPageOptions="[10, 25, 50]"
            responsiveLayout="scroll"
          >
            <Column field="timestamp" header="Date" style="width: 15%">
              <template #body="{ data }">
                {{ formatDate(data.timestamp) }}
              </template>
            </Column>
            <Column field="user" header="User" style="width: 15%" />
            <Column field="action" header="Action" style="width: 15%" />
            <Column field="details" header="Details" style="width: 55%" />
          </DataTable>
        </TabPanel>
      </TabView>

      <template #footer>
        <div class="flex justify-content-between">
          <div>
            <Button 
              v-if="!isNew" 
              label="Delete" 
              icon="pi pi-trash" 
              class="p-button-danger" 
              @click="confirmDelete"
            />
          </div>
          <div>
            <Button 
              label="Cancel" 
              icon="pi pi-times" 
              class="p-button-text" 
              @click="handleCancel"
            />
            <Button 
              :label="isNew ? 'Create' : 'Update'" 
              icon="pi pi-check" 
              class="p-button-success" 
              @click="handleSubmit"
              :loading="saving"
            />
          </div>
        </div>
      </template>
    </Card>

    <ConfirmDialog />
    <ReportExportDialog 
      ref="exportDialog"
      :formats="exportFormats"
      @export="handleExportConfirm"
    />
</template>

<script lang="ts">
import { defineComponent, ref, reactive, computed, onMounted } from 'vue';
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

// Import types and constants from gl-account module
import type { 
  GlAccount, 
  GlAccountFilters, 
  AccountType, 
  AccountCategory, 
  AccountStatus, 
  CreateGlAccountDto, 
  UpdateGlAccountDto,
  ACCOUNT_TYPES,
  ACCOUNT_CATEGORIES,
  ACCOUNT_STATUS
} from '../types/gl-account';
import {
  ACCOUNT_TYPES,
  ACCOUNT_CATEGORIES,
  ACCOUNT_STATUS
} from '../types/gl-account-constants';

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
  },
  setup(props) {
    const router = useRouter();
    const glAccountStore = useGlAccountStore();
    const glCategoryStore = useGlCategoryStore();
    const { showSuccess, showError } = useNotification();
    
    // Initialize with default values
    const currencies = ref([{ code: 'USD', name: 'US Dollar' }, { code: 'PKR', name: 'Pakistani Rupee' }]);

    const isNew = computed(() => !props.id);
    const loading = ref(false);
    const saving = ref(false);
    const loadingAccounts = ref(false);
    const loadingCurrencies = ref(false);
    const loadingActivity = ref(false);
    const exportDialog = ref();

    // Form state
    const formState = reactive<CreateGlAccountDto | UpdateGlAccountDto>({
      accountNumber: '',
      name: '',
      accountType: ACCOUNT_TYPES.ASSET as AccountType, // Default to ASSET type
      accountCategory: ACCOUNT_CATEGORIES.CURRENT_ASSET, // Default category
      description: '',
      parentAccountId: null,
      status: ACCOUNT_STATUS.ACTIVE,
      isDetailAccount: true,
      currency: 'PKR',
      isLocked: false,
      sortOrder: 0,
    });

    // Validation rules
    const rules = {
      accountNumber: { 
        required: helpers.withMessage('Account number is required', required),
        maxLength: helpers.withMessage('Maximum 20 characters allowed', maxLength(20)),
      },
      name: { 
        required: helpers.withMessage('Account name is required', required),
        maxLength: helpers.withMessage('Maximum 100 characters allowed', maxLength(100)),
      },
      accountType: { 
        required: helpers.withMessage('Account type is required', required),
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

    const v$ = useVuelidate(rules, formState);

    // Data options
    const accountTypes = ref(
      Object.entries(ACCOUNT_TYPES).map(([key, value]) => ({
        label: key.charAt(0).toUpperCase() + key.slice(1).toLowerCase(),
        value,
      }))
    );

    const accountStatuses = ref(
      Object.entries(ACCOUNT_STATUS).map(([key, value]) => ({
        label: key.split('_').map(word => word.charAt(0) + word.slice(1).toLowerCase()).join(' '),
        value,
      }))
    );
    
    const accountCategories = ref(
      Object.entries(ACCOUNT_CATEGORIES).map(([key, value]) => ({
        label: key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' '),
        value,
      }))
    );

    const parentAccountOptions = ref<Array<any>>([]);
    const activityLogs = ref<Array<any>>([]);
    const customFields = ref<Array<any>>([]);
    const exportFormats = ref([
      { label: 'PDF', value: 'pdf', icon: 'pi pi-file-pdf' },
      { label: 'Excel', value: 'xlsx', icon: 'pi pi-file-excel' },
      { label: 'CSV', value: 'csv', icon: 'pi pi-file' },
    ]);

    // Methods
    const loadAccount = async () => {
      if (!props.id) return;
      
      loading.value = true;
      try {
        // Use fetchAccountById to get the account details
        const account = await glAccountStore.fetchAccountById(props.id);
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
