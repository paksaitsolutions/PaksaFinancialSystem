<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <v-row class="mb-6">
      <v-col>
        <div class="d-flex align-center mb-4">
          <v-icon size="48" color="blue" class="mr-4">mdi-credit-card</v-icon>
          <div>
            <h1 class="text-h3 font-weight-bold">Accounts Payable</h1>
            <p class="text-subtitle-1 text-medium-emphasis">Vendor management and invoice processing</p>
          </div>
        </div>
      </v-col>
      <v-col cols="auto">
        <v-btn color="primary" prepend-icon="mdi-plus" class="mr-2">
          New Bill
        </v-btn>
        <v-btn color="success" prepend-icon="mdi-cash">
          Make Payment
        </v-btn>
      </v-col>
    </v-row>

    <!-- Stats Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex justify-space-between align-center">
              <div>
                <div class="text-h4 font-weight-bold text-error">$125,430</div>
                <div class="text-subtitle-2 text-medium-emphasis">Outstanding Bills</div>
              </div>
              <v-icon size="40" color="error">mdi-file-document-alert</v-icon>
            </div>
            <v-progress-linear color="error" :model-value="75" height="4" rounded class="mt-3" />
            <div class="text-caption mt-1">75% of credit limit used</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex justify-space-between align-center">
              <div>
                <div class="text-h4 font-weight-bold text-warning">$45,200</div>
                <div class="text-subtitle-2 text-medium-emphasis">Overdue Bills</div>
              </div>
              <v-icon size="40" color="warning">mdi-clock-alert</v-icon>
            </div>
            <div class="text-caption mt-3 text-warning">12 bills overdue</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex justify-space-between align-center">
              <div>
                <div class="text-h4 font-weight-bold text-success">$89,750</div>
                <div class="text-subtitle-2 text-medium-emphasis">Paid This Month</div>
              </div>
              <v-icon size="40" color="success">mdi-check-circle</v-icon>
            </div>
            <div class="text-caption mt-3 text-success">+15% vs last month</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex justify-space-between align-center">
              <div>
                <div class="text-h4 font-weight-bold text-info">156</div>
                <div class="text-subtitle-2 text-medium-emphasis">Active Vendors</div>
              </div>
              <v-icon size="40" color="info">mdi-account-group</v-icon>
            </div>
            <div class="text-caption mt-3">8 new this month</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Actions & Recent Bills -->
    <v-row>
      <!-- Quick Actions -->
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Quick Actions</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item prepend-icon="mdi-plus" title="Create New Bill" to="/ap/bills/new" />
              <v-list-item prepend-icon="mdi-account-plus" title="Add Vendor" to="/ap/vendors/new" />
              <v-list-item prepend-icon="mdi-cash" title="Record Payment" to="/ap/payments/new" />
              <v-list-item prepend-icon="mdi-file-import" title="Import Bills" to="/ap/import" />
              <v-list-item prepend-icon="mdi-chart-line" title="AP Reports" to="/ap/reports" />
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recent Bills -->
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Recent Bills</span>
            <v-btn variant="text" to="/ap/bills">View All</v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :items="recentBills"
              :headers="billHeaders"
              hide-default-footer
              :items-per-page="5"
            >
              <template #item.vendor="{ item }">
                <div class="font-weight-medium">{{ item.vendor }}</div>
              </template>
              
              <template #item.amount="{ item }">
                <div class="font-weight-bold">${{ item.amount.toLocaleString() }}</div>
              </template>
              
              <template #item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  size="small"
                  variant="tonal"
                >
                  {{ item.status }}
                </v-chip>
              </template>
              
              <template #item.dueDate="{ item }">
                <div :class="getDueDateClass(item.dueDate)">
                  {{ formatDate(item.dueDate) }}
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Aging Report -->
    <v-row class="mt-6">
      <v-col>
        <v-card>
          <v-card-title>Aging Report</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="2" v-for="aging in agingData" :key="aging.period">
                <div class="text-center">
                  <div class="text-h5 font-weight-bold" :class="aging.color">
                    ${{ aging.amount.toLocaleString() }}
                  </div>
                  <div class="text-caption">{{ aging.period }}</div>
                  <div class="text-caption text-medium-emphasis">{{ aging.count }} bills</div>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'

const billHeaders = [
  { title: 'Bill #', key: 'billNumber' },
  { title: 'Vendor', key: 'vendor' },
  { title: 'Amount', key: 'amount' },
  { title: 'Due Date', key: 'dueDate' },
  { title: 'Status', key: 'status' }
]

const recentBills = ref([
  {
    billNumber: 'BILL-001',
    vendor: 'ABC Supplies Co.',
    amount: 2500,
    dueDate: new Date('2024-02-15'),
    status: 'Pending'
  },
  {
    billNumber: 'BILL-002',
    vendor: 'XYZ Services Ltd.',
    amount: 1800,
    dueDate: new Date('2024-02-10'),
    status: 'Overdue'
  },
  {
    billNumber: 'BILL-003',
    vendor: 'Tech Solutions Inc.',
    amount: 3200,
    dueDate: new Date('2024-02-20'),
    status: 'Approved'
  },
  {
    billNumber: 'BILL-004',
    vendor: 'Office Depot',
    amount: 450,
    dueDate: new Date('2024-02-25'),
    status: 'Paid'
  },
  {
    billNumber: 'BILL-005',
    vendor: 'Utility Company',
    amount: 890,
    dueDate: new Date('2024-02-12'),
    status: 'Pending'
  }
])

const agingData = ref([
  { period: 'Current', amount: 45200, count: 23, color: 'text-success' },
  { period: '1-30 Days', amount: 28500, count: 15, color: 'text-info' },
  { period: '31-60 Days', amount: 18200, count: 8, color: 'text-warning' },
  { period: '61-90 Days', amount: 12800, count: 5, color: 'text-error' },
  { period: '90+ Days', amount: 8900, count: 3, color: 'text-error' }
])

const getStatusColor = (status) => {
  switch (status) {
    case 'Paid': return 'success'
    case 'Approved': return 'info'
    case 'Pending': return 'warning'
    case 'Overdue': return 'error'
    default: return 'grey'
  }
}

const getDueDateClass = (dueDate) => {
  const today = new Date()
  const due = new Date(dueDate)
  
  if (due < today) return 'text-error font-weight-bold'
  if (due <= new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)) return 'text-warning'
  return ''
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}
</script>