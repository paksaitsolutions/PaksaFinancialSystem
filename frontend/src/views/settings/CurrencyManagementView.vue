<template>
  <div class="currency-management">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center">
              <h2>Currency Management</h2>
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="openCurrencyDialog">
                <v-icon left>mdi-plus</v-icon>
                Add Currency
              </v-btn>
            </v-card-title>

            <v-card-text>
              <v-tabs v-model="activeTab">
                <v-tab value="currencies">Currencies</v-tab>
                <v-tab value="rates">Exchange Rates</v-tab>
              </v-tabs>

              <v-window v-model="activeTab" class="mt-4">
                <!-- Currencies Tab -->
                <v-window-item value="currencies">
                  <v-data-table
                    :headers="currencyHeaders"
                    :items="currencies"
                    :loading="loading"
                    :items-per-page="10"
                  >
                    <template v-slot:item.is_base="{ item }">
                      <v-chip :color="item.is_base ? 'success' : 'grey'" small>
                        {{ item.is_base ? 'Base' : 'Foreign' }}
                      </v-chip>
                    </template>
                    
                    <template v-slot:item.is_active="{ item }">
                      <v-chip :color="item.is_active ? 'success' : 'error'" small>
                        {{ item.is_active ? 'Active' : 'Inactive' }}
                      </v-chip>
                    </template>
                    
                    <template v-slot:item.actions="{ item }">
                      <v-btn icon small @click="editCurrency(item)">
                        <v-icon small>mdi-pencil</v-icon>
                      </v-btn>
                      <v-btn
                        icon
                        small
                        @click="toggleCurrencyStatus(item)"
                        :disabled="item.is_base"
                      >
                        <v-icon small>
                          {{ item.is_active ? 'mdi-pause' : 'mdi-play' }}
                        </v-icon>
                      </v-btn>
                    </template>
                  </v-data-table>
                </v-window-item>

                <!-- Exchange Rates Tab -->
                <v-window-item value="rates">
                  <v-row class="mb-4">
                    <v-col cols="12" md="4">
                      <v-select
                        v-model="selectedCurrency"
                        :items="activeCurrencies"
                        item-title="name"
                        item-value="code"
                        label="Select Currency"
                        @update:modelValue="loadExchangeRates"
                      ></v-select>
                    </v-col>
                    <v-col cols="12" md="4">
                      <v-btn color="primary" @click="openRateDialog" :disabled="!selectedCurrency">
                        <v-icon left>mdi-plus</v-icon>
                        Add Rate
                      </v-btn>
                    </v-col>
                    <v-col cols="12" md="4">
                      <v-btn color="info" @click="updateRatesFromAPI" :loading="updatingRates">
                        <v-icon left>mdi-refresh</v-icon>
                        Update from API
                      </v-btn>
                    </v-col>
                  </v-row>

                  <v-data-table
                    :headers="rateHeaders"
                    :items="exchangeRates"
                    :loading="ratesLoading"
                    :items-per-page="10"
                  >
                    <template v-slot:item.effective_date="{ item }">
                      {{ formatDate(item.effective_date) }}
                    </template>
                    
                    <template v-slot:item.rate="{ item }">
                      {{ formatRate(item.rate) }}
                    </template>
                    
                    <template v-slot:item.is_current="{ item }">
                      <v-chip :color="item.is_current ? 'success' : 'grey'" small>
                        {{ item.is_current ? 'Current' : 'Historical' }}
                      </v-chip>
                    </template>
                    
                    <template v-slot:item.actions="{ item }">
                      <v-btn icon small @click="editRate(item)">
                        <v-icon small>mdi-pencil</v-icon>
                      </v-btn>
                      <v-btn
                        icon
                        small
                        @click="setCurrentRate(item)"
                        :disabled="item.is_current"
                      >
                        <v-icon small>mdi-check</v-icon>
                      </v-btn>
                    </template>
                  </v-data-table>
                </v-window-item>
              </v-window>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Currency Dialog -->
    <v-dialog v-model="currencyDialog" max-width="500px">
      <v-card>
        <v-card-title>{{ editingCurrency ? 'Edit Currency' : 'Add Currency' }}</v-card-title>
        <v-card-text>
          <v-form ref="currencyForm" v-model="currencyFormValid">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="editedCurrency.code"
                  label="Currency Code"
                  :rules="[v => !!v || 'Code is required', v => v.length === 3 || 'Code must be 3 characters']"
                  maxlength="3"
                  :disabled="editingCurrency"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="editedCurrency.name"
                  label="Currency Name"
                  :rules="[v => !!v || 'Name is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="editedCurrency.symbol"
                  label="Symbol"
                  :rules="[v => !!v || 'Symbol is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="editedCurrency.decimal_places"
                  label="Decimal Places"
                  type="number"
                  min="0"
                  max="4"
                  :rules="[v => v >= 0 && v <= 4 || 'Must be between 0 and 4']"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="editedCurrency.is_active"
                  label="Active"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="currencyDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            @click="saveCurrency"
            :disabled="!currencyFormValid"
            :loading="saving"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Exchange Rate Dialog -->
    <v-dialog v-model="rateDialog" max-width="500px">
      <v-card>
        <v-card-title>{{ editingRate ? 'Edit Exchange Rate' : 'Add Exchange Rate' }}</v-card-title>
        <v-card-text>
          <v-form ref="rateForm" v-model="rateFormValid">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="editedRate.rate"
                  label="Exchange Rate"
                  type="number"
                  step="0.000001"
                  :rules="[v => !!v || 'Rate is required', v => v > 0 || 'Rate must be positive']"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="editedRate.effective_date"
                  label="Effective Date"
                  type="date"
                  :rules="[v => !!v || 'Date is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="editedRate.notes"
                  label="Notes"
                  rows="2"
                ></v-textarea>
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="editedRate.is_current"
                  label="Set as current rate"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="rateDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            @click="saveRate"
            :disabled="!rateFormValid"
            :loading="saving"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: 'CurrencyManagementView',
  data: () => ({
    activeTab: 'currencies',
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

    async saveCurrency() {
      if (!this.$refs.currencyForm.validate()) return

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
      if (!this.$refs.rateForm.validate()) return

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