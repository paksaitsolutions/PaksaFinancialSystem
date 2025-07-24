<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title>Tax Calculator</v-card-title>
      
      <v-card-text>
        <v-form ref="form" v-model="valid">
          <v-row>
            <v-col cols="12" md="6">
              <v-select
                v-model="selectedJurisdiction"
                :items="jurisdictions"
                item-title="name"
                item-value="id"
                label="Tax Jurisdiction"
                :rules="[v => !!v || 'Jurisdiction is required']"
                @update:modelValue="loadTaxRates"
              ></v-select>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="selectedTaxType"
                :items="taxTypes"
                label="Tax Type"
                :rules="[v => !!v || 'Tax type is required']"
                @update:modelValue="loadTaxRates"
              ></v-select>
            </v-col>
          </v-row>
          
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="taxableAmount"
                label="Taxable Amount"
                type="number"
                step="0.01"
                prefix="$"
                :rules="[v => !!v || 'Amount is required', v => v > 0 || 'Amount must be positive']"
                @input="calculateTax"
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="selectedTaxRate"
                :items="availableRates"
                item-title="display_name"
                item-value="id"
                label="Tax Rate"
                :rules="[v => !!v || 'Tax rate is required']"
                @update:modelValue="calculateTax"
              ></v-select>
            </v-col>
          </v-row>
          
          <v-divider class="my-4"></v-divider>
          
          <v-row v-if="calculation">
            <v-col cols="12" md="4">
              <v-text-field
                :value="formatCurrency(calculation.taxable_amount)"
                label="Taxable Amount"
                readonly
                variant="outlined"
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-text-field
                :value="formatCurrency(calculation.tax_amount)"
                label="Tax Amount"
                readonly
                variant="outlined"
                color="warning"
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-text-field
                :value="formatCurrency(calculation.total_amount)"
                label="Total Amount"
                readonly
                variant="outlined"
                color="success"
              ></v-text-field>
            </v-col>
          </v-row>
          
          <v-row v-if="selectedRateDetails">
            <v-col cols="12">
              <v-card variant="outlined">
                <v-card-title class="text-subtitle-1">Tax Rate Details</v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="6">
                      <strong>Rate:</strong> {{ (selectedRateDetails.rate * 100).toFixed(4) }}%
                    </v-col>
                    <v-col cols="6">
                      <strong>Type:</strong> {{ selectedRateDetails.tax_type }}
                    </v-col>
                    <v-col cols="6">
                      <strong>Effective Date:</strong> {{ formatDate(selectedRateDetails.effective_date) }}
                    </v-col>
                    <v-col cols="6">
                      <strong>Expiry Date:</strong> 
                      {{ selectedRateDetails.expiry_date ? formatDate(selectedRateDetails.expiry_date) : 'No expiry' }}
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="saveTransaction" :disabled="!valid || !calculation">
          Save as Transaction
        </v-btn>
      </v-card-actions>
    </v-card>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import { taxApiService } from '../services/taxApiService'

export default {
  name: 'TaxCalculator',
  components: { ResponsiveContainer },
  
  data: () => ({
    valid: false,
    selectedJurisdiction: null,
    selectedTaxType: null,
    selectedTaxRate: null,
    taxableAmount: 0,
    calculation: null,
    jurisdictions: [],
    availableRates: [],
    taxTypes: [
      'income',
      'sales',
      'vat',
      'gst',
      'payroll',
      'property',
      'excise'
    ]
  }),
  
  computed: {
    selectedRateDetails() {
      return this.availableRates.find(rate => rate.id === this.selectedTaxRate)
    }
  },
  
  async mounted() {
    await this.loadJurisdictions()
  },
  
  methods: {
    async loadJurisdictions() {
      try {
        this.jurisdictions = await taxApiService.getJurisdictions()
      } catch (error) {
        console.error('Error loading jurisdictions:', error)
      }
    },
    
    async loadTaxRates() {
      if (!this.selectedJurisdiction || !this.selectedTaxType) return
      
      try {
        const rate = await taxApiService.getRateForJurisdiction(
          this.selectedJurisdiction,
          this.selectedTaxType
        )
        
        if (rate) {
          this.availableRates = [{
            ...rate,
            display_name: `${rate.name} (${(rate.rate * 100).toFixed(2)}%)`
          }]
          this.selectedTaxRate = rate.id
        } else {
          this.availableRates = []
          this.selectedTaxRate = null
        }
      } catch (error) {
        console.error('Error loading tax rates:', error)
        this.availableRates = []
      }
    },
    
    async calculateTax() {
      if (!this.taxableAmount || !this.selectedTaxRate) {
        this.calculation = null
        return
      }
      
      try {
        this.calculation = await taxApiService.calculateTax(
          parseFloat(this.taxableAmount),
          this.selectedTaxRate
        )
      } catch (error) {
        console.error('Error calculating tax:', error)
        this.calculation = null
      }
    },
    
    async saveTransaction() {
      if (!this.calculation) return
      
      try {
        const transaction = {
          transaction_date: new Date().toISOString().split('T')[0],
          document_number: `CALC-${Date.now()}`,
          tax_rate_id: this.selectedTaxRate,
          taxable_amount: this.calculation.taxable_amount,
          tax_amount: this.calculation.tax_amount,
          total_amount: this.calculation.total_amount,
          status: 'draft',
          components: []
        }
        
        await taxApiService.createTaxTransaction(transaction)
        this.$emit('transaction-saved')
        
        // Reset form
        this.taxableAmount = 0
        this.calculation = null
      } catch (error) {
        console.error('Error saving transaction:', error)
      }
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>