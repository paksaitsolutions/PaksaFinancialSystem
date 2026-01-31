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
          <Column field="employee_id" header="ID" sortable />
          <Column header="Name" sortable>
            <template #body="{ data }">
              {{ data.first_name }} {{ data.last_name }}
            </template>
          </Column>
          <Column field="email" header="Email" sortable />
          <Column field="job_title" header="Position" sortable />
          <Column header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.is_active ? 'Active' : 'Inactive'" :severity="data.is_active ? 'success' : 'danger'" />
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

    <EmployeeForm 
      v-model:visible="employeeDialog" 
      :employee="employee" 
      :departments="departmentsList"
      :saving="saving"
      @save="saveEmployee" 
      @cancel="hideDialog"
    />

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
import { hrmService, type Employee, type Department } from '@/services/hrmService'

const toast = useToast()
const loading = ref(false)
const employeeDialog = ref(false)
const deleteEmployeeDialog = ref(false)
const saving = ref(false)

const employees = ref<Employee[]>([])
const employee = ref<Employee | null>(null)
const departmentsList = ref<Department[]>([])

const openNew = () => {
  employee.value = null
  employeeDialog.value = true
}

const editEmployee = (emp: Employee) => {
  employee.value = { ...emp }
  employeeDialog.value = true
}

const hideDialog = () => {
  employeeDialog.value = false
}

const saveEmployee = async (employeeData: any) => {
  saving.value = true
  try {
    if (employee.value?.id) {
      await hrmService.updateEmployee(employee.value.id, employeeData)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Employee updated', life: 3000 })
    } else {
      await hrmService.createEmployee(employeeData)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Employee created', life: 3000 })
    }
    employeeDialog.value = false
    await loadEmployees()
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'Operation failed', life: 3000 })
  } finally {
    saving.value = false
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

const loadEmployees = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/v1/hrm/employees')
    if (response.ok) {
      employees.value = await response.json()
    } else {
      employees.value = []
    }
  } catch (error: any) {
    console.error('Error loading employees:', error)
    employees.value = []
  } finally {
    loading.value = false
  }
}

const loadDepartments = async () => {
  try {
    const response = await fetch('/api/v1/hrm/departments')
    if (response.ok) {
      departmentsList.value = await response.json()
    } else {
      departmentsList.value = []
    }
  } catch (error) {
    console.error('Error loading departments:', error)
    departmentsList.value = []
  }
}

onMounted(() => {
  loadEmployees()
  loadDepartments()
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