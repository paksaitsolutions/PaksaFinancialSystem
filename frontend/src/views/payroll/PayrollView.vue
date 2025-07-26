<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Payroll Management</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Total Employees</v-card-title>
          <v-card-text>
            <div class="text-h3 text-primary">{{ payrollData.length }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Gross Payroll</v-card-title>
          <v-card-text>
            <div class="text-h3 text-success">{{ formatCurrency(totalGross) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Total Deductions</v-card-title>
          <v-card-text>
            <div class="text-h3 text-warning">{{ formatCurrency(totalDeductions) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Net Payroll</v-card-title>
          <v-card-text>
            <div class="text-h3 text-info">{{ formatCurrency(totalNet) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between">
            Payroll Summary
            <div>
              <v-btn color="primary" @click="processPayroll" :loading="processing" class="mr-2">
                <v-icon start>mdi-play</v-icon>
                Process Payroll
              </v-btn>
              <v-btn color="success" @click="generateReports">
                <v-icon start>mdi-file-document</v-icon>
                Generate Reports
              </v-btn>
            </div>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :items="payrollData"
              :headers="headers"
              class="elevation-1"
            >
              <template #item.grossPay="{ item }">
                {{ formatCurrency(item.grossPay) }}
              </template>
              <template #item.deductions="{ item }">
                {{ formatCurrency(item.deductions) }}
              </template>
              <template #item.netPay="{ item }">
                {{ formatCurrency(item.netPay) }}
              </template>
              <template #item.status="{ item }">
                <v-chip :color="getStatusColor(item.status)" size="small">
                  {{ item.status }}
                </v-chip>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'

const processing = ref(false)

const payrollData = ref([
  { id: 1, employeeName: 'John Doe', department: 'IT', grossPay: 6250, deductions: 1875, netPay: 4375, status: 'Processed' },
  { id: 2, employeeName: 'Jane Smith', department: 'HR', grossPay: 7083, deductions: 2125, netPay: 4958, status: 'Processed' },
  { id: 3, employeeName: 'Bob Johnson', department: 'Finance', grossPay: 5417, deductions: 1625, netPay: 3792, status: 'Pending' }
])

const headers = [
  { title: 'Employee', key: 'employeeName' },
  { title: 'Department', key: 'department' },
  { title: 'Gross Pay', key: 'grossPay' },
  { title: 'Deductions', key: 'deductions' },
  { title: 'Net Pay', key: 'netPay' },
  { title: 'Status', key: 'status' }
]

const totalGross = computed(() => payrollData.value.reduce((sum, emp) => sum + emp.grossPay, 0))
const totalDeductions = computed(() => payrollData.value.reduce((sum, emp) => sum + emp.deductions, 0))
const totalNet = computed(() => payrollData.value.reduce((sum, emp) => sum + emp.netPay, 0))

const getStatusColor = (status) => {
  switch (status) {
    case 'Processed': return 'success'
    case 'Pending': return 'warning'
    case 'Failed': return 'error'
    default: return 'grey'
  }
}

const processPayroll = () => {
  processing.value = true
  setTimeout(() => {
    payrollData.value.forEach(emp => {
      if (emp.status === 'Pending') {
        emp.status = 'Processed'
      }
    })
    processing.value = false
  }, 2000)
}

const generateReports = () => {
  // Generate payroll reports
  console.log('Generating payroll reports...')
}

const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
</script>