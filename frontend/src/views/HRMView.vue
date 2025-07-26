<template>
  <div class="hrm-view">
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1>Human Resource Management</h1>
          <p>Advanced HRM dashboard for employee management, payroll, attendance, and analytics.</p>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>Employee Directory</v-card-title>
            <v-data-table :headers="employeeHeaders" :items="employees" :loading="loadingEmployees" class="elevation-1">
              <template #item.actions="{ item }">
                <v-btn icon @click="viewEmployee(item)"><v-icon>mdi-eye</v-icon></v-btn>
                <v-btn icon @click="editEmployee(item)"><v-icon>mdi-pencil</v-icon></v-btn>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>Attendance Overview</v-card-title>
            <v-chart :options="attendanceChartOptions" :data="attendanceData" />
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>Payroll Summary</v-card-title>
            <v-data-table :headers="payrollHeaders" :items="payrolls" :loading="loadingPayrolls" class="elevation-1" />
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>HR Analytics</v-card-title>
            <v-chart :options="analyticsChartOptions" :data="analyticsData" />
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    <v-dialog v-model="showEmployeeDialog" max-width="600">
      <v-card>
        <v-card-title>Employee Details</v-card-title>
        <v-card-text>
          <div v-if="selectedEmployee">
            <p><strong>Name:</strong> {{ selectedEmployee.name }}</p>
            <p><strong>Position:</strong> {{ selectedEmployee.position }}</p>
            <p><strong>Email:</strong> {{ selectedEmployee.email }}</p>
            <p><strong>Status:</strong> {{ selectedEmployee.status }}</p>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" text @click="showEmployeeDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
// Assume Vuetify and chart components are globally available

const loadingEmployees = ref(false);
const loadingPayrolls = ref(false);
const showEmployeeDialog = ref(false);
const selectedEmployee = ref(null);

const employees = ref([
  { name: 'John Doe', position: 'Software Engineer', email: 'john@company.com', status: 'Active' },
  { name: 'Jane Smith', position: 'HR Manager', email: 'jane@company.com', status: 'Active' },
  // ...more employees
]);

const employeeHeaders = [
  { text: 'Name', value: 'name' },
  { text: 'Position', value: 'position' },
  { text: 'Email', value: 'email' },
  { text: 'Status', value: 'status' },
  { text: 'Actions', value: 'actions', sortable: false },
];

const payrolls = ref([
  { month: 'July', total: '$50,000', processed: true },
  { month: 'June', total: '$48,000', processed: true },
  // ...more payrolls
]);

const payrollHeaders = [
  { text: 'Month', value: 'month' },
  { text: 'Total', value: 'total' },
  { text: 'Processed', value: 'processed' },
];

const attendanceData = ref({ /* chart data */ });
const attendanceChartOptions = ref({ /* chart options */ });
const analyticsData = ref({ /* chart data */ });
const analyticsChartOptions = ref({ /* chart options */ });

function viewEmployee(employee: any) {
  selectedEmployee.value = employee;
  showEmployeeDialog.value = true;
}
function editEmployee(employee: any) {
  // Open edit dialog or route
}

onMounted(() => {
  // Fetch employees, payrolls, attendance, analytics from API
});
</script>

<style scoped>
.hrm-view {
  padding: 2rem;
}
</style>
