<template>
  <div class="employees-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Employee Management</h1>
        <p class="text-color-secondary">Manage your organization's employees</p>
      </div>
      <Button label="Add Employee" icon="pi pi-plus" @click="openNew" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="employees" :loading="loading" paginator :rows="10">
          <Column field="employeeId" header="ID" sortable />
          <Column field="name" header="Name" sortable />
          <Column field="email" header="Email" sortable />
          <Column field="department" header="Department" sortable />
          <Column field="position" header="Position" sortable />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editEmployee(data)" />
              <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="confirmDeleteEmployee(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="employeeDialog" header="Employee Details" :modal="true" :style="{width: '500px'}">
      <div class="field">
        <label>Name</label>
        <InputText v-model="employee.name" class="w-full" :class="{'p-invalid': submitted && !employee.name}" />
        <small class="p-error" v-if="submitted && !employee.name">Name is required.</small>
      </div>
      <div class="field">
        <label>Email</label>
        <InputText v-model="employee.email" class="w-full" :class="{'p-invalid': submitted && !employee.email}" />
        <small class="p-error" v-if="submitted && !employee.email">Email is required.</small>
      </div>
      <div class="field">
        <label>Phone</label>
        <InputText v-model="employee.phone" class="w-full" />
      </div>
      <div class="field">
        <label>Department</label>
        <Dropdown v-model="employee.department" :options="departments" placeholder="Select Department" class="w-full" />
      </div>
      <div class="field">
        <label>Position</label>
        <InputText v-model="employee.position" class="w-full" />
      </div>
      <div class="field">
        <label>Status</label>
        <Dropdown v-model="employee.status" :options="statuses" optionLabel="label" optionValue="value" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="hideDialog" />
        <Button label="Save" @click="saveEmployee" />
      </template>
    </Dialog>

    <Dialog v-model:visible="deleteEmployeeDialog" header="Confirm" :modal="true" :style="{width: '450px'}">
      <div class="flex align-items-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="employee">Are you sure you want to delete <b>{{ employee.name }}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" class="p-button-text" @click="deleteEmployeeDialog = false" />
        <Button label="Yes" class="p-button-danger" @click="deleteEmployee" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { hrmService, type Employee } from '@/services/hrmService'

const toast = useToast()
const loading = ref(false)
const employeeDialog = ref(false)
const deleteEmployeeDialog = ref(false)
const submitted = ref(false)

const employees = ref<Employee[]>([])
const employee = ref<Employee>({
  employeeId: '',
  name: '',
  email: '',
  phone: '',
  department: '',
  position: '',
  status: 'active'
})

const departments = ref(['IT', 'HR', 'Finance', 'Sales', 'Marketing', 'Operations'])
const statuses = ref([
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'On Leave', value: 'on_leave' },
  { label: 'Terminated', value: 'terminated' }
])

const openNew = () => {
  employee.value = {
    employeeId: `EMP${Date.now()}`,
    name: '',
    email: '',
    phone: '',
    department: '',
    position: '',
    status: 'active'
  }
  submitted.value = false
  employeeDialog.value = true
}

const editEmployee = (emp: Employee) => {
  employee.value = { ...emp }
  employeeDialog.value = true
}

const hideDialog = () => {
  employeeDialog.value = false
  submitted.value = false
}

const saveEmployee = async () => {
  submitted.value = true
  if (employee.value.name && employee.value.email) {
    try {
      if (employee.value.id) {
        await hrmService.updateEmployee(employee.value.id, employee.value)
        toast.add({ severity: 'success', summary: 'Success', detail: 'Employee updated', life: 3000 })
      } else {
        await hrmService.createEmployee(employee.value)
        toast.add({ severity: 'success', summary: 'Success', detail: 'Employee created', life: 3000 })
      }
      employeeDialog.value = false
      await loadEmployees()
    } catch (error: any) {
      toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'Operation failed', life: 3000 })
    }
  }
}

const confirmDeleteEmployee = (emp: Employee) => {
  employee.value = { ...emp }
  deleteEmployeeDialog.value = true
}

const deleteEmployee = async () => {
  try {
    if (employee.value.id) {
      await hrmService.deleteEmployee(employee.value.id)
      deleteEmployeeDialog.value = false
      toast.add({ severity: 'success', summary: 'Success', detail: 'Employee deleted', life: 3000 })
      await loadEmployees()
    }
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'Delete failed', life: 3000 })
  }
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'active':
      return 'success'
    case 'inactive':
      return 'danger'
    case 'on_leave':
      return 'warning'
    default:
      return 'info'
  }
}

const loadEmployees = async () => {
  loading.value = true
  try {
    employees.value = await hrmService.getEmployees()
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load employees', life: 3000 })
    // Fallback to mock data for demo
    employees.value = [
      { id: '1', employeeId: 'EMP001', name: 'John Doe', email: 'john@company.com', phone: '123-456-7890', department: 'IT', position: 'Software Engineer', status: 'active' },
      { id: '2', employeeId: 'EMP002', name: 'Jane Smith', email: 'jane@company.com', phone: '123-456-7891', department: 'HR', position: 'HR Manager', status: 'active' },
      { id: '3', employeeId: 'EMP003', name: 'Mike Johnson', email: 'mike@company.com', phone: '123-456-7892', department: 'Finance', position: 'Financial Analyst', status: 'on_leave' }
    ]
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadEmployees()
})
</script>

<style scoped>
.employees-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>