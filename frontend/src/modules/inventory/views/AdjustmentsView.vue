<template>
  <div class="adjustments-view">
    <Card>
      <template #title>
        <div class="header-content">
          <div class="header-text">
            <h2 class="m-0">Inventory Adjustments</h2>
            <p class="text-600 mt-1 mb-0">Track inventory quantity adjustments</p>
          </div>
          <div class="header-actions">
            <Button icon="pi pi-plus" label="New Adjustment" @click="showCreateDialog = true" />
          </div>
        </div>
      </template>
      
      <template #content>
        <DataTable :value="adjustments" :loading="loading" paginator :rows="10">
          <Column field="adjustment_number" header="Adjustment #" sortable />
          <Column field="adjustment_date" header="Date" sortable>
            <template #body="{ data }">
              {{ formatDate(data.adjustment_date) }}
            </template>
          </Column>
          <Column field="reason" header="Reason" />
          <Column field="total_adjustment_value" header="Total Value">
            <template #body="{ data }">
              {{ formatCurrency(data.total_adjustment_value || 0) }}
            </template>
          </Column>
          <Column field="status" header="Status">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" size="small" text @click="viewAdjustment(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="showCreateDialog" modal header="New Adjustment" :style="{ width: '600px' }">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Adjustment Number *</label>
            <InputText v-model="newAdjustment.adjustment_number" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Date *</label>
            <Calendar v-model="newAdjustment.adjustment_date" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Reason</label>
            <InputText v-model="newAdjustment.reason" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Total Adjustment Value</label>
            <InputNumber v-model="newAdjustment.total_adjustment_value" mode="currency" currency="USD" class="w-full" />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showCreateDialog = false" />
        <Button label="Save" @click="saveAdjustment" :loading="saving" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { inventoryService, type InventoryAdjustment } from '@/services/inventoryService'
import { formatCurrency } from '@/utils/formatters'

const toast = useToast()
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const adjustments = ref<InventoryAdjustment[]>([])

const newAdjustment = reactive({
  adjustment_number: '',
  adjustment_date: new Date(),
  reason: '',
  total_adjustment_value: 0
})

const loadAdjustments = async () => {
  loading.value = true
  try {
    adjustments.value = await inventoryService.getAdjustments()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load adjustments' })
  } finally {
    loading.value = false
  }
}

const saveAdjustment = async () => {
  saving.value = true
  try {
    await inventoryService.createAdjustment({
      ...newAdjustment,
      adjustment_date: newAdjustment.adjustment_date.toISOString()
    })
    toast.add({ severity: 'success', summary: 'Success', detail: 'Adjustment created successfully' })
    showCreateDialog.value = false
    Object.assign(newAdjustment, { adjustment_number: '', adjustment_date: new Date(), reason: '', total_adjustment_value: 0 })
    loadAdjustments()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create adjustment' })
  } finally {
    saving.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'draft': return 'info'
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    default: return 'info'
  }
}

const viewAdjustment = (adjustment: InventoryAdjustment) => {
  console.log('View adjustment:', adjustment)
}

onMounted(() => {
  loadAdjustments()
})
</script>

<style scoped>
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

@media screen and (max-width: 960px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>