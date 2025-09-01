<template>
  <div class="budget-version-comparison">
    <Card>
      <template #title>Budget Version Comparison</template>
      <template #content>
        <div v-if="versions && versions.length >= 2" class="comparison-content">
          <div class="version-selector mb-4">
            <div class="grid">
              <div class="col-6">
                <div class="field">
                  <label>Version A</label>
                  <Dropdown 
                    v-model="selectedVersionA"
                    :options="versions"
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Select version"
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-6">
                <div class="field">
                  <label>Version B</label>
                  <Dropdown 
                    v-model="selectedVersionB"
                    :options="versions"
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Select version"
                    class="w-full"
                  />
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="comparisonData" class="comparison-results">
            <div class="summary-cards mb-4">
              <div class="grid">
                <div class="col-4">
                  <Card class="text-center">
                    <template #content>
                      <div class="text-2xl font-bold">
                        {{ formatCurrency(comparisonData.totalDifference) }}
                      </div>
                      <div class="text-sm text-500">Total Difference</div>
                    </template>
                  </Card>
                </div>
                <div class="col-4">
                  <Card class="text-center">
                    <template #content>
                      <div class="text-2xl font-bold text-green-500">
                        {{ comparisonData.increasedCategories }}
                      </div>
                      <div class="text-sm text-500">Increased Categories</div>
                    </template>
                  </Card>
                </div>
                <div class="col-4">
                  <Card class="text-center">
                    <template #content>
                      <div class="text-2xl font-bold text-red-500">
                        {{ comparisonData.decreasedCategories }}
                      </div>
                      <div class="text-sm text-500">Decreased Categories</div>
                    </template>
                  </Card>
                </div>
              </div>
            </div>
            
            <DataTable :value="comparisonData.categoryComparisons" class="p-datatable-sm">
              <Column field="category" header="Category" :sortable="true" />
              <Column field="versionA" header="Version A" :sortable="true">
                <template #body="{ data }">
                  {{ formatCurrency(data.versionA) }}
                </template>
              </Column>
              <Column field="versionB" header="Version B" :sortable="true">
                <template #body="{ data }">
                  {{ formatCurrency(data.versionB) }}
                </template>
              </Column>
              <Column field="difference" header="Difference" :sortable="true">
                <template #body="{ data }">
                  <span :class="getDifferenceClass(data.difference)">
                    {{ formatCurrency(data.difference) }}
                  </span>
                </template>
              </Column>
              <Column field="percentageChange" header="% Change" :sortable="true">
                <template #body="{ data }">
                  <span :class="getDifferenceClass(data.difference)">
                    {{ data.percentageChange }}%
                  </span>
                </template>
              </Column>
            </DataTable>
          </div>
          
          <div v-else class="text-center p-4">
            <p class="text-500">Select two versions to compare</p>
          </div>
        </div>
        
        <div v-else class="text-center p-4">
          <i class="pi pi-info-circle text-4xl text-500 mb-3"></i>
          <p class="text-500">At least two budget versions are required for comparison.</p>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface BudgetVersion {
  id: number
  name: string
  totalAmount: number
  categories: { name: string; amount: number }[]
  createdDate: string
}

interface CategoryComparison {
  category: string
  versionA: number
  versionB: number
  difference: number
  percentageChange: number
}

interface ComparisonData {
  totalDifference: number
  increasedCategories: number
  decreasedCategories: number
  categoryComparisons: CategoryComparison[]
}

const props = defineProps<{
  versions: BudgetVersion[]
}>()

const selectedVersionA = ref<number | null>(null)
const selectedVersionB = ref<number | null>(null)

const comparisonData = computed<ComparisonData | null>(() => {
  if (!selectedVersionA.value || !selectedVersionB.value) return null
  
  const versionA = props.versions.find(v => v.id === selectedVersionA.value)
  const versionB = props.versions.find(v => v.id === selectedVersionB.value)
  
  if (!versionA || !versionB) return null
  
  const categoryComparisons: CategoryComparison[] = []
  const allCategories = new Set([
    ...versionA.categories.map(c => c.name),
    ...versionB.categories.map(c => c.name)
  ])
  
  let increasedCategories = 0
  let decreasedCategories = 0
  
  allCategories.forEach(categoryName => {
    const amountA = versionA.categories.find(c => c.name === categoryName)?.amount || 0
    const amountB = versionB.categories.find(c => c.name === categoryName)?.amount || 0
    const difference = amountB - amountA
    const percentageChange = amountA > 0 ? ((difference / amountA) * 100) : 0
    
    if (difference > 0) increasedCategories++
    else if (difference < 0) decreasedCategories++
    
    categoryComparisons.push({
      category: categoryName,
      versionA: amountA,
      versionB: amountB,
      difference,
      percentageChange: Math.round(percentageChange * 100) / 100
    })
  })
  
  return {
    totalDifference: versionB.totalAmount - versionA.totalAmount,
    increasedCategories,
    decreasedCategories,
    categoryComparisons: categoryComparisons.sort((a, b) => Math.abs(b.difference) - Math.abs(a.difference))
  }
})

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const getDifferenceClass = (difference: number) => {
  if (difference > 0) return 'text-green-500 font-bold'
  if (difference < 0) return 'text-red-500 font-bold'
  return 'text-500'
}

// Auto-select first two versions if available
watch(() => props.versions, (newVersions) => {
  if (newVersions && newVersions.length >= 2) {
    if (!selectedVersionA.value) selectedVersionA.value = newVersions[0].id
    if (!selectedVersionB.value) selectedVersionB.value = newVersions[1].id
  }
}, { immediate: true })
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

.summary-cards .p-card {
  height: 100%;
}
</style>