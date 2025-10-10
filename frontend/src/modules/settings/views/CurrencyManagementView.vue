<template>
  <div class="currency-management">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2 class="text-2xl font-semibold text-900 m-0">Currency Management</h2>
      <Button 
        label="Add Currency" 
        icon="pi pi-plus" 
        @click="openCurrencyDialog"
      />
    </div>

    <TabView v-model:activeIndex="activeTabIndex">
      <!-- Currencies Tab -->
      <TabPanel header="Currencies">
        <Card>
          <template #content>
            <DataTable
              :value="currencies"
              :loading="loading"
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
              <Column field="is_base" header="Type">
                <template #body="{ data }">
                  <Tag :value="data.is_base ? 'Base' : 'Foreign'" :severity="data.is_base ? 'success' : 'secondary'" />
                </template>
              </Column>
              <Column field="is_active" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.is_active ? 'Active' : 'Inactive'" :severity="data.is_active ? 'success' : 'danger'" />
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
                      :icon="data.is_active ? 'pi pi-pause' : 'pi pi-play'" 
                      class="p-button-text p-button-sm" 
                      @click="toggleCurrencyStatus(data)"
                      :disabled="data.is_base"
                      v-tooltip.top="data.is_active ? 'Deactivate' : 'Activate'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>

      <!-- Exchange Rates Tab -->
      <TabPanel header="Exchange Rates">
        <Card>
          <template #content>
            <div class="grid mb-4">
              <div class="col-12 md:col-4">
                <div class="field">
                  <label class="font-semibold">Select Currency</label>
                  <Dropdown
                    v-model="selectedCurrency"
                    :options="activeCurrencies"
                    optionLabel="name"
                    optionValue="code"
                    placeholder="Select Currency"
                    @change="loadExchangeRates"
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-4">
                <div class="field">
                  <label class="font-semibold">&nbsp;</label>
                  <Button 
                    label="Add Rate" 
                    icon="pi pi-plus" 
                    @click="openRateDialog" 
                    :disabled="!selectedCurrency"
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-4">
                <div class="field">
                  <label class="font-semibold">&nbsp;</label>
                  <Button 
                    label="Update from API" 
                    icon="pi pi-refresh" 
                    @click="updateRatesFromAPI" 
                    :loading="updatingRates"
                    severity="info"
                    class="w-full"
                  />
                </div>
              </div>
            </div>

            <DataTable
              :value="exchangeRates"
              :loading="ratesLoading"
              :paginator="true"
              :rows="10"
              responsiveLayout="scroll"
              class="p-datatable-sm"
            >
              <template #empty>No exchange rates found.</template>
              <Column field="effective_date" header="Effective Date" sortable>
                <template #body="{ data }">
                  {{ formatDate(data.effective_date) }}
                </template>
              </Column>
              <Column field="rate" header="Rate" sortable>
                <template #body="{ data }">
                  {{ formatRate(data.rate) }}
                </template>
              </Column>
              <Column field="is_current" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.is_current ? 'Current' : 'Historical'" :severity="data.is_current ? 'success' : 'secondary'" />
                </template>
              </Column>
              <Column field="notes" header="Notes" />
              <Column header="Actions" style="width: 120px">
                <template #body="{ data }">
                  <div class="flex gap-1">
                    <Button 
                      icon="pi pi-pencil" 
                      class="p-button-text p-button-sm" 
                      @click="editRate(data)"
                      v-tooltip.top="'Edit Rate'"
                    />
                    <Button 
                      icon="pi pi-check" 
                      class="p-button-text p-button-sm p-button-success" 
                      @click="setCurrentRate(data)"
                      :disabled="data.is_current"
                      v-tooltip.top="'Set as Current'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>
    </TabView>
    <!-- Currency Dialog -->
    <Dialog v-model:visible="currencyDialog" :header="editingCurrency ? 'Edit Currency' : 'Add Currency'" :style="{ width: '500px' }" :modal="true">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label for="currencyCode">Currency Code</label>
            <InputText 
              id="currencyCode"
              v-model="editedCurrency.code"
              :class="{ 'p-invalid': errors.code }"
              :disabled="editingCurrency"
              maxlength="3"
              class="w-full"
            />
            <small v-if="errors.code" class="p-error">{{ errors.code }}</small>
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="currencyName">Currency Name</label>
            <InputText 
              id="currencyName"
              v-model="editedCurrency.name"
              :class="{ 'p-invalid': errors.name }"
              class="w-full"
            />
            <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="currencySymbol">Symbol</label>
            <InputText 
              id="currencySymbol"
              v-model="editedCurrency.symbol"
              :class="{ 'p-invalid': errors.symbol }"
              class="w-full"
            />
            <small v-if="errors.symbol" class="p-error">{{ errors.symbol }}</small>
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
            <Checkbox id="isActive" v-model="editedCurrency.is_active" :binary="true" />
            <label for="isActive">Active</label>
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

    <!-- Exchange Rate Dialog -->
    <Dialog v-model:visible="rateDialog" :header="editingRate ? 'Edit Exchange Rate' : 'Add Exchange Rate'" :style="{ width: '500px' }" :modal="true">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label for="exchangeRate">Exchange Rate</label>
            <InputNumber 
              id="exchangeRate"
              v-model="editedRate.rate"
              :minFractionDigits="6"
              :maxFractionDigits="6"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="effectiveDate">Effective Date</label>
            <Calendar 
              id="effectiveDate"
              v-model="editedRate.effective_date"
              dateFormat="yy-mm-dd"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="rateNotes">Notes</label>
            <Textarea 
              id="rateNotes"
              v-model="editedRate.notes"
              rows="2"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox id="isCurrent" v-model="editedRate.is_current" :binary="true" />
            <label for="isCurrent">Set as current rate</label>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" @click="rateDialog = false" class="p-button-text" />
        <Button 
          label="Save" 
          @click="saveRate" 
          :loading="saving"
        />
      </template>
    </Dialog>
  </div>
</template>

<script>
import AppLayout from '@/layouts/AppLayout.vue'

export default {
  components: {
    AppLayout
  },
  name: 'CurrencyManagementView',
  data: () => ({
    activeTabIndex: 0,
    errors: {},
    loading: false,
    ratesLoading: false,
    saving: false,
    updatingRates: false,
    currencyDialog: false,
    rateDialog: false,
    currencyFormValid: false,
    rateFormValid: false,
    editingCurrency: false,
    editingRate: false,
    selectedCurrency: null,
    currencies: [
      {
        id: 1,
        code: 'USD',
        name: 'US Dollar',
        symbol: '$',
        decimal_places: 2,
        is_base: true,
        is_active: true
      },
      {
        id: 2,
        code: 'EUR',
        name: 'Euro',
        symbol: '€',
        decimal_places: 2,
        is_base: false,
        is_active: true
      },
      {
        id: 3,
        code: 'GBP',
        name: 'British Pound',
        symbol: '£',
        decimal_places: 2,
        is_base: false,
        is_active: true
      },
      {
        id: 4,
        code: 'JPY',
        name: 'Japanese Yen',
        symbol: '¥',
        decimal_places: 0,
        is_base: false,
        is_active: false
      }
    ],
    exchangeRates: [],
    editedCurrency: {
      code: '',
      name: '',
      symbol: '',
      decimal_places: 2,
      is_active: true
    },
    editedRate: {
      currency_code: '',
      rate: 0,
      effective_date: new Date().toISOString().substr(0, 10),
      notes: '',
      is_current: true
    },
    currencyHeaders: [
      { title: 'Code', key: 'code' },
      { title: 'Name', key: 'name' },
      { title: 'Symbol', key: 'symbol' },
      { title: 'Decimal Places', key: 'decimal_places' },
      { title: 'Type', key: 'is_base' },
      { title: 'Status', key: 'is_active' },
      { title: 'Actions', key: 'actions', sortable: false }
    ],
    rateHeaders: [
      { title: 'Effective Date', key: 'effective_date' },
      { title: 'Rate', key: 'rate' },
      { title: 'Status', key: 'is_current' },
      { title: 'Notes', key: 'notes' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
  }),

  computed: {
    activeCurrencies() {
      return this.currencies.filter(c => c.is_active && !c.is_base)
    }
  },

  methods: {
    openCurrencyDialog() {
      this.editingCurrency = false
      this.editedCurrency = {
        code: '',
        name: '',
        symbol: '',
        decimal_places: 2,
        is_active: true
      }
      this.currencyDialog = true
    },

    editCurrency(currency) {
      this.editingCurrency = true
      this.editedCurrency = { ...currency }
      this.currencyDialog = true
    },

    validateCurrency() {
      this.errors = {}
      
      if (!this.editedCurrency.code) {
        this.errors.code = 'Code is required'
      } else if (this.editedCurrency.code.length !== 3) {
        this.errors.code = 'Code must be 3 characters'
      }
      
      if (!this.editedCurrency.name) {
        this.errors.name = 'Name is required'
      }
      
      if (!this.editedCurrency.symbol) {
        this.errors.symbol = 'Symbol is required'
      }
      
      return Object.keys(this.errors).length === 0
    },

    async saveCurrency() {
      if (!this.validateCurrency()) return

      this.saving = true
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        if (this.editingCurrency) {
          const index = this.currencies.findIndex(c => c.id === this.editedCurrency.id)
          this.currencies[index] = { ...this.editedCurrency }
        } else {
          this.currencies.push({
            ...this.editedCurrency,
            id: Date.now(),
            is_base: false
          })
        }
        
        this.currencyDialog = false
      } catch (error) {
        console.error('Error saving currency:', error)
      } finally {
        this.saving = false
      }
    },

    async toggleCurrencyStatus(currency) {
      try {
        currency.is_active = !currency.is_active
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500))
      } catch (error) {
        console.error('Error toggling currency status:', error)
        currency.is_active = !currency.is_active
      }
    },

    loadExchangeRates() {
      if (!this.selectedCurrency) return

      this.ratesLoading = true
      // Simulate loading exchange rates
      setTimeout(() => {
        this.exchangeRates = [
          {
            id: 1,
            currency_code: this.selectedCurrency,
            rate: 1.0850,
            effective_date: '2024-01-15',
            is_current: true,
            notes: 'Current market rate'
          },
          {
            id: 2,
            currency_code: this.selectedCurrency,
            rate: 1.0823,
            effective_date: '2024-01-14',
            is_current: false,
            notes: 'Previous day rate'
          }
        ]
        this.ratesLoading = false
      }, 1000)
    },

    openRateDialog() {
      this.editingRate = false
      this.editedRate = {
        currency_code: this.selectedCurrency,
        rate: 0,
        effective_date: new Date().toISOString().substr(0, 10),
        notes: '',
        is_current: true
      }
      this.rateDialog = true
    },

    editRate(rate) {
      this.editingRate = true
      this.editedRate = { ...rate }
      this.rateDialog = true
    },

    async saveRate() {
      this.saving = true
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        if (this.editingRate) {
          const index = this.exchangeRates.findIndex(r => r.id === this.editedRate.id)
          this.exchangeRates[index] = { ...this.editedRate }
        } else {
          this.exchangeRates.unshift({
            ...this.editedRate,
            id: Date.now()
          })
        }
        
        this.rateDialog = false
      } catch (error) {
        console.error('Error saving rate:', error)
      } finally {
        this.saving = false
      }
    },

    async setCurrentRate(rate) {
      try {
        // Set all rates to not current
        this.exchangeRates.forEach(r => r.is_current = false)
        // Set selected rate as current
        rate.is_current = true
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500))
      } catch (error) {
        console.error('Error setting current rate:', error)
      }
    },

    async updateRatesFromAPI() {
      this.updatingRates = true
      try {
        // Simulate API call to external service
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Update rates with mock data
        this.loadExchangeRates()
      } catch (error) {
        console.error('Error updating rates from API:', error)
      } finally {
        this.updatingRates = false
      }
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    },

    formatRate(rate) {
      return parseFloat(rate).toFixed(6)
    }
  }
}
</script>

<style scoped>
.currency-management {
  padding: 16px;
}
</style>