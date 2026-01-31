<template>
  <div class="employee-list">
    <Card>
      <template #header>
        <div class="flex justify-content-between align-items-center">
          <h2>Employee Management</h2>
          <div class="flex gap-2">
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText v-model="search" placeholder="Search employees" />
            </span>
            <Button label="Add Employee" icon="pi pi-plus" @click="openCreateDialog" />
          </div>
        </div>
      </template>
      
      <template #content>
        <DataTable
          :value="employees"
          :loading="loading"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[10, 25, 50, 100]"
          :globalFilter="search"
          responsiveLayout="scroll"
        >
          <Column field="employee_id" header="ID" sortable />
          <Column field="full_name" header="Name" sortable />
          <Column field="department" header="Department" sortable />
          <Column field="job_title" header="Job Title" sortable />
          <Column field="email" header="Email" sortable />
          <Column field="status" header="Status">
            <template #body="{ data }">
              <Tag :value="data.is_active ? 'Active' : 'Inactive'" :severity="data.is_active ? 'success' : 'danger'" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button icon="pi pi-pencil" size="small" @click="openEditDialog(data)" />
                <Button icon="pi pi-trash" size="small" severity="danger" @click="confirmDelete(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Employee Form Dialog -->
    <EmployeeForm 
      v-model:visible="dialog" 
      :employee="editedIndex !== -1 ? editedItem : null" 
      :departments="departmentsList"
      :saving="saving"
      @save="save" 
      @cancel="close"
    />

    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:visible="deleteDialog" :style="{width: '450px'}" header="Delete Employee" :modal="true">
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to delete this employee? This action cannot be undone.</span>
      </div>
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" @click="deleteDialog = false" class="p-button-text" />
        <Button label="Delete" icon="pi pi-check" @click="deleteItemConfirm" class="p-button-danger" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'

const search = ref('')
const loading = ref(false)
const saving = ref(false)
const dialog = ref(false)
const deleteDialog = ref(false)
const employees = ref([])
const departmentsList = ref([])
const editedIndex = ref(-1)

const defaultItem = {
  id: '',
  employee_id: '',
  first_name: '',
  last_name: '',
  email: '',
  phone_number: '',
  department: '',
  job_title: '',
  employment_type: 'FULL_TIME',
  base_salary: 0,
  is_active: true
}

const editedItem = ref({ ...defaultItem })

const formTitle = computed(() => {
  return editedIndex.value === -1 ? 'New Employee' : 'Edit Employee'
})

const fetchEmployees = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/payroll/employees')
    const data = await response.json()
    employees.value = data.items || []
  } catch (error) {
    console.error('Error fetching employees:', error)
  } finally {
    loading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    const response = await fetch('/api/payroll/employees/departments/list')
    const data = await response.json()
    if (data && data.length) {
      departmentsList.value = data.map((dept: string) => ({ id: dept, name: dept }))
    } else {
      departmentsList.value = [
        { id: 'HR', name: 'HR' },
        { id: 'Finance', name: 'Finance' },
        { id: 'IT', name: 'IT' },
        { id: 'Marketing', name: 'Marketing' },
        { id: 'Operations', name: 'Operations' },
        { id: 'Sales', name: 'Sales' }
      ]
    }
  } catch (error) {
    console.error('Error fetching departments:', error)
    departmentsList.value = [
      { id: 'HR', name: 'HR' },
      { id: 'Finance', name: 'Finance' },
      { id: 'IT', name: 'IT' },
      { id: 'Marketing', name: 'Marketing' },
      { id: 'Operations', name: 'Operations' },
      { id: 'Sales', name: 'Sales' }
    ]
  }
}

const openCreateDialog = () => {
  editedIndex.value = -1
  editedItem.value = { ...defaultItem }
  dialog.value = true
}

const openEditDialog = (item: any) => {
  editedIndex.value = employees.value.indexOf(item)
  editedItem.value = { ...item }
  dialog.value = true
}

const close = () => {
  dialog.value = false
  nextTick(() => {
    editedItem.value = { ...defaultItem }
    editedIndex.value = -1
  })
}

const save = async (employeeData: any) => {
  saving.value = true
  try {
    if (editedIndex.value > -1) {
      await updateEmployee({ ...employeeData, id: editedItem.value.id })
    } else {
      await createEmployee(employeeData)
    }
    close()
    fetchEmployees()
  } catch (error) {
    console.error('Error saving employee:', error)
  } finally {
    saving.value = false
  }
}

const createEmployee = async (employee: any) => {
  await fetch('/api/payroll/employees', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(employee)
  })
}

const updateEmployee = async (employee: any) => {
  await fetch(`/api/payroll/employees/${employee.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(employee)
  })
}

const confirmDelete = (item: any) => {
  editedItem.value = { ...item }
  deleteDialog.value = true
}

const deleteItemConfirm = async () => {
  try {
    await fetch(`/api/payroll/employees/${editedItem.value.id}`, {
      method: 'DELETE'
    })
    deleteDialog.value = false
    fetchEmployees()
  } catch (error) {
    console.error('Error deleting employee:', error)
  }
}

onMounted(() => {
  fetchEmployees()
  fetchDepartments()
})
</script>

<style scoped>
.employee-list {
  padding: 16px;
}
</style>