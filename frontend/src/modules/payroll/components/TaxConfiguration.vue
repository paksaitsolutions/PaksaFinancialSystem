<template>
  <v-card>
    <v-card-title>
      <span class="text-h5">Tax Configuration</span>
    </v-card-title>
    
    <v-card-text>
      <v-tabs v-model="activeTab">
        <v-tab value="federal">Federal Taxes</v-tab>
        <v-tab value="state">State Taxes</v-tab>
        <v-tab value="local">Local Taxes</v-tab>
        <v-tab value="multi-state">Multi-State</v-tab>
      </v-tabs>
      
      <v-tabs-window v-model="activeTab">
        <!-- Federal Tax Configuration -->
        <v-tabs-window-item value="federal">
          <v-card flat>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="federalConfig.social_security_rate"
                    label="Social Security Rate (%)"
                    type="number"
                    step="0.01"
                    suffix="%"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="federalConfig.social_security_wage_base"
                    label="Social Security Wage Base"
                    type="number"
                    prefix="$"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="federalConfig.medicare_rate"
                    label="Medicare Rate (%)"
                    type="number"
                    step="0.01"
                    suffix="%"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="federalConfig.additional_medicare_threshold"
                    label="Additional Medicare Threshold"
                    type="number"
                    prefix="$"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="federalConfig.futa_rate"
                    label="FUTA Rate (%)"
                    type="number"
                    step="0.01"
                    suffix="%"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="federalConfig.futa_wage_base"
                    label="FUTA Wage Base"
                    type="number"
                    prefix="$"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-tabs-window-item>
        
        <!-- State Tax Configuration -->
        <v-tabs-window-item value="state">
          <v-card flat>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="4">
                  <v-select
                    v-model="selectedState"
                    :items="states"
                    label="Select State"
                    @update:modelValue="loadStateConfig"
                  ></v-select>
                </v-col>
                
                <v-col cols="12" md="8" v-if="selectedState">
                  <v-btn color="primary" @click="addStateConfig">
                    Add State Configuration
                  </v-btn>
                </v-col>
              </v-row>
              
              <v-data-table
                :headers="stateHeaders"
                :items="stateConfigs"
                class="mt-4"
              >
                <template v-slot:item.actions="{ item }">
                  <v-btn icon size="small" @click="editStateConfig(item)">
                    <v-icon>mdi-pencil</v-icon>
                  </v-btn>
                  <v-btn icon size="small" @click="deleteStateConfig(item)">
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-tabs-window-item>
        
        <!-- Local Tax Configuration -->
        <v-tabs-window-item value="local">
          <v-card flat>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <v-btn color="primary" @click="addLocalTax">
                    Add Local Tax
                  </v-btn>
                </v-col>
              </v-row>
              
              <v-data-table
                :headers="localHeaders"
                :items="localTaxes"
                class="mt-4"
              >
                <template v-slot:item.actions="{ item }">
                  <v-btn icon size="small" @click="editLocalTax(item)">
                    <v-icon>mdi-pencil</v-icon>
                  </v-btn>
                  <v-btn icon size="small" @click="deleteLocalTax(item)">
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-tabs-window-item>
        
        <!-- Multi-State Configuration -->
        <v-tabs-window-item value="multi-state">
          <v-card flat>
            <v-card-text>
              <v-alert type="info" class="mb-4">
                Configure tax rules for employees working in different states than their residence.
              </v-alert>
              
              <v-row>
                <v-col cols="12" md="6">
                  <v-switch
                    v-model="multiStateConfig.enabled"
                    label="Enable Multi-State Tax Calculations"
                  ></v-switch>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-switch
                    v-model="multiStateConfig.reciprocity_enabled"
                    label="Apply Reciprocity Agreements"
                    :disabled="!multiStateConfig.enabled"
                  ></v-switch>
                </v-col>
              </v-row>
              
              <v-expansion-panels v-if="multiStateConfig.enabled">
                <v-expansion-panel title="Reciprocity Agreements">
                  <v-expansion-panel-text>
                    <v-data-table
                      :headers="reciprocityHeaders"
                      :items="reciprocityAgreements"
                      density="compact"
                    >
                      <template v-slot:item.actions="{ item }">
                        <v-btn icon size="small" @click="editReciprocity(item)">
                          <v-icon>mdi-pencil</v-icon>
                        </v-btn>
                      </template>
                    </v-data-table>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-card-text>
          </v-card>
        </v-tabs-window-item>
      </v-tabs-window>
    </v-card-text>
    
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="primary" @click="saveTaxConfiguration" :loading="saving">
        Save Configuration
      </v-btn>
    </v-card-actions>
    
    <!-- State Configuration Dialog -->
    <v-dialog v-model="stateDialog" max-width="600px">
      <v-card>
        <v-card-title>State Tax Configuration</v-card-title>
        <v-card-text>
          <v-form ref="stateForm">
            <v-row>
              <v-col cols="12">
                <v-select
                  v-model="editingState.state"
                  :items="states"
                  label="State"
                  required
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editingState.income_tax_rate"
                  label="Income Tax Rate (%)"
                  type="number"
                  step="0.01"
                  suffix="%"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editingState.standard_deduction"
                  label="Standard Deduction"
                  type="number"
                  prefix="$"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editingState.sdi_rate"
                  label="SDI Rate (%)"
                  type="number"
                  step="0.01"
                  suffix="%"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editingState.sdi_wage_base"
                  label="SDI Wage Base"
                  type="number"
                  prefix="$"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editingState.sui_rate"
                  label="SUI Rate (%)"
                  type="number"
                  step="0.01"
                  suffix="%"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editingState.sui_wage_base"
                  label="SUI Wage Base"
                  type="number"
                  prefix="$"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="stateDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveStateConfig">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'TaxConfiguration',
  setup() {
    const activeTab = ref('federal')
    const saving = ref(false)
    const stateDialog = ref(false)
    const selectedState = ref('')
    
    const federalConfig = ref({
      social_security_rate: 6.2,
      social_security_wage_base: 160200,
      medicare_rate: 1.45,
      additional_medicare_threshold: 200000,
      futa_rate: 0.6,
      futa_wage_base: 7000
    })
    
    const multiStateConfig = ref({
      enabled: false,
      reciprocity_enabled: false
    })
    
    const editingState = ref({
      state: '',
      income_tax_rate: 0,
      standard_deduction: 0,
      sdi_rate: 0,
      sdi_wage_base: 0,
      sui_rate: 0,
      sui_wage_base: 0
    })
    
    const states = [
      'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
      'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
      'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
      'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
      'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    ]
    
    const stateConfigs = ref([
      { state: 'CA', income_tax_rate: 7.25, standard_deduction: 4803, sdi_rate: 0.9, sdi_wage_base: 153164 },
      { state: 'NY', income_tax_rate: 6.85, standard_deduction: 8000, sdi_rate: 0.5, sdi_wage_base: 120000 }
    ])
    
    const localTaxes = ref([
      { jurisdiction: 'New York City', tax_type: 'Income', rate: 3.0, applies_to: 'Residents' },
      { jurisdiction: 'Philadelphia', tax_type: 'Income', rate: 1.0, applies_to: 'Workers' }
    ])
    
    const reciprocityAgreements = ref([
      { work_state: 'PA', residence_state: 'NJ', agreement_type: 'Full Reciprocity' },
      { work_state: 'VA', residence_state: 'MD', agreement_type: 'Partial Reciprocity' }
    ])
    
    const stateHeaders = [
      { title: 'State', key: 'state' },
      { title: 'Income Tax Rate (%)', key: 'income_tax_rate' },
      { title: 'Standard Deduction', key: 'standard_deduction' },
      { title: 'SDI Rate (%)', key: 'sdi_rate' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
    
    const localHeaders = [
      { title: 'Jurisdiction', key: 'jurisdiction' },
      { title: 'Tax Type', key: 'tax_type' },
      { title: 'Rate (%)', key: 'rate' },
      { title: 'Applies To', key: 'applies_to' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
    
    const reciprocityHeaders = [
      { title: 'Work State', key: 'work_state' },
      { title: 'Residence State', key: 'residence_state' },
      { title: 'Agreement Type', key: 'agreement_type' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
    
    const loadStateConfig = () => {
      // Load configuration for selected state
    }
    
    const addStateConfig = () => {
      editingState.value = {
        state: selectedState.value,
        income_tax_rate: 0,
        standard_deduction: 0,
        sdi_rate: 0,
        sdi_wage_base: 0,
        sui_rate: 0,
        sui_wage_base: 0
      }
      stateDialog.value = true
    }
    
    const editStateConfig = (item) => {
      editingState.value = { ...item }
      stateDialog.value = true
    }
    
    const saveStateConfig = () => {
      // Save state configuration
      const index = stateConfigs.value.findIndex(s => s.state === editingState.value.state)
      if (index >= 0) {
        stateConfigs.value[index] = { ...editingState.value }
      } else {
        stateConfigs.value.push({ ...editingState.value })
      }
      stateDialog.value = false
    }
    
    const deleteStateConfig = (item) => {
      const index = stateConfigs.value.findIndex(s => s.state === item.state)
      if (index >= 0) {
        stateConfigs.value.splice(index, 1)
      }
    }
    
    const addLocalTax = () => {
      // Add local tax configuration
    }
    
    const editLocalTax = (item) => {
      // Edit local tax configuration
    }
    
    const deleteLocalTax = (item) => {
      // Delete local tax configuration
    }
    
    const editReciprocity = (item) => {
      // Edit reciprocity agreement
    }
    
    const saveTaxConfiguration = async () => {
      saving.value = true
      try {
        // Save all tax configurations
        console.log('Saving tax configuration...')
        // API call would go here
      } catch (error) {
        console.error('Error saving configuration:', error)
      } finally {
        saving.value = false
      }
    }
    
    return {
      activeTab,
      saving,
      stateDialog,
      selectedState,
      federalConfig,
      multiStateConfig,
      editingState,
      states,
      stateConfigs,
      localTaxes,
      reciprocityAgreements,
      stateHeaders,
      localHeaders,
      reciprocityHeaders,
      loadStateConfig,
      addStateConfig,
      editStateConfig,
      saveStateConfig,
      deleteStateConfig,
      addLocalTax,
      editLocalTax,
      deleteLocalTax,
      editReciprocity,
      saveTaxConfiguration
    }
  }
}
</script>