<template>
  <Dialog 
    v-model:visible="visible" 
    :header="isEditing ? 'Edit Budget' : 'Create New Budget'"
    :modal="true"
    :style="{ width: '800px' }"
    @hide="handleClose"
  >
    <form @submit.prevent="handleSubmit">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="name">Budget Name <span class="text-red-500">*</span></label>
            <InputText 
              id="name"
              v-model="formData.name"
              class="w-full"
              :class="{ 'p-invalid': errors.name }"
              placeholder="Enter budget name"
            />
            <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="department">Department <span class="text-red-500">*</span></label>
            <Dropdown 
              id="department"
              v-model="formData.departmentId"
              :options="departments"
              optionLabel="name"
              optionValue="id"
              placeholder="Select department"
              class="w-full"
              :class="{ 'p-invalid': errors.departmentId }"
            />
            <small v-if="errors.departmentId" class="p-error">{{ errors.departmentId }}</small>
          </div>
        </div>
        
        <div class="col-12">
          <div class="field">
            <label for="description">Description</label>
            <Textarea 
              id="description"
              v-model="formData.description"
              rows="2"
              class="w-full"
              placeholder="Enter budget description"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="startDate">Start Date <span class="text-red-500">*</span></label>
            <Calendar 
              id="startDate"
              v-model="formData.startDate"
              dateFormat="yy-mm-dd"
              :showIcon="true"
              class="w-full"
              :class="{ 'p-invalid': errors.startDate }"
            />
            <small v-if="errors.startDate" class="p-error">{{ errors.startDate }}</small>
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="endDate">End Date <span class="text-red-500">*</span></label>
            <Calendar 
              id="endDate"
              v-model="formData.endDate"
              dateFormat="yy-mm-dd"
              :showIcon="true"
              class="w-full"
              :class="{ 'p-invalid': errors.endDate }"
            />
            <small v-if="errors.endDate" class="p-error">{{ errors.endDate }}</small>
          </div>
        </div>
        
        <div class="col-12">
          <div class="field">
            <label>Budget Categories</label>
            <div class="budget-categories">
              <div v-for="(category, index) in formData.categories" :key="index" class="category-row mb-2">
                <div class="grid">
                  <div class="col-5">
                    <InputText 
                      v-model="category.name"
                      placeholder="Category name"
                      class="w-full"
                    />
                  </div>
                  <div class="col-5">
                    <InputNumber 
                      v-model="category.amount"
                      mode="currency"
                      currency="USD"
                      locale="en-US"
                      placeholder="Amount"
                      class="w-full"
                    />
                  </div>
                  <div class="col-2">
                    <Button 
                      icon="pi pi-trash"
                      class="p-button-danger p-button-text"
                      @click="removeCategory(index)"
                      :disabled="formData.categories.length <= 1"
                    />
                  </div>
                </div>
              </div>
              
              <Button 
                label="Add Category"
                icon="pi pi-plus"
                class="p-button-outlined p-button-sm"
                @click="addCategory"
              />
            </div>
          </div>
        </div>
        
        <div class="col-12">
          <div class="field">
            <div class="flex justify-content-between align-items-center p-3 bg-primary-50 border-round">
              <span class="font-medium">Total Budget Amount:</span>
              <span class="text-2xl font-bold text-primary">
                {{ formatCurrency(totalAmount) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </form>
    
    <template #footer>
      <Button 
        label="Cancel"
        class="p-button-text"
        @click="handleClose"
        :disabled="saving"
      />
      <Button 
        :label="isEditing ? 'Update' : 'Create'"
        @click="handleSubmit"
        :loading="saving"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface BudgetCategory {
  name: string
  amount: number
}

interface BudgetFormData {
  name: string
  description: string
  departmentId: number | null
  startDate: Date | null
  endDate: Date | null
  categories: BudgetCategory[]
}

interface Budget {
  id?: number
  name: string
  description: string
  departmentId: number
  startDate: string
  endDate: string
  categories: BudgetCategory[]
}

const props = defineProps<{
  visible: boolean
  budget?: Budget
}>()

const emit = defineEmits(['update:visible', 'save'])

const saving = ref(false)
const errors = ref<Record<string, string>>({})

const departments = ref([
  { id: 1, name: 'Finance' },
  { id: 2, name: 'Marketing' },
  { id: 3, name: 'Operations' },
  { id: 4, name: 'HR' },
  { id: 5, name: 'IT' }
])

const formData = ref<BudgetFormData>({
  name: '',
  description: '',
  departmentId: null,
  startDate: null,
  endDate: null,
  categories: [{ name: '', amount: 0 }]
})

const isEditing = computed(() => !!props.budget?.id)

const totalAmount = computed(() => {
  return formData.value.categories.reduce((sum, category) => sum + (category.amount || 0), 0)
})

const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    departmentId: null,
    startDate: null,
    endDate: null,
    categories: [{ name: '', amount: 0 }]
  }
  errors.value = {}
}

const loadBudgetData = () => {
  if (props.budget) {
    formData.value = {
      name: props.budget.name,
      description: props.budget.description,
      departmentId: props.budget.departmentId,
      startDate: new Date(props.budget.startDate),
      endDate: new Date(props.budget.endDate),
      categories: [...props.budget.categories]
    }
  }
}

const validateForm = () => {
  errors.value = {}
  
  if (!formData.value.name.trim()) {
    errors.value.name = 'Budget name is required'
  }
  
  if (!formData.value.departmentId) {
    errors.value.departmentId = 'Department is required'
  }
  
  if (!formData.value.startDate) {
    errors.value.startDate = 'Start date is required'
  }
  
  if (!formData.value.endDate) {
    errors.value.endDate = 'End date is required'
  }
  
  if (formData.value.startDate && formData.value.endDate && formData.value.startDate >= formData.value.endDate) {
    errors.value.endDate = 'End date must be after start date'
  }
  
  return Object.keys(errors.value).length === 0
}

const addCategory = () => {
  formData.value.categories.push({ name: '', amount: 0 })
}

const removeCategory = (index: number) => {
  if (formData.value.categories.length > 1) {
    formData.value.categories.splice(index, 1)
  }
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  saving.value = true
  try {
    const budgetData = {
      ...formData.value,
      startDate: formData.value.startDate?.toISOString().split('T')[0],
      endDate: formData.value.endDate?.toISOString().split('T')[0],
      totalAmount: totalAmount.value
    }
    
    emit('save', budgetData)
    handleClose()
  } finally {
    saving.value = false
  }
}

const handleClose = () => {
  emit('update:visible', false)
  resetForm()
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

// Watch for budget prop changes
watch(() => props.budget, () => {
  if (props.visible) {
    if (props.budget) {
      loadBudgetData()
    } else {
      resetForm()
    }
  }
}, { immediate: true })

// Watch for dialog visibility changes
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    if (props.budget) {
      loadBudgetData()
    } else {
      resetForm()
    }
  }
})
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color-secondary);
}

.category-row {
  border: 1px solid var(--surface-border);
  border-radius: 6px;
  padding: 0.5rem;
  background: var(--surface-50);
}

.budget-categories {
  border: 1px solid var(--surface-border);
  border-radius: 6px;
  padding: 1rem;
  background: var(--surface-0);
}
</style>