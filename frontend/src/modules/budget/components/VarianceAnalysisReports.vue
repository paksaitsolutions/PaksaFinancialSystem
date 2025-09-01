<template>
  <div class="variance-analysis-reports">
    <Card>
      <template #title>Variance Analysis Reports</template>
      <template #content>
        <div class="report-controls mb-4">
          <div class="grid">
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Report Period</label>
                <Dropdown 
                  v-model="selectedPeriod"
                  :options="periodOptions"
                  optionLabel="label"
                  optionValue="value"
                  class="w-full"
                />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Department</label>
                <Dropdown 
                  v-model="selectedDepartment"
                  :options="departmentOptions"
                  optionLabel="label"
                  optionValue="value"
                  class="w-full"
                />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Variance Type</label>
                <Dropdown 
                  v-model="selectedVarianceType"
                  :options="varianceTypeOptions"
                  optionLabel="label"
                  optionValue="value"
                  class="w-full"
                />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Actions</label>
                <div class="flex gap-2">
                  <Button 
                    label="Generate"
                    icon="pi pi-chart-bar"
                    @click="generateReport"
                    :loading="generating"
                  />
                  <Button 
                    label="Export"
                    icon="pi pi-download"
                    class="p-button-outlined"
                    @click="exportReport"
                    :disabled="!reportData"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="reportData" class="variance-report">
          <div class="summary-section mb-4">
            <div class="grid">
              <div class="col-12 md:col-3">
                <Card class="text-center h-full">
                  <template #content>
                    <div class="text-3xl font-bold text-primary">
                      {{ reportData.totalBudgets }}
                    </div>
                    <div class="text-sm text-500">Total Budgets</div>
                  </template>
                </Card>
              </div>
              <div class="col-12 md:col-3">
                <Card class="text-center h-full">
                  <template #content>
                    <div class="text-3xl font-bold" :class="reportData.totalVariance >= 0 ? 'text-green-500' : 'text-red-500'">
                      {{ formatCurrency(reportData.totalVariance) }}
                    </div>
                    <div class="text-sm text-500">Total Variance</div>
                  </template>
                </Card>
              </div>
              <div class="col-12 md:col-3">
                <Card class="text-center h-full">
                  <template #content>
                    <div class="text-3xl font-bold text-green-500">
                      {{ reportData.favorableVariances }}
                    </div>
                    <div class="text-sm text-500">Favorable Variances</div>
                  </template>
                </Card>
              </div>
              <div class="col-12 md:col-3">
                <Card class="text-center h-full">
                  <template #content>
                    <div class="text-3xl font-bold text-red-500">
                      {{ reportData.unfavorableVariances }}
                    </div>
                    <div class="text-sm text-500">Unfavorable Variances</div>
                  </template>
                </Card>
              </div>
            </div>
          </div>
          
          <div class="variance-details">
            <h4>Variance Analysis Details</h4>
            <DataTable :value="reportData.varianceDetails" class="p-datatable-sm" :sortable="true">
              <Column field="budget" header="Budget" :sortable="true" />
              <Column field="department" header="Department" :sortable="true" />
              <Column field="budgetAmount" header="Budget Amount" :sortable="true">
                <template #body="{ data }">
                  {{ formatCurrency(data.budgetAmount) }}
                </template>
              </Column>
              <Column field="actualAmount" header="Actual Amount" :sortable="true">
                <template #body="{ data }">
                  {{ formatCurrency(data.actualAmount) }}
                </template>
              </Column>
              <Column field="variance" header="Variance" :sortable="true">
                <template #body="{ data }">
                  <span :class="data.variance >= 0 ? 'text-green-500' : 'text-red-500'" class="font-bold">
                    {{ formatCurrency(data.variance) }}
                  </span>
                </template>
              </Column>
              <Column field="variancePercent" header="Variance %" :sortable="true">
                <template #body="{ data }">
                  <span :class="data.variance >= 0 ? 'text-green-500' : 'text-red-500'" class="font-bold">
                    {{ data.variancePercent }}%
                  </span>
                </template>
              </Column>
              <Column field="status" header="Status" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getVarianceStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column field="explanation" header="Explanation" />
            </DataTable>
          </div>
          
          <div class="variance-trends mt-4">
            <h4>Variance Trends</h4>
            <div class="grid">
              <div class="col-12 md:col-6">
                <Card>
                  <template #title>Top Favorable Variances</template>
                  <template #content>
                    <div v-for="item in reportData.topFavorable" :key="item.budget" class="flex justify-content-between align-items-center mb-2">
                      <span>{{ item.budget }}</span>
                      <span class="text-green-500 font-bold">{{ formatCurrency(item.variance) }}</span>
                    </div>
                  </template>
                </Card>
              </div>
              <div class="col-12 md:col-6">
                <Card>
                  <template #title>Top Unfavorable Variances</template>
                  <template #content>
                    <div v-for="item in reportData.topUnfavorable" :key="item.budget" class="flex justify-content-between align-items-center mb-2">
                      <span>{{ item.budget }}</span>
                      <span class="text-red-500 font-bold">{{ formatCurrency(item.variance) }}</span>
                    </div>
                  </template>
                </Card>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center p-4">
          <i class="pi pi-chart-line text-4xl text-500 mb-3"></i>
          <p class="text-500">Click "Generate" to create variance analysis report</p>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface VarianceDetail {
  budget: string
  department: string
  budgetAmount: number
  actualAmount: number
  variance: number
  variancePercent: number
  status: string
  explanation: string
}

interface ReportData {
  totalBudgets: number
  totalVariance: number
  favorableVariances: number
  unfavorableVariances: number
  varianceDetails: VarianceDetail[]
  topFavorable: { budget: string; variance: number }[]
  topUnfavorable: { budget: string; variance: number }[]
}

const selectedPeriod = ref('current')
const selectedDepartment = ref('all')
const selectedVarianceType = ref('all')
const generating = ref(false)
const reportData = ref<ReportData | null>(null)

const periodOptions = [
  { label: 'Current Period', value: 'current' },
  { label: 'Q1 2024', value: 'q1_2024' },
  { label: 'Q2 2024', value: 'q2_2024' },
  { label: 'Q3 2024', value: 'q3_2024' },
  { label: 'Q4 2024', value: 'q4_2024' }
]

const departmentOptions = [
  { label: 'All Departments', value: 'all' },
  { label: 'Finance', value: 'finance' },
  { label: 'Marketing', value: 'marketing' },
  { label: 'Operations', value: 'operations' },
  { label: 'HR', value: 'hr' },
  { label: 'IT', value: 'it' }
]

const varianceTypeOptions = [
  { label: 'All Variances', value: 'all' },
  { label: 'Favorable Only', value: 'favorable' },
  { label: 'Unfavorable Only', value: 'unfavorable' },
  { label: 'Significant (>10%)', value: 'significant' }
]

const generateReport = async () => {
  generating.value = true
  try {
    // Mock report generation
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Mock report data
    reportData.value = {
      totalBudgets: 15,
      totalVariance: -25000,
      favorableVariances: 8,
      unfavorableVariances: 7,
      varianceDetails: [
        {
          budget: 'Marketing Q1',
          department: 'Marketing',
          budgetAmount: 100000,
          actualAmount: 95000,
          variance: 5000,
          variancePercent: 5.0,
          status: 'Favorable',
          explanation: 'Lower advertising costs due to negotiated rates'
        },
        {
          budget: 'IT Equipment',
          department: 'IT',
          budgetAmount: 50000,
          actualAmount: 65000,
          variance: -15000,
          variancePercent: -30.0,
          status: 'Unfavorable',
          explanation: 'Emergency server replacement required'
        },
        {
          budget: 'HR Training',
          department: 'HR',
          budgetAmount: 25000,
          actualAmount: 22000,
          variance: 3000,
          variancePercent: 12.0,
          status: 'Favorable',
          explanation: 'Online training reduced travel costs'
        },
        {
          budget: 'Operations Supplies',
          department: 'Operations',
          budgetAmount: 75000,
          actualAmount: 82000,
          variance: -7000,
          variancePercent: -9.3,
          status: 'Unfavorable',
          explanation: 'Increased material costs due to inflation'
        }
      ],
      topFavorable: [
        { budget: 'Marketing Q1', variance: 5000 },
        { budget: 'HR Training', variance: 3000 },
        { budget: 'Finance Operations', variance: 2500 }
      ],
      topUnfavorable: [
        { budget: 'IT Equipment', variance: -15000 },
        { budget: 'Operations Supplies', variance: -7000 },
        { budget: 'Facility Maintenance', variance: -3000 }
      ]
    }
  } finally {
    generating.value = false
  }
}

const exportReport = () => {
  // Mock export functionality
  console.log('Exporting variance analysis report...')
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const getVarianceStatusSeverity = (status: string) => {
  switch (status) {
    case 'Favorable': return 'success'
    case 'Unfavorable': return 'danger'
    case 'Neutral': return 'info'
    default: return 'info'
  }
}
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color-secondary);
}
</style>