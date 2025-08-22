<template>
  <v-card>
    <v-card-title>
      <span class="text-h5">Multi-Jurisdiction Tax Management</span>
      <v-spacer></v-spacer>
      <v-btn color="primary" @click="addJurisdiction">
        Add Jurisdiction
      </v-btn>
    </v-card-title>
    
    <v-card-text>
      <v-tabs v-model="activeTab">
        <v-tab value="jurisdictions">Jurisdictions</v-tab>
        <v-tab value="rates">Tax Rates</v-tab>
        <v-tab value="calculator">Tax Calculator</v-tab>
        <v-tab value="compliance">Compliance</v-tab>
      </v-tabs>
      
      <v-tabs-window v-model="activeTab">
        <!-- Jurisdictions Management -->
        <v-tabs-window-item value="jurisdictions">
          <v-data-table
            :headers="jurisdictionHeaders"
            :items="jurisdictions"
            class="mt-4"
          >
            <template v-slot:item.jurisdiction_type="{ item }">
              <v-chip :color="getJurisdictionTypeColor(item.jurisdiction_type)" size="small">
                {{ item.jurisdiction_type.toUpperCase() }}
              </v-chip>
            </template>
            
            <template v-slot:item.is_active="{ item }">
              <v-chip :color="item.is_active ? 'success' : 'error'" size="small">
                {{ item.is_active ? 'Active' : 'Inactive' }}
              </v-chip>
            </template>
            
            <template v-slot:item.actions="{ item }">
              <v-btn icon size="small" @click="editJurisdiction(item)">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn icon size="small" @click="viewRates(item)">
                <v-icon>mdi-percent</v-icon>
              </v-btn>
              <v-btn icon size="small" @click="deleteJurisdiction(item)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-tabs-window-item>
        
        <!-- Tax Rates Management -->
        <v-tabs-window-item value="rates">
          <v-row class="mt-4">
            <v-col cols="12" md="4">
              <v-select
                v-model="selectedJurisdiction"
                :items="jurisdictions"
                item-title="name"
                item-value="id"
                label="Select Jurisdiction"
                @update:modelValue="loadTaxRates"
              ></v-select>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-select
                v-model="filterTaxType"
                :items="taxTypes"
                label="Filter by Tax Type"
                clearable
              ></v-select>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-btn color="primary" @click="addTaxRate" :disabled="!selectedJurisdiction">
                Add Tax Rate
              </v-btn>
            </v-col>
          </v-row>
          
          <v-data-table
            :headers="rateHeaders"
            :items="filteredTaxRates"
            class="mt-4"
          >
            <template v-slot:item.rate="{ item }">
              {{ item.rate }}{{ item.rate_type === 'percentage' ? '%' : '' }}
            </template>
            
            <template v-slot:item.effective_date="{ item }">
              {{ formatDate(item.effective_date) }}
            </template>
            
            <template v-slot:item.is_active="{ item }">
              <v-chip :color="item.is_active ? 'success' : 'error'" size="small">
                {{ item.is_active ? 'Active' : 'Inactive' }}
              </v-chip>
            </template>
            
            <template v-slot:item.actions="{ item }">
              <v-btn icon size="small" @click="editTaxRate(item)">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn icon size="small" @click="deleteTaxRate(item)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-tabs-window-item>
        
        <!-- Tax Calculator -->
        <v-tabs-window-item value="calculator">
          <v-card flat class="mt-4">
            <v-card-title>Multi-Jurisdiction Tax Calculator</v-card-title>
            <v-card-text>
              <v-form ref="calculatorForm">
                <v-row>
                  <v-col cols="12" md="3">
                    <v-text-field
                      v-model="calculation.taxable_amount"
                      label="Taxable Amount"
                      type="number"
                      step="0.01"
                      prefix="$"
                      required
                    ></v-text-field>
                  </v-col>
                  
                  <v-col cols="12" md="3">
                    <v-select
                      v-model="calculation.state"
                      :items="states"
                      label="State"
                      required
                    ></v-select>
                  </v-col>
                  
                  <v-col cols="12" md="3">
                    <v-text-field
                      v-model="calculation.county"
                      label="County (Optional)"
                    ></v-text-field>
                  </v-col>
                  
                  <v-col cols="12" md="3">
                    <v-text-field
                      v-model="calculation.city"
                      label="City (Optional)"
                    ></v-text-field>
                  </v-col>
                  
                  <v-col cols="12" md="4">
                    <v-select
                      v-model="calculation.transaction_type"
                      :items="transactionTypes"
                      label="Transaction Type"
                      required
                    ></v-select>
                  </v-col>
                  
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="calculation.tax_period"
                      label="Tax Period"
                      type="date"
                      required
                    ></v-text-field>
                  </v-col>
                  
                  <v-col cols="12" md="4">
                    <v-btn 
                      color="primary" 
                      @click="calculateTax"
                      :loading="calculating"
                      block
                    >
                      Calculate Tax
                    </v-btn>
                  </v-col>
                </v-row>
              </v-form>
              
              <!-- Tax Calculation Results -->
              <v-card v-if="taxResults.length > 0" class="mt-4">
                <v-card-title>Tax Calculation Results</v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="4">
                      <v-card color="primary" dark>
                        <v-card-text>
                          <div class="text-h4">${{ totalTax.toLocaleString() }}</div>
                          <div class="text-subtitle-1">Total Tax</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    
                    <v-col cols="12" md="4">
                      <v-card color="success" dark>
                        <v-card-text>
                          <div class="text-h4">{{ effectiveRate.toFixed(3) }}%</div>
                          <div class="text-subtitle-1">Effective Rate</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    
                    <v-col cols="12" md="4">
                      <v-card color="info" dark>
                        <v-card-text>
                          <div class="text-h4">{{ taxResults.length }}</div>
                          <div class="text-subtitle-1">Jurisdictions</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                  
                  <!-- Detailed Results by Jurisdiction -->
                  <v-expansion-panels class="mt-4">
                    <v-expansion-panel
                      v-for="result in taxResults"
                      :key="result.jurisdiction_id"
                      :title="result.jurisdiction_name"
                    >
                      <v-expansion-panel-text>
                        <v-simple-table>
                          <thead>
                            <tr>
                              <th>Tax Type</th>
                              <th>Rate</th>
                              <th>Taxable Amount</th>
                              <th>Tax Amount</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="calc in result.tax_calculations" :key="calc.tax_type">
                              <td>{{ calc.tax_type }}</td>
                              <td>{{ calc.tax_rate }}%</td>
                              <td>${{ calc.taxable_amount.toLocaleString() }}</td>
                              <td>${{ calc.tax_amount.toLocaleString() }}</td>
                            </tr>
                          </tbody>
                        </v-simple-table>
                        
                        <div class="mt-2">
                          <strong>Jurisdiction Total: ${{ result.total_tax.toLocaleString() }}</strong>
                        </div>
                      </v-expansion-panel-text>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </v-card-text>
              </v-card>
            </v-card-text>
          </v-card>
        </v-tabs-window-item>
        
        <!-- Compliance Dashboard -->
        <v-tabs-window-item value="compliance">
          <v-card flat class="mt-4">
            <v-card-title>Jurisdiction Compliance Summary</v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="complianceStartDate"
                    label="Start Date"
                    type="date"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="complianceEndDate"
                    label="End Date"
                    type="date"
                  ></v-text-field>
                </v-col>
              </v-row>
              
              <v-btn color="primary" @click="loadComplianceSummary" class="mb-4">
                Load Compliance Summary
              </v-btn>
              
              <v-data-table
                v-if="complianceSummary.length > 0"
                :headers="complianceHeaders"
                :items="complianceSummary"
              >
                <template v-slot:item.compliance_status="{ item }">
                  <v-chip :color="getComplianceColor(item.compliance_status)" size="small">
                    {{ item.compliance_status }}
                  </v-chip>
                </template>
                
                <template v-slot:item.total_tax_due="{ item }">
                  ${{ item.total_tax_due.toLocaleString() }}
                </template>
                
                <template v-slot:item.total_tax_paid="{ item }">
                  ${{ item.total_tax_paid.toLocaleString() }}
                </template>
                
                <template v-slot:item.outstanding_balance="{ item }">
                  <span :class="item.outstanding_balance > 0 ? 'text-error' : 'text-success'">
                    ${{ item.outstanding_balance.toLocaleString() }}
                  </span>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-tabs-window-item>
      </v-tabs-window>
    </v-card-text>
    
    <!-- Jurisdiction Dialog -->
    <v-dialog v-model="jurisdictionDialog" max-width="600px">
      <v-card>
        <v-card-title>
          {{ editingJurisdiction.id ? 'Edit' : 'Add' }} Jurisdiction
        </v-card-title>
        
        <v-card-text>
          <v-form ref="jurisdictionForm">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="editingJurisdiction.name"
                  label="Jurisdiction Name"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editingJurisdiction.jurisdiction_type"
                  :items="jurisdictionTypes"
                  label="Jurisdiction Type"
                  required
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editingJurisdiction.state_code"
                  :items="states"
                  label="State"
                  required
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6" v-if="editingJurisdiction.jurisdiction_type === 'county'">
                <v-text-field
                  v-model="editingJurisdiction.county_name"
                  label="County Name"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6" v-if="editingJurisdiction.jurisdiction_type === 'city'">
                <v-text-field
                  v-model="editingJurisdiction.city_name"
                  label="City Name"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="editingJurisdiction.description"
                  label="Description"
                  rows="3"
                ></v-textarea>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-switch
                  v-model="editingJurisdiction.requires_registration"
                  label="Requires Registration"
                ></v-switch>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-switch
                  v-model="editingJurisdiction.is_active"
                  label="Active"
                ></v-switch>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="jurisdictionDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveJurisdiction">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'MultiJurisdictionManager',
  setup() {
    const activeTab = ref('jurisdictions')
    const jurisdictionDialog = ref(false)
    const selectedJurisdiction = ref(null)
    const filterTaxType = ref(null)
    const calculating = ref(false)
    
    const jurisdictions = ref([
      {
        id: 1,
        name: 'Federal',
        jurisdiction_type: 'federal',
        state_code: 'US',
        description: 'Federal tax jurisdiction',
        requires_registration: false,
        is_active: true
      },
      {
        id: 2,
        name: 'California State',
        jurisdiction_type: 'state',
        state_code: 'CA',
        description: 'California state tax jurisdiction',
        requires_registration: true,
        is_active: true
      }
    ])
    
    const taxRates = ref([
      {
        id: 1,
        jurisdiction_id: 1,
        tax_type: 'income',
        rate: 22.0,
        rate_type: 'percentage',
        effective_date: '2024-01-01',
        is_active: true
      },
      {
        id: 2,
        jurisdiction_id: 2,
        tax_type: 'income',
        rate: 7.25,
        rate_type: 'percentage',
        effective_date: '2024-01-01',
        is_active: true
      }
    ])
    
    const editingJurisdiction = ref({
      id: null,
      name: '',
      jurisdiction_type: '',
      state_code: '',
      county_name: '',
      city_name: '',
      description: '',
      requires_registration: false,
      is_active: true
    })
    
    const calculation = ref({
      taxable_amount: 0,
      state: '',
      county: '',
      city: '',
      transaction_type: '',
      tax_period: new Date().toISOString().split('T')[0]
    })
    
    const taxResults = ref([])
    const complianceSummary = ref([])
    const complianceStartDate = ref('')
    const complianceEndDate = ref('')
    
    const jurisdictionTypes = [
      { title: 'Federal', value: 'federal' },
      { title: 'State', value: 'state' },
      { title: 'County', value: 'county' },
      { title: 'City', value: 'city' },
      { title: 'District', value: 'district' }
    ]
    
    const taxTypes = [
      { title: 'Income Tax', value: 'income' },
      { title: 'Sales Tax', value: 'sales' },
      { title: 'Property Tax', value: 'property' },
      { title: 'Excise Tax', value: 'excise' }
    ]
    
    const states = [
      'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
      'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
      'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
      'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
      'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    ]
    
    const transactionTypes = [
      { title: 'Sale', value: 'sale' },
      { title: 'Service', value: 'service' },
      { title: 'Rental', value: 'rental' },
      { title: 'Other', value: 'other' }
    ]
    
    const jurisdictionHeaders = [
      { title: 'Name', key: 'name' },
      { title: 'Type', key: 'jurisdiction_type' },
      { title: 'State', key: 'state_code' },
      { title: 'Registration Required', key: 'requires_registration' },
      { title: 'Status', key: 'is_active' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
    
    const rateHeaders = [
      { title: 'Tax Type', key: 'tax_type' },
      { title: 'Rate', key: 'rate' },
      { title: 'Rate Type', key: 'rate_type' },
      { title: 'Effective Date', key: 'effective_date' },
      { title: 'Status', key: 'is_active' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
    
    const complianceHeaders = [
      { title: 'Jurisdiction', key: 'jurisdiction_name' },
      { title: 'Returns Filed', key: 'returns_filed' },
      { title: 'Tax Due', key: 'total_tax_due' },
      { title: 'Tax Paid', key: 'total_tax_paid' },
      { title: 'Outstanding', key: 'outstanding_balance' },
      { title: 'Status', key: 'compliance_status' }
    ]
    
    const filteredTaxRates = computed(() => {
      let filtered = taxRates.value
      
      if (selectedJurisdiction.value) {
        filtered = filtered.filter(r => r.jurisdiction_id === selectedJurisdiction.value)
      }
      
      if (filterTaxType.value) {
        filtered = filtered.filter(r => r.tax_type === filterTaxType.value)
      }
      
      return filtered
    })
    
    const totalTax = computed(() => {
      return taxResults.value.reduce((sum, result) => sum + result.total_tax, 0)
    })
    
    const effectiveRate = computed(() => {
      if (calculation.value.taxable_amount > 0) {
        return (totalTax.value / calculation.value.taxable_amount) * 100
      }
      return 0
    })
    
    const getJurisdictionTypeColor = (type) => {
      const colors = {
        'federal': 'blue',
        'state': 'green',
        'county': 'orange',
        'city': 'purple',
        'district': 'teal'
      }
      return colors[type] || 'grey'
    }
    
    const getComplianceColor = (status) => {
      const colors = {
        'compliant': 'success',
        'overdue': 'error',
        'pending': 'warning'
      }
      return colors[status] || 'grey'
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }
    
    const addJurisdiction = () => {
      editingJurisdiction.value = {
        id: null,
        name: '',
        jurisdiction_type: '',
        state_code: '',
        county_name: '',
        city_name: '',
        description: '',
        requires_registration: false,
        is_active: true
      }
      jurisdictionDialog.value = true
    }
    
    const editJurisdiction = (jurisdiction) => {
      editingJurisdiction.value = { ...jurisdiction }
      jurisdictionDialog.value = true
    }
    
    const saveJurisdiction = () => {
      if (editingJurisdiction.value.id) {
        // Update existing
        const index = jurisdictions.value.findIndex(j => j.id === editingJurisdiction.value.id)
        if (index >= 0) {
          jurisdictions.value[index] = { ...editingJurisdiction.value }
        }
      } else {
        // Add new
        editingJurisdiction.value.id = Date.now()
        jurisdictions.value.push({ ...editingJurisdiction.value })
      }
      jurisdictionDialog.value = false
    }
    
    const deleteJurisdiction = (jurisdiction) => {
      const index = jurisdictions.value.findIndex(j => j.id === jurisdiction.id)
      if (index >= 0) {
        jurisdictions.value.splice(index, 1)
      }
    }
    
    const viewRates = (jurisdiction) => {
      selectedJurisdiction.value = jurisdiction.id
      activeTab.value = 'rates'
    }
    
    const loadTaxRates = () => {
      // Load tax rates for selected jurisdiction
    }
    
    const addTaxRate = () => {
      // Add tax rate dialog
    }
    
    const editTaxRate = (rate) => {
      // Edit tax rate
    }
    
    const deleteTaxRate = (rate) => {
      // Delete tax rate
    }
    
    const calculateTax = async () => {
      calculating.value = true
      try {
        // Mock calculation results
        taxResults.value = [
          {
            jurisdiction_id: 1,
            jurisdiction_name: 'Federal',
            jurisdiction_type: 'federal',
            total_tax: calculation.value.taxable_amount * 0.22,
            tax_calculations: [
              {
                tax_type: 'income',
                tax_rate: 22.0,
                taxable_amount: calculation.value.taxable_amount,
                tax_amount: calculation.value.taxable_amount * 0.22
              }
            ]
          },
          {
            jurisdiction_id: 2,
            jurisdiction_name: 'California State',
            jurisdiction_type: 'state',
            total_tax: calculation.value.taxable_amount * 0.0725,
            tax_calculations: [
              {
                tax_type: 'income',
                tax_rate: 7.25,
                taxable_amount: calculation.value.taxable_amount,
                tax_amount: calculation.value.taxable_amount * 0.0725
              }
            ]
          }
        ]
      } catch (error) {
        console.error('Tax calculation failed:', error)
      } finally {
        calculating.value = false
      }
    }
    
    const loadComplianceSummary = () => {
      // Mock compliance data
      complianceSummary.value = [
        {
          jurisdiction_name: 'Federal',
          returns_filed: 4,
          total_tax_due: 50000,
          total_tax_paid: 50000,
          outstanding_balance: 0,
          compliance_status: 'compliant'
        },
        {
          jurisdiction_name: 'California State',
          returns_filed: 3,
          total_tax_due: 15000,
          total_tax_paid: 12000,
          outstanding_balance: 3000,
          compliance_status: 'overdue'
        }
      ]
    }
    
    return {
      activeTab,
      jurisdictionDialog,
      selectedJurisdiction,
      filterTaxType,
      calculating,
      jurisdictions,
      taxRates,
      editingJurisdiction,
      calculation,
      taxResults,
      complianceSummary,
      complianceStartDate,
      complianceEndDate,
      jurisdictionTypes,
      taxTypes,
      states,
      transactionTypes,
      jurisdictionHeaders,
      rateHeaders,
      complianceHeaders,
      filteredTaxRates,
      totalTax,
      effectiveRate,
      getJurisdictionTypeColor,
      getComplianceColor,
      formatDate,
      addJurisdiction,
      editJurisdiction,
      saveJurisdiction,
      deleteJurisdiction,
      viewRates,
      loadTaxRates,
      addTaxRate,
      editTaxRate,
      deleteTaxRate,
      calculateTax,
      loadComplianceSummary
    }
  }
}
</script>