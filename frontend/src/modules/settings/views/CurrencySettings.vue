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
        <DataTable :value="currencies" paginator :rows="10" dataKey="id">
          <Column field="code" header="Code" sortable />
          <Column field="name" header="Name" sortable />
          <Column field="symbol" header="Symbol" sortable />
          <Column field="rate" header="Exchange Rate" sortable>
            <template #body="slotProps">
              {{ slotProps.data.rate.toFixed(4) }}
            </template>
          </Column>
          <Column field="isBase" header="Base Currency" sortable>
            <template #body="slotProps">
              <Tag v-if="slotProps.data.isBase" value="Base" severity="success" />
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="slotProps">
              <Tag :value="slotProps.data.status" :severity="slotProps.data.status === 'Active' ? 'success' : 'danger'" />
            </template>
          </Column>
          <Column field="lastUpdated" header="Last Updated" sortable />
          <Column header="Actions">
            <template #body="slotProps">
              <div class="flex gap-2">
                <Button icon="pi pi-pencil" size="small" @click="editCurrency(slotProps.data)" />
                <Button icon="pi pi-refresh" size="small" severity="secondary" @click="updateRate(slotProps.data)" />
                <Button v-if="!slotProps.data.isBase" icon="pi pi-star" size="small" severity="warning" @click="setBaseCurrency(slotProps.data)" />
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
          <InputText v-model="newCurrency.code" class="w-full" placeholder="USD" />
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
          <label>Exchange Rate</label>
          <InputNumber v-model="newCurrency.rate" class="w-full" :minFractionDigits="4" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showAddDialog = false" />
        <Button label="Add Currency" @click="addCurrency" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const showAddDialog = ref(false)

const currencies = ref([
  {
    id: 1,
    code: 'USD',
    name: 'US Dollar',
    symbol: '$',
    rate: 1.0000,
    isBase: true,
    status: 'Active',
    lastUpdated: '2024-01-15'
  },
  {
    id: 2,
    code: 'EUR',
    name: 'Euro',
    symbol: '€',
    rate: 0.8500,
    isBase: false,
    status: 'Active',
    lastUpdated: '2024-01-15'
  },
  {
    id: 3,
    code: 'GBP',
    name: 'British Pound',
    symbol: '£',
    rate: 0.7500,
    isBase: false,
    status: 'Active',
    lastUpdated: '2024-01-15'
  }
])

const newCurrency = ref({
  code: '',
  name: '',
  symbol: '',
  rate: 1.0000
})

const activeCurrencies = computed(() => 
  currencies.value.filter(c => c.status === 'Active').length
)

const baseCurrency = computed(() => 
  currencies.value.find(c => c.isBase)
)

const editCurrency = (currency: any) => {
  console.log('Edit currency:', currency)
}

const updateRate = (currency: any) => {
  console.log('Update rate for:', currency)
}

const setBaseCurrency = (currency: any) => {
  currencies.value.forEach(c => c.isBase = false)
  currency.isBase = true
}

const addCurrency = () => {
  const id = Math.max(...currencies.value.map(c => c.id)) + 1
  currencies.value.push({
    id,
    ...newCurrency.value,
    isBase: false,
    status: 'Active',
    lastUpdated: new Date().toISOString().split('T')[0]
  })
  showAddDialog.value = false
  newCurrency.value = { code: '', name: '', symbol: '', rate: 1.0000 }
}
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