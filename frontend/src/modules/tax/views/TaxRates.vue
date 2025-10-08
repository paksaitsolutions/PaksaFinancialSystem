<template>
  <div class="grid">
    <div class="col-12">
      <div class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center mb-4 gap-3">
        <div>
          <h1>Tax Rates</h1>
          <p class="text-color-secondary">Manage tax rates and jurisdictions for accurate tax calculations.</p>
        </div>
        <div>
          <Button label="New Tax Rate" icon="pi pi-plus" class="p-button-success" @click="showNewRateDialog" />
        </div>
      </div>
    </div>

    <div class="col-12">
      <Card>
        <template #title>
          <span>Tax Rates</span>
        </template>
        <template #content>
          <DataTable :value="taxRates" :loading="loading" responsiveLayout="scroll" :paginator="true" :rows="10">
            <Column field="name" header="Tax Name" :sortable="true" />
            <Column field="code" header="Tax Code" :sortable="true" />
            <Column field="rate" header="Rate (%)" :sortable="true">
              <template #body="{ data }">
                {{ data.rate }}%
              </template>
            </Column>
            <Column field="jurisdiction" header="Jurisdiction" :sortable="true" />
            <Column field="type" header="Type" :sortable="true">
              <template #body="{ data }">
                <Tag :value="data.type" :severity="getTypeSeverity(data.type)" />
              </template>
            </Column>
            <Column field="status" header="Status" :sortable="true">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button icon="pi pi-pencil" class="p-button-text p-button-sm" @click="editRate(data)" v-tooltip="'Edit'" />
                  <Button icon="pi pi-trash" class="p-button-text p-button-sm p-button-danger" @click="deleteRate(data)" v-tooltip="'Delete'" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>
  </div>

  <Dialog v-model:visible="showRateDialog" header="Tax Rate" :style="{ width: '500px' }" :modal="true">
    <div class="field">
      <label for="name">Tax Name</label>
      <InputText id="name" v-model="rate.name" placeholder="Enter tax name" />
    </div>
    <div class="field">
      <label for="code">Tax Code</label>
      <InputText id="code" v-model="rate.code" placeholder="Enter tax code" />
    </div>
    <div class="field">
      <label for="rate">Rate (%)</label>
      <InputNumber id="rate" v-model="rate.rate" :min="0" :max="100" suffix="%" />
    </div>
    <div class="field">
      <label for="jurisdiction">Jurisdiction</label>
      <InputText id="jurisdiction" v-model="rate.jurisdiction" placeholder="Enter jurisdiction" />
    </div>
    <div class="field">
      <label for="type">Type</label>
      <Dropdown id="type" v-model="rate.type" :options="typeOptions" optionLabel="label" optionValue="value" />
    </div>
    <template #footer>
      <Button label="Cancel" icon="pi pi-times" outlined @click="showRateDialog = false" />
      <Button label="Save" icon="pi pi-check" @click="saveRate" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const loading = ref(false)
const showRateDialog = ref(false)

const rate = ref({
  name: '',
  code: '',
  rate: 0,
  jurisdiction: '',
  type: 'SALES',
  status: 'ACTIVE'
})

const typeOptions = [
  { label: 'Sales Tax', value: 'SALES' },
  { label: 'VAT', value: 'VAT' },
  { label: 'GST', value: 'GST' },
  { label: 'Income Tax', value: 'INCOME' },
  { label: 'Property Tax', value: 'PROPERTY' }
]

const taxRates = ref([
  { id: 1, name: 'California Sales Tax', code: 'CA-SALES', rate: 7.25, jurisdiction: 'California', type: 'SALES', status: 'ACTIVE' },
  { id: 2, name: 'New York Sales Tax', code: 'NY-SALES', rate: 8.0, jurisdiction: 'New York', type: 'SALES', status: 'ACTIVE' },
  { id: 3, name: 'UK VAT', code: 'UK-VAT', rate: 20.0, jurisdiction: 'United Kingdom', type: 'VAT', status: 'ACTIVE' },
  { id: 4, name: 'Canada GST', code: 'CA-GST', rate: 5.0, jurisdiction: 'Canada', type: 'GST', status: 'ACTIVE' }
])

const getTypeSeverity = (type: string) => {
  switch (type) {
    case 'SALES': return 'info'
    case 'VAT': return 'success'
    case 'GST': return 'warning'
    case 'INCOME': return 'danger'
    case 'PROPERTY': return 'secondary'
    default: return 'info'
  }
}

const getStatusSeverity = (status: string) => {
  return status === 'ACTIVE' ? 'success' : 'danger'
}

const showNewRateDialog = () => {
  rate.value = { name: '', code: '', rate: 0, jurisdiction: '', type: 'SALES', status: 'ACTIVE' }
  showRateDialog.value = true
}

const editRate = (rateData: any) => {
  rate.value = { ...rateData }
  showRateDialog.value = true
}

const saveRate = () => {
  showRateDialog.value = false
  toast.add({ severity: 'success', summary: 'Tax Rate Saved', detail: `${rate.value.name} has been saved` })
}

const deleteRate = (rateData: any) => {
  toast.add({ severity: 'success', summary: 'Tax Rate Deleted', detail: `${rateData.name} has been deleted` })
}

onMounted(() => {
  // Load tax rates from API
})
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}
</style>
