<template>
  <div class="tax-exemption-form space-y-6">
    <form @submit.prevent="handleSubmit">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Customer Selection with Search -->
        <div class="form-group" :class="{ 'has-error': v$.customerId.$error }">
          <label for="customer" class="block text-sm font-medium text-gray-700">
            {{ $t('tax.customer') }} <span class="text-red-500">*</span>
          </label>
          <div class="relative mt-1">
            <CustomerSelect
              id="customer"
              v-model="formData.customerId"
              :error="v$.customerId.$errors[0]?.$message"
              :filter-fields="['name', 'taxId', 'email']"
              :show-create-button="true"
              required
              class="w-full"
              @create:customer="handleCustomerCreate"
            />
            <div v-if="v$.customerId.$error" class="mt-1 text-sm text-red-600">
              {{ v$.customerId.$errors[0].$message }}
            </div>
          </div>
        </div>

        <!-- Tax Code -->
        <div class="form-group" :class="{ 'has-error': v$.taxCode.$error }">
          <label for="taxCode" class="block text-sm font-medium text-gray-700">
            {{ $t('tax.taxCode') }} <span class="text-red-500">*</span>
          </label>
          <TaxCodeSelect
            id="taxCode"
            v-model="formData.taxCode"
            :error="v$.taxCode.$errors[0]?.$message"
            required
            class="mt-1"
          />
        </div>

        <!-- Exemption Details -->
        <div class="form-group" :class="{ 'has-error': v$.exemptionReason.$error }">
          <label for="exemptionReason" class="block text-sm font-medium text-gray-700">
            {{ $t('tax.exemptionReason') }} <span class="text-red-500">*</span>
          </label>
          <InputText
            id="exemptionReason"
            v-model="formData.exemptionReason"
            :error="v$.exemptionReason.$errors[0]?.$message"
            :placeholder="t('tax.exemptionReasonPlaceholder')"
            class="w-full"
            required
            class="mt-1"
          />
        </div>

        <div class="form-group">
          <label for="exemptionCertificateNumber" class="block text-sm font-medium text-gray-700">
            {{ $t('tax.exemptionCertificateNumber') }}
          </label>
          <InputText
            id="exemptionCertificateNumber"
            v-model="formData.exemptionCertificateNumber"
            class="mt-1"
          />
        </div>

        <!-- Date Range with Validation -->
        <div class="form-group">
          <label for="startDate" class="block text-sm font-medium text-gray-700">
            {{ $t('common.startDate') }} <span class="text-red-500">*</span>
          </label>
          <div class="relative mt-1">
            <DatePicker
              id="startDate"
              v-model="formData.startDate"
              :error="v$.startDate.$error"
              :max-date="formData.endDate || null"
              :disabled-dates="{ days: [0, 6] }"
              required
              class="w-full"
              @update:model-value="validateDateRange"
            />
            <div v-if="v$.startDate.$error" class="mt-1 text-sm text-red-600">
              {{ v$.startDate.$errors[0].$message }}
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="endDate" class="block text-sm font-medium text-gray-700">
            {{ $t('common.endDate') }}
            <span v-if="formData.endDate" class="text-xs text-gray-500 ml-1">({{ dateRangeDuration }} days)</span>
          </label>
          <div class="relative mt-1">
            <DatePicker
              id="endDate"
              v-model="formData.endDate"
              :min-date="formData.startDate"
              :disabled="!formData.startDate"
              :disabled-dates="{ days: [0, 6] }"
              class="w-full"
              @update:model-value="validateDateRange"
            >
              <template #footer>
                <div class="flex justify-between p-2 border-t border-gray-200">
                  <button
                    type="button"
                    class="text-xs text-blue-600 hover:text-blue-800"
                    @click="setEndDate(30)"
                  >
                    30 days
                  </button>
                  <button
                    type="button"
                    class="text-xs text-blue-600 hover:text-blue-800"
                    @click="setEndDate(90)"
                  >
                    90 days
                  </button>
                  <button
                    type="button"
                    class="text-xs text-blue-600 hover:text-blue-800"
                    @click="setEndDate(365)"
                  >
                    1 year
                  </button>
                </div>
              </template>
            </DatePicker>
            <div v-if="v$.endDate.$error" class="mt-1 text-sm text-red-600">
              {{ v$.endDate.$errors[0]?.$message }}
            </div>
          </div>
        </div>

        <!-- Status -->
        <div class="form-group">
          <label for="status" class="block text-sm font-medium text-gray-700">
            {{ $t('common.status') }} <span class="text-red-500">*</span>
          </label>
          <Dropdown
            id="status"
            v-model="formData.status"
            :options="statusOptions"
            option-label="label"
            option-value="value"
            :error="v$.status.$errors[0]?.$message"
            required
            class="mt-1"
          />
        </div>

        <!-- Notes -->
        <div class="form-group md:col-span-2">
          <label for="notes" class="block text-sm font-medium text-gray-700">
            {{ $t('common.notes') }}
          </label>
          <Textarea
            id="notes"
            v-model="formData.notes"
            rows="3"
            class="mt-1"
          />
        </div>
      </div>

      <!-- Exemption Items -->
      <div class="mt-6">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-3">
          <div>
            <h3 class="text-lg font-medium text-gray-900">
              {{ $t('tax.exemptionItems') }}
            </h3>
            <p class="text-sm text-gray-500">
              {{ $t('tax.exemptionItemsDescription') }}
            </p>
          </div>
          <div class="flex items-center space-x-2 w-full sm:w-auto">
            <Button
              type="button"
              variant="outline"
              size="sm"
              class="w-full sm:w-auto justify-center"
              @click="addExemptionItem"
            >
              <PlusIcon class="w-4 h-4 mr-1" />
              {{ $t('tax.addItem') }}
            </Button>
            <Button
              v-if="formData.items.length > 1"
              type="button"
              variant="outline"
              size="sm"
              class="w-full sm:w-auto justify-center"
              @click="removeAllItems"
            >
              <TrashIcon class="w-4 h-4 mr-1" />
              {{ $t('common.removeAll') }}
            </Button>
          </div>
        </div>

        <div v-if="formData.items.length === 0" class="text-center py-4 text-gray-500">
          {{ $t('tax.noExemptionItems') }}
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="(item, index) in formData.items"
            :key="item.key || index"
            class="border rounded-lg p-4 relative transition-all duration-200 hover:shadow-md"
            :class="{ 'border-blue-200 bg-blue-50': isItemActive(item) }"
          >
            <button
              type="button"
              class="absolute top-2 right-2 text-gray-400 hover:text-red-500"
              @click="removeExemptionItem(index)"
            >
              <i class="pi pi-times"></i>
            </button>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <!-- Product/Service Selection -->
              <div class="form-group">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ $t('tax.itemType') }}
                </label>
                <div class="flex space-x-2">
                  <Button
                    type="button"
                    :variant="item.productId ? 'outline' : 'solid'"
                    size="sm"
                    @click="setItemType(index, 'product')"
                  >
                    {{ $t('common.product') }}
                  </Button>
                  <Button
                    type="button"
                    :variant="item.serviceId ? 'outline' : 'solid'"
                    size="sm"
                    @click="setItemType(index, 'service')"
                  >
                    {{ $t('common.service') }}
                  </Button>
                </div>
              </div>

              <!-- Product/Service Selector -->
              <div class="form-group">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ item.productId ? $t('common.product') : $t('common.service') }}
                </label>
                <ProductSelect
                  v-if="item.productId"
                  v-model="item.productId"
                  :error="getItemError(index, 'productId')"
                  class="w-full"
                />
                <ServiceSelect
                  v-else
                  v-model="item.serviceId"
                  :error="getItemError(index, 'serviceId')"
                  class="w-full"
                />
              </div>

              <!-- Tax Code -->
              <div class="form-group">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ $t('tax.taxCode') }} <span class="text-red-500">*</span>
                </label>
                <TaxCodeSelect
                  v-model="item.taxCode"
                  :error="getItemError(index, 'taxCode')"
                  required
                  class="w-full"
                />
              </div>

              <!-- Exemption Rate -->
              <div class="form-group">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ $t('tax.exemptionRate') }} (%)
                </label>
                <div class="flex items-center">
                  <InputNumber
                    v-model="item.exemptionRate"
                    :min="0"
                    :max="100"
                    :error="getItemError(index, 'exemptionRate')"
                    class="w-full"
                  />
                  <span class="ml-2">%</span>
                </div>
              </div>

              <!-- Effective Dates -->
              <div class="form-group">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ $t('common.effectiveFrom') }} <span class="text-red-500">*</span>
                </label>
                <DatePicker
                  v-model="item.effectiveFrom"
                  :min-date="formData.startDate"
                  :max-date="item.effectiveTo || formData.endDate"
                  :error="getItemError(index, 'effectiveFrom')"
                  required
                  class="w-full"
                />
              </div>

              <div class="form-group">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ $t('common.effectiveTo') }}
                </label>
                <DatePicker
                  v-model="item.effectiveTo"
                  :min-date="item.effectiveFrom || formData.startDate"
                  :max-date="formData.endDate"
                  class="w-full"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Form Validation Summary -->
      <div v-if="v$.$errors.length" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <ExclamationCircleIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">
              {{ t('form.validationErrors', { count: v$.$errors.length }) }}
            </h3>
            <div class="mt-2 text-sm text-red-700">
              <ul role="list" class="list-disc pl-5 space-y-1">
                <li v-for="error in v$.$errors" :key="error.$uid" class="error-message">
                  {{ error.$message }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="mt-6 flex flex-col sm:flex-row justify-end space-y-3 sm:space-y-0 sm:space-x-3">
        <Button
          type="button"
          variant="secondary"
          :disabled="loading"
          @click="handleCancel"
          class="w-full sm:w-auto"
        >
          {{ $t('common.cancel') }}
        </Button>
        <Button
          type="submit"
          :loading="loading"
          :disabled="v$.$invalid || loading"
          class="w-full sm:w-auto"
        >
          {{ isEditing ? $t('common.update') : $t('common.save') }}
        </Button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useVuelidate } from '@vuelidate/core';
import { required, minLength, minValue, maxValue, helpers } from '@vuelidate/validators';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { format, parseISO } from 'date-fns';
import { useTaxStore } from '@/store/tax';
import type { TaxExemption, TaxExemptionFormData, TaxExemptionItem } from '@/types/tax';

// Components
import Button from '@/components/ui/Button.vue';
import InputText from '@/components/ui/InputText.vue';
import Textarea from '@/components/ui/Textarea.vue';
import Dropdown from '@/components/ui/Dropdown.vue';
import DatePicker from '@/components/ui/DatePicker.vue';
import InputNumber from '@/components/ui/InputNumber.vue';
import CustomerSelect from '@/components/selects/CustomerSelect.vue';
import TaxCodeSelect from '@/components/selects/TaxCodeSelect.vue';
import ProductSelect from '@/components/selects/ProductSelect.vue';
import ServiceSelect from '@/components/selects/ServiceSelect.vue';

// Define the form item type
type TaxExemptionFormItem = {
  id?: string | null;
  key: string;
  productId: string | null;
  serviceId: string | null;
  taxCode: string;
  taxRate: number;
  exemptionRate: number;
  effectiveFrom: string;
  effectiveTo: string | null;
  taxAmount: number | null;
  totalAmount: number | null;
  productName?: string;
  productCode?: string;
  serviceName?: string;
  serviceCode?: string;
};

// Define the form data type
type FormData = Omit<TaxExemptionFormData, 'items' | 'effectiveDate' | 'expiryDate'> & {
  startDate: string;
  endDate: string | null;
  items: TaxExemptionFormItem[];
};

// Define props with TypeScript
type Props = {
  modelValue: FormData;
  loading?: boolean;
  isEditing?: boolean;
  errors?: Record<string, string>;
};

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  isEditing: false,
  errors: () => ({}),
  modelValue: () => ({
    id: null,
    customerId: '',
    customerName: '',
    taxCode: '',
    exemptionReason: '',
    exemptionCertificateNumber: '',
    startDate: format(new Date(), 'yyyy-MM-dd'),
    endDate: null,
    status: 'draft',
    notes: '',
    items: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: '',
    updatedBy: ''
  } as unknown as FormData)
});

// Define emits with TypeScript
const emit = defineEmits<{
  (e: 'update:modelValue', value: TaxExemptionFormData): void;
  (e: 'submit', value: TaxExemptionFormData): void;
  (e: 'cancel'): void;
  (e: 'customer:create', customer: any): void;
}>();

const { t } = useI18n();
const toast = useToast();
const confirm = useConfirm();
const taxStore = useTaxStore();

// Watch for external changes to modelValue
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal) {
      formData.value = { 
        ...formData.value, 
        ...newVal,
        // Preserve existing items if not provided in newVal
        items: newVal.items?.length ? [...newVal.items] : formData.value.items
      };
    }
  },
  { immediate: true, deep: true }
);

// Watch for form changes to update parent
watch(
  () => formData.value,
  (newVal) => {
    emit('update:modelValue', { ...newVal });
  },
  { deep: true }
);

// Form data with defaults from props
const formData = ref<TaxExemptionFormData>({
  ...props.modelValue,
  id: props.modelValue.id || null,
  exemptionCode: props.modelValue.exemptionCode || '',
  description: props.modelValue.description || '',
  certificateRequired: props.modelValue.certificateRequired || false,
  validFrom: props.modelValue.validFrom || format(new Date(), 'yyyy-MM-dd'),
  validTo: props.modelValue.validTo || null,
  status: props.modelValue.status || 'draft',
  items: (props.modelValue.items || []).map(item => ({
    ...item,
    id: item.id || null,
    key: item.key || `item-${Date.now()}`,
    productId: item.productId || null,
    serviceId: item.serviceId || null,
    taxCode: item.taxCode || '',
    taxRate: item.taxRate || 0,
    exemptionRate: item.exemptionRate || 0,
    effectiveFrom: item.effectiveFrom || format(new Date(), 'yyyy-MM-dd'),
    effectiveTo: item.effectiveTo || null,
    taxAmount: item.taxAmount || 0,
    totalAmount: item.totalAmount || 0,
    productName: item.productName || '',
    productCode: item.productCode || '',
    serviceName: item.serviceName || '',
    serviceCode: item.serviceCode || ''
  }))
});

// Status options
const statusOptions = [
  { label: t('tax.status.active'), value: 'active' },
  { label: t('tax.status.pending'), value: 'pending' },
  { label: t('tax.status.revoked'), value: 'revoked' },
  { label: t('tax.status.draft'), value: 'draft' },
];

// Check if editing
const isEditing = computed(() => props.isEditing);

// Initialize form with existing data if editing
onMounted(() => {
  if (props.modelValue) {
    formData.value = {
      ...props.modelValue,
      startDate: format(new Date(props.modelValue.validFrom), 'yyyy-MM-dd'),
      endDate: props.modelValue.validTo ? format(new Date(props.modelValue.validTo), 'yyyy-MM-dd') : null,
      items: (props.modelValue.items || []).map(item => ({
        ...item,
        key: `item-${Date.now()}`,
        productId: item.productId || null,
        serviceId: item.serviceId || null,
        effectiveFrom: format(new Date(item.effectiveFrom), 'yyyy-MM-dd'),
        effectiveTo: item.effectiveTo ? format(new Date(item.effectiveTo), 'yyyy-MM-dd') : null
      }))
    };
  }
});

// Required if helper function
const requiredIf = (condition: () => boolean) => (value: any) => {
  return !condition() || (value !== undefined && value !== null && value !== '');
};

// Format date helper
const formatDate = (date: string | Date | null | undefined): string => {
  if (!date) return '';
  try {
    return format(new Date(date), 'yyyy-MM-dd');
  } catch (error) {
    console.error('Error formatting date:', error);
    return '';
  }
};

// Validation rules
const rules = {
  customerId: { required },
  taxCode: { required },
  startDate: { required },
  endDate: {
    required: (value: string | null) => !!value || 'End date is required',
    minDate: (value: string | null) => {
      if (!value || !formData.value.startDate) return true;
      return new Date(value) >= new Date(formData.value.startDate) || 'End date must be after start date';
    }
  },
  items: {
    required,
    $each: helpers.forEach({
      taxCode: { required },
      exemptionRate: {
        required,
        minValue: minValue(0),
        maxValue: maxValue(100)
      },
      effectiveFrom: { required },
      effectiveTo: {
        minDate: (value: string | null, siblings: any) => {
          if (!value || !siblings?.effectiveFrom) return true;
          return new Date(value) >= new Date(siblings.effectiveFrom) || 'End date must be after start date';
        }
      }
    })
  }
};

const v$ = useVuelidate(rules, formData);

// Handle form submission
const handleSubmit = async () => {
  const isValid = await v$.value.$validate();
  if (!isValid) {
    toast.add({
      severity: 'error',
      summary: t('common.error'),
      detail: t('validation.formValidationFailed'),
      life: 5000,
    });
    return;
  }

  // Prepare the form data for submission
  const submissionData: TaxExemptionFormData = {
    ...formData.value,
    validFrom: new Date(formData.value.startDate).toISOString(),
    validTo: formData.value.endDate ? new Date(formData.value.endDate).toISOString() : null,
    items: formData.value.items.map(item => ({
      ...item,
      effectiveFrom: new Date(item.effectiveFrom).toISOString(),
      effectiveTo: item.effectiveTo ? new Date(item.effectiveTo).toISOString() : null,
      taxAmount: item.taxAmount || 0,
      totalAmount: item.totalAmount || 0,
      // Clear any empty strings
      productName: item.productName || undefined,
      productCode: item.productCode || undefined,
      serviceName: item.serviceName || undefined,
      serviceCode: item.serviceCode || undefined
    }))
  };

  // Emit the submit event with the form data
  emit('submit', submissionData as unknown as TaxExemptionFormData);
};

// Handle adding a new exemption item
const addExemptionItem = () => {
  if (!formData.value.items) {
    formData.value.items = [];
  }
  
  formData.value.items.push({
    id: null,
    key: `item-${Date.now()}`,
    productId: null,
    serviceId: null,
    taxCode: '',
    taxRate: 0,
    exemptionRate: 100,
    effectiveFrom: formData.value.validFrom,
    effectiveTo: formData.value.validTo,
    taxAmount: null,
    totalAmount: null,
    productName: '',
    productCode: '',
    serviceName: '',
    serviceCode: ''
  });
};

// Handle removing an exemption item
const removeExemptionItem = (index: number) => {
  if (formData.value.items && index >= 0 && index < formData.value.items.length) {
    formData.value.items.splice(index, 1);
  }
};

// Set item type (product or service)
const setItemType = (index: number, type: 'product' | 'service') => {
  if (!formData.value.items || index < 0 || index >= formData.value.items.length) return;
  
  const item = formData.value.items[index];
  if (type === 'product') {
    delete item.serviceId;
    item.productId = '';
  } else {
    delete item.productId;
    item.serviceId = '';
  }
};

// Get error message for a specific item field
const getItemError = (itemIndex: number, field: string) => {
  const errors = v$.value.items?.$each?.$response?.$errors?.[itemIndex]?.[field];
  return errors?.[0]?.$message || '';
};

// Handle customer creation
const handleCustomerCreate = (customer: any) => {
  emit('customer:create', customer);
};

// Handle form cancellation
const handleCancel = () => {
  emit('cancel');
};
  },
});
</script>

<style scoped>
.tax-exemption-form .form-group {
  @apply mb-4;
}

.tax-exemption-form .form-group.has-error :deep(input),
.tax-exemption-form .form-group.has-error :deep(select),
.tax-exemption-form .form-group.has-error :deep(textarea) {
  @apply border-red-300 text-red-900 placeholder-red-300 focus:outline-none focus:ring-red-500 focus:border-red-500;
}

.tax-exemption-form .form-group.has-error :deep(.p-dropdown) {
  @apply border-red-300;
}

.tax-exemption-form .form-group .error-message {
  @apply mt-1 text-sm text-red-600;
}

.tax-exemption-form .item-actions {
  @apply opacity-0 group-hover:opacity-100 transition-opacity duration-200;
}

.tax-exemption-form .item-card:hover .item-actions {
  @apply opacity-100;
}

.tax-exemption-form .item-card:last-child {
  @apply mb-0;
}

.tax-exemption-form .item-card:not(:last-child) {
  @apply mb-4;
}

.tax-exemption-form .item-card .remove-item {
  @apply absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 hover:bg-red-600 transition-colors duration-200;
}

.tax-exemption-form .item-card:hover .remove-item {
  @apply opacity-100;
}

.tax-exemption-form {
  @apply p-4 bg-white rounded-lg shadow;
}

.form-group {
  @apply mb-4;
}

/* Add any additional styles here */
</style>
