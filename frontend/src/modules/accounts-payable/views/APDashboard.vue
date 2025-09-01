<template>
  <div class="ap-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="header-info">
          <i class="pi pi-credit-card header-icon"></i>
          <div>
            <h1>Accounts Payable</h1>
            <p>Vendor management and invoice processing</p>
          </div>
        </div>
        <div class="header-actions">
          <Button label="New Bill" icon="pi pi-plus" class="p-button-primary mr-2" @click="$router.push('/ap/create-bill')" />
          <Button label="Make Payment" icon="pi pi-dollar" class="p-button-success" @click="$router.push('/ap/record-payment')" />
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-value error">$125,430</div>
              <div class="stat-label">Outstanding Bills</div>
            </div>
            <i class="pi pi-file stat-icon error"></i>
          </div>
          <ProgressBar :value="75" class="mt-3" />
          <div class="stat-note">75% of credit limit used</div>
        </template>
      </Card>

      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-value warning">$45,200</div>
              <div class="stat-label">Overdue Bills</div>
            </div>
            <i class="pi pi-clock stat-icon warning"></i>
          </div>
          <div class="stat-note warning">12 bills overdue</div>
        </template>
      </Card>

      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-value success">$89,750</div>
              <div class="stat-label">Paid This Month</div>
            </div>
            <i class="pi pi-check-circle stat-icon success"></i>
          </div>
          <div class="stat-note success">+15% vs last month</div>
        </template>
      </Card>

      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-value info">156</div>
              <div class="stat-label">Active Vendors</div>
            </div>
            <i class="pi pi-users stat-icon info"></i>
          </div>
          <div class="stat-note">8 new this month</div>
        </template>
      </Card>
    </div>

    <!-- Quick Actions & Recent Bills -->
    <div class="content-grid">
      <!-- Quick Actions -->
      <Card class="quick-actions-card">
        <template #title>Quick Actions</template>
        <template #content>
          <div class="quick-actions">
            <Button label="Create New Bill" icon="pi pi-plus" class="p-button-outlined action-btn" @click="$router.push('/ap/create-bill')" />
            <Button label="Add Vendor" icon="pi pi-user-plus" class="p-button-outlined action-btn" @click="$router.push('/ap/add-vendor')" />
            <Button label="Record Payment" icon="pi pi-dollar" class="p-button-outlined action-btn" @click="$router.push('/ap/record-payment')" />
            <Button label="Import Bills" icon="pi pi-upload" class="p-button-outlined action-btn" @click="$router.push('/ap/import-bills')" />
            <Button label="AP Reports" icon="pi pi-chart-line" class="p-button-outlined action-btn" @click="$router.push('/ap/reports')" />
          </div>
        </template>
      </Card>

      <!-- Recent Bills -->
      <Card class="recent-bills-card">
        <template #title>
          <div class="card-header">
            <span>Recent Bills</span>
            <Button label="View All" class="p-button-text" />
          </div>
        </template>
        <template #content>
          <DataTable :value="recentBills" responsiveLayout="scroll">
            <Column field="billNumber" header="Bill #"></Column>
            <Column field="vendor" header="Vendor"></Column>
            <Column field="amount" header="Amount">
              <template #body="slotProps">
                <span class="font-bold">${{ slotProps.data.amount.toLocaleString() }}</span>
              </template>
            </Column>
            <Column field="dueDate" header="Due Date">
              <template #body="slotProps">
                <span :class="getDueDateClass(slotProps.data.dueDate)">
                  {{ formatDate(slotProps.data.dueDate) }}
                </span>
              </template>
            </Column>
            <Column field="status" header="Status">
              <template #body="slotProps">
                <Tag :value="slotProps.data.status" :severity="getStatusSeverity(slotProps.data.status)" />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>

    <!-- Aging Report -->
    <Card class="aging-report">
      <template #title>Aging Report</template>
      <template #content>
        <div class="aging-grid">
          <div v-for="aging in agingData" :key="aging.period" class="aging-item">
            <div class="aging-amount" :class="aging.color">
              ${{ aging.amount.toLocaleString() }}
            </div>
            <div class="aging-period">{{ aging.period }}</div>
            <div class="aging-count">{{ aging.count }} bills</div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

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
  { period: 'Current', amount: 45200, count: 23, color: 'success' },
  { period: '1-30 Days', amount: 28500, count: 15, color: 'info' },
  { period: '31-60 Days', amount: 18200, count: 8, color: 'warning' },
  { period: '61-90 Days', amount: 12800, count: 5, color: 'error' },
  { period: '90+ Days', amount: 8900, count: 3, color: 'error' }
])

const getStatusSeverity = (status) => {
  switch (status) {
    case 'Paid': return 'success'
    case 'Approved': return 'info'
    case 'Pending': return 'warning'
    case 'Overdue': return 'danger'
    default: return null
  }
}

const getDueDateClass = (dueDate) => {
  const today = new Date()
  const due = new Date(dueDate)
  
  if (due < today) return 'text-red-500 font-bold'
  if (due <= new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)) return 'text-orange-500'
  return ''
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}
</script>

<style scoped>
.ap-dashboard {
  padding: 0;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  font-size: 3rem;
  color: #007bff;
}

.header-info h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: bold;
}

.header-info p {
  margin: 0;
  color: #6c757d;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.stat-label {
  color: #6c757d;
  font-size: 0.875rem;
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-note {
  font-size: 0.75rem;
  margin-top: 0.5rem;
}

.error { color: #dc3545; }
.warning { color: #ffc107; }
.success { color: #28a745; }
.info { color: #17a2b8; }

.content-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.action-btn {
  justify-content: flex-start;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.aging-report {
  margin-top: 2rem;
}

.aging-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  text-align: center;
}

.aging-amount {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.aging-period {
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.aging-count {
  font-size: 0.75rem;
  color: #6c757d;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-actions {
    flex-direction: row;
    flex-wrap: wrap;
  }
}
</style>