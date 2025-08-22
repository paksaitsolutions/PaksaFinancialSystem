<template>
  <form @submit.prevent="$emit('submit', formData)">
    <div class="grid">
      <!-- Left Column -->
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="accountNumber" class="font-medium">Account Number <span class="text-red-500">*</span></label>
          <InputText 
            id="accountNumber" 
            v-model="formData.accountNumber" 
            class="w-full" 
            :disabled="isEditMode"
            :class="{ 'p-invalid': v$.accountNumber.$error }"
          />
          <small v-if="v$.accountNumber.$error" class="p-error">
            {{ v$.accountNumber.$errors[0].$message }}
          </small>
          <small v-else class="p-inline-help">
            A unique identifier for this account
          </small>
        </div>

        <div class="field">
          <label for="name" class="font-medium">Account Name <span class="text-red-500">*</span></label>
          <InputText 
            id="name" 
            v-model="formData.name" 
            class="w-full"
            :class="{ 'p-invalid': v$.name.$error }"
          />
          <small v-if="v$.name.$error" class="p-error">
            {{ v$.name.$errors[0].$message }}
          </small>
        </div>

        <div class="field">
          <label for="description" class="font-medium">Description</label>
          <Textarea 
            id="description" 
            v-model="formData.description" 
            rows="3" 
            class="w-full"
            :class="{ 'p-invalid': v$.description.$error }"
          />
          <small v-if="v$.description.$error" class="p-error">
            {{ v$.description.$errors[0].$message }}
          </small>
        </div>

        <div class="field">
          <label for="parentId" class="font-medium">Parent Account</label>
          <TreeSelect 
            v-model="formData.parentId"
            :options="parentAccountOptions"
            placeholder="Select parent account"
            class="w-full"
            :loading="loadingParentAccounts"
            :disabled="isEditMode"
            :showClear="true"
            :loadingIcon="'pi pi-spinner pi-spin'"
            :class="{ 'p-invalid': v$.parentId.$error }"
          >
            <template #value="slotProps">
              <div v-if="slotProps.value">
                {{ getAccountLabel(slotProps.value) }}
              </div>
              <span v-else>
                {{ slotProps.placeholder }}
              </span>
            </template>
            <template #option="slotProps">
              <div>
                <span :style="{ 'margin-left': `${(slotProps.node.level || 0) * 1}rem` }">
                  <i :class="getAccountIcon(slotProps.node)" class="mr-2" />
                  {{ slotProps.node.label }}
                  <small class="text-500 ml-2">{{ slotProps.node.data?.accountNumber }}</small>
                </span>
              </div>
            </template>
          </TreeSelect>
          <small v-if="v$.parentId.$error" class="p-error">
            {{ v$.parentId.$errors[0].$message }}
          </small>
        </div>

        <div class="field">
          <label for="accountType" class="font-medium">Account Type <span class="text-red-500">*</span></label>
          <Dropdown 
            id="accountType"
            v-model="formData.accountType"
            :options="accountTypeOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full"
            :disabled="isEditMode"
            :class="{ 'p-invalid': v$.accountType.$error }"
          />
          <small v-if="v$.accountType.$error" class="p-error">
            {{ v$.accountType.$errors[0].$message }}
          </small>
          <small v-else class="p-inline-help">
            Select the appropriate account type for financial reporting
          </small>
        </div>
      </div>

      <!-- Right Column -->
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="status" class="font-medium">Status</label>
          <Dropdown 
            id="status"
            v-model="formData.status"
            :options="statusOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full"
            :class="{ 'p-invalid': v$.status.$error }"
          />
          <small v-if="v$.status.$error" class="p-error">
            {{ v$.status.$errors[0].$message }}
          </small>
        </div>

        <div class="field">
          <label for="currency" class="font-medium">Currency <span class="text-red-500">*</span></label>
          <Dropdown 
            id="currency"
            v-model="formData.currency"
            :options="currencyOptions"
            optionLabel="name"
            optionValue="code"
            class="w-full"
            :disabled="isEditMode"
            :class="{ 'p-invalid': v$.currency.$error }"
          >
            <template #value="slotProps">
              <div v-if="slotProps.value" class="flex align-items-center">
                <span :class="'fi fi-' + (currencyMap[slotProps.value]?.toLowerCase() || 'xx')" class="mr-2"></span>
                <div>{{ slotProps.value }} - {{ getCurrencyName(slotProps.value) }}</div>
              </div>
              <span v-else>
                {{ slotProps.placeholder }}
              </span>
            </template>
            <template #option="slotProps">
              <div class="flex align-items-center">
                <span :class="'fi fi-' + (currencyMap[slotProps.option.code]?.toLowerCase() || 'xx')" class="mr-2"></span>
                <div>{{ slotProps.option.code }} - {{ slotProps.option.name }}</div>
              </div>
            </template>
          </Dropdown>
          <small v-if="v$.currency.$error" class="p-error">
            {{ v$.currency.$errors[0].$message }}
          </small>
        </div>

        <div class="field">
          <label for="taxCode" class="font-medium">Tax Code</label>
          <Dropdown 
            id="taxCode"
            v-model="formData.taxCode"
            :options="taxCodeOptions"
            optionLabel="name"
            optionValue="code"
            class="w-full"
            :class="{ 'p-invalid': v$.taxCode.$error }"
          />
          <small v-if="v$.taxCode.$error" class="p-error">
            {{ v$.taxCode.$errors[0].$message }}
          </small>
          <small v-else class="p-inline-help">
            Optional tax classification for this account
          </small>
        </div>

        <div class="field">
          <label for="openingBalance" class="font-medium">Opening Balance</label>
          <InputNumber 
            id="openingBalance"
            v-model="formData.openingBalance"
            mode="decimal"
            :minFractionDigits="2"
            :maxFractionDigits="2"
            class="w-full"
            :class="{ 'p-invalid': v$.openingBalance.$error }"
          >
            <template #prefix>{{ formData.currency || 'USD' }} </template>
          </InputNumber>
          <small v-if="v$.openingBalance.$error" class="p-error">
            {{ v$.openingBalance.$errors[0].$message }}
          </small>
          <small v-else class="p-inline-help">
            Initial balance when this account is created
          </small>
        </div>

        <div class="field">
          <label for="asOfDate" class="font-medium">Balance As Of</label>
          <Calendar 
            id="asOfDate"
            v-model="formData.asOfDate"
            :showIcon="true"
            dateFormat="yy-mm-dd"
            class="w-full"
            :class="{ 'p-invalid': v$.asOfDate.$error }"
          />
          <small v-if="v$.asOfDate.$error" class="p-error">
            {{ v$.asOfDate.$errors[0].$message }}
          </small>
        </div>
      </div>

      <!-- Full Width Fields -->
      <div class="col-12">
        <div class="field">
          <label for="notes" class="font-medium">Notes</label>
          <Textarea 
            id="notes" 
            v-model="formData.notes" 
            rows="2" 
            class="w-full"
            :class="{ 'p-invalid': v$.notes.$error }"
          />
          <small v-if="v$.notes.$error" class="p-error">
            {{ v$.notes.$errors[0].$message }}
          </small>
        </div>

        <div class="flex justify-content-end gap-2 mt-4">
          <Button 
            type="button" 
            label="Cancel" 
            icon="pi pi-times" 
            class="p-button-text"
            :disabled="loading"
            @click="$emit('cancel')"
          />
          <Button 
            type="submit" 
            :label="isEditMode ? 'Update Account' : 'Create Account'" 
            icon="pi pi-check" 
            :loading="loading"
          />
        </div>
      </div>
    </div>
  </form>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import { useVuelidate } from '@vuelidate/core';
import { required, minLength, maxLength, numeric, decimal, helpers } from '@vuelidate/validators';
import { useGlAccountStore } from '@/modules/general-ledger/store/gl-account';
import { GlAccount, AccountType, AccountStatus } from '@/modules/general-ledger/types/gl-account';
import { Currency } from '@/shared/types/currency';

export default defineComponent({
  name: 'GlAccountForm',
  
  props: {
    account: {
      type: Object as () => Partial<GlAccount>,
      default: () => ({
        status: AccountStatus.ACTIVE,
        accountType: AccountType.EXPENSE,
        currency: 'USD',
      }),
    },
    mode: {
      type: String as () => 'create' | 'edit',
      default: 'create',
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  
  emits: ['submit', 'cancel'],
  
  setup(props, { emit }) {
    const accountStore = useGlAccountStore();
    const loadingParentAccounts = ref(false);
    
    // Form data with default values
    const formData = ref<Partial<GlAccount>>({
      accountNumber: '',
      name: '',
      description: '',
      parentId: null,
      accountType: AccountType.EXPENSE,
      status: AccountStatus.ACTIVE,
      currency: 'USD',
      taxCode: '',
      openingBalance: 0,
      asOfDate: new Date().toISOString().split('T')[0],
      notes: '',
      isSystemAccount: false,
    });
    
    // Update form data when account prop changes
    watch(() => props.account, (newVal) => {
      if (newVal) {
        formData.value = { ...formData.value, ...newVal };
      }
    }, { immediate: true, deep: true });
    
    // Form validation rules
    const rules = {
      accountNumber: { 
        required: helpers.withMessage('Account number is required', required),
        minLength: helpers.withMessage('Account number must be at least 3 characters', minLength(3)),
        maxLength: helpers.withMessage('Account number cannot exceed 20 characters', maxLength(20)),
      },
      name: { 
        required: helpers.withMessage('Account name is required', required),
        minLength: helpers.withMessage('Account name must be at least 3 characters', minLength(3)),
        maxLength: helpers.withMessage('Account name cannot exceed 100 characters', maxLength(100)),
      },
      description: {
        maxLength: helpers.withMessage('Description cannot exceed 500 characters', maxLength(500)),
      },
      accountType: { 
        required: helpers.withMessage('Account type is required', required),
      },
      status: { 
        required: helpers.withMessage('Status is required', required),
      },
      currency: { 
        required: helpers.withMessage('Currency is required', required),
      },
      openingBalance: {
        decimal: helpers.withMessage('Must be a valid number', (value: any) => {
          if (value === null || value === undefined || value === '') return true;
          return /^\d+(\.\d{1,2})?$/.test(String(value));
        }),
      },
      notes: {
        maxLength: helpers.withMessage('Notes cannot exceed 1000 characters', maxLength(1000)),
      },
    };
    
    const v$ = useVuelidate(rules, formData);
    
    // Computed
    const isEditMode = computed(() => props.mode === 'edit');
    
    // Account type options
    const accountTypeOptions = [
      { label: 'Asset', value: AccountType.ASSET },
      { label: 'Liability', value: AccountType.LIABILITY },
      { label: 'Equity', value: AccountType.EQUITY },
      { label: 'Revenue', value: AccountType.REVENUE },
      { label: 'Expense', value: AccountType.EXPENSE },
      { label: 'Gain', value: AccountType.GAIN },
      { label: 'Loss', value: AccountType.LOSS },
    ];
    
    // Status options
    const statusOptions = [
      { label: 'Active', value: AccountStatus.ACTIVE },
      { label: 'Inactive', value: AccountStatus.INACTIVE },
    ];
    
    // Currency options (simplified, would come from a service in a real app)
    const currencyOptions = [
      { code: 'USD', name: 'US Dollar' },
      { code: 'EUR', name: 'Euro' },
      { code: 'GBP', name: 'British Pound' },
      { code: 'JPY', name: 'Japanese Yen' },
      { code: 'AUD', name: 'Australian Dollar' },
      { code: 'CAD', name: 'Canadian Dollar' },
      { code: 'CHF', name: 'Swiss Franc' },
      { code: 'CNY', name: 'Chinese Yuan' },
      { code: 'PKR', name: 'Pakistani Rupee' },
      { code: 'INR', name: 'Indian Rupee' },
      { code: 'SAR', name: 'Saudi Riyal' },
      { code: 'AED', name: 'UAE Dirham' },
    ];
    
    // Currency to country code mapping for flags (using flag-icons CSS)
    const currencyMap: Record<string, string> = {
      USD: 'us',
      EUR: 'eu',
      GBP: 'gb',
      JPY: 'jp',
      AUD: 'au',
      CAD: 'ca',
      CHF: 'ch',
      CNY: 'cn',
      PKR: 'pk',
      INR: 'in',
      SAR: 'sa',
      AED: 'ae',
    };
    
    // Tax code options (simplified, would come from a service in a real app)
    const taxCodeOptions = [
      { code: 'VAT_STANDARD', name: 'VAT Standard Rate' },
      { code: 'VAT_REDUCED', name: 'VAT Reduced Rate' },
      { code: 'VAT_ZERO', name: 'VAT Zero Rated' },
      { code: 'VAT_EXEMPT', name: 'VAT Exempt' },
      { code: 'GST', name: 'GST' },
      { code: 'SALES_TAX', name: 'Sales Tax' },
      { code: 'NONE', name: 'No Tax' },
    ];
    
    // Parent account options (will be loaded from the store)
    const parentAccountOptions = ref<Array<{label: string, value: string, data: any, children?: any[]}>>([]);
    
    // Methods
    const getCurrencyName = (code: string) => {
      const currency = currencyOptions.find(c => c.code === code);
      return currency ? currency.name : code;
    };
    
    const getAccountLabel = (accountId: string) => {
      // In a real app, this would find the account in the hierarchy
      return accountId; // Simplified for this example
    };
    
    const getAccountIcon = (node: any) => {
      if (node.children && node.children.length > 0) {
        return node.expanded ? 'pi pi-folder-open' : 'pi pi-folder';
      }
      return 'pi pi-file';
    };
    
    const loadParentAccountOptions = async () => {
      try {
        loadingParentAccounts.value = true;
        // In a real app, this would fetch the account hierarchy from the store
        // For now, we'll simulate a delay and return an empty array
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // This would come from the store in a real app
        parentAccountOptions.value = [];
      } catch (error) {
        console.error('Error loading parent accounts:', error);
      } finally {
        loadingParentAccounts.value = false;
      }
    };
    
    // Lifecycle hooks
    onMounted(() => {
      loadParentAccountOptions();
    });
    
    return {
      // Refs
      formData,
      loadingParentAccounts,
      v$,
      
      // Computed
      isEditMode,
      
      // Options
      accountTypeOptions,
      statusOptions,
      currencyOptions,
      taxCodeOptions,
      parentAccountOptions,
      currencyMap,
      
      // Methods
      getCurrencyName,
      getAccountLabel,
      getAccountIcon,
    };
  },
});
</script>

<style scoped>
/* Add any custom styles here */
</style>
