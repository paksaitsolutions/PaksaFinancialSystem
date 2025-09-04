<template>
  <div class="tax-rate-management">
    <div class="dashboard-header">
      <h1>Tax Rate Management</h1>
      <p>Configure tax rates and jurisdictions</p>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Tax Rates</span>
            <Button label="Add Tax Rate" icon="pi pi-plus" @click="showAddRate = true" />
          </div>
        </template>
        <template #content>
          <DataTable :value="taxRates" responsiveLayout="scroll">
            <Column field="name" header="Tax Name" />
            <Column field="jurisdiction" header="Jurisdiction" />
            <Column field="rate" header="Rate (%)">
              <template #body="{ data }">
                {{ data.rate }}%
              </template>
            </Column>
            <Column field="type" header="Type" />
            <Column field="effectiveDate" header="Effective Date">
              <template #body="{ data }">
                {{ formatDate(data.effectiveDate) }}
              </template>
            </Column>
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button icon="pi pi-pencil" class="p-button-rounded p-button-text" @click="editRate(data)" />
                  <Button icon="pi pi-trash" class="p-button-rounded p-button-text p-button-danger" @click="deleteRate(data)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>
          <span>Tax Settings</span>
        </template>
        <template #content>
          <div class="grid p-fluid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Default Tax Calculation Method</label>
                <Dropdown v-model="taxSettings.calculationMethod" :options="calculationMethods" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Tax Rounding</label>
                <Dropdown v-model="taxSettings.rounding" :options="roundingOptions" />
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="taxSettings.compoundTax" binary />
                  <span class="ml-2">Enable compound tax calculation</span>
                </label>
              </div>
            </div>
          </div>
        </template>
        <template #footer>
          <Button label="Save Settings" icon="pi pi-check" @click="saveSettings" />
        </template>
      </Card>
    </div>

    <Dialog v-model:visible="showAddRate" modal header="Add Tax Rate" :style="{ width: '500px' }">
      <div class="grid p-fluid">
        <div class="col-12">
          <div class="field">
            <label>Tax Name</label>
            <InputText v-model="newRate.name" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Jurisdiction</label>
            <Dropdown v-model="newRate.jurisdiction" :options="jurisdictions" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Rate (%)</label>
            <InputNumber v-model="newRate.rate" :min="0" :max="100" :maxFractionDigits="4" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Type</label>
            <Dropdown v-model="newRate.type" :options="taxTypes" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Effective Date</label>
            <Calendar v-model="newRate.effectiveDate" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showAddRate = false" />
        <Button label="Add" @click="addRate" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showAddRate = ref(false)

const taxRates = ref([
  { id: 1, name: 'Sales Tax', jurisdiction: 'State', rate: 8.25, type: 'Sales', effectiveDate: '2023-01-01', status: 'Active' },
  { id: 2, name: 'Federal Income Tax', jurisdiction: 'Federal', rate: 21.0, type: 'Income', effectiveDate: '2023-01-01', status: 'Active' },
  { id: 3, name: 'Local Tax', jurisdiction: 'City', rate: 2.5, type: 'Sales', effectiveDate: '2023-01-01', status: 'Active' }
])

const taxSettings = ref({
  calculationMethod: 'Inclusive',
  rounding: 'Round to nearest cent',
  compoundTax: false
})

const newRate = ref({
  name: '',
  jurisdiction: '',
  rate: 0,
  type: '',
  effectiveDate: new Date()
})

const jurisdictions = ref(['Federal', 'State', 'County', 'City', 'Local'])
const taxTypes = ref(['Sales', 'Income', 'Property', 'Payroll', 'VAT', 'GST'])
const calculationMethods = ref(['Inclusive', 'Exclusive'])
const roundingOptions = ref(['Round to nearest cent', 'Round up', 'Round down', 'No rounding'])

const formatDate = (dateString: string) => new Date(dateString).toLocaleDateString()

const getStatusSeverity = (status: string) => {
  return status === 'Active' ? 'success' : 'secondary'
}

const addRate = () => {
  taxRates.value.push({
    id: Date.now(),
    ...newRate.value,
    effectiveDate: newRate.value.effectiveDate.toISOString().split('T')[0],
    status: 'Active'
  })
  newRate.value = { name: '', jurisdiction: '', rate: 0, type: '', effectiveDate: new Date() }
  showAddRate.value = false
}

const editRate = (rate: any) => {
  console.log('Editing rate:', rate)
}

const deleteRate = (rate: any) => {
  console.log('Deleting rate:', rate)
}

const saveSettings = () => {
  console.log('Saving tax settings:', taxSettings.value)
}
</script>

<style scoped>
.tax-rate-management {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.dashboard-header p {
  color: #6b7280;
  margin: 0;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

.content-card {
  height: fit-content;
}

.card-title-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}

@media (max-width: 768px) {
  .tax-rate-management {
    padding: 1rem;
  }
}
</style>