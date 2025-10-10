<template>
  <div class="budget-export">
    <h2>Export Budget</h2>
    
    <Card>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label>Select Budget</label>
              <Dropdown v-model="selectedBudget" :options="budgets" optionLabel="name" optionValue="id" placeholder="Select Budget" class="w-full" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label>Export Format</label>
              <Dropdown v-model="exportFormat" :options="formats" optionLabel="label" optionValue="value" placeholder="Select Format" class="w-full" />
            </div>
          </div>
          <div class="col-12">
            <div class="field-checkbox">
              <Checkbox v-model="includeActuals" :binary="true" />
              <label>Include Actual vs Budget Comparison</label>
            </div>
          </div>
          <div class="col-12">
            <div class="field-checkbox">
              <Checkbox v-model="includeVariance" :binary="true" />
              <label>Include Variance Analysis</label>
            </div>
          </div>
          <div class="col-12">
            <div class="field-checkbox">
              <Checkbox v-model="includeCharts" :binary="true" />
              <label>Include Charts and Graphs</label>
            </div>
          </div>
        </div>
        
        <div class="export-actions mt-4">
          <Button label="Export Budget" icon="pi pi-download" @click="exportBudget" :loading="exporting" :disabled="!selectedBudget || !exportFormat" />
          <Button label="Schedule Export" icon="pi pi-clock" severity="secondary" @click="scheduleExport" class="ml-2" />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import budgetService from '@/services/budgetService'

const toast = useToast()
const exporting = ref(false)
const budgets = ref([])
const selectedBudget = ref('')
const exportFormat = ref('')
const includeActuals = ref(true)
const includeVariance = ref(true)
const includeCharts = ref(false)

const formats = ref([
  { label: 'Excel (.xlsx)', value: 'excel' },
  { label: 'CSV (.csv)', value: 'csv' },
  { label: 'PDF Report', value: 'pdf' }
])

const exportBudget = async () => {
  exporting.value = true
  try {
    const blob = await budgetService.exportBudget(selectedBudget.value, exportFormat.value)
    
    // Create download link
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `budget_export.${exportFormat.value}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Budget exported successfully' 
    })
  } catch (error) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to export budget' 
    })
  } finally {
    exporting.value = false
  }
}

const scheduleExport = () => {
  toast.add({ 
    severity: 'info', 
    summary: 'Scheduled', 
    detail: 'Export scheduled for processing' 
  })
}

onMounted(async () => {
  try {
    budgets.value = await budgetService.getBudgets()
  } catch (error) {
    console.error('Error loading budgets:', error)
  }
})
</script>

<style scoped>
.export-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.field {
  margin-bottom: 1rem;
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
</style>