<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <h2>Currency Management</h2>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              @click="openCurrencyDialog()"
            >
              Add Currency
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="currencies"
              :loading="loading"
              class="elevation-1"
            >
              <template v-slot:item.symbol="{ item }">
                {{ item.symbol || '-' }}
              </template>
              
              <template v-slot:item.is_base_currency="{ item }">
                <v-chip
                  v-if="item.is_base_currency"
                  color="primary"
                  size="small"
                >
                  Base Currency
                </v-chip>
                <span v-else>-</span>
              </template>
              
              <template v-slot:item.status="{ item }">
                <v-chip
                  :color="item.status === 'active' ? 'success' : 'error'"
                  size="small"
                >
                  {{ item.status }}
                </v-chip>
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  variant="text"
                  @click="openCurrencyDialog(item)"
                >
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn
                  icon
                  variant="text"
                  @click="openExchangeRateDialog(item)"
                >
                  <v-icon>mdi-currency-usd-exchange</v-icon>
                </v-btn>
                <v-btn
                  icon
                  variant="text"
                  @click="confirmDeleteCurrency(item)"
                  :disabled="item.is_base_currency"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Exchange Rates Section -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <h2>Exchange Rates</h2>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              @click="openExchangeRateDialog()"
            >
              Add Exchange Rate
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-select
                  v-model="sourceCurrency"
                  :items="currencies"
                  item-title="code"
                  item-value="code"
                  label="From Currency"
                  @update:model-value="loadExchangeRates"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-select
                  v-model="targetCurrency"
                  :items="currencies"
                  item-title="code"
                  item-value="code"
                  label="To Currency"
                  @update:model-value="loadExchangeRates"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-menu
                  ref="dateMenu"
                  v-model="dateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="formattedDate"
                      label="As of Date"
                      prepend-icon="mdi-calendar"
                      readonly
                      v-bind="props"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="rateDate"
                    @update:model-value="dateMenu = false; loadExchangeRates()"
                  ></v-date-picker>
                </v-menu>
              </v-col>
            </v-row>
            
            <v-alert
              v-if="currentRate"
              color="info"
              icon="mdi-information"
              class="mt-4"
            >
              <strong>Current Rate:</strong> 1 {{ sourceCurrency }} = {{ currentRate }} {{ targetCurrency }}
              <div class="text-caption">
                Last updated: {{ formatDate(currentRateDate) }}
              </div>
            </v-alert>
            
            <v-alert
              v-else-if="exchangeRateLoaded"
              color="warning"
              icon="mdi-alert"
              class="mt-4"
            >
              No exchange rate found for {{ sourceCurrency }} to {{ targetCurrency }}
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Currency Conversion Section -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <h2>Currency Conversion</h2>
          </v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="conversionAmount"
                  label="Amount"
                  type="number"
                  min="0"
                  step="0.01"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="3">
                <v-select
                  v-model="conversionFromCurrency"
                  :items="currencies"
                  item-title="code"
                  item-value="code"
                  label="From Currency"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="3">
                <v-select
                  v-model="conversionToCurrency"
                  :items="currencies"
                  item-title="code"
                  item-value="code"
                  label="To Currency"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="2">
                <v-btn
                  color="primary"
                  block
                  class="mt-2"
                  @click="convertCurrency"
                  :loading="converting"
                >
                  Convert
                </v-btn>
              </v-col>
            </v-row>
            
            <v-alert
              v-if="conversionResult"
              color="success"
              icon="mdi-check-circle"
              class="mt-4"
            >
              <strong>{{ conversionResult.original_amount }} {{ conversionResult.original_currency }}</strong> = 
              <strong>{{ conversionResult.converted_amount }} {{ conversionResult.target_currency }}</strong>
              <div class="text-caption">
                Exchange Rate: {{ conversionResult.exchange_rate }} ({{ conversionResult.conversion_date }})
              </div>
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Currency Dialog -->
    <v-dialog v-model="currencyDialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ editMode ? 'Edit Currency' : 'Add Currency' }}</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="currencyForm">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedCurrency.code"
                  label="Currency Code"
                  :rules="[v => !!v || 'Code is required', v => v.length === 3 || 'Code must be 3 characters']"
                  :disabled="editMode"
                  maxlength="3"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedCurrency.symbol"
                  label="Symbol"
                  maxlength="10"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="editedCurrency.name"
                  label="Currency Name"
                  :rules="[v => !!v || 'Name is required']"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedCurrency.decimal_places"
                  label="Decimal Places"
                  type="number"
                  min="0"
                  max="10"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedCurrency.status"
                  :items="['active', 'inactive']"
                  label="Status"
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-checkbox
                  v-model="editedCurrency.is_base_currency"
                  label="Set as Base Currency"
                  hint="This will unset any existing base currency"
                  persistent-hint
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="blue-darken-1"
            variant="text"
            @click="closeCurrencyDialog"
          >
            Cancel
          </v-btn>
          <v-btn
            color="blue-darken-1"
            variant="text"
            @click="saveCurrency"
            :loading="saving"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Exchange Rate Dialog -->
    <v-dialog v-model="exchangeRateDialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="text-h5">Add Exchange Rate</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="exchangeRateForm">
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedExchangeRate.source_currency_code"
                  :items="currencies"
                  item-title="code"
                  item-value="code"
                  label="From Currency"
                  :rules="[v => !!v || 'From Currency is required']"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedExchangeRate.target_currency_code"
                  :items="currencies"
                  item-title="code"
                  item-value="code"
                  label="To Currency"
                  :rules="[v => !!v || 'To Currency is required', v => v !== editedExchangeRate.source_currency_code || 'Currencies must be different']"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedExchangeRate.rate"
                  label="Exchange Rate"
                  type="number"
                  min="0.0000001"
                  step="0.0000001"
                  :rules="[v => !!v || 'Rate is required', v => parseFloat(v) > 0 || 'Rate must be positive']"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-menu
                  ref="effectiveDateMenu"
                  v-model="effectiveDateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="formattedEffectiveDate"
                      label="Effective Date"
                      prepend-icon="mdi-calendar"
                      readonly
                      v-bind="props"
                      :rules="[v => !!v || 'Effective Date is required']"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="editedExchangeRate.effective_date"
                    @update:model-value="effectiveDateMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedExchangeRate.rate_type"
                  :items="['spot', 'forward', 'historical']"
                  label="Rate Type"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-checkbox
                  v-model="editedExchangeRate.is_official"
                  label="Official Rate"
                ></v-checkbox>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="editedExchangeRate.source"
                  label="Source"
                  hint="e.g., Manual, ECB, Central Bank"
                  persistent-hint
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="blue-darken-1"
            variant="text"
            @click="closeExchangeRateDialog"
          >
            Cancel
          </v-btn>
          <v-btn
            color="blue-darken-1"
            variant="text"
            @click="saveExchangeRate"
            :loading="saving"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Delete Currency</v-card-title>
        <v-card-text>
          Are you sure you want to delete the currency <strong>{{ currencyToDelete?.code }}</strong>?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="blue-darken-1"
            variant="text"
            @click="deleteDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="red-darken-1"
            variant="text"
            @click="deleteCurrency"
            :loading="deleting"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { format } from 'date-fns';
import currencyService from '@/services/currencyService';
import { useSnackbar } from '@/composables/useSnackbar';

export default {
  name: 'CurrencyManagementView',
  
  setup() {
    const { showSnackbar } = useSnackbar();
    
    // Data tables
    const headers = [
      { title: 'Code', key: 'code', sortable: true },
      { title: 'Name', key: 'name', sortable: true },
      { title: 'Symbol', key: 'symbol', sortable: false },
      { title: 'Decimal Places', key: 'decimal_places', sortable: true },
      { title: 'Base Currency', key: 'is_base_currency', sortable: true },
      { title: 'Status', key: 'status', sortable: true },
      { title: 'Actions', key: 'actions', sortable: false }
    ];
    
    // State
    const currencies = ref([]);
    const loading = ref(false);
    const saving = ref(false);
    const deleting = ref(false);
    const converting = ref(false);
    
    // Currency dialog
    const currencyDialog = ref(false);
    const editMode = ref(false);
    const editedCurrency = ref({
      code: '',
      name: '',
      symbol: '',
      decimal_places: 2,
      status: 'active',
      is_base_currency: false
    });
    const defaultCurrency = {
      code: '',
      name: '',
      symbol: '',
      decimal_places: 2,
      status: 'active',
      is_base_currency: false
    };
    const currencyForm = ref(null);
    
    // Exchange rate dialog
    const exchangeRateDialog = ref(false);
    const editedExchangeRate = ref({
      source_currency_code: '',
      target_currency_code: '',
      rate: 1,
      effective_date: new Date().toISOString().substr(0, 10),
      rate_type: 'spot',
      is_official: true,
      source: 'Manual'
    });
    const defaultExchangeRate = {
      source_currency_code: '',
      target_currency_code: '',
      rate: 1,
      effective_date: new Date().toISOString().substr(0, 10),
      rate_type: 'spot',
      is_official: true,
      source: 'Manual'
    };
    const exchangeRateForm = ref(null);
    const effectiveDateMenu = ref(false);
    
    // Delete dialog
    const deleteDialog = ref(false);
    const currencyToDelete = ref(null);
    
    // Exchange rate lookup
    const sourceCurrency = ref('USD');
    const targetCurrency = ref('EUR');
    const rateDate = ref(new Date().toISOString().substr(0, 10));
    const dateMenu = ref(false);
    const currentRate = ref(null);
    const currentRateDate = ref(null);
    const exchangeRateLoaded = ref(false);
    
    // Currency conversion
    const conversionAmount = ref(100);
    const conversionFromCurrency = ref('USD');
    const conversionToCurrency = ref('EUR');
    const conversionResult = ref(null);
    
    // Computed properties
    const formattedDate = computed(() => {
      return format(new Date(rateDate.value), 'MMM dd, yyyy');
    });
    
    const formattedEffectiveDate = computed(() => {
      if (!editedExchangeRate.value.effective_date) return '';
      return format(new Date(editedExchangeRate.value.effective_date), 'MMM dd, yyyy');
    });
    
    // Methods
    const loadCurrencies = async () => {
      loading.value = true;
      try {
        const response = await currencyService.getAllCurrencies(true);
        currencies.value = response.data;
        
        // Set default currencies for exchange rate lookup
        if (currencies.value.length > 0) {
          const baseCurrency = currencies.value.find(c => c.is_base_currency);
          if (baseCurrency) {
            sourceCurrency.value = baseCurrency.code;
          } else {
            sourceCurrency.value = currencies.value[0].code;
          }
          
          if (currencies.value.length > 1) {
            targetCurrency.value = currencies.value.find(c => c.code !== sourceCurrency.value)?.code || currencies.value[1].code;
          }
          
          // Set default currencies for conversion
          conversionFromCurrency.value = sourceCurrency.value;
          conversionToCurrency.value = targetCurrency.value;
        }
        
        // Load exchange rates
        loadExchangeRates();
      } catch (error) {
        console.error('Failed to load currencies:', error);
        showSnackbar('Failed to load currencies', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const loadExchangeRates = async () => {
      if (!sourceCurrency.value || !targetCurrency.value) return;
      
      exchangeRateLoaded.value = false;
      currentRate.value = null;
      currentRateDate.value = null;
      
      try {
        const response = await currencyService.getExchangeRate(
          sourceCurrency.value,
          targetCurrency.value,
          new Date(rateDate.value)
        );
        
        if (response.data && response.data.rate) {
          currentRate.value = response.data.rate;
          currentRateDate.value = response.data.date;
        }
      } catch (error) {
        console.error('Failed to load exchange rate:', error);
        // Don't show error notification as this is expected when no rate exists
      } finally {
        exchangeRateLoaded.value = true;
      }
    };
    
    const openCurrencyDialog = (currency = null) => {
      if (currency) {
        editMode.value = true;
        editedCurrency.value = { ...currency };
      } else {
        editMode.value = false;
        editedCurrency.value = { ...defaultCurrency };
      }
      currencyDialog.value = true;
    };
    
    const closeCurrencyDialog = () => {
      currencyDialog.value = false;
      editedCurrency.value = { ...defaultCurrency };
    };
    
    const saveCurrency = async () => {
      if (!currencyForm.value.validate()) return;
      
      saving.value = true;
      try {
        if (editMode.value) {
          await currencyService.updateCurrency(editedCurrency.value.id, editedCurrency.value);
          showSnackbar(`Currency ${editedCurrency.value.code} updated successfully`, 'success');
        } else {
          await currencyService.createCurrency(editedCurrency.value);
          showSnackbar(`Currency ${editedCurrency.value.code} created successfully`, 'success');
        }
        
        closeCurrencyDialog();
        loadCurrencies();
      } catch (error) {
        console.error('Failed to save currency:', error);
        showSnackbar(`Failed to save currency: ${error.response?.data?.detail || error.message}`, 'error');
      } finally {
        saving.value = false;
      }
    };
    
    const openExchangeRateDialog = (currency = null) => {
      editedExchangeRate.value = { ...defaultExchangeRate };
      
      if (currency) {
        editedExchangeRate.value.source_currency_code = currency.code;
        
        // Set target currency to base currency if available
        const baseCurrency = currencies.value.find(c => c.is_base_currency);
        if (baseCurrency && baseCurrency.code !== currency.code) {
          editedExchangeRate.value.target_currency_code = baseCurrency.code;
        } else {
          // Otherwise set to first currency that's not the source
          const otherCurrency = currencies.value.find(c => c.code !== currency.code);
          if (otherCurrency) {
            editedExchangeRate.value.target_currency_code = otherCurrency.code;
          }
        }
      } else {
        // Default to current source/target currencies
        editedExchangeRate.value.source_currency_code = sourceCurrency.value;
        editedExchangeRate.value.target_currency_code = targetCurrency.value;
      }
      
      exchangeRateDialog.value = true;
    };
    
    const closeExchangeRateDialog = () => {
      exchangeRateDialog.value = false;
      editedExchangeRate.value = { ...defaultExchangeRate };
    };
    
    const saveExchangeRate = async () => {
      if (!exchangeRateForm.value.validate()) return;
      
      saving.value = true;
      try {
        await currencyService.createExchangeRate({
          ...editedExchangeRate.value,
          effective_date: new Date(editedExchangeRate.value.effective_date)
        });
        
        showSnackbar('Exchange rate created successfully', 'success');
        closeExchangeRateDialog();
        loadExchangeRates();
      } catch (error) {
        console.error('Failed to save exchange rate:', error);
        showSnackbar(`Failed to save exchange rate: ${error.response?.data?.detail || error.message}`, 'error');
      } finally {
        saving.value = false;
      }
    };
    
    const confirmDeleteCurrency = (currency) => {
      currencyToDelete.value = currency;
      deleteDialog.value = true;
    };
    
    const deleteCurrency = async () => {
      if (!currencyToDelete.value) return;
      
      deleting.value = true;
      try {
        await currencyService.deleteCurrency(currencyToDelete.value.id);
        showSnackbar(`Currency ${currencyToDelete.value.code} deleted successfully`, 'success');
        deleteDialog.value = false;
        loadCurrencies();
      } catch (error) {
        console.error('Failed to delete currency:', error);
        showSnackbar(`Failed to delete currency: ${error.response?.data?.detail || error.message}`, 'error');
      } finally {
        deleting.value = false;
      }
    };
    
    const convertCurrency = async () => {
      if (!conversionAmount.value || !conversionFromCurrency.value || !conversionToCurrency.value) {
        showSnackbar('Please fill in all conversion fields', 'warning');
        return;
      }
      
      converting.value = true;
      try {
        const response = await currencyService.convertCurrency({
          amount: parseFloat(conversionAmount.value),
          from_currency: conversionFromCurrency.value,
          to_currency: conversionToCurrency.value
        });
        
        conversionResult.value = response.data;
      } catch (error) {
        console.error('Failed to convert currency:', error);
        showSnackbar(`Failed to convert currency: ${error.response?.data?.detail || error.message}`, 'error');
      } finally {
        converting.value = false;
      }
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return '';
      return format(new Date(dateString), 'MMM dd, yyyy');
    };
    
    // Watch for changes to source/target currency
    watch([sourceCurrency, targetCurrency, rateDate], () => {
      loadExchangeRates();
    });
    
    // Load data on mount
    onMounted(() => {
      loadCurrencies();
    });
    
    return {
      // Data
      headers,
      currencies,
      loading,
      saving,
      deleting,
      converting,
      
      // Currency dialog
      currencyDialog,
      editMode,
      editedCurrency,
      currencyForm,
      
      // Exchange rate dialog
      exchangeRateDialog,
      editedExchangeRate,
      exchangeRateForm,
      effectiveDateMenu,
      
      // Delete dialog
      deleteDialog,
      currencyToDelete,
      
      // Exchange rate lookup
      sourceCurrency,
      targetCurrency,
      rateDate,
      dateMenu,
      currentRate,
      currentRateDate,
      exchangeRateLoaded,
      
      // Currency conversion
      conversionAmount,
      conversionFromCurrency,
      conversionToCurrency,
      conversionResult,
      
      // Computed
      formattedDate,
      formattedEffectiveDate,
      
      // Methods
      loadCurrencies,
      loadExchangeRates,
      openCurrencyDialog,
      closeCurrencyDialog,
      saveCurrency,
      openExchangeRateDialog,
      closeExchangeRateDialog,
      saveExchangeRate,
      confirmDeleteCurrency,
      deleteCurrency,
      convertCurrency,
      formatDate
    };
  }
};
</script>

<style scoped>
.v-data-table {
  width: 100%;
}
</style>