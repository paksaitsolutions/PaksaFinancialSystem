<template>
  <div class="tax-dashboard">
    <!-- Header -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-3xl font-bold text-900 m-0">Tax Management</h1>
        <p class="text-600 mt-1 mb-0">Comprehensive tax compliance and reporting</p>
      </div>
      <div class="flex gap-2">
        <Button icon="pi pi-refresh" label="Refresh" severity="secondary" @click="refreshData" />
        <Button icon="pi pi-plus" label="New Tax Code" @click="$router.push('/tax/codes')" />
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid mb-4">
      <div class="col-12 md:col-3">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Total Tax Liability</div>
                <div class="text-2xl font-bold text-900">{{ formatCurrency(kpis.totalLiability) }}</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-arrow-up text-red-500 mr-1"></i>
                  {{ kpis.liabilityChange }}% from last period
                </div>
              </div>
              <div class="bg-red-100 border-round p-3">
                <i class="pi pi-exclamation-triangle text-red-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-3">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Active Tax Codes</div>
                <div class="text-2xl font-bold text-900">{{ kpis.activeTaxCodes }}</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-check-circle text-green-500 mr-1"></i>
                  All codes current
                </div>
              </div>
              <div class="bg-blue-100 border-round p-3">
                <i class="pi pi-code text-blue-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-3">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Pending Returns</div>
                <div class="text-2xl font-bold text-orange-500">{{ kpis.pendingReturns }}</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-clock text-orange-500 mr-1"></i>
                  {{ kpis.daysUntilDue }} days until due
                </div>
              </div>
              <div class="bg-orange-100 border-round p-3">
                <i class="pi pi-file-o text-orange-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-3">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Compliance Score</div>
                <div class="text-2xl font-bold text-green-500">{{ kpis.complianceScore }}%</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-shield text-green-500 mr-1"></i>
                  Excellent rating
                </div>
              </div>
              <div class="bg-green-100 border-round p-3">
                <i class="pi pi-shield text-green-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Quick Actions & Recent Activity -->
    <div class="grid">
      <div class="col-12 lg:col-6">
        <Card>
          <template #title>Quick Actions</template>
          <template #content>
            <div class="grid">
              <div class="col-6">
                <Button
                  label="Calculate Tax"
                  icon="pi pi-calculator"
                  class="w-full mb-3"
                  @click="$router.push('/tax/codes')"
                />
              </div>
              <div class="col-6">
                <Button
                  label="File Return"
                  icon="pi pi-file"
                  class="w-full mb-3"
                  severity="success"
                  @click="$router.push('/tax/returns')"
                />
              </div>
              <div class="col-6">
                <Button
                  label="View Reports"
                  icon="pi pi-chart-line"
                  class="w-full mb-3"
                  severity="info"
                  @click="$router.push('/tax/reports')"
                />
              </div>
              <div class="col-6">
                <Button
                  label="Manage Exemptions"
                  icon="pi pi-shield"
                  class="w-full mb-3"
                  severity="warning"
                  @click="$router.push('/tax/exemptions')"
                />
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-6">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Recent Tax Activity</span>
              <Button label="View All" text @click="$router.push('/tax/reports')" />
            </div>
          </template>
          <template #content>
            <div v-if="recentActivity.length === 0" class="text-center py-4">
              <i class="pi pi-inbox text-4xl text-400 mb-3"></i>
              <p class="text-500">No recent activity</p>
            </div>
            <div v-else>
              <div v-for="activity in recentActivity" :key="activity.id" class="flex align-items-center justify-content-between py-2 border-bottom-1 surface-border">
                <div class="flex align-items-center">
                  <div class="bg-primary-100 border-round p-2 mr-3">
                    <i :class="getActivityIcon(activity.type)" class="text-primary"></i>
                  </div>
                  <div>
                    <div class="font-medium text-900">{{ activity.description }}</div>
                    <div class="text-sm text-500">{{ formatDate(activity.date) }}</div>
                  </div>
                </div>
                <Tag :value="activity.status" :severity="getStatusSeverity(activity.status)" />
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Upcoming Deadlines -->
    <div class="mt-4">
      <Card>
        <template #title>Upcoming Tax Deadlines</template>
        <template #content>
          <DataTable :value="upcomingDeadlines" responsiveLayout="scroll" class="p-datatable-sm">
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
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <Button icon="pi pi-eye" size="small" text @click="viewDeadline(data)" />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { formatCurrency } from '@/utils/formatters'
import taxService from '@/services/taxService'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'

const router = useRouter()
const toast = useToast()
const loading = ref(false)

// KPI Data
const kpis = ref({
  totalLiability: 0,
  liabilityChange: 0,
  activeTaxCodes: 0,
  pendingReturns: 0,
  daysUntilDue: 0,
  complianceScore: 0
})

// Recent Activity
const recentActivity = ref([])

// Upcoming Deadlines
const upcomingDeadlines = ref([])

// Methods
const loadDashboardData = async () => {
  loading.value = true
  try {
    const [kpiData, rates, transactions, deadlines] = await Promise.all([
      taxService.getTaxKPIs(),
      taxService.getTaxRates({ active_only: true }),
      taxService.getTaxTransactions({ limit: 5 }),
      taxService.getUpcomingDeadlines()
    ])
    
    // Update KPIs
    kpis.value = {
      totalLiability: kpiData.total_liability,
      liabilityChange: kpiData.liability_change,
      activeTaxCodes: kpiData.active_tax_codes,
      pendingReturns: kpiData.pending_returns,
      daysUntilDue: kpiData.days_until_due,
      complianceScore: kpiData.compliance_score
    }

    // Update recent activity from transactions
    recentActivity.value = transactions.slice(0, 3).map(t => ({
      id: t.id,
      type: 'calculation',
      description: `${t.entity_type} tax calculated - ${formatCurrency(t.tax_amount)}`,
      date: new Date(t.transaction_date),
      status: 'completed'
    }))

    // Update upcoming deadlines
    upcomingDeadlines.value = deadlines.map(d => ({
      id: d.id,
      description: d.description,
      jurisdiction: d.jurisdiction,
      dueDate: new Date(d.due_date),
      daysRemaining: d.days_remaining,
      status: d.status
    }))

  } catch (error) {
    console.error('Error loading dashboard data:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load tax data' })
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  await loadDashboardData()
  toast.add({ severity: 'success', summary: 'Refreshed', detail: 'Tax data refreshed successfully' })
}

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date)
}

const getActivityIcon = (type: string) => {
  const icons = {
    calculation: 'pi pi-calculator',
    filing: 'pi pi-file',
    exemption: 'pi pi-shield'
  }
  return icons[type] || 'pi pi-circle'
}

const getStatusSeverity = (status: string) => {
  const severities = {
    completed: 'success',
    submitted: 'info',
    approved: 'success',
    pending: 'warning',
    draft: 'secondary',
    overdue: 'danger'
  }
  return severities[status] || 'info'
}

const getDaysSeverity = (days: number) => {
  if (days <= 7) return 'danger'
  if (days <= 14) return 'warning'
  return 'success'
}

const viewDeadline = (deadline: any) => {
  router.push(`/tax/returns/${deadline.id}`)
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.tax-dashboard {
  padding: 1.5rem;
}
</style>
