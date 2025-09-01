<template>
  <Card>
    <template #header>
      <h3 class="p-4 m-0">Budget Variance Analysis</h3>
    </template>
    <template #content>
      <div v-if="data && data.length > 0">
        <DataTable
          :value="data"
          :paginator="true"
          :rows="10"
          responsiveLayout="scroll"
        >
          <Column field="category" header="Category"></Column>
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
          <Column field="variance_amount" header="Variance Amount">
            <template #body="{ data }">
              <span :class="getVarianceClass(data.variance_amount)">
                {{ data.variance_amount > 0 ? '+' : '' }}${{ formatCurrency(Math.abs(data.variance_amount)) }}
              </span>
            </template>
          </Column>
          <Column field="variance_percentage" header="Variance %">
            <template #body="{ data }">
              <Tag :value="`${data.variance_percentage > 0 ? '+' : ''}${data.variance_percentage.toFixed(1)}%`" :severity="getVarianceSeverity(data.variance_percentage)" />
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
        <i class="pi pi-chart-line text-6xl text-500"></i>
        <p class="text-xl mt-2">No variance data available</p>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
interface VarianceData {
  category: string
  budget_amount: number
  actual_amount: number
  variance_amount: number
  variance_percentage: number
  status: string
}

interface Props {
  data: VarianceData[]
}

defineProps<Props>()

const headers = [
  { text: 'Category', value: 'category' },
  { text: 'Budget Amount', value: 'budget_amount', align: 'right' },
  { text: 'Actual Amount', value: 'actual_amount', align: 'right' },
  { text: 'Variance Amount', value: 'variance_amount', align: 'right' },
  { text: 'Variance %', value: 'variance_percentage', align: 'center' },
  { text: 'Status', value: 'status', align: 'center' }
]

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const getVarianceSeverity = (variance: number) => {
  if (Math.abs(variance) > 15) return 'danger'
  if (Math.abs(variance) > 10) return 'warning'
  return 'success'
}

const getVarianceClass = (variance: number) => {
  if (variance > 0) return 'text-red-500'
  if (variance < 0) return 'text-green-500'
  return 'text-gray-500'
}

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'on track': return 'success'
    case 'at risk': return 'warning'
    case 'over budget': return 'danger'
    case 'under budget': return 'info'
    default: return 'secondary'
  }
}
</script>