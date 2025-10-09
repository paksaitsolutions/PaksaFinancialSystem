<template>
  <div class="depreciation-view">
    <Card>
      <template #title>
        <div class="header-content">
          <div class="header-text">
            <h2 class="m-0">Asset Depreciation</h2>
            <p class="text-600 mt-1 mb-0">Manage depreciation schedules and calculations</p>
          </div>
          <div class="header-actions">
            <Button icon="pi pi-plus" label="Add Depreciation" @click="showCreateDialog = true" />
          </div>
        </div>
      </template>
      
      <template #content>
        <!-- Asset Selection -->
        <div class="mb-4">
          <div class="field">
            <label>Select Asset</label>
            <Dropdown 
              v-model="selectedAssetId" 
              :options="assets" 
              optionLabel="asset_name" 
              optionValue="id" 
              placeholder="Select an asset" 
              class="w-full md:w-20rem"
              @change="loadDepreciationRecords"
            />
          </div>
        </div>

        <!-- Depreciation Records -->
        <DataTable :value="depreciationRecords" :loading="loading" paginator :rows="10">
          <template #empty>
            <div class="text-center p-4">
              <i class="pi pi-info-circle text-4xl text-400 mb-3"></i>
              <p class="text-600">{{ selectedAssetId ? 'No depreciation records found for this asset' : 'Please select an asset to view depreciation records' }}</p>
            </div>
          </template>
          
          <Column field="depreciation_date" header="Date" sortable>
            <template #body="{ data }">
              {{ formatDate(data.depreciation_date) }}
            </template>
          </Column>
          <Column field="depreciation_amount" header="Depreciation Amount" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.depreciation_amount) }}
            </template>
          </Column>
          <Column field="accumulated_depreciation" header="Accumulated Depreciation" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.accumulated_depreciation) }}
            </template>
          </Column>
          <Column field="book_value" header="Book Value" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.book_value) }}
            </template>
          </Column>
          <Column field="notes" header="Notes" />
        </DataTable>
      </template>
    </Card>

    <!-- Create Depreciation Dialog -->
    <Dialog v-model:visible="showCreateDialog" modal header="Add Depreciation Entry" :style="{ width: '500px' }">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label>Asset *</label>
            <Dropdown 
              v-model="newDepreciation.asset_id" 
              :options="assets" 
              optionLabel="asset_name" 
              optionValue="id" 
              placeholder="Select asset" 
              class="w-full"
              :class="{ 'p-invalid': submitted && !newDepreciation.asset_id }"
            />
            <small class="p-error" v-if="submitted && !newDepreciation.asset_id">Asset is required</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Depreciation Date *</label>
            <InputText v-model="newDepreciation.depreciation_date" type="date" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Depreciation Amount *</label>
            <InputNumber 
              v-model="newDepreciation.depreciation_amount" 
              mode="currency" 
              currency="USD" 
              class="w-full" 
              :min="0"
              :class="{ 'p-invalid': submitted && !newDepreciation.depreciation_amount }"
            />
            <small class="p-error" v-if="submitted && !newDepreciation.depreciation_amount">Amount is required</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Accumulated Depreciation *</label>
            <InputNumber 
              v-model="newDepreciation.accumulated_depreciation" 
              mode="currency" 
              currency="USD" 
              class="w-full" 
              :min="0"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Book Value *</label>
            <InputNumber 
              v-model="newDepreciation.book_value" 
              mode="currency" 
              currency="USD" 
              class="w-full" 
              :min="0"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Notes</label>
            <Textarea v-model="newDepreciation.notes" rows="3" class="w-full" />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showCreateDialog = false" />
        <Button label="Save" @click="saveDepreciation" :loading="saving" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { fixedAssetsService, type FixedAsset, type AssetDepreciation } from '@/services/fixedAssetsService'
import { formatCurrency } from '@/utils/formatters'

const toast = useToast()
const loading = ref(false)
const saving = ref(false)
const submitted = ref(false)
const showCreateDialog = ref(false)
const selectedAssetId = ref<string>('')

const assets = ref<FixedAsset[]>([])
const depreciationRecords = ref<AssetDepreciation[]>([])

const newDepreciation = reactive({
  asset_id: '',
  depreciation_date: new Date().toISOString().split('T')[0],
  depreciation_amount: 0,
  accumulated_depreciation: 0,
  book_value: 0,
  notes: ''
})

const loadAssets = async () => {
  try {
    assets.value = await fixedAssetsService.getAssets()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load assets' })
  }
}

const loadDepreciationRecords = async () => {
  if (!selectedAssetId.value) {
    depreciationRecords.value = []
    return
  }

  loading.value = true
  try {
    depreciationRecords.value = await fixedAssetsService.getAssetDepreciation(selectedAssetId.value)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load depreciation records' })
  } finally {
    loading.value = false
  }
}

const saveDepreciation = async () => {
  submitted.value = true
  
  if (!newDepreciation.asset_id || !newDepreciation.depreciation_amount) {
    return
  }

  saving.value = true
  try {
    await fixedAssetsService.createDepreciationEntry(newDepreciation.asset_id, {
      depreciation_date: newDepreciation.depreciation_date,
      depreciation_amount: newDepreciation.depreciation_amount,
      accumulated_depreciation: newDepreciation.accumulated_depreciation,
      book_value: newDepreciation.book_value,
      notes: newDepreciation.notes
    })
    
    toast.add({ severity: 'success', summary: 'Success', detail: 'Depreciation entry created successfully' })
    showCreateDialog.value = false
    submitted.value = false
    
    // Reset form
    Object.assign(newDepreciation, {
      asset_id: '',
      depreciation_date: new Date().toISOString().split('T')[0],
      depreciation_amount: 0,
      accumulated_depreciation: 0,
      book_value: 0,
      notes: ''
    })
    
    // Reload records if viewing the same asset
    if (selectedAssetId.value === newDepreciation.asset_id) {
      await loadDepreciationRecords()
    }
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create depreciation entry' })
  } finally {
    saving.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  loadAssets()
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