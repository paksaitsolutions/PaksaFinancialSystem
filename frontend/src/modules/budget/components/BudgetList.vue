<template>
  <div class="budget-list">
    <Card>
      <template #title>Budget List</template>
      <template #content>
        <div class="flex justify-content-between align-items-center mb-4">
          <div class="flex align-items-center gap-2">
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText 
                v-model="searchTerm" 
                placeholder="Search budgets..." 
                class="p-inputtext-sm"
              />
            </span>
            <Dropdown 
              v-model="selectedStatus"
              :options="statusOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="All Status"
              class="p-inputtext-sm"
            />
          </div>
          <Button 
            label="New Budget" 
            icon="pi pi-plus"
            @click="$emit('create-budget')"
          />
        </div>
        
        <DataTable 
          :value="filteredBudgets" 
          :loading="loading"
          responsiveLayout="scroll"
          :paginator="true"
          :rows="10"
        >
          <Column field="name" header="Budget Name" :sortable="true">
            <template #body="{ data }">
              <div class="cursor-pointer" @click="$emit('view-budget', data)">
                <div class="font-medium">{{ data.name }}</div>
                <div class="text-sm text-500">{{ data.description }}</div>
              </div>
            </template>
          </Column>
          
          <Column field="period" header="Period" :sortable="true">
            <template #body="{ data }">
              {{ formatPeriod(data.startDate, data.endDate) }}
            </template>
          </Column>
          
          <Column field="totalAmount" header="Total Amount" :sortable="true">
            <template #body="{ data }">
              <span class="font-bold">
                {{ formatCurrency(data.totalAmount) }}
              </span>
            </template>
          </Column>
          
          <Column field="spent" header="Spent" :sortable="true">
            <template #body="{ data }">
              <div>
                <div class="font-medium">{{ formatCurrency(data.spent) }}</div>
                <ProgressBar 
                  :value="(data.spent / data.totalAmount) * 100" 
                  :showValue="false"
                  class="mt-1"
                  style="height: 4px"
                />
              </div>
            </template>
          </Column>
          
          <Column field="remaining" header="Remaining" :sortable="true">
            <template #body="{ data }">
              <span :class="data.remaining >= 0 ? 'text-green-500' : 'text-red-500'" class="font-bold">
                {{ formatCurrency(data.remaining) }}
              </span>
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          
          <Column>
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-text p-button-sm"
                  @click="$emit('view-budget', data)"
                  v-tooltip.top="'View'"
                />
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-sm"
                  @click="$emit('edit-budget', data)"
                  v-tooltip.top="'Edit'"
                />
                <Button 
                  icon="pi pi-copy" 
                  class="p-button-text p-button-sm"
                  @click="$emit('copy-budget', data)"
                  v-tooltip.top="'Copy'"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-danger"
                  @click="$emit('delete-budget', data)"
                  v-tooltip.top="'Delete'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Budget {
  id: number
  name: string
  description: string
  startDate: string
  endDate: string
  totalAmount: number
  spent: number
  remaining: number
  status: string
}

const props = defineProps<{
  budgets: Budget[]
  loading?: boolean
}>()

const emit = defineEmits(['create-budget', 'view-budget', 'edit-budget', 'copy-budget', 'delete-budget'])

const searchTerm = ref('')
const selectedStatus = ref('')

const statusOptions = [
  { label: 'All Status', value: '' },
  { label: 'Draft', value: 'Draft' },
  { label: 'Active', value: 'Active' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Cancelled', value: 'Cancelled' }
]

const filteredBudgets = computed(() => {
  let filtered = props.budgets || []
  
  if (searchTerm.value) {
    filtered = filtered.filter(budget => 
      budget.name.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
      budget.description.toLowerCase().includes(searchTerm.value.toLowerCase())
    )
  }
  
  if (selectedStatus.value) {
    filtered = filtered.filter(budget => budget.status === selectedStatus.value)
  }
  
  return filtered
})

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const formatPeriod = (startDate: string, endDate: string) => {
  const start = new Date(startDate).toLocaleDateString()
  const end = new Date(endDate).toLocaleDateString()
  return `${start} - ${end}`
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'Active': return 'success'
    case 'Draft': return 'info'
    case 'Completed': return 'success'
    case 'Cancelled': return 'danger'
    default: return 'info'
  }
}
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.cursor-pointer:hover {
  background-color: var(--surface-hover);
}
</style>