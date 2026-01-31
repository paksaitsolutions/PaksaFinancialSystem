<template>
  <form @submit.prevent="handleSubmit" class="p-fluid">
    <div class="grid">
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="name">Budget Name *</label>
          <InputText
            id="name"
            v-model="form.name"
            :class="{ 'p-invalid': submitted && !form.name }"
            placeholder="Enter budget name"
          />
          <small v-if="submitted && !form.name" class="p-error">Budget name is required</small>
        </div>
      </div>

      <div class="col-12 md:col-6">
        <div class="field">
          <label for="type">Budget Type *</label>
          <Dropdown
            id="type"
            v-model="form.type"
            :options="budgetTypes"
            option-label="label"
            option-value="value"
            :class="{ 'p-invalid': submitted && !form.type }"
            placeholder="Select budget type"
          />
          <small v-if="submitted && !form.type" class="p-error">Budget type is required</small>
        </div>
      </div>

      <div class="col-12 md:col-6">
        <div class="field">
          <label for="amount">Total Amount *</label>
          <InputNumber
            id="amount"
            v-model="form.amount"
            :class="{ 'p-invalid': submitted && (!form.amount || form.amount <= 0) }"
            mode="currency"
            currency="USD"
            locale="en-US"
            placeholder="0.00"
          />
          <small v-if="submitted && (!form.amount || form.amount <= 0)" class="p-error">
            Amount must be greater than 0
          </small>
        </div>
      </div>

      <div class="col-12 md:col-6">
        <div class="field">
          <label for="status">Status</label>
          <Dropdown
            id="status"
            v-model="form.status"
            :options="statusOptions"
            option-label="label"
            option-value="value"
            placeholder="Select status"
          />
        </div>
      </div>

      <div class="col-12 md:col-6">
        <div class="field">
          <label for="startDate">Start Date *</label>
          <Calendar
            id="startDate"
            v-model="form.start_date"
            :class="{ 'p-invalid': submitted && !form.start_date }"
            date-format="yy-mm-dd"
            placeholder="Select start date"
          />
          <small v-if="submitted && !form.start_date" class="p-error">Start date is required</small>
        </div>
      </div>

      <div class="col-12 md:col-6">
        <div class="field">
          <label for="endDate">End Date *</label>
          <Calendar
            id="endDate"
            v-model="form.end_date"
            :class="{ 'p-invalid': submitted && !form.end_date }"
            date-format="yy-mm-dd"
            placeholder="Select end date"
            :min-date="form.start_date"
          />
          <small v-if="submitted && !form.end_date" class="p-error">End date is required</small>
        </div>
      </div>

      <div class="col-12">
        <div class="field">
          <label for="description">Description</label>
          <Textarea
            id="description"
            v-model="form.description"
            rows="3"
            placeholder="Enter budget description"
          />
        </div>
      </div>
    </div>

    <!-- Line Items Section -->
    <div class="mt-4">
      <div class="flex justify-content-between align-items-center mb-3">
        <h4 class="text-lg font-semibold">Budget Line Items</h4>
        <Button
          type="button"
          label="Add Line Item"
          icon="pi pi-plus"
          size="small"
          outlined
          @click="addLineItem"
        />
      </div>

      <DataTable
        :value="form.line_items"
        class="p-datatable-sm"
        responsive-layout="scroll"
      >
        <Column field="category" header="Category">
          <template #body="{ data, index }">
            <InputText
              v-model="data.category"
              placeholder="Category"
              class="w-full"
            />
          </template>
        </Column>
        <Column field="description" header="Description">
          <template #body="{ data, index }">
            <InputText
              v-model="data.description"
              placeholder="Description"
              class="w-full"
            />
          </template>
        </Column>
        <Column field="amount" header="Amount">
          <template #body="{ data, index }">
            <InputNumber
              v-model="data.amount"
              mode="currency"
              currency="USD"
              locale="en-US"
              class="w-full"
            />
          </template>
        </Column>
        <Column header="Actions" style="width: 80px">
          <template #body="{ index }">
            <Button
              icon="pi pi-trash"
              size="small"
              outlined
              severity="danger"
              @click="removeLineItem(index)"
            />
          </template>
        </Column>
      </DataTable>

      <div v-if="form.line_items.length > 0" class="mt-3 text-right">
        <strong>Total Line Items: {{ formatCurrency(lineItemsTotal) }}</strong>
      </div>
    </div>

    <!-- Form Actions -->
    <div class="flex justify-content-end gap-2 mt-4">
      <Button
        type="button"
        label="Cancel"
        severity="secondary"
        outlined
        @click="$emit('cancel')"
      />
      <Button
        type="submit"
        :label="isEdit ? 'Update Budget' : 'Create Budget'"
        :loading="loading"
        icon="pi pi-save"
      />
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { BudgetCreate, BudgetLineItem } from '../types/budget'

// PrimeVue Components
import Calendar from 'primevue/calendar'

interface Props {
  initialData?: Partial<BudgetCreate>
  loading?: boolean
  isEdit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  isEdit: false
})

const emit = defineEmits<{
  submit: [data: BudgetCreate]
  cancel: []
}>()

const submitted = ref(false)

const form = ref<BudgetCreate>({
  name: '',
  amount: 0,
  type: 'OPERATIONAL',
  start_date: '',
  end_date: '',
  description: '',
  line_items: []
})

const budgetTypes = [
  { label: 'Operational', value: 'OPERATIONAL' },
  { label: 'Capital', value: 'CAPITAL' },
  { label: 'Project', value: 'PROJECT' },
  { label: 'Department', value: 'DEPARTMENT' }
]

const statusOptions = [
  { label: 'Draft', value: 'DRAFT' },
  { label: 'Pending Approval', value: 'PENDING_APPROVAL' },
  { label: 'Approved', value: 'APPROVED' },
  { label: 'Rejected', value: 'REJECTED' },
  { label: 'Archived', value: 'ARCHIVED' }
]

const lineItemsTotal = computed(() => {
  return form.value.line_items?.reduce((sum, item) => sum + (item.amount || 0), 0) || 0
})

const validateForm = () => {
  return form.value.name &&
         form.value.amount &&
         form.value.amount > 0 &&
         form.value.type &&
         form.value.start_date &&
         form.value.end_date
}

const handleSubmit = () => {
  submitted.value = true
  
  if (!validateForm()) {
    return
  }

  // Convert dates to strings if they're Date objects
  const formData = {
    ...form.value,
    start_date: form.value.start_date instanceof Date 
      ? form.value.start_date.toISOString().split('T')[0]
      : form.value.start_date,
    end_date: form.value.end_date instanceof Date
      ? form.value.end_date.toISOString().split('T')[0]
      : form.value.end_date
  }

  emit('submit', formData)
}

const addLineItem = () => {
  if (!form.value.line_items) {
    form.value.line_items = []
  }
  
  form.value.line_items.push({
    category: '',
    description: '',
    amount: 0
  })
}

const removeLineItem = (index: number) => {
  if (form.value.line_items) {
    form.value.line_items.splice(index, 1)
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

// Watch for initial data changes
watch(() => props.initialData, (newData) => {
  if (newData) {
    Object.assign(form.value, newData)
    
    // Convert string dates to Date objects for Calendar component
    if (newData.start_date && typeof newData.start_date === 'string') {
      form.value.start_date = new Date(newData.start_date) as any
    }
    if (newData.end_date && typeof newData.end_date === 'string') {
      form.value.end_date = new Date(newData.end_date) as any
    }
  }
}, { immediate: true })

// Auto-calculate total amount from line items
watch(lineItemsTotal, (newTotal) => {
  if (form.value.line_items && form.value.line_items.length > 0) {
    form.value.amount = newTotal
  }
})
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field > label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

@media (max-width: 768px) {
  .field {
    margin-bottom: 0.75rem;
  }
}
</style>