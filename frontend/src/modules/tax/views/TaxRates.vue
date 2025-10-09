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
            <Column field="tax_type" header="Type" :sortable="true">
              <template #body="{ data }">
                <Tag :value="taxService.getTaxTypeLabel(data.tax_type)" :severity="getTypeSeverity(data.tax_type)" />
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

  <Dialog v-model:visible="showRateDialog" :header="editing ? 'Edit Tax Rate' : 'New Tax Rate'" :style="{ width: '600px' }" :modal="true">
    <div class="grid">
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="name">Tax Name *</label>
          <InputText id="name" v-model="rate.name" placeholder="Enter tax name" />
        </div>
      </div>
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="code">Tax Code *</label>
          <InputText id="code" v-model="rate.code" placeholder="Enter tax code" :disabled="editing" />
        </div>
      </div>
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="rate">Rate (%) *</label>
          <InputNumber id="rate" v-model="rate.rate" :min="0" :max="100" :maxFractionDigits="4" />
        </div>
      </div>
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="type">Tax Type *</label>
          <Dropdown id="type" v-model="rate.tax_type" :options="typeOptions" optionLabel="label" optionValue="value" />
        </div>
      </div>
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="jurisdiction">Jurisdiction *</label>
          <InputText id="jurisdiction" v-model="rate.jurisdiction" placeholder="Enter jurisdiction" />
        </div>
      </div>
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="country_code">Country Code *</label>
          <InputText id="country_code" v-model="rate.country_code" placeholder="US, CA, GB" maxlength="2" />
        </div>
      </div>
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="state_code">State/Province Code</label>
          <InputText id="state_code" v-model="rate.state_code" placeholder="CA, NY, ON" />
        </div>
      </div>
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="city">City</label>
          <InputText id="city" v-model="rate.city" placeholder="Enter city" />
        </div>
      </div>
      <div class="col-12">
        <div class="field">
          <label for="description">Description</label>
          <Textarea id="description" v-model="rate.description" rows="3" placeholder="Enter description" />
        </div>
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" icon="pi pi-times" outlined @click="showRateDialog = false" />
      <Button :label="editing ? 'Update' : 'Create'" icon="pi pi-check" @click="saveRate" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import taxService, { type TaxRate } from '@/services/taxService'

// Make taxService available in template
const { getTaxTypeLabel } = taxService

const toast = useToast()
const confirm = useConfirm()
const loading = ref(false)
const showRateDialog = ref(false)
const editing = ref(false)

const rate = ref({
  name: '',
  code: '',
  rate: 0,
  jurisdiction: '',
  tax_type: 'sales',
  country_code: 'US',
  state_code: '',
  city: '',
  description: ''
})

const typeOptions = [
  { label: 'Sales Tax', value: 'sales' },
  { label: 'VAT', value: 'vat' },
  { label: 'GST', value: 'gst' },
  { label: 'Income Tax', value: 'income' },
  { label: 'Property Tax', value: 'property' }
]

const taxRates = ref<TaxRate[]>([])

const loadTaxRates = async () => {
  loading.value = true
  try {
    taxRates.value = await taxService.getTaxRates()
  } catch (error) {
    console.error('Error loading tax rates:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load tax rates' })
  } finally {
    loading.value = false
  }
}

const getTypeSeverity = (type: string) => {
  switch (type) {
    case 'sales': return 'info'
    case 'vat': return 'success'
    case 'gst': return 'warning'
    case 'income': return 'danger'
    case 'property': return 'secondary'
    default: return 'info'
  }
}

const getStatusSeverity = (status: string) => {
  return status === 'active' ? 'success' : 'danger'
}

const showNewRateDialog = () => {
  rate.value = {
    name: '',
    code: '',
    rate: 0,
    jurisdiction: '',
    tax_type: 'sales',
    country_code: 'US',
    state_code: '',
    city: '',
    description: ''
  }
  editing.value = false
  showRateDialog.value = true
}

const editRate = (rateData: TaxRate) => {
  rate.value = {
    name: rateData.name,
    code: rateData.code,
    rate: rateData.rate,
    jurisdiction: rateData.jurisdiction,
    tax_type: rateData.tax_type,
    country_code: rateData.country_code,
    state_code: rateData.state_code || '',
    city: rateData.city || '',
    description: rateData.description || ''
  }
  editing.value = true
  showRateDialog.value = true
}

const saveRate = async () => {
  try {
    if (editing.value) {
      // Update existing rate
      const existingRate = taxRates.value.find(r => r.code === rate.value.code)
      if (existingRate) {
        await taxService.updateTaxRate(existingRate.id, rate.value)
        toast.add({ severity: 'success', summary: 'Updated', detail: 'Tax rate updated successfully' })
      }
    } else {
      // Create new rate
      await taxService.createTaxRate(rate.value)
      toast.add({ severity: 'success', summary: 'Created', detail: 'Tax rate created successfully' })
    }
    
    showRateDialog.value = false
    await loadTaxRates()
  } catch (error) {
    console.error('Error saving tax rate:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save tax rate' })
  }
}

const deleteRate = (rateData: TaxRate) => {
  confirm.require({
    message: `Are you sure you want to delete ${rateData.name}?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try {
        await taxService.deleteTaxRate(rateData.id)
        toast.add({ severity: 'success', summary: 'Deleted', detail: 'Tax rate deleted successfully' })
        await loadTaxRates()
      } catch (error) {
        console.error('Error deleting tax rate:', error)
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete tax rate' })
      }
    }
  })
}

onMounted(() => {
  loadTaxRates()
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
