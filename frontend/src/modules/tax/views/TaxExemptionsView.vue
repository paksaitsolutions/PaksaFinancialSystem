<template>
  <div class="grid">
    <div class="col-12">
      <div class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center mb-4 gap-3">
        <div>
          <h1>Tax Exemptions</h1>
          <p class="text-color-secondary">Manage tax exemptions and certificates for customers and vendors.</p>
        </div>
        <div>
          <Button label="New Exemption" icon="pi pi-plus" class="p-button-success" @click="showNewExemptionDialog" />
        </div>
      </div>
    </div>

    <div class="col-12">
      <Card>
        <template #title>
          <span>Tax Exemptions</span>
        </template>
        <template #content>
          <div class="grid mb-4">
            <div class="col-12 md:col-4">
              <div class="field">
                <label for="search">Search</label>
                <InputText id="search" v-model="searchTerm" placeholder="Search exemptions..." />
              </div>
            </div>
            <div class="col-12 md:col-4">
              <div class="field">
                <label for="type">Exemption Type</label>
                <Dropdown id="type" v-model="selectedType" :options="exemptionTypes" optionLabel="label" optionValue="value" placeholder="All Types" />
              </div>
            </div>
            <div class="col-12 md:col-4">
              <div class="field">
                <label for="status">Status</label>
                <Dropdown id="status" v-model="selectedStatus" :options="statusOptions" optionLabel="label" optionValue="value" placeholder="All Status" />
              </div>
            </div>
          </div>

          <DataTable :value="exemptions" :loading="loading" responsiveLayout="scroll" :paginator="true" :rows="10">
            <Column field="code" header="Exemption Code" :sortable="true" />
            <Column field="name" header="Name" :sortable="true" />
            <Column field="type" header="Type" :sortable="true">
              <template #body="{ data }">
                <Tag :value="data.type" :severity="getTypeSeverity(data.type)" />
              </template>
            </Column>
            <Column field="entity" header="Entity" :sortable="true" />
            <Column field="validFrom" header="Valid From" :sortable="true">
              <template #body="{ data }">
                {{ formatDate(data.validFrom) }}
              </template>
            </Column>
            <Column field="validTo" header="Valid To" :sortable="true">
              <template #body="{ data }">
                {{ data.validTo ? formatDate(data.validTo) : 'No expiration' }}
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
                  <Button icon="pi pi-pencil" class="p-button-text p-button-sm" @click="editExemption(data)" v-tooltip="'Edit'" />
                  <Button icon="pi pi-trash" class="p-button-text p-button-sm p-button-danger" @click="deleteExemption(data)" v-tooltip="'Delete'" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>
  </div>

  <Dialog v-model:visible="showExemptionDialog" header="Tax Exemption" :style="{ width: '600px' }" :modal="true">
    <div class="field">
      <label for="code">Exemption Code</label>
      <InputText id="code" v-model="exemption.code" placeholder="Enter exemption code" />
    </div>
    <div class="field">
      <label for="name">Name</label>
      <InputText id="name" v-model="exemption.name" placeholder="Enter exemption name" />
    </div>
    <div class="field">
      <label for="type">Type</label>
      <Dropdown id="type" v-model="exemption.type" :options="exemptionTypes" optionLabel="label" optionValue="value" />
    </div>
    <div class="field">
      <label for="entity">Entity</label>
      <InputText id="entity" v-model="exemption.entity" placeholder="Enter entity name" />
    </div>
    <div class="field">
      <label for="validFrom">Valid From</label>
      <Calendar id="validFrom" v-model="exemption.validFrom" />
    </div>
    <div class="field">
      <label for="validTo">Valid To</label>
      <Calendar id="validTo" v-model="exemption.validTo" />
    </div>
    <template #footer>
      <Button label="Cancel" icon="pi pi-times" outlined @click="showExemptionDialog = false" />
      <Button label="Save" icon="pi pi-check" @click="saveExemption" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const loading = ref(false)
const showExemptionDialog = ref(false)
const searchTerm = ref('')
const selectedType = ref(null)
const selectedStatus = ref(null)

const exemption = ref({
  code: '',
  name: '',
  type: 'SALES_TAX',
  entity: '',
  validFrom: null,
  validTo: null,
  status: 'ACTIVE'
})

const exemptionTypes = [
  { label: 'Sales Tax Exemption', value: 'SALES_TAX' },
  { label: 'VAT Exemption', value: 'VAT' },
  { label: 'GST Exemption', value: 'GST' },
  { label: 'Withholding Tax Exemption', value: 'WITHHOLDING' },
  { label: 'Custom Exemption', value: 'CUSTOM' }
]

const statusOptions = [
  { label: 'Active', value: 'ACTIVE' },
  { label: 'Inactive', value: 'INACTIVE' },
  { label: 'Expired', value: 'EXPIRED' }
]

const exemptions = ref([
  { id: 1, code: 'EX001', name: 'Non-Profit Organization', type: 'SALES_TAX', entity: 'ABC Charity', validFrom: '2024-01-01', validTo: '2024-12-31', status: 'ACTIVE' },
  { id: 2, code: 'EX002', name: 'Government Entity', type: 'VAT', entity: 'City Council', validFrom: '2024-01-01', validTo: null, status: 'ACTIVE' },
  { id: 3, code: 'EX003', name: 'Educational Institution', type: 'GST', entity: 'University XYZ', validFrom: '2024-01-01', validTo: '2025-12-31', status: 'ACTIVE' },
  { id: 4, code: 'EX004', name: 'Medical Exemption', type: 'SALES_TAX', entity: 'Hospital ABC', validFrom: '2023-01-01', validTo: '2023-12-31', status: 'EXPIRED' }
])

const getTypeSeverity = (type: string) => {
  switch (type) {
    case 'SALES_TAX': return 'info'
    case 'VAT': return 'success'
    case 'GST': return 'warning'
    case 'WITHHOLDING': return 'danger'
    case 'CUSTOM': return 'secondary'
    default: return 'info'
  }
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'ACTIVE': return 'success'
    case 'INACTIVE': return 'warning'
    case 'EXPIRED': return 'danger'
    default: return 'info'
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const showNewExemptionDialog = () => {
  exemption.value = { code: '', name: '', type: 'SALES_TAX', entity: '', validFrom: null, validTo: null, status: 'ACTIVE' }
  showExemptionDialog.value = true
}

const editExemption = (exemptionData: any) => {
  exemption.value = { ...exemptionData }
  showExemptionDialog.value = true
}

const saveExemption = () => {
  showExemptionDialog.value = false
  toast.add({ severity: 'success', summary: 'Tax Exemption Saved', detail: `${exemption.value.name} has been saved` })
}

const deleteExemption = (exemptionData: any) => {
  toast.add({ severity: 'success', summary: 'Tax Exemption Deleted', detail: `${exemptionData.name} has been deleted` })
}

onMounted(() => {
  // Load exemptions from API
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