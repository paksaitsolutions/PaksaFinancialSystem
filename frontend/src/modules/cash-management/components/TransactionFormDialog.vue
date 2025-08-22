<template>
  <Dialog
    v-model:visible="modelValue"
    :header="editing ? 'Edit Transaction' : 'New Transaction'"
    :modal="true"
    :style="{ width: '700px' }"
    @hide="onClose"
  >
    <form @submit.prevent="saveTransaction">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Left Column -->
        <div class="space-y-4">
          <div class="field">
            <label for="account_id">Bank Account <span class="text-red-500">*</span></label>
            <Dropdown 
              id="account_id"
              v-model="formData.account_id"
              :options="accounts"
              optionLabel="name"
              optionValue="id"
              placeholder="Select account"
              class="w-full"
              :class="{ 'p-invalid': submitted && !formData.account_id }"
              :filter="true"
              filterPlaceholder="Search accounts..."
              :disabled="editing"
            >
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex items-center">
                  <div class="mr-2">
                    <i class="pi" :class="getAccountIcon(getAccountById(slotProps.value)?.account_type)"></i>
                  </div>
                  <div>
                    <div>{{ getAccountById(slotProps.value)?.name }}</div>
                    <div class="text-xs text-gray-500">
                      {{ getAccountById(slotProps.value)?.account_number }}
                    </div>
                  </div>
                </div>
                <span v-else>
                  {{ slotProps.placeholder }}
                </span>
              </template>
              <template #option="slotProps">
                <div class="flex items-center">
                  <div class="mr-2">
                    <i class="pi" :class="getAccountIcon(slotProps.option.account_type)"></i>
                  </div>
                  <div>
                    <div>{{ slotProps.option.name }}</div>
                    <div class="text-xs text-gray-500">
                      {{ slotProps.option.account_number }} • {{ slotProps.option.bank_name }}
                    </div>
                  </div>
                </div>
              </template>
            </Dropdown>
            <small v-if="submitted && !formData.account_id" class="p-error">
              Account is required.
            </small>
          </div>

          <div class="field">
            <label for="transaction_date">Date <span class="text-red-500">*</span></label>
            <Calendar 
              id="transaction_date"
              v-model="formData.transaction_date"
              dateFormat="yy-mm-dd"
              showIcon
              class="w-full"
              :class="{ 'p-invalid': submitted && !formData.transaction_date }"
            />
            <small v-if="submitted && !formData.transaction_date" class="p-error">
              Date is required.
            </small>
          </div>

          <div class="field">
            <label for="value_date">Value Date</label>
            <Calendar 
              id="value_date"
              v-model="formData.value_date"
              dateFormat="yy-mm-dd"
              showIcon
              class="w-full"
            />
          </div>

          <div class="field">
            <label for="amount">Amount <span class="text-red-500">*</span></label>
            <div class="p-inputgroup">
              <span class="p-inputgroup-addon">
                {{ getCurrencySymbol(formData.account_id) }}
              </span>
              <InputNumber 
                id="amount"
                v-model="formData.amount"
                mode="decimal"
                :minFractionDigits="2"
                :maxFractionDigits="2"
                class="w-full"
                :class="{ 'p-invalid': submitted && formData.amount === null }"
              />
            </div>
            <small v-if="submitted && formData.amount === null" class="p-error">
              Amount is required.
            </small>
          </div>

          <div class="field">
            <label>Transaction Type</label>
            <div class="flex border-1 border-round" style="border-color: var(--surface-300);">
              <Button 
                type="button"
                label="Income"
                :class="{
                  'flex-1 font-medium': true,
                  'p-button-success': formData.amount >= 0,
                  'p-button-outlined': formData.amount < 0
                }"
                @click="setTransactionType('income')"
              />
              <Button 
                type="button"
                label="Expense"
                :class="{
                  'flex-1 font-medium': true,
                  'p-button-danger': formData.amount < 0,
                  'p-button-outlined': formData.amount >= 0
                }"
                @click="setTransactionType('expense')"
              />
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="space-y-4">
          <div class="field">
            <label for="reference">Reference</label>
            <InputText 
              id="reference"
              v-model="formData.reference"
              class="w-full"
              placeholder="e.g. Check #123, Transfer ID"
            />
          </div>

          <div class="field">
            <label for="description">Description</label>
            <Textarea 
              id="description"
              v-model="formData.description"
              rows="3"
              class="w-full"
              placeholder="Add a description or notes about this transaction"
            />
          </div>

          <div class="field">
            <label for="category">Category</label>
            <Dropdown 
              id="category"
              v-model="formData.category"
              :options="categoryOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Select a category"
              class="w-full"
              :filter="true"
            >
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex items-center">
                  <Tag 
                    :value="getCategoryLabel(slotProps.value)" 
                    :severity="getCategorySeverity(slotProps.value)"
                    class="text-xs"
                  />
                </div>
                <span v-else>
                  {{ slotProps.placeholder }}
                </span>
              </template>
              <template #option="slotProps">
                <Tag 
                  :value="slotProps.option.label" 
                  :severity="getCategorySeverity(slotProps.option.value)"
                  class="text-xs w-full text-left"
                />
              </template>
            </Dropdown>
          </div>

          <div class="field">
            <label for="payment_method">Payment Method</label>
            <Dropdown 
              id="payment_method"
              v-model="formData.payment_method"
              :options="paymentMethodOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Select payment method"
              class="w-full"
            />
          </div>

          <div class="field">
            <label for="status">Status</label>
            <Dropdown 
              id="status"
              v-model="formData.status"
              :options="statusOptions"
              optionLabel="label"
              optionValue="value"
              class="w-full"
            />
          </div>
        </div>
      </div>

      <div class="flex justify-between items-center mt-6">
        <div>
          <Button 
            v-if="editing"
            label="Delete" 
            icon="pi pi-trash" 
            class="p-button-text p-button-danger"
            @click="confirmDelete"
          />
        </div>
        <div class="space-x-2">
          <Button 
            label="Cancel" 
            icon="pi pi-times" 
            class="p-button-text" 
            @click="onClose" 
          />
          <Button 
            type="submit" 
            :label="editing ? 'Update' : 'Create'" 
            icon="pi pi-check" 
            :loading="loading"
          />
        </div>
      </div>
    </form>
  </Dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import TransactionService from '@/services/TransactionService';

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  transaction: {
    type: Object,
    default: null
  },
  editing: {
    type: Boolean,
    default: false
  },
  accounts: {
    type: Array,
    required: true,
    default: () => []
  }
});

const emit = defineEmits([
  'update:modelValue',
  'saved',
  'deleted',
  'closed'
]);

const toast = useToast();
const confirm = useConfirm();
const loading = ref(false);
const submitted = ref(false);

// Form data
const formData = ref({
  id: null,
  account_id: null,
  transaction_date: new Date(),
  value_date: null,
  reference: '',
  description: '',
  amount: null,
  category: null,
  payment_method: null,
  status: 'posted',
  related_document_type: null,
  related_document_id: null,
  metadata: null
});

// Constants
const statusOptions = [
  { label: 'Posted', value: 'posted' },
  { label: 'Pending', value: 'pending' },
  { label: 'Cancelled', value: 'cancelled' }
];

const categoryOptions = [
  { label: 'Income', value: 'income' },
  { label: 'Expense', value: 'expense' },
  { label: 'Transfer', value: 'transfer' },
  { label: 'Fee', value: 'fee' },
  { label: 'Interest', value: 'interest' },
  { label: 'Payment', value: 'payment' },
  { label: 'Refund', value: 'refund' },
  { label: 'Deposit', value: 'deposit' },
  { label: 'Withdrawal', value: 'withdrawal' }
];

const paymentMethodOptions = [
  { label: 'Bank Transfer', value: 'bank_transfer' },
  { label: 'Credit Card', value: 'credit_card' },
  { label: 'Debit Card', value: 'debit_card' },
  { label: 'Cash', value: 'cash' },
  { label: 'Check', value: 'check' },
  { label: 'Direct Debit', value: 'direct_debit' },
  { label: 'Standing Order', value: 'standing_order' },
  { label: 'Other', value: 'other' }
];

// Watchers
watch(() => props.transaction, (newVal) => {
  if (newVal) {
    // Update form data when transaction prop changes
    formData.value = {
      id: newVal.id,
      account_id: newVal.account_id,
      transaction_date: new Date(newVal.transaction_date),
      value_date: newVal.value_date ? new Date(newVal.value_date) : null,
      reference: newVal.reference || '',
      description: newVal.description || '',
      amount: Math.abs(newVal.amount) * (newVal.amount >= 0 ? 1 : -1),
      category: newVal.category,
      payment_method: newVal.payment_method,
      status: newVal.status || 'posted',
      related_document_type: newVal.related_document_type,
      related_document_id: newVal.related_document_id,
      metadata: newVal.metadata
    };
  } else {
    // Reset form when transaction is cleared
    resetForm();
  }
}, { immediate: true });

// Methods
const saveTransaction = async () => {
  submitted.value = true;
  
  // Validate form
  if (!formData.value.account_id || !formData.value.transaction_date || formData.value.amount === null) {
    return;
  }
  
  try {
    loading.value = true;
    
    // Prepare data for API
    const data = { ...formData.value };
    
    // Convert dates to ISO string
    if (data.transaction_date) {
      data.transaction_date = data.transaction_date.toISOString().split('T')[0];
    }
    
    if (data.value_date) {
      data.value_date = data.value_date.toISOString().split('T')[0];
    }
    
    // Call API
    let response;
    if (props.editing && data.id) {
      response = await TransactionService.updateTransaction(data.id, data);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Transaction updated successfully',
        life: 3000
      });
    } else {
      response = await TransactionService.createTransaction(data);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Transaction created successfully',
        life: 3000
      });
    }
    
    // Emit saved event with the response data
    emit('saved', response.data);
    
    // Close the dialog
    emit('update:modelValue', false);
  } catch (error) {
    console.error('Error saving transaction:', error);
    
    let errorMessage = 'Failed to save transaction';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response?.data?.errors) {
      errorMessage = Object.values(error.response.data.errors).flat().join(' ');
    }
    
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage,
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

const confirmDelete = () => {
  confirm.require({
    message: 'Are you sure you want to delete this transaction?',
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: deleteTransaction,
    reject: () => {}
  });
};

const deleteTransaction = async () => {
  if (!formData.value.id) return;
  
  try {
    await TransactionService.deleteTransaction(formData.value.id);
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Transaction deleted successfully',
      life: 3000
    });
    
    // Emit deleted event
    emit('deleted', formData.value.id);
    
    // Close the dialog
    emit('update:modelValue', false);
  } catch (error) {
    console.error('Error deleting transaction:', error);
    
    let errorMessage = 'Failed to delete transaction';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage,
      life: 5000
    });
  }
};

const setTransactionType = (type) => {
  if (formData.value.amount === null || formData.value.amount === 0) return;
  
  const amount = Math.abs(formData.value.amount);
  formData.value.amount = type === 'income' ? amount : -amount;
};

const resetForm = () => {
  formData.value = {
    id: null,
    account_id: null,
    transaction_date: new Date(),
    value_date: null,
    reference: '',
    description: '',
    amount: null,
    category: null,
    payment_method: null,
    status: 'posted',
    related_document_type: null,
    related_document_id: null,
    metadata: null
  };
  submitted.value = false;
};

const onClose = () => {
  emit('update:modelValue', false);
  emit('closed');
};

// Helper methods
const getAccountIcon = (accountType) => {
  switch (accountType) {
    case 'savings':
      return 'pi pi-wallet';
    case 'credit_card':
      return 'pi pi-credit-card';
    case 'loan':
      return 'pi pi-money-bill';
    default:
      return 'pi pi-bank';
  }
};

const getAccountById = (id) => {
  return props.accounts.find(account => account.id === id);
};

const getCurrencySymbol = (accountId) => {
  if (!accountId) return '$';
  const account = getAccountById(accountId);
  return account?.currency?.symbol || '$';
};

const getCategorySeverity = (category) => {
  if (!category) return 'info';
  
  const severityMap = {
    income: 'success',
    expense: 'danger',
    transfer: 'info',
    fee: 'warning',
    interest: 'success',
    payment: 'primary',
    refund: 'help',
    deposit: 'success',
    withdrawal: 'danger'
  };
  
  return severityMap[category] || 'info';
};

const getCategoryLabel = (value) => {
  if (!value) return '';
  const category = categoryOptions.find(cat => cat.value === value);
  return category ? category.label : value;
};
</script>
