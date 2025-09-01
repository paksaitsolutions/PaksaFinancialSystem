<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Financial Dashboard</h1>
      <p>Welcome to Paksa Financial System</p>
    </div>

    <div class="dashboard-cards">
      <Card class="dashboard-card">
        <template #content>
          <div class="card-content">
            <div class="card-icon">
              <i class="pi pi-dollar"></i>
            </div>
            <div class="card-info">
              <h3>Total Revenue</h3>
              <p class="card-value">$1,234,567</p>
              <small class="card-change positive">+12.5% from last month</small>
            </div>
          </div>
        </template>
      </Card>

      <Card class="dashboard-card">
        <template #content>
          <div class="card-content">
            <div class="card-icon">
              <i class="pi pi-credit-card"></i>
            </div>
            <div class="card-info">
              <h3>Accounts Receivable</h3>
              <p class="card-value">$456,789</p>
              <small class="card-change negative">-3.2% from last month</small>
            </div>
          </div>
        </template>
      </Card>

      <Card class="dashboard-card">
        <template #content>
          <div class="card-content">
            <div class="card-icon">
              <i class="pi pi-money-bill"></i>
            </div>
            <div class="card-info">
              <h3>Accounts Payable</h3>
              <p class="card-value">$234,567</p>
              <small class="card-change positive">-8.1% from last month</small>
            </div>
          </div>
        </template>
      </Card>

      <Card class="dashboard-card">
        <template #content>
          <div class="card-content">
            <div class="card-icon">
              <i class="pi pi-wallet"></i>
            </div>
            <div class="card-info">
              <h3>Cash Balance</h3>
              <p class="card-value">$789,123</p>
              <small class="card-change positive">+5.7% from last month</small>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <div class="dashboard-content">
      <div class="dashboard-section">
        <Card>
          <template #title>Recent Transactions</template>
          <template #content>
            <DataTable :value="recentTransactions" responsiveLayout="scroll">
              <Column field="date" header="Date"></Column>
              <Column field="description" header="Description"></Column>
              <Column field="amount" header="Amount">
                <template #body="slotProps">
                  <span :class="{ 'text-green-500': slotProps.data.amount > 0, 'text-red-500': slotProps.data.amount < 0 }">
                    ${{ Math.abs(slotProps.data.amount).toLocaleString() }}
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

      <div class="dashboard-section">
        <Card>
          <template #title>Quick Actions</template>
          <template #content>
            <div class="quick-actions">
              <Button 
                label="Create Invoice" 
                icon="pi pi-plus" 
                class="p-button-outlined"
                @click="$router.push('/ar/invoices')"
              />
              <Button 
                label="Record Payment" 
                icon="pi pi-credit-card" 
                class="p-button-outlined"
                @click="$router.push('/ap/payments')"
              />
              <Button 
                label="Journal Entry" 
                icon="pi pi-book" 
                class="p-button-outlined"
                @click="$router.push('/gl/journal-entries')"
              />
              <Button 
                label="View Reports" 
                icon="pi pi-chart-bar" 
                class="p-button-outlined"
                @click="$router.push('/reports')"
              />
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const recentTransactions = ref([
  {
    date: '2024-01-15',
    description: 'Customer Payment - INV-001',
    amount: 5000,
    status: 'Completed'
  },
  {
    date: '2024-01-14',
    description: 'Office Supplies Purchase',
    amount: -250,
    status: 'Pending'
  },
  {
    date: '2024-01-13',
    description: 'Service Revenue',
    amount: 3500,
    status: 'Completed'
  },
  {
    date: '2024-01-12',
    description: 'Utility Bill Payment',
    amount: -450,
    status: 'Completed'
  }
])

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'Completed': return 'success'
    case 'Pending': return 'warning'
    case 'Failed': return 'danger'
    default: return 'info'
  }
}
</script>

<style scoped>
.dashboard {
  padding: 0;
  background: transparent;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.dashboard-header p {
  margin: 0;
  color: var(--text-color-secondary);
}

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.dashboard-card {
  height: auto;
  min-height: 120px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  height: 100%;
}

.card-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #007bff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
}

.card-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.card-value {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
}

.card-change {
  font-size: 0.75rem;
}

.card-change.positive {
  color: var(--green-500);
}

.card-change.negative {
  color: var(--red-500);
}

.dashboard-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
}

.dashboard-section {
  margin-bottom: 1rem;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
  
  .quick-actions {
    flex-direction: row;
    flex-wrap: wrap;
  }
}
</style>