<template>
  <Dialog 
    :visible="visible" 
    :header="employee?.id ? 'Edit Employee' : 'Add New Employee'"
    :modal="true"
    :style="{ width: '50vw' }"
    :maximizable="true"
    @update:visible="$emit('update:visible', $event)"
  >
    <div class="grid p-fluid">
      <div class="col-12 md:col-4">
        <div class="flex flex-column align-items-center">
          <Avatar 
            :image="formData.avatar" 
            :label="getInitials(formData.first_name + ' ' + formData.last_name)" 
            size="xlarge" 
            shape="circle" 
            class="mb-3"
          />
          <Button 
            label="Change Photo" 
            icon="pi pi-camera" 
            class="p-button-text"
            @click="triggerFileInput"
          />
          <input 
            ref="fileInput" 
            type="file" 
            accept="image/*" 
            style="display: none" 
            @change="handlePhotoChange"
          />
        </div>
      </div>
      
      <div class="col-12 md:col-8">
        <div class="grid formgrid p-fluid">
          <div class="field col-12 md:col-6">
            <label for="first_name">First Name *</label>
            <InputText 
              id="first_name" 
              v-model="formData.first_name" 
              :class="{'p-invalid': submitted && !formData.first_name}"
            />
            <small class="p-error" v-if="submitted && !formData.first_name">First name is required.</small>
          </div>
          
          <div class="field col-12 md:col-6">
            <label for="last_name">Last Name *</label>
            <InputText 
              id="last_name" 
              v-model="formData.last_name"
              :class="{'p-invalid': submitted && !formData.last_name}"
            />
            <small class="p-error" v-if="submitted && !formData.last_name">Last name is required.</small>
          </div>
          
          <div class="field col-12 md:col-6">
            <label for="employee_id">Employee ID *</label>
            <InputText 
              id="employee_id" 
              v-model="formData.employee_id" 
              :disabled="!!employee?.id"
              :class="{'p-invalid': submitted && !formData.employee_id}"
            />
            <small class="p-error" v-if="submitted && !formData.employee_id">Employee ID is required.</small>
          </div>
          
          <div class="field col-12 md:col-6">
            <label for="email">Email *</label>
            <InputText 
              id="email" 
              v-model="formData.email"
              :class="{'p-invalid': submitted && !formData.email}"
            />
            <small class="p-error" v-if="submitted && !formData.email">Email is required.</small>
          </div>
          
          <div class="field col-12 md:col-6">
            <label for="phone_number">Phone</label>
            <InputText id="phone_number" v-model="formData.phone_number" />
          </div>
          
          <div class="field col-12 md:col-6">
            <label for="department">Department</label>
            <Dropdown 
              id="department" 
              v-model="formData.department_id" 
              :options="departments" 
              optionLabel="name" 
              optionValue="id"
              placeholder="Select Department"
            />
          </div>
          
          <div class="field col-12 md:col-6">
            <label for="job_title">Job Title</label>
            <InputText id="job_title" v-model="formData.job_title" />
          </div>
          
          <div class="field col-12 md:col-6">
            <label for="hire_date">Hire Date *</label>
            <Calendar 
              id="hire_date" 
              v-model="formData.hire_date" 
              dateFormat="yy-mm-dd" 
              showIcon
              :class="{'p-invalid': submitted && !formData.hire_date}"
            />
            <small class="p-error" v-if="submitted && !formData.hire_date">Hire date is required.</small>
          </div>
          
          <div class="field col-12 md:col-6">
            <label for="employment_type">Employment Type</label>
            <Dropdown 
              id="employment_type" 
              v-model="formData.employment_type" 
              :options="employmentTypes" 
              optionLabel="label" 
              optionValue="value"
              placeholder="Select Employment Type"
            />
          </div>
          
          <div class="field col-12 md:col-6">
            <label for="base_salary">Base Salary</label>
            <InputNumber 
              id="base_salary" 
              v-model="formData.base_salary" 
              mode="currency" 
              currency="USD" 
              locale="en-US"
            />
          </div>
          
          <div class="field col-12">
            <label>Status</label>
            <div class="flex flex-wrap gap-3 mt-2">
              <div class="flex align-items-center">
                <RadioButton 
                  id="status_active" 
                  name="status" 
                  :value="true" 
                  v-model="formData.is_active"
                />
                <label for="status_active" class="ml-2">Active</label>
              </div>
              <div class="flex align-items-center">
                <RadioButton 
                  id="status_inactive" 
                  name="status" 
                  :value="false" 
                  v-model="formData.is_active"
                />
                <label for="status_inactive" class="ml-2">Inactive</label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <template #footer>
      <Button 
        label="Cancel" 
        icon="pi pi-times" 
        @click="$emit('cancel')" 
        class="p-button-text"
      />
      <Button 
        :label="employee?.id ? 'Update' : 'Save'" 
        icon="pi pi-check" 
        @click="save" 
        class="p-button-primary"
        :loading="saving"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { hrmService, type Employee, type Department } from '@/services/hrmService'
import { useToast } from 'primevue/usetoast'

interface Props {
  visible: boolean
  employee?: Employee | null
  departments?: Department[]
  saving?: boolean
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'save', employee: any): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  employee: null,
  departments: () => [],
  saving: false
})

const emit = defineEmits<Emits>()

const toast = useToast()
const submitted = ref(false)
const fileInput = ref<HTMLInputElement>()

const employmentTypes = [
  { label: 'Full Time', value: 'FULL_TIME' },
  { label: 'Part Time', value: 'PART_TIME' },
  { label: 'Contract', value: 'CONTRACT' },
  { label: 'Temporary', value: 'TEMPORARY' },
  { label: 'Intern', value: 'INTERN' }
]

const defaultFormData = {
  employee_id: '',
  first_name: '',
  last_name: '',
  email: '',
  phone_number: '',
  department_id: '',
  job_title: '',
  hire_date: new Date().toISOString().split('T')[0],
  employment_type: 'FULL_TIME',
  base_salary: 0,
  is_active: true,
  avatar: ''
}

const formData = ref({ ...defaultFormData })

const getInitials = (name: string) => {
  if (!name) return ''
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
}

const isValid = computed(() => {
  return formData.value.first_name && 
         formData.value.last_name && 
         formData.value.employee_id && 
         formData.value.email && 
         formData.value.hire_date
})

const save = () => {
  submitted.value = true
  if (isValid.value) {
    emit('save', { ...formData.value })
    submitted.value = false
  }
}

watch(() => props.employee, (newEmployee) => {
  if (newEmployee) {
    formData.value = { ...newEmployee }
  } else {
    formData.value = { ...defaultFormData }
    // Generate new employee ID
    formData.value.employee_id = `EMP${Date.now().toString().slice(-6)}`
  }
  submitted.value = false
}, { immediate: true })

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handlePhotoChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      toast.add({
        severity: 'error',
        summary: 'File Too Large',
        detail: 'Please select an image smaller than 5MB',
        life: 3000
      })
      return
    }
    
    const reader = new FileReader()
    reader.onload = (e) => {
      formData.value.avatar = e.target?.result as string
      toast.add({
        severity: 'success',
        summary: 'Photo Updated',
        detail: 'Profile photo has been updated',
        life: 3000
      })
    }
    reader.readAsDataURL(file)
  }
}

watch(() => props.visible, (newVisible) => {
  if (!newVisible) {
    submitted.value = false
  }
})
</script>