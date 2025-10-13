<template>
  <UnifiedDashboard 
    title="Tax Management" 
    subtitle="Comprehensive tax compliance and reporting"
  >
    <template #actions>
      <Button label="New Tax Code" icon="pi pi-plus" class="btn-primary" @click="navigateToTaxCodes" />
    </template>
    
    <template #metrics>
      <UnifiedMetrics :metrics="dashboardMetrics" />
    </template>
    
    <template #content>
      <div class="content-grid">
        <Card>
          <template #header>
            <h3 class="card-title">Quick Actions</h3>
          </template>
          <template #content>
            <div class="actions-list">
              <Button label="Calculate Tax" icon="pi pi-calculator" class="action-btn" @click="navigateToTaxCodes" />
              <Button label="File Return" icon="pi pi-file" class="action-btn btn-secondary" @click="navigateToReturns" />
              <Button label="View Reports" icon="pi pi-chart-line" class="action-btn" @click="navigateToReports" />
              <Button label="Manage Exemptions" icon="pi pi-shield" class="action-btn" @click="navigateToExemptions" />
            </div>
          </template>
        </Card>
        
        <Card>
          <template #header>
            <h3 class="card-title">Upcoming Tax Deadlines</h3>
          </template>
          <template #content>
            <DataTable :value="upcomingDeadlines" :rows="5" class="compact-table">
              <Column field="description" header="Description" />
              <Column field="jurisdiction" header="Jurisdiction" />
              <Column field="dueDate" header="Due Date">
                <template #body="{ data }">
                  {{ formatDate(data.dueDate) }}
                </template>
              </Column>
              <Column field="daysRemaining" header="Days Remaining">
                <template #body="{ data }">
                  <Tag :value="`${data.daysRemaining} days`" :severity="getDaysSeverity(data.daysRemaining)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </template>
  </UnifiedDashboard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { formatCurrency } from '@/utils/formatters'
import UnifiedDashboard from '@/components/ui/UnifiedDashboard.vue'
import UnifiedMetrics from '@/components/ui/UnifiedMetrics.vue'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'

const router = useRouter()

const stats = ref({
  totalLiability: 0,
  activeTaxCodes: 0,
  pendingReturns: 0,
  complianceScore: 0
})

const dashboardMetrics = computed(() => [
  {
    id: 'liability',
    icon: 'pi pi-exclamation-triangle',
    value: formatCurrency(stats.value.totalLiability),
    label: 'Total Tax Liability',
    color: 'var(--red-500)'
  },
  {
    id: 'codes',
    icon: 'pi pi-code',
    value: stats.value.activeTaxCodes,
    label: 'Active Tax Codes',
    color: 'var(--blue-500)'
  },
  {
    id: 'returns',
    icon: 'pi pi-file-o',
    value: stats.value.pendingReturns,
    label: 'Pending Returns',
    color: 'var(--orange-500)'
  },
  {
    id: 'compliance',
    icon: 'pi pi-shield',
    value: `${stats.value.complianceScore}%`,
    label: 'Compliance Score',
    color: 'var(--green-500)'
  }
])

const upcomingDeadlines = ref([])
const loading = ref(false)

const loadDashboardData = async () => {
  loading.value = true
  try {
    const [statsResponse, deadlinesResponse] = await Promise.all([
      fetch('http://localhost:8000/api/v1/tax/dashboard/stats'),
      fetch('http://localhost:8000/api/v1/tax/dashboard/deadlines')
    ])
    
    if (statsResponse.ok) {
      const data = await statsResponse.json()
      stats.value = {
        totalLiability: data.total_liability || 0,
        activeTaxCodes: data.active_tax_codes || 0,
        pendingReturns: data.pending_returns || 0,
        complianceScore: data.compliance_score || 0
      }
    }
    
    if (deadlinesResponse.ok) {
      const data = await deadlinesResponse.json()
      upcomingDeadlines.value = data.map(d => ({
        id: d.id,
        description: d.description,
        jurisdiction: d.jurisdiction,
        dueDate: new Date(d.due_date),
        daysRemaining: d.days_remaining,
        status: d.status
      }))
    }
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboardData()
})

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date)
}

const getDaysSeverity = (days: number) => {
  if (days <= 7) return 'danger'
  if (days <= 14) return 'warning'
  return 'success'
}

const navigateToTaxCodes = () => router.push('/tax/codes')
const navigateToReturns = () => router.push('/tax/returns')
const navigateToReports = () => router.push('/tax/reports')
const navigateToExemptions = () => router.push('/tax/exemptions')
</script>

<style scoped>
.content-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--spacing-lg);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  margin: 0;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.action-btn {
  width: 100%;
  justify-content: flex-start;
}

:deep(.compact-table .p-datatable-tbody td) {
  padding: var(--spacing-sm) var(--spacing-md);
}

:deep(.compact-table .p-datatable-thead th) {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
}
</style>
