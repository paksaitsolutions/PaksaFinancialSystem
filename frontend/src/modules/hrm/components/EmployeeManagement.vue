<template>
  <div class="employee-management">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h3>Employee Management</h3>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openEmployeeDialog">
          Add Employee
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <!-- Filters -->
        <v-row class="mb-4">
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.department"
              label="Department"
              :items="departments"
              clearable
              @update:model-value="fetchEmployees"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.employment_type"
              label="Employment Type"
              :items="employmentTypes"
              clearable
              @update:model-value="fetchEmployees"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="6" class="d-flex align-center justify-end">
            <v-btn
              prepend-icon="mdi-refresh"
              @click="fetchEmployees"
              :loading="loading"
            >
              Refresh
            </v-btn>
          </v-col>
        </v-row>
        
        <v-data-table
          :headers="headers"
          :items="employees"
          :loading="loading"
          class="elevation-1"
        >
          <template v-slot:item.name="{ item }">
            <div>
              <strong>{{ item.first_name }} {{ item.last_name }}</strong>
              <div class="text-caption">{{ item.employee_id }}</div>
            </div>
          </template>
          
          <template v-slot:item.contact="{ item }">
            <div>
              <div>{{ item.email }}</div>
              <div v-if="item.phone" class="text-caption">{{ item.phone }}</div>
            </div>
          </template>
          
          <template v-slot:item.employment="{ item }">
            <div>
              <div>{{ item.position || 'N/A' }}</div>
              <div class="text-caption">{{ item.department || 'Unassigned' }}</div>
            </div>
          </template>
          
          <template v-slot:item.hire_date="{ item }">
            {{ formatDate(item.hire_date) }}
          </template>
          
          <template v-slot:item.is_active="{ item }">
            <v-chip :color="item.is_active ? 'success' : 'error'" size="small">
              {{ item.is_active ? 'Active' : 'Inactive' }}
            </v-chip>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn icon size="small" v-bind="props">
                  <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              
              <v-list>
                <v-list-item @click="editEmployee(item)">
                  <v-list-item-title>Edit</v-list-item-title>
                </v-list-item>
                
                <v-list-item @click="viewProfile(item)">
                  <v-list-item-title>View Profile</v-list-item-title>
                </v-list-item>
                
                <v-list-item @click="viewAttendance(item)">
                  <v-list-item-title>Attendance</v-list-item-title>
                </v-list-item>
                
                <v-list-item @click="viewLeaves(item)">
                  <v-list-item-title>Leave History</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
    
    <!-- Employee Dialog -->
    <v-dialog v-model="employeeDialog.show" max-width="800px">
      <v-card>
        <v-card-title>{{ employeeDialog.isEdit ? 'Edit' : 'Add' }} Employee</v-card-title>
        <v-card-text>
          <v-form ref="employeeForm" v-model="employeeDialog.valid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="employeeDialog.formData.employee_id"
                  label="Employee ID*"
                  :rules="[v => !!v || 'Employee ID is required']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="employeeDialog.formData.email"
                  label="Email*"
                  type="email"
                  :rules="[v => !!v || 'Email is required']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="employeeDialog.formData.first_name"
                  label="First Name*"
                  :rules="[v => !!v || 'First name is required']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="employeeDialog.formData.last_name"
                  label="Last Name*"
                  :rules="[v => !!v || 'Last name is required']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="employeeDialog.formData.phone"
                  label="Phone"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="employeeDialog.formData.hire_date"
                  label="Hire Date*"
                  type="date"
                  :rules="[v => !!v || 'Hire date is required']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="employeeDialog.formData.department"
                  label="Department"
                  :items="departments"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="employeeDialog.formData.position"
                  label="Position"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="employeeDialog.formData.employment_type"
                  label="Employment Type"
                  :items="employmentTypes"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="employeeDialog.formData.salary"
                  label="Salary"
                  type="number"
                  step="0.01"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="employeeDialog.formData.date_of_birth"
                  label="Date of Birth"
                  type="date"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="employeeDialog.formData.emergency_contact"
                  label="Emergency Contact"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="employeeDialog.formData.address"
                  label="Address"
                  rows="2"
                ></v-textarea>
              </v-col>
              
              <v-col cols="12">
                <v-checkbox
                  v-model="employeeDialog.formData.is_active"
                  label="Active"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="employeeDialog.show = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="employeeDialog.saving"
            :disabled="!employeeDialog.valid"
            @click="saveEmployee"
          >
            {{ employeeDialog.isEdit ? 'Update' : 'Create' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

const { showSnackbar } = useSnackbar();

// Data
const loading = ref(false);
const employees = ref([]);

const filters = reactive({
  department: null,
  employment_type: null
});

const employeeDialog = reactive({
  show: false,
  isEdit: false,
  valid: false,
  saving: false,
  formData: {
    employee_id: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    department: '',
    position: '',
    hire_date: '',
    employment_type: 'full_time',
    salary: null,
    date_of_birth: '',
    address: '',
    emergency_contact: '',
    is_active: true
  },
  editId: null
});

// Options
const departments = [
  'Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations'
];

const employmentTypes = [
  { title: 'Full Time', value: 'full_time' },
  { title: 'Part Time', value: 'part_time' },
  { title: 'Contract', value: 'contract' }
];

const headers = [
  { title: 'Employee', key: 'name', sortable: true },
  { title: 'Contact', key: 'contact', sortable: false },
  { title: 'Role', key: 'employment', sortable: false },
  { title: 'Hire Date', key: 'hire_date', sortable: true },
  { title: 'Type', key: 'employment_type', sortable: true },
  { title: 'Status', key: 'is_active', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
];

// Methods
const fetchEmployees = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    if (filters.department) params.append('department', filters.department);
    if (filters.employment_type) params.append('employment_type', filters.employment_type);
    
    const response = await apiClient.get(`/api/v1/hrm/employees?${params}`);
    employees.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load employees', 'error');
    console.error('Error fetching employees:', error);
  } finally {
    loading.value = false;
  }
};

const openEmployeeDialog = () => {
  employeeDialog.isEdit = false;
  employeeDialog.editId = null;
  employeeDialog.formData = {
    employee_id: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    department: '',
    position: '',
    hire_date: '',
    employment_type: 'full_time',
    salary: null,
    date_of_birth: '',
    address: '',
    emergency_contact: '',
    is_active: true
  };
  employeeDialog.show = true;
};

const editEmployee = (employee) => {
  employeeDialog.isEdit = true;
  employeeDialog.editId = employee.id;
  employeeDialog.formData = { ...employee };
  employeeDialog.show = true;
};

const saveEmployee = async () => {
  if (!employeeDialog.valid) return;
  
  employeeDialog.saving = true;
  try {
    if (employeeDialog.isEdit) {
      await apiClient.put(
        `/api/v1/hrm/employees/${employeeDialog.editId}`,
        employeeDialog.formData
      );
      showSnackbar('Employee updated successfully', 'success');
    } else {
      await apiClient.post('/api/v1/hrm/employees', employeeDialog.formData);
      showSnackbar('Employee created successfully', 'success');
    }
    
    employeeDialog.show = false;
    fetchEmployees();
  } catch (error) {
    showSnackbar('Failed to save employee', 'error');
    console.error('Save employee error:', error);
  } finally {
    employeeDialog.saving = false;
  }
};

const viewProfile = (employee) => {
  console.log('View profile:', employee);
};

const viewAttendance = (employee) => {
  console.log('View attendance:', employee);
};

const viewLeaves = (employee) => {
  console.log('View leaves:', employee);
};

// Lifecycle
onMounted(() => {
  fetchEmployees();
});
</script>

<style scoped>
.employee-management {
  padding: 16px;
}
</style>