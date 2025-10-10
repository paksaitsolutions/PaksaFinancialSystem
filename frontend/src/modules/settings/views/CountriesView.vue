<template>
  <div class="countries-view">
    <div class="page-header">
      <h1>Country Management</h1>
      <Button label="Add Country" icon="pi pi-plus" @click="showAddDialog = true" />
    </div>

    <Card>
      <template #title>Countries</template>
      <template #content>
        <DataTable :value="countries" :loading="loading" paginator :rows="10" dataKey="id">
          <Column field="code" header="Code" sortable />
          <Column field="name" header="Name" sortable />
          <Column field="region.name" header="Region" sortable />
          <Column field="phone_code" header="Phone Code" />
          <Column field="capital" header="Capital" />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status ? 'Active' : 'Inactive'" :severity="data.status ? 'success' : 'danger'" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button icon="pi pi-pencil" size="small" @click="editCountry(data)" />
                <Button icon="pi pi-trash" size="small" severity="danger" @click="deleteCountry(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="showAddDialog" modal header="Add Country" :style="{ width: '35rem' }">
      <div class="grid">
        <div class="col-12 md:col-6">
          <label>Country Code</label>
          <InputText v-model="newCountry.code" class="w-full" placeholder="US" maxlength="2" />
        </div>
        <div class="col-12 md:col-6">
          <label>Alpha-3 Code</label>
          <InputText v-model="newCountry.code_alpha3" class="w-full" placeholder="USA" maxlength="3" />
        </div>
        <div class="col-12">
          <label>Country Name</label>
          <InputText v-model="newCountry.name" class="w-full" placeholder="United States" />
        </div>
        <div class="col-12">
          <label>Official Name</label>
          <InputText v-model="newCountry.official_name" class="w-full" placeholder="United States of America" />
        </div>
        <div class="col-12 md:col-6">
          <label>Region</label>
          <Dropdown
            v-model="newCountry.region_id"
            :options="activeRegions"
            optionLabel="name"
            optionValue="id"
            placeholder="Select Region"
            class="w-full"
          />
        </div>
        <div class="col-12 md:col-6">
          <label>Phone Code</label>
          <InputText v-model="newCountry.phone_code" class="w-full" placeholder="+1" />
        </div>
        <div class="col-12 md:col-6">
          <label>Capital</label>
          <InputText v-model="newCountry.capital" class="w-full" placeholder="Washington, D.C." />
        </div>
        <div class="col-12 md:col-6">
          <label>Timezone</label>
          <InputText v-model="newCountry.timezone" class="w-full" placeholder="UTC-5" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showAddDialog = false" />
        <Button label="Add Country" @click="addCountry" :loading="saving" />
      </template>
    </Dialog>

    <Dialog v-model:visible="showEditDialog" modal header="Edit Country" :style="{ width: '35rem' }">
      <div class="grid">
        <div class="col-12 md:col-6">
          <label>Country Code</label>
          <InputText v-model="editedCountry.code" class="w-full" disabled />
        </div>
        <div class="col-12 md:col-6">
          <label>Alpha-3 Code</label>
          <InputText v-model="editedCountry.code_alpha3" class="w-full" />
        </div>
        <div class="col-12">
          <label>Country Name</label>
          <InputText v-model="editedCountry.name" class="w-full" />
        </div>
        <div class="col-12">
          <label>Official Name</label>
          <InputText v-model="editedCountry.official_name" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Region</label>
          <Dropdown
            v-model="editedCountry.region_id"
            :options="activeRegions"
            optionLabel="name"
            optionValue="id"
            placeholder="Select Region"
            class="w-full"
          />
        </div>
        <div class="col-12 md:col-6">
          <label>Phone Code</label>
          <InputText v-model="editedCountry.phone_code" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Capital</label>
          <InputText v-model="editedCountry.capital" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Timezone</label>
          <InputText v-model="editedCountry.timezone" class="w-full" />
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox id="countryActive" v-model="editedCountry.status" :binary="true" />
            <label for="countryActive">Active</label>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showEditDialog = false" />
        <Button label="Update Country" @click="updateCountry" :loading="saving" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { regionService, type Region, type Country } from '@/api/regionService'

const toast = useToast()
const confirm = useConfirm()

const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)

const countries = ref<Country[]>([])
const regions = ref<Region[]>([])

const newCountry = ref({
  code: '',
  code_alpha3: '',
  name: '',
  official_name: '',
  region_id: '',
  phone_code: '',
  capital: '',
  timezone: ''
})

const editedCountry = ref({
  id: '',
  code: '',
  code_alpha3: '',
  name: '',
  official_name: '',
  region_id: '',
  phone_code: '',
  capital: '',
  timezone: '',
  status: true
})

const activeRegions = computed(() => regions.value.filter(r => r.status))

const loadCountries = async () => {
  loading.value = true
  try {
    countries.value = await regionService.getCountries(true)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load countries' })
  } finally {
    loading.value = false
  }
}

const loadRegions = async () => {
  try {
    regions.value = await regionService.getRegions(true)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load regions' })
  }
}

const editCountry = (country: Country) => {
  editedCountry.value = { ...country }
  showEditDialog.value = true
}

const addCountry = async () => {
  saving.value = true
  try {
    await regionService.createCountry({ ...newCountry.value, status: true })
    toast.add({ severity: 'success', summary: 'Success', detail: 'Country added successfully' })
    showAddDialog.value = false
    newCountry.value = {
      code: '',
      code_alpha3: '',
      name: '',
      official_name: '',
      region_id: '',
      phone_code: '',
      capital: '',
      timezone: ''
    }
    await loadCountries()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to add country' })
  } finally {
    saving.value = false
  }
}

const updateCountry = async () => {
  saving.value = true
  try {
    await regionService.updateCountry(editedCountry.value.id, editedCountry.value)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Country updated successfully' })
    showEditDialog.value = false
    await loadCountries()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to update country' })
  } finally {
    saving.value = false
  }
}

const deleteCountry = (country: Country) => {
  confirm.require({
    message: `Are you sure you want to delete country "${country.name}"?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try {
        await regionService.deleteCountry(country.id)
        toast.add({ severity: 'success', summary: 'Success', detail: 'Country deleted successfully' })
        await loadCountries()
      } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete country' })
      }
    }
  })
}

onMounted(async () => {
  await Promise.all([loadRegions(), loadCountries()])
})
</script>

<style scoped>
.countries-view {
  padding: 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
</style>