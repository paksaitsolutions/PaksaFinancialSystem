<template>
  <div class="currency-settings">
    <div class="page-header">
      <h1>Currency Settings</h1>
      <Button label="Add Currency" icon="pi pi-plus" @click="showAddDialog = true" />
    </div>

    <div class="grid">
      <div class="col-12 md:col-4">
        <Card>
          <template #content>
            <div class="stat-card">
              <div class="stat-value">{{ currencies.length }}</div>
              <div class="stat-label">Total Currencies</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-4">
        <Card>
          <template #content>
            <div class="stat-card">
              <div class="stat-value">{{ activeCurrencies }}</div>
              <div class="stat-label">Active Currencies</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-4">
        <Card>
          <template #content>
            <div class="stat-card">
              <div class="stat-value">{{ baseCurrency?.code || 'USD' }}</div>
              <div class="stat-label">Base Currency</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Card class="mt-4">
      <template #title>Currency Management</template>
      <template #content>
        <DataTable :value="currencies" :loading="loading" paginator :rows="10" dataKey="id">
          <Column field="code" header="Code" sortable />
          <Column field="name" header="Name" sortable />
          <Column field="symbol" header="Symbol" sortable />
          <Column field="decimal_places" header="Decimal Places" sortable />
          <Column field="is_base_currency" header="Base Currency" sortable>
            <template #body="{ data }">
              <Tag v-if="data.is_base_currency" value="Base" severity="success" />
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status === 'active' ? 'Active' : 'Inactive'" :severity="data.status === 'active' ? 'success' : 'danger'" />
            </template>
          </Column>
          <Column field="updated_at" header="Last Updated" sortable>
            <template #body="{ data }">
              {{ formatDate(data.updated_at) }}
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button icon="pi pi-pencil" size="small" @click="editCurrency(data)" />
                <Button v-if="!data.is_base_currency" icon="pi pi-star" size="small" severity="warning" @click="setBaseCurrency(data)" />
                <Button icon="pi pi-trash" size="small" severity="danger" @click="deleteCurrency(data)" :disabled="data.is_base_currency" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="showAddDialog" modal header="Add Currency" :style="{ width: '30rem' }">
      <div class="grid">
        <div class="col-12">
          <label>Currency Code</label>
          <InputText v-model="newCurrency.code" class="w-full" placeholder="USD" maxlength="3" />
        </div>
        <div class="col-12">
          <label>Currency Name</label>
          <InputText v-model="newCurrency.name" class="w-full" placeholder="US Dollar" />
        </div>
        <div class="col-12">
          <label>Symbol</label>
          <InputText v-model="newCurrency.symbol" class="w-full" placeholder="$" />
        </div>
        <div class="col-12">
          <label>Decimal Places</label>
          <InputNumber v-model="newCurrency.decimal_places" class="w-full" :min="0" :max="4" />
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox id="isBaseCurrency" v-model="newCurrency.is_base_currency" :binary="true" />
            <label for="isBaseCurrency">Base Currency</label>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showAddDialog = false" />
        <Button label="Add Currency" @click="addCurrency" :loading="saving" />
      </template>
    </Dialog>

    <Dialog v-model:visible="showEditDialog" modal header="Edit Currency" :style="{ width: '30rem' }">
      <div class="grid">
        <div class="col-12">
          <label>Currency Code</label>
          <InputText v-model="editedCurrency.code" class="w-full" disabled />
        </div>
        <div class="col-12">
          <label>Currency Name</label>
          <InputText v-model="editedCurrency.name" class="w-full" />
        </div>
        <div class="col-12">
          <label>Symbol</label>
          <InputText v-model="editedCurrency.symbol" class="w-full" />
        </div>
        <div class="col-12">
          <label>Decimal Places</label>
          <InputNumber v-model="editedCurrency.decimal_places" class="w-full" :min="0" :max="4" />
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox id="editIsBaseCurrency" v-model="editedCurrency.is_base_currency" :binary="true" />
            <label for="editIsBaseCurrency">Base Currency</label>
          </div>
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox id="editIsActive" v-model="editedCurrency.is_active" :binary="true" />
            <label for="editIsActive">Active</label>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showEditDialog = false" />
        <Button label="Update Currency" @click="updateCurrency" :loading="saving" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import currencyService, { type Currency } from '@/services/currencyService'

const toast = useToast()
const confirm = useConfirm()

const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)

const currencies = ref<Currency[]>([])

const newCurrency = ref({
  code: '',
  name: '',
  symbol: '',
  decimal_places: 2,
  is_base_currency: false
})

const editedCurrency = ref({
  id: '',
  code: '',
  name: '',
  symbol: '',
  decimal_places: 2,
  is_base_currency: false,
  is_active: true
})

const activeCurrencies = computed(() => 
  currencies.value.filter(c => c.status === 'active').length
)

const baseCurrency = computed(() => 
  currencies.value.find(c => c.is_base_currency)
)

const loadCurrencies = async () => {
  loading.value = true
  try {
    const response = await currencyService.getAllCurrencies(true)
    currencies.value = response.data
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load currencies' })
  } finally {
    loading.value = false
  }
}

const editCurrency = (currency: Currency) => {
  editedCurrency.value = {
    ...currency,
    is_active: currency.status === 'active'
  }
  showEditDialog.value = true
}

const setBaseCurrency = async (currency: Currency) => {
  try {
    await currencyService.updateCurrency(currency.id, { is_base_currency: true })
    toast.add({ severity: 'success', summary: 'Success', detail: 'Base currency updated' })
    await loadCurrencies()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to update base currency' })
  }
}

const addCurrency = async () => {
  saving.value = true
  try {
    const currencyData = {
      ...newCurrency.value,
      status: 'active' as const
    }
    await currencyService.createCurrency(currencyData)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Currency added successfully' })
    showAddDialog.value = false
    newCurrency.value = { code: '', name: '', symbol: '', decimal_places: 2, is_base_currency: false }
    await loadCurrencies()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to add currency' })
  } finally {
    saving.value = false
  }
}

const updateCurrency = async () => {
  saving.value = true
  try {
    const currencyData = {
      ...editedCurrency.value,
      status: editedCurrency.value.is_active ? 'active' as const : 'inactive' as const
    }
    delete currencyData.is_active
    delete currencyData.id
    
    await currencyService.updateCurrency(editedCurrency.value.id, currencyData)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Currency updated successfully' })
    showEditDialog.value = false
    await loadCurrencies()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to update currency' })
  } finally {
    saving.value = false
  }
}

const deleteCurrency = (currency: Currency) => {
  confirm.require({
    message: `Are you sure you want to delete currency "${currency.name}"?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try {
        await currencyService.deleteCurrency(currency.id)
        toast.add({ severity: 'success', summary: 'Success', detail: 'Currency deleted successfully' })
        await loadCurrencies()
      } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete currency' })
      }
    }
  })
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  loadCurrencies()
})
</script>

<style scoped>
.currency-settings {
  padding: 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--primary-color);
}

.stat-label {
  color: var(--text-color-secondary);
  margin-top: 0.5rem;
}
</style>