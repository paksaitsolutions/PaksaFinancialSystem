<template>
  <div class="region-currency-management">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2 class="text-2xl font-semibold text-900 m-0">Region & Currency Management</h2>
    </div>

    <TabView v-model:activeIndex="activeTabIndex">
      <!-- Regions Tab -->
      <TabPanel header="Regions">
        <Card>
          <template #content>
            <div class="flex justify-content-between align-items-center mb-3">
              <h3 class="text-lg font-semibold m-0">Regions</h3>
              <Button 
                label="Add Region" 
                icon="pi pi-plus" 
                @click="openRegionDialog"
                size="small"
              />
            </div>
            
            <DataTable
              :value="regions"
              :loading="regionsLoading"
              :paginator="true"
              :rows="10"
              responsiveLayout="scroll"
              class="p-datatable-sm"
            >
              <template #empty>No regions found.</template>
              <Column field="code" header="Code" sortable />
              <Column field="name" header="Name" sortable />
              <Column field="status" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.status ? 'Active' : 'Inactive'" :severity="data.status ? 'success' : 'danger'" />
                </template>
              </Column>
              <Column header="Actions" style="width: 120px">
                <template #body="{ data }">
                  <div class="flex gap-1">
                    <Button 
                      icon="pi pi-pencil" 
                      class="p-button-text p-button-sm" 
                      @click="editRegion(data)"
                      v-tooltip.top="'Edit Region'"
                    />
                    <Button 
                      icon="pi pi-trash" 
                      class="p-button-text p-button-sm p-button-danger" 
                      @click="deleteRegion(data)"
                      v-tooltip.top="'Delete Region'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>

      <!-- Countries Tab -->
      <TabPanel header="Countries">
        <Card>
          <template #content>
            <div class="flex justify-content-between align-items-center mb-3">
              <h3 class="text-lg font-semibold m-0">Countries</h3>
              <Button 
                label="Add Country" 
                icon="pi pi-plus" 
                @click="openCountryDialog"
                size="small"
              />
            </div>
            
            <DataTable
              :value="countries"
              :loading="countriesLoading"
              :paginator="true"
              :rows="10"
              responsiveLayout="scroll"
              class="p-datatable-sm"
            >
              <template #empty>No countries found.</template>
              <Column field="code" header="Code" sortable />
              <Column field="name" header="Name" sortable />
              <Column field="region.name" header="Region" sortable />
              <Column field="phone_code" header="Phone Code" />
              <Column field="capital" header="Capital" />
              <Column field="status" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.status ? 'Active' : 'Inactive'" :severity="data.status ? 'success' : 'danger'" />
                </template>
              </Column>
              <Column header="Actions" style="width: 120px">
                <template #body="{ data }">
                  <div class="flex gap-1">
                    <Button 
                      icon="pi pi-pencil" 
                      class="p-button-text p-button-sm" 
                      @click="editCountry(data)"
                      v-tooltip.top="'Edit Country'"
                    />
                    <Button 
                      icon="pi pi-trash" 
                      class="p-button-text p-button-sm p-button-danger" 
                      @click="deleteCountry(data)"
                      v-tooltip.top="'Delete Country'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>

      <!-- Currencies Tab -->
      <TabPanel header="Currencies">
        <Card>
          <template #content>
            <div class="flex justify-content-between align-items-center mb-3">
              <h3 class="text-lg font-semibold m-0">Currencies</h3>
              <Button 
                label="Add Currency" 
                icon="pi pi-plus" 
                @click="openCurrencyDialog"
                size="small"
              />
            </div>
            
            <DataTable
              :value="currencies"
              :loading="currenciesLoading"
              :paginator="true"
              :rows="10"
              responsiveLayout="scroll"
              class="p-datatable-sm"
            >
              <template #empty>No currencies found.</template>
              <Column field="code" header="Code" sortable />
              <Column field="name" header="Name" sortable />
              <Column field="symbol" header="Symbol" />
              <Column field="decimal_places" header="Decimal Places" />
              <Column field="is_base_currency" header="Type">
                <template #body="{ data }">
                  <Tag :value="data.is_base_currency ? 'Base' : 'Foreign'" :severity="data.is_base_currency ? 'success' : 'secondary'" />
                </template>
              </Column>
              <Column field="status" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.status === 'active' ? 'Active' : 'Inactive'" :severity="data.status === 'active' ? 'success' : 'danger'" />
                </template>
              </Column>
              <Column header="Actions" style="width: 120px">
                <template #body="{ data }">
                  <div class="flex gap-1">
                    <Button 
                      icon="pi pi-pencil" 
                      class="p-button-text p-button-sm" 
                      @click="editCurrency(data)"
                      v-tooltip.top="'Edit Currency'"
                    />
                    <Button 
                      icon="pi pi-trash" 
                      class="p-button-text p-button-sm p-button-danger" 
                      @click="deleteCurrency(data)"
                      :disabled="data.is_base_currency"
                      v-tooltip.top="'Delete Currency'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>
    </TabView>

    <!-- Region Dialog -->
    <Dialog v-model:visible="regionDialog" :header="editingRegion ? 'Edit Region' : 'Add Region'" :style="{ width: '400px' }" :modal="true">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label for="regionCode">Region Code</label>
            <InputText 
              id="regionCode"
              v-model="editedRegion.code"
              :disabled="editingRegion"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="regionName">Region Name</label>
            <InputText 
              id="regionName"
              v-model="editedRegion.name"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox id="regionActive" v-model="editedRegion.status" :binary="true" />
            <label for="regionActive">Active</label>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" @click="regionDialog = false" class="p-button-text" />
        <Button 
          label="Save" 
          @click="saveRegion" 
          :loading="saving"
        />
      </template>
    </Dialog>

    <!-- Country Dialog -->
    <Dialog v-model:visible="countryDialog" :header="editingCountry ? 'Edit Country' : 'Add Country'" :style="{ width: '600px' }" :modal="true">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="countryCode">Country Code</label>
            <InputText 
              id="countryCode"
              v-model="editedCountry.code"
              :disabled="editingCountry"
              maxlength="2"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="countryCodeAlpha3">Alpha-3 Code</label>
            <InputText 
              id="countryCodeAlpha3"
              v-model="editedCountry.code_alpha3"
              maxlength="3"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="countryName">Country Name</label>
            <InputText 
              id="countryName"
              v-model="editedCountry.name"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="officialName">Official Name</label>
            <InputText 
              id="officialName"
              v-model="editedCountry.official_name"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="countryRegion">Region</label>
            <Dropdown
              id="countryRegion"
              v-model="editedCountry.region_id"
              :options="activeRegions"
              optionLabel="name"
              optionValue="id"
              placeholder="Select Region"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="phoneCode">Phone Code</label>
            <InputText 
              id="phoneCode"
              v-model="editedCountry.phone_code"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="capital">Capital</label>
            <InputText 
              id="capital"
              v-model="editedCountry.capital"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="timezone">Timezone</label>
            <InputText 
              id="timezone"
              v-model="editedCountry.timezone"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox id="countryActive" v-model="editedCountry.status" :binary="true" />
            <label for="countryActive">Active</label>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" @click="countryDialog = false" class="p-button-text" />
        <Button 
          label="Save" 
          @click="saveCountry" 
          :loading="saving"
        />
      </template>
    </Dialog>

    <!-- Currency Dialog -->
    <Dialog v-model:visible="currencyDialog" :header="editingCurrency ? 'Edit Currency' : 'Add Currency'" :style="{ width: '500px' }" :modal="true">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label for="currencyCode">Currency Code</label>
            <InputText 
              id="currencyCode"
              v-model="editedCurrency.code"
              :disabled="editingCurrency"
              maxlength="3"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="currencyName">Currency Name</label>
            <InputText 
              id="currencyName"
              v-model="editedCurrency.name"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="currencySymbol">Symbol</label>
            <InputText 
              id="currencySymbol"
              v-model="editedCurrency.symbol"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="decimalPlaces">Decimal Places</label>
            <InputNumber 
              id="decimalPlaces"
              v-model="editedCurrency.decimal_places"
              :min="0"
              :max="4"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox id="currencyActive" v-model="editedCurrency.is_active" :binary="true" />
            <label for="currencyActive">Active</label>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" @click="currencyDialog = false" class="p-button-text" />
        <Button 
          label="Save" 
          @click="saveCurrency" 
          :loading="saving"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { regionService, type Region, type Country } from '@/api/regionService'
import currencyService, { type Currency } from '@/services/currencyService'

const toast = useToast()
const confirm = useConfirm()

// State
const activeTabIndex = ref(0)
const regionsLoading = ref(false)
const countriesLoading = ref(false)
const currenciesLoading = ref(false)
const saving = ref(false)

// Data
const regions = ref<Region[]>([])
const countries = ref<Country[]>([])
const currencies = ref<Currency[]>([])

// Dialogs
const regionDialog = ref(false)
const countryDialog = ref(false)
const currencyDialog = ref(false)

const editingRegion = ref(false)
const editingCountry = ref(false)
const editingCurrency = ref(false)

// Form data
const editedRegion = ref({
  code: '',
  name: '',
  status: true
})

const editedCountry = ref({
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

const editedCurrency = ref({
  code: '',
  name: '',
  symbol: '',
  decimal_places: 2,
  is_active: true
})

// Computed
const activeRegions = computed(() => regions.value.filter(r => r.status))

// Methods
const loadRegions = async () => {
  regionsLoading.value = true
  try {
    regions.value = await regionService.getRegions(true)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load regions' })
  } finally {
    regionsLoading.value = false
  }
}

const loadCountries = async () => {
  countriesLoading.value = true
  try {
    countries.value = await regionService.getCountries(true)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load countries' })
  } finally {
    countriesLoading.value = false
  }
}

const loadCurrencies = async () => {
  currenciesLoading.value = true
  try {
    const response = await currencyService.getAllCurrencies(true)
    currencies.value = response.data
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load currencies' })
  } finally {
    currenciesLoading.value = false
  }
}

// Region methods
const openRegionDialog = () => {
  editingRegion.value = false
  editedRegion.value = { code: '', name: '', status: true }
  regionDialog.value = true
}

const editRegion = (region: Region) => {
  editingRegion.value = true
  editedRegion.value = { ...region }
  regionDialog.value = true
}

const saveRegion = async () => {
  saving.value = true
  try {
    if (editingRegion.value) {
      await regionService.updateRegion(editedRegion.value.id, editedRegion.value)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Region updated successfully' })
    } else {
      await regionService.createRegion(editedRegion.value)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Region created successfully' })
    }
    regionDialog.value = false
    await loadRegions()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save region' })
  } finally {
    saving.value = false
  }
}

const deleteRegion = (region: Region) => {
  confirm.require({
    message: `Are you sure you want to delete region "${region.name}"?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try {
        await regionService.deleteRegion(region.id)
        toast.add({ severity: 'success', summary: 'Success', detail: 'Region deleted successfully' })
        await loadRegions()
      } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete region' })
      }
    }
  })
}

// Country methods
const openCountryDialog = () => {
  editingCountry.value = false
  editedCountry.value = {
    code: '',
    code_alpha3: '',
    name: '',
    official_name: '',
    region_id: '',
    phone_code: '',
    capital: '',
    timezone: '',
    status: true
  }
  countryDialog.value = true
}

const editCountry = (country: Country) => {
  editingCountry.value = true
  editedCountry.value = { ...country }
  countryDialog.value = true
}

const saveCountry = async () => {
  saving.value = true
  try {
    if (editingCountry.value) {
      await regionService.updateCountry(editedCountry.value.id, editedCountry.value)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Country updated successfully' })
    } else {
      await regionService.createCountry(editedCountry.value)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Country created successfully' })
    }
    countryDialog.value = false
    await loadCountries()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save country' })
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

// Currency methods
const openCurrencyDialog = () => {
  editingCurrency.value = false
  editedCurrency.value = {
    code: '',
    name: '',
    symbol: '',
    decimal_places: 2,
    is_active: true
  }
  currencyDialog.value = true
}

const editCurrency = (currency: Currency) => {
  editingCurrency.value = true
  editedCurrency.value = {
    ...currency,
    is_active: currency.status === 'active'
  }
  currencyDialog.value = true
}

const saveCurrency = async () => {
  saving.value = true
  try {
    const currencyData = {
      ...editedCurrency.value,
      status: editedCurrency.value.is_active ? 'active' : 'inactive'
    }
    delete currencyData.is_active

    if (editingCurrency.value) {
      await currencyService.updateCurrency(editedCurrency.value.id, currencyData)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Currency updated successfully' })
    } else {
      await currencyService.createCurrency(currencyData)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Currency created successfully' })
    }
    currencyDialog.value = false
    await loadCurrencies()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save currency' })
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

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadRegions(),
    loadCountries(),
    loadCurrencies()
  ])
})
</script>

<style scoped>
.region-currency-management {
  padding: 16px;
}
</style>