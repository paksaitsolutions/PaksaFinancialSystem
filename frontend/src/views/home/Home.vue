<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Financial Dashboard</h1>
      <p>Welcome to Paksa Financial System</p>
    </div>

    <div class="dashboard-grid">
      <!-- Quick Stats -->
      <div class="stats-row">
        <Card class="stat-card">
          <template #content>
            <div class="stat-content">
              <div class="stat-icon bg-blue-100">
                <i class="pi pi-dollar text-blue-600"></i>
              </div>
              <div class="stat-info">
                <h3>Total Revenue</h3>
                <p class="stat-value">$125,430</p>
                <span class="stat-change positive">+12.5%</span>
              </div>
            </div>
          </template>
        </Card>

        <Card class="stat-card">
          <template #content>
            <div class="stat-content">
              <div class="stat-icon bg-green-100">
                <i class="pi pi-chart-line text-green-600"></i>
              </div>
              <div class="stat-info">
                <h3>Net Profit</h3>
                <p class="stat-value">$45,230</p>
                <span class="stat-change positive">+8.2%</span>
              </div>
            </div>
          </template>
        </Card>

        <Card class="stat-card">
          <template #content>
            <div class="stat-content">
              <div class="stat-icon bg-orange-100">
                <i class="pi pi-users text-orange-600"></i>
              </div>
              <div class="stat-info">
                <h3>Customers</h3>
                <p class="stat-value">1,234</p>
                <span class="stat-change positive">+5.1%</span>
              </div>
            </div>
          </template>
        </Card>

        <Card class="stat-card">
          <template #content>
            <div class="stat-content">
              <div class="stat-icon bg-red-100">
                <i class="pi pi-exclamation-triangle text-red-600"></i>
              </div>
              <div class="stat-info">
                <h3>Overdue</h3>
                <p class="stat-value">$8,450</p>
                <span class="stat-change negative">-2.3%</span>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Quick Actions -->
      <Card class="quick-actions">
        <template #title>Quick Actions</template>
        <template #content>
          <div class="action-grid">
            <Button label="New Invoice" icon="pi pi-plus" @click="$router.push('/ar')" />
            <Button label="Record Payment" icon="pi pi-credit-card" @click="$router.push('/ap')" />
            <Button label="Journal Entry" icon="pi pi-book" @click="$router.push('/accounting/journal-entry')" />
            <Button label="View Reports" icon="pi pi-chart-bar" @click="$router.push('/reports')" />
          </div>
        </template>
      </Card>

      <!-- Recent Transactions -->
      <Card class="recent-transactions">
        <template #title>Recent Transactions</template>
        <template #content>
          <DataTable :value="recentTransactions" responsiveLayout="scroll">
            <Column field="date" header="Date" />
            <Column field="description" header="Description" />
            <Column field="amount" header="Amount">
              <template #body="{ data }">
                <span :class="data.amount >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const recentTransactions = ref([
  { date: '2024-01-15', description: 'Sales Invoice #1001', amount: 2500 },
  { date: '2024-01-14', description: 'Office Supplies', amount: -450 },
  { date: '2024-01-13', description: 'Customer Payment', amount: 1800 },
  { date: '2024-01-12', description: 'Utility Bill', amount: -320 },
  { date: '2024-01-11', description: 'Service Revenue', amount: 3200 }
])

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.dashboard-header p {
  color: #6b7280;
  margin: 0;
}

.dashboard-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.stat-card {
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.stat-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

.stat-change {
  font-size: 0.75rem;
  font-weight: 500;
}

.stat-change.positive {
  color: #059669;
}

.stat-change.negative {
  color: #dc2626;
}

.quick-actions,
.recent-transactions {
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
}
</style>