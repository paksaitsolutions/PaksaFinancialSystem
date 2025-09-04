<template>
  <div class="budget-dashboard">
    <div class="dashboard-header">
      <h1>Budget Management Dashboard</h1>
      <p>Welcome to the Budget Management module. This dashboard provides an overview of your budget data.</p>
    </div>
      
    <!-- Quick Actions -->
    <Card class="quick-actions-card">
      <template #title>
        <div class="card-title">
          <i class="pi pi-bolt"></i>
          <span>Quick Actions</span>
        </div>
      </template>
      <template #content>
        <div class="quick-actions-grid">
          <Button 
            label="Create Budget" 
            icon="pi pi-plus" 
            class="p-button-outlined action-btn"
            @click="$router.push('/budget/manage')"
          />
          <Button 
            label="Budget Planning" 
            icon="pi pi-calendar" 
            class="p-button-outlined action-btn"
            @click="$router.push('/budget/planning')"
          />
          <Button 
            label="Budget Monitoring" 
            icon="pi pi-eye" 
            class="p-button-outlined action-btn"
            @click="$router.push('/budget/monitoring')"
          />
          <Button 
            label="Budget Reports" 
            icon="pi pi-file-pdf" 
            class="p-button-outlined action-btn"
            @click="$router.push('/budget/reports')"
          />
          <Button 
            label="Budget Approval" 
            icon="pi pi-check" 
            class="p-button-outlined action-btn"
            @click="$router.push('/budget/approval')"
          />
          <Button 
            label="Variance Analysis" 
            icon="pi pi-chart-line" 
            class="p-button-outlined action-btn"
            @click="$router.push('/budget/reports')"
          />
          <Button 
            label="Budget vs Actual" 
            icon="pi pi-chart-bar" 
            class="p-button-outlined action-btn"
            @click="$router.push('/budget/reports')"
          />
          <Button 
            label="Forecasting" 
            icon="pi pi-trending-up" 
            class="p-button-outlined action-btn"
            @click="$router.push('/budget/forecasting')"
          />
        </div>
      </template>
    </Card>

    <!-- Summary Cards -->
    <div class="summary-cards">
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-wallet text-blue"></i>
            <span>Total Budget</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-blue">{{ formatCurrency(totalBudget) }}</div>
          <div class="summary-date">Current Year</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-chart-line text-orange"></i>
            <span>Total Spent</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-orange">{{ formatCurrency(totalSpent) }}</div>
          <div class="summary-date">Year to Date</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-check-circle text-green"></i>
            <span>Remaining Budget</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-green">{{ formatCurrency(remainingBudget) }}</div>
          <div class="summary-date">Available</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-percentage" :class="variancePercent >= 0 ? 'text-green' : 'text-red'"></i>
            <span>Budget Variance</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount" :class="variancePercent >= 0 ? 'text-green' : 'text-red'">
            {{ variancePercent.toFixed(1) }}%
          </div>
          <div class="summary-date">vs Plan</div>
        </template>
      </Card>
    </div>
      
    <!-- Main Content Area -->
    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Recent Budgets</span>
            <Button 
              label="View All" 
              icon="pi pi-arrow-right" 
              iconPos="right" 
              class="p-button-text p-button-sm" 
              @click="$router.push('/budget/manage')" 
            />
          </div>
        </template>
        <template #content>
          <DataTable 
            :value="recentBudgets" 
            :rows="5" 
            :paginator="false"
            responsiveLayout="scroll"
          >
            <Column field="name" header="Budget Name">
              <template #body="{ data }">
                <span class="font-medium">{{ data.name }}</span>
              </template>
            </Column>
            <Column field="type" header="Type">
              <template #body="{ data }">
                <Tag :value="data.type" :severity="getTypeSeverity(data.type)" />
              </template>
            </Column>
            <Column field="amount" header="Amount">
              <template #body="{ data }">
                <span class="font-medium">{{ formatCurrency(data.amount) }}</span>
              </template>
            </Column>
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-rounded p-button-text p-button-sm" 
                  @click="viewBudget(data.id)" 
                />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Budget by Category</span>
            <Button 
              label="View Details" 
              icon="pi pi-arrow-right" 
              iconPos="right" 
              class="p-button-text p-button-sm" 
              @click="$router.push('/budget/reports')" 
            />
          </div>
        </template>
        <template #content>
          <DataTable 
            :value="budgetByCategory" 
            :paginator="false"
            responsiveLayout="scroll"
          >
            <Column field="category" header="Category">
              <template #body="{ data }">
                <div class="category-item">
                  <div class="category-indicator" :class="getCategoryColor(data.category)"></div>
                  <span>{{ data.category }}</span>
                </div>
              </template>
            </Column>
            <Column field="budgeted" header="Budgeted">
              <template #body="{ data }">
                <span class="text-blue">{{ formatCurrency(data.budgeted) }}</span>
              </template>
            </Column>
            <Column field="spent" header="Spent">
              <template #body="{ data }">
                <span class="text-orange">{{ formatCurrency(data.spent) }}</span>
              </template>
            </Column>
            <Column field="variance" header="Variance">
              <template #body="{ data }">
                <span :class="data.variance >= 0 ? 'text-green' : 'text-red'">
                  {{ formatCurrency(data.variance) }}
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'

const router = useRouter()

const formatCurrency = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
const formatDate = (date: Date) => new Intl.DateTimeFormat('en-US').format(date)

// Mock data
const totalBudget = ref(500000)
const totalSpent = ref(375000)
const remainingBudget = computed(() => totalBudget.value - totalSpent.value)
const variancePercent = computed(() => ((remainingBudget.value / totalBudget.value) * 100))

const recentBudgets = ref([
  { id: 1, name: 'Marketing Q1 2024', type: 'OPERATIONAL', amount: 50000, status: 'APPROVED' },
  { id: 2, name: 'IT Infrastructure', type: 'CAPITAL', amount: 100000, status: 'PENDING_APPROVAL' },
  { id: 3, name: 'HR Training Program', type: 'DEPARTMENT', amount: 25000, status: 'DRAFT' },
  { id: 4, name: 'New Product Launch', type: 'PROJECT', amount: 75000, status: 'APPROVED' },
  { id: 5, name: 'Office Renovation', type: 'CAPITAL', amount: 30000, status: 'REJECTED' }
])

const budgetByCategory = ref([
  { category: 'Marketing', budgeted: 120000, spent: 85000, variance: 35000 },
  { category: 'Operations', budgeted: 150000, spent: 125000, variance: 25000 },
  { category: 'IT', budgeted: 100000, spent: 95000, variance: 5000 },
  { category: 'HR', budgeted: 80000, spent: 70000, variance: 10000 },
  { category: 'Facilities', budgeted: 50000, spent: 55000, variance: -5000 }
])

const getTypeSeverity = (type: string) => {
  switch (type) {
    case 'OPERATIONAL': return 'info'
    case 'CAPITAL': return 'warning'
    case 'PROJECT': return 'success'
    case 'DEPARTMENT': return 'secondary'
    default: return 'info'
  }
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'APPROVED': return 'success'
    case 'DRAFT': return 'secondary'
    case 'PENDING_APPROVAL': return 'warning'
    case 'REJECTED': return 'danger'
    default: return 'secondary'
  }
}

const getCategoryColor = (category: string) => {
  const colors = {
    'Marketing': 'bg-blue-500',
    'Operations': 'bg-green-500',
    'IT': 'bg-purple-500',
    'HR': 'bg-orange-500',
    'Facilities': 'bg-teal-500'
  }
  return colors[category] || 'bg-gray-500'
}

const viewBudget = (id: number) => {
  router.push(`/budget/manage`)
}

onMounted(() => {
  // Load dashboard data
})
</script>

<style scoped>
.budget-dashboard {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.dashboard-header p {
  color: #6b7280;
  margin: 0;
}

.quick-actions-card {
  margin-bottom: 2rem;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.card-title i {
  color: #3b82f6;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-btn {
  width: 100%;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  height: 100%;
}

.summary-amount {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.summary-date {
  font-size: 0.75rem;
  color: #6b7280;
}

.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.content-card {
  height: fit-content;
}

.card-title-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.text-blue { color: #3b82f6; }
.text-red { color: #ef4444; }
.text-green { color: #10b981; }
.text-orange { color: #f59e0b; }

.bg-blue-500 { background-color: #3b82f6; }
.bg-green-500 { background-color: #10b981; }
.bg-purple-500 { background-color: #8b5cf6; }
.bg-orange-500 { background-color: #f59e0b; }
.bg-teal-500 { background-color: #14b8a6; }
.bg-gray-500 { background-color: #6b7280; }

@media (max-width: 768px) {
  .budget-dashboard {
    padding: 1rem;
  }
  
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>