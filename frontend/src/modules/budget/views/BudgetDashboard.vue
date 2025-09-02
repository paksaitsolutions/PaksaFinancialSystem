<template>
  <div class="budget-dashboard">
    <!-- Header with Actions -->
    <div class="dashboard-header">
      <h1 class="dashboard-title">Budget Management</h1>
      <div class="header-actions">
        <Button label="New Budget" icon="pi pi-plus" @click="showCreateDialog = true" />
        <Button label="Import" icon="pi pi-upload" severity="secondary" @click="showImportDialog = true" />
        <Button label="Export" icon="pi pi-download" severity="secondary" @click="exportBudgets" />
      </div>
    </div>

    <!-- Quick Actions -->
    <Card class="quick-actions-card">
      <template #header>
        <h3 class="section-header">Quick Actions</h3>
      </template>
      <template #content>
        <div class="quick-actions">
          <Button label="Create Budget" icon="pi pi-plus" @click="showCreateDialog = true" class="action-btn" />
          <Button label="Budget Planning" icon="pi pi-calendar" @click="navigateTo('/budget/planning')" class="action-btn" />
          <Button label="Budget Reports" icon="pi pi-chart-line" @click="navigateTo('/budget/reports')" class="action-btn" />
          <Button label="Variance Analysis" icon="pi pi-chart-bar" @click="showVarianceDialog = true" class="action-btn" />
          <Button label="Budget Approval" icon="pi pi-check" @click="showApprovalDialog = true" class="action-btn" />
          <Button label="Budget Monitoring" icon="pi pi-eye" @click="navigateTo('/budget/monitoring')" class="action-btn" />
        </div>
      </template>
    </Card>

    <!-- Overview Cards -->
    <div class="overview-cards">
      <div class="card-item">
        <BudgetOverviewCard
          title="Total Budgets"
          :value="totalBudgets"
          :percentage="budgetPerformance.variance_percentage"
          icon="pi pi-chart-bar"
          color="#2196F3"
        />
      </div>

      <div class="card-item">
        <BudgetOverviewCard
          title="Total Amount"
          :value="formatCurrency(totalAmount)"
          :percentage="budgetPerformance.variance_percentage"
          icon="pi pi-dollar"
          color="#4CAF50"
        />
      </div>

      <div class="card-item">
        <BudgetOverviewCard
          title="Approved"
          :value="approvedBudgets"
          :percentage="approvedPercentage"
          icon="pi pi-check-circle"
          color="#4CAF50"
        />
      </div>

      <div class="card-item">
        <BudgetOverviewCard
          title="Pending"
          :value="pendingBudgets"
          :percentage="pendingPercentage"
          icon="pi pi-clock"
          color="#FFC107"
        />
      </div>
    </div>

    <!-- Analysis Sections -->
    <div class="analysis-section">
      <BudgetDepartmentAnalysis :data="departmentalAnalysis" />
    </div>

    <div class="analysis-section">
      <BudgetProjectAnalysis :data="projectAnalysis" />
    </div>

    <div class="analysis-section">
      <BudgetTrendChart :data="trendAnalysis" />
    </div>

    <div class="analysis-section">
      <BudgetAllocationAnalysis :data="allocationAnalysis" />
    </div>

    <div class="analysis-section">
      <BudgetVarianceAnalysis :data="varianceAnalysis" />
    </div>

    <!-- Budget Management Table -->
    <div class="analysis-section">
      <Card>
        <template #header>
          <div class="flex justify-content-between align-items-center">
            <h3 class="section-header">Budget Management</h3>
            <div class="table-actions">
              <Button label="View All" icon="pi pi-list" severity="secondary" size="small" @click="showAllBudgets = true" />
            </div>
          </div>
        </template>
        <template #content>
          <DataTable
            :value="budgetStore.budgets"
            :paginator="true"
            :rows="10"
            responsiveLayout="scroll"
            :loading="loading"
          >
            <Column field="name" header="Name">
              <template #body="{ data }">
                <span class="cursor-pointer text-primary" @click="editBudget(data)">{{ data.name }}</span>
              </template>
            </Column>
            <Column field="type" header="Type"></Column>
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column field="amount" header="Amount">
              <template #body="{ data }">
                ${{ formatCurrency(data.amount || 0) }}
              </template>
            </Column>
            <Column field="startDate" header="Start Date">
              <template #body="{ data }">
                {{ formatDate(data.startDate) }}
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button icon="pi pi-eye" size="small" severity="info" @click="viewBudget(data)" />
                  <Button icon="pi pi-pencil" size="small" severity="warning" @click="editBudget(data)" />
                  <Button icon="pi pi-trash" size="small" severity="danger" @click="deleteBudget(data.id)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>

    <!-- Create Budget Dialog -->
    <Dialog v-model:visible="showCreateDialog" modal header="Create New Budget" :style="{ width: '50rem' }">
      <BudgetForm @submit="handleCreateBudget" @cancel="showCreateDialog = false" />
    </Dialog>

    <!-- Edit Budget Dialog -->
    <Dialog v-model:visible="showEditDialog" modal header="Edit Budget" :style="{ width: '50rem' }">
      <BudgetForm v-if="selectedBudget" :budget="selectedBudget" @submit="handleEditBudget" @cancel="showEditDialog = false" />
    </Dialog>

    <!-- View Budget Dialog -->
    <Dialog v-model:visible="showViewDialog" modal header="Budget Details" :style="{ width: '60rem' }">
      <div v-if="selectedBudget" class="budget-details">
        <div class="detail-grid">
          <div class="detail-item">
            <label>Name:</label>
            <span>{{ selectedBudget.name }}</span>
          </div>
          <div class="detail-item">
            <label>Type:</label>
            <span>{{ selectedBudget.type }}</span>
          </div>
          <div class="detail-item">
            <label>Status:</label>
            <Tag :value="selectedBudget.status" :severity="getStatusSeverity(selectedBudget.status)" />
          </div>
          <div class="detail-item">
            <label>Amount:</label>
            <span>${{ formatCurrency(selectedBudget.amount || 0) }}</span>
          </div>
        </div>
      </div>
    </Dialog>

    <!-- Import Dialog -->
    <Dialog v-model:visible="showImportDialog" modal header="Import Budgets" :style="{ width: '30rem' }">
      <div class="import-section">
        <FileUpload mode="basic" name="budgets" accept=".csv,.xlsx" :maxFileSize="1000000" @upload="handleImport" />
      </div>
    </Dialog>

    <!-- Variance Analysis Dialog -->
    <Dialog v-model:visible="showVarianceDialog" modal header="Variance Analysis" :style="{ width: '70rem' }">
      <BudgetVarianceAnalysis :data="varianceAnalysis" />
    </Dialog>

    <!-- Approval Dialog -->
    <Dialog v-model:visible="showApprovalDialog" modal header="Budget Approvals" :style="{ width: '60rem' }">
      <DataTable :value="pendingApprovals" responsiveLayout="scroll">
        <Column field="name" header="Budget Name"></Column>
        <Column field="amount" header="Amount">
          <template #body="{ data }">
            ${{ formatCurrency(data.amount || 0) }}
          </template>
        </Column>
        <Column header="Actions">
          <template #body="{ data }">
            <div class="flex gap-2">
              <Button label="Approve" icon="pi pi-check" size="small" severity="success" @click="approveBudget(data.id)" />
              <Button label="Reject" icon="pi pi-times" size="small" severity="danger" @click="rejectBudget(data.id)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBudgetStore } from '../store/budget'
import { 
  BudgetStatus, 
  BudgetType,
  type BudgetAnalysisData,
  type BudgetTrendData,
  type BudgetAllocationAnalysis as BudgetAllocationAnalysisType,
  type BudgetVarianceAnalysis as BudgetVarianceAnalysisType
} from '../../types/budget'

import BudgetOverviewCard from '../components/BudgetOverviewCard.vue'
import BudgetDepartmentAnalysis from '../components/BudgetDepartmentAnalysis.vue'
import BudgetProjectAnalysis from '../components/BudgetProjectAnalysis.vue'
import BudgetTrendChart from '../components/BudgetTrendChart.vue'
import BudgetAllocationAnalysis from '../components/BudgetAllocationAnalysis.vue'
import BudgetVarianceAnalysis from '../components/BudgetVarianceAnalysis.vue'
import BudgetForm from '../components/BudgetForm.vue'

const router = useRouter()

// Define budget interface
interface Budget {
  id: number
  name: string
  budget_type: BudgetType
  status: BudgetStatus
  total_amount: number
  created_at: string
}

const budgetStore = useBudgetStore()

// Dialog states
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showViewDialog = ref(false)
const showImportDialog = ref(false)
const showVarianceDialog = ref(false)
const showApprovalDialog = ref(false)
const showAllBudgets = ref(false)
const selectedBudget = ref(null)
const loading = ref(false)

// Computed values
const totalBudgets = computed(() => budgetStore.budgets.length)
const totalAmount = computed(() => {
  return budgetStore.budgets.reduce((sum: number, budget: any) => sum + (budget.amount || 0), 0)
})

const approvedBudgets = computed(() => {
  return budgetStore.budgets.filter((b: any) => b.status === 'approved').length
})

const pendingBudgets = computed(() => {
  return budgetStore.budgets.filter((b: any) => b.status === 'draft').length
})

const pendingApprovals = computed(() => {
  return budgetStore.budgets.filter((b: any) => b.status === 'pending_approval')
})

const recentBudgets = computed(() => {
  return budgetStore.budgets
    .sort((a: any, b: any) => new Date(b.createdAt || '').getTime() - new Date(a.createdAt || '').getTime())
    .slice(0, 5)
})

// Analytics data - using mock data for now
const budgetPerformance = ref({ variance_percentage: 0 })
const departmentalAnalysis = ref([])
const projectAnalysis = ref([])
const trendAnalysis = ref([])
const allocationAnalysis = ref([])
const varianceAnalysis = ref([])

// Helper functions
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'draft':
      return 'info'
    case 'approved':
      return 'success'
    case 'rejected':
      return 'danger'
    case 'pending_approval':
      return 'warning'
    case 'archived':
      return 'secondary'
    default:
      return 'info'
  }
}

// Navigation functions
const navigateTo = (path: string) => {
  router.push(path)
}

// Budget management functions
const viewBudget = (budget: any) => {
  selectedBudget.value = budget
  showViewDialog.value = true
}

const editBudget = (budget: any) => {
  selectedBudget.value = budget
  showEditDialog.value = true
}

const deleteBudget = async (budgetId: number) => {
  if (confirm('Are you sure you want to delete this budget?')) {
    try {
      await budgetStore.deleteBudget(budgetId)
      await loadBudgets()
    } catch (error) {
      console.error('Error deleting budget:', error)
    }
  }
}

const handleCreateBudget = async (budgetData: any) => {
  try {
    await budgetStore.createBudget(budgetData)
    showCreateDialog.value = false
    await loadBudgets()
  } catch (error) {
    console.error('Error creating budget:', error)
  }
}

const handleEditBudget = async (budgetData: any) => {
  try {
    await budgetStore.updateBudget(selectedBudget.value.id, budgetData)
    showEditDialog.value = false
    selectedBudget.value = null
    await loadBudgets()
  } catch (error) {
    console.error('Error updating budget:', error)
  }
}

const approveBudget = async (budgetId: number) => {
  try {
    await budgetStore.approveBudget(budgetId, 'Approved from dashboard')
    await loadBudgets()
  } catch (error) {
    console.error('Error approving budget:', error)
  }
}

const rejectBudget = async (budgetId: number) => {
  const reason = prompt('Please provide a reason for rejection:')
  if (reason) {
    try {
      await budgetStore.rejectBudget(budgetId, reason)
      await loadBudgets()
    } catch (error) {
      console.error('Error rejecting budget:', error)
    }
  }
}

const exportBudgets = () => {
  const csvContent = budgetStore.budgets.map(budget => 
    `${budget.name},${budget.type},${budget.status},${budget.amount}`
  ).join('\n')
  
  const blob = new Blob([`Name,Type,Status,Amount\n${csvContent}`], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'budgets.csv'
  a.click()
  window.URL.revokeObjectURL(url)
}

const handleImport = (event: any) => {
  console.log('Import file:', event.files[0])
  showImportDialog.value = false
}

const loadBudgets = async () => {
  try {
    loading.value = true
    await budgetStore.fetchBudgets()
  } catch (error) {
    console.error('Error loading budgets:', error)
  } finally {
    loading.value = false
  }
}

// Fetch data on mount
onMounted(async () => {
  await loadBudgets()
  // Mock analytics data
  budgetPerformance.value = { variance_percentage: 5.2 }
  departmentalAnalysis.value = [
    { department: 'IT', budget_amount: 100000, actual_amount: 95000, variance: -5 },
    { department: 'HR', budget_amount: 80000, actual_amount: 85000, variance: 6.25 }
  ]
  projectAnalysis.value = [
    { project: 'Project A', budget_amount: 50000, actual_amount: 48000, variance: -4, status: 'active' }
  ]
  trendAnalysis.value = [
    { period: '2024-01', budget: 100000, actual: 95000 },
    { period: '2024-02', budget: 110000, actual: 105000 }
  ]
  allocationAnalysis.value = [
    { category: 'Personnel', amount: 60000, percentage: 60 },
    { category: 'Equipment', amount: 40000, percentage: 40 }
  ]
  varianceAnalysis.value = [
    { category: 'Personnel', budget_amount: 60000, actual_amount: 58000, variance_amount: -2000, variance_percentage: -3.33, status: 'on track' }
  ]
})

// Table headers
const recentHeaders = [
  { text: 'Name', value: 'name' },
  { text: 'Type', value: 'type' },
  { text: 'Status', value: 'status' },
  { text: 'Amount', value: 'amount', align: 'right' },
  { text: 'Created At', value: 'createdAt' }
]

// Calculated percentages for overview cards
const approvedPercentage = computed(() => {
  const total = totalBudgets.value
  const approved = approvedBudgets.value
  return total > 0 ? ((approved / total) * 100).toFixed(1) : '0'
})

const pendingPercentage = computed(() => {
  const total = totalBudgets.value
  const pending = pendingBudgets.value
  return total > 0 ? ((pending / total) * 100).toFixed(1) : '0'
})
</script>

<style scoped>
.budget-dashboard {
  padding: 1.5rem;
  max-width: 100%;
  overflow-x: hidden;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--surface-border);
}

.dashboard-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.quick-actions-card {
  margin-bottom: 2rem;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-btn {
  width: 100%;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.card-item {
  min-height: 120px;
}

.analysis-section {
  margin-bottom: 2rem;
}

.section-header {
  padding: 1rem;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
}

.table-actions {
  display: flex;
  gap: 0.5rem;
}

.budget-details {
  padding: 1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-item label {
  font-weight: 600;
  color: var(--text-color-secondary);
}

.import-section {
  padding: 1rem;
  text-align: center;
}

.cursor-pointer {
  cursor: pointer;
}

.cursor-pointer:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .budget-dashboard {
    padding: 1rem;
  }
  
  .overview-cards {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1025px) {
  .overview-cards {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
