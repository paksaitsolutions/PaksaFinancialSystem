<template>
  <Card>
    <template #header>
      <h3 class="p-4 m-0">Project Budget Analysis</h3>
    </template>
    <template #content>
      <div v-if="data && data.length > 0">
        <DataTable
          :value="data"
          :paginator="true"
          :rows="10"
          responsiveLayout="scroll"
        >
          <Column field="project" header="Project"></Column>
          <Column field="budget_amount" header="Budget Amount">
            <template #body="{ data }">
              ${{ formatCurrency(data.budget_amount) }}
            </template>
          </Column>
          <Column field="actual_amount" header="Actual Amount">
            <template #body="{ data }">
              ${{ formatCurrency(data.actual_amount) }}
            </template>
          </Column>
          <Column field="variance" header="Variance">
            <template #body="{ data }">
              <Tag :value="`${data.variance > 0 ? '+' : ''}${data.variance.toFixed(1)}%`" :severity="getVarianceSeverity(data.variance)" />
            </template>
          </Column>
          <Column field="status" header="Status">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
        </DataTable>
      </div>
      <div v-else class="text-center p-4">
        <i class="pi pi-folder text-6xl text-500"></i>
        <p class="text-xl mt-2">No project data available</p>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
interface ProjectAnalysis {
  project: string
  budget_amount: number
  actual_amount: number
  variance: number
  status: string
}

interface Props {
  data: ProjectAnalysis[]
}

defineProps<Props>()

const headers = [
  { text: 'Project', value: 'project' },
  { text: 'Budget Amount', value: 'budget_amount', align: 'right' },
  { text: 'Actual Amount', value: 'actual_amount', align: 'right' },
  { text: 'Variance', value: 'variance', align: 'center' },
  { text: 'Status', value: 'status', align: 'center' }
]

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const getVarianceSeverity = (variance: number) => {
  if (variance > 10) return 'danger'
  if (variance > 5) return 'warning'
  return 'success'
}

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'active': return 'success'
    case 'pending': return 'warning'
    case 'completed': return 'info'
    case 'cancelled': return 'danger'
    default: return 'secondary'
  }
}
</script>