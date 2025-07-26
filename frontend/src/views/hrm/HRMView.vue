<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Human Resources Management</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Total Employees</v-card-title>
          <v-card-text>
            <div class="text-h3 text-primary">{{ employees.length }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Active Employees</v-card-title>
          <v-card-text>
            <div class="text-h3 text-success">{{ activeEmployees }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>On Leave</v-card-title>
          <v-card-text>
            <div class="text-h3 text-warning">{{ onLeaveEmployees }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Departments</v-card-title>
          <v-card-text>
            <div class="text-h3 text-info">{{ departments.length }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between">
            Employee Directory
            <v-btn color="primary" @click="showAddDialog = true">
              <v-icon start>mdi-plus</v-icon>
              Add Employee
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :items="employees"
              :headers="headers"
              class="elevation-1"
            >
              <template #item.status="{ item }">
                <v-chip :color="getStatusColor(item.status)" size="small">
                  {{ item.status }}
                </v-chip>
              </template>
              <template #item.salary="{ item }">
                {{ formatCurrency(item.salary) }}
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Add Employee Dialog -->
    <v-dialog v-model="showAddDialog" max-width="600px">
      <v-card>
        <v-card-title>Add Employee</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="addEmployee">
            <v-text-field v-model="newEmployee.name" label="Full Name" required />
            <v-text-field v-model="newEmployee.email" label="Email" type="email" required />
            <v-text-field v-model="newEmployee.position" label="Position" required />
            <v-select v-model="newEmployee.department" :items="departments" label="Department" required />
            <v-text-field v-model="newEmployee.salary" label="Salary" type="number" prefix="$" required />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showAddDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="addEmployee">Add Employee</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'

const showAddDialog = ref(false)

const employees = ref([
  { id: 1, name: 'John Doe', email: 'john@company.com', position: 'Developer', department: 'IT', salary: 75000, status: 'Active' },
  { id: 2, name: 'Jane Smith', email: 'jane@company.com', position: 'Manager', department: 'HR', salary: 85000, status: 'Active' },
  { id: 3, name: 'Bob Johnson', email: 'bob@company.com', position: 'Analyst', department: 'Finance', salary: 65000, status: 'On Leave' }
])

const departments = ['IT', 'HR', 'Finance', 'Marketing', 'Operations']

const newEmployee = ref({
  name: '',
  email: '',
  position: '',
  department: '',
  salary: ''
})

const headers = [
  { title: 'Name', key: 'name' },
  { title: 'Email', key: 'email' },
  { title: 'Position', key: 'position' },
  { title: 'Department', key: 'department' },
  { title: 'Salary', key: 'salary' },
  { title: 'Status', key: 'status' }
]

const activeEmployees = computed(() => employees.value.filter(emp => emp.status === 'Active').length)
const onLeaveEmployees = computed(() => employees.value.filter(emp => emp.status === 'On Leave').length)

const getStatusColor = (status) => {
  switch (status) {
    case 'Active': return 'success'
    case 'On Leave': return 'warning'
    case 'Inactive': return 'error'
    default: return 'grey'
  }
}

const addEmployee = () => {
  employees.value.push({
    id: Date.now(),
    name: newEmployee.value.name,
    email: newEmployee.value.email,
    position: newEmployee.value.position,
    department: newEmployee.value.department,
    salary: parseFloat(newEmployee.value.salary),
    status: 'Active'
  })
  newEmployee.value = { name: '', email: '', position: '', department: '', salary: '' }
  showAddDialog.value = false
}

const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
</script>