<template>
  <div class="tax-calculator">
    <v-card>
      <v-card-title>
        <h2>Tax Calculator</h2>
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-card outlined>
              <v-card-title>Employee Tax Calculation</v-card-title>
              <v-card-text>
                <v-form ref="taxForm" v-model="formValid">
                  <v-row>
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="taxRequest.gross_pay"
                        label="Gross Pay"
                        type="number"
                        step="0.01"
                        prefix="$"
                        :rules="[v => !!v && v > 0 || 'Gross pay is required']"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-select
                        v-model="taxRequest.pay_period"
                        :items="payPeriods"
                        label="Pay Period"
                        :rules="[v => !!v || 'Pay period is required']"
                      ></v-select>
                    </v-col>
                  </v-row>
                  
                  <v-row>
                    <v-col cols="12" md="6">
                      <v-select
                        v-model="taxRequest.filing_status"
                        :items="filingStatuses"
                        label="Filing Status"
                        :rules="[v => !!v || 'Filing status is required']"
                      ></v-select>
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="taxRequest.allowances"
                        label="Allowances"
                        type="number"
                        min="0"
                      ></v-text-field>
                    </v-col>
                  </v-row>
                  
                  <v-row>
                    <v-col cols="12" md="6">
                      <v-select
                        v-model="taxRequest.state"
                        :items="states"
                        label="State"
                      ></v-select>
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="taxRequest.additional_withholding"
                        label="Additional Withholding"
                        type="number"
                        step="0.01"
                        prefix="$"
                      ></v-text-field>
                    </v-col>
                  </v-row>
                  
                  <v-row>
                    <v-col cols="12">
                      <v-btn
                        color="primary"
                        @click="calculateTaxes"
                        :loading="calculating"
                        :disabled="!formValid"
                        block
                      >
                        Calculate Taxes
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="6">
            <v-card outlined>
              <v-card-title>Tax Calculation Results</v-card-title>
              <v-card-text>
                <div v-if="!taxResult">
                  <p class="text-center text-grey">Enter details and click "Calculate Taxes" to see results</p>
                </div>
                
                <div v-else>
                  <v-simple-table>
                    <template v-slot:default>
                      <tbody>
                        <tr>
                          <td><strong>Gross Pay</strong></td>
                          <td class="text-right">{{ formatCurrency(taxResult.gross_pay) }}</td>
                        </tr>
                        <tr>
                          <td>Federal Income Tax</td>
                          <td class="text-right">{{ formatCurrency(taxResult.federal_income_tax) }}</td>
                        </tr>
                        <tr>
                          <td>State Income Tax</td>
                          <td class="text-right">{{ formatCurrency(taxResult.state_income_tax) }}</td>
                        </tr>
                        <tr>
                          <td>Social Security Tax</td>
                          <td class="text-right">{{ formatCurrency(taxResult.social_security_tax) }}</td>
                        </tr>
                        <tr>
                          <td>Medicare Tax</td>
                          <td class="text-right">{{ formatCurrency(taxResult.medicare_tax) }}</td>
                        </tr>
                        <tr>
                          <td>Unemployment Tax</td>
                          <td class="text-right">{{ formatCurrency(taxResult.unemployment_tax) }}</td>
                        </tr>
                        <tr>
                          <td>Disability Tax</td>
                          <td class="text-right">{{ formatCurrency(taxResult.disability_tax) }}</td>
                        </tr>
                        <tr class="font-weight-bold">
                          <td><strong>Total Taxes</strong></td>
                          <td class="text-right">{{ formatCurrency(taxResult.total_tax) }}</td>
                        </tr>
                        <tr class="font-weight-bold success--text">
                          <td><strong>Net Pay</strong></td>
                          <td class="text-right">{{ formatCurrency(taxResult.net_pay) }}</td>
                        </tr>
                        <tr>
                          <td>Effective Tax Rate</td>
                          <td class="text-right">{{ taxResult.effective_tax_rate.toFixed(2) }}%</td>
                        </tr>
                        <tr>
                          <td>Marginal Tax Rate</td>
                          <td class="text-right">{{ taxResult.marginal_tax_rate.toFixed(2) }}%</td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Annual Estimate -->
        <v-row class="mt-4" v-if="taxResult">
          <v-col cols="12">
            <v-card outlined>
              <v-card-title>Annual Tax Estimate</v-card-title>
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="3">
                    <v-card class="text-center pa-4" color="blue lighten-5">
                      <h3>{{ formatCurrency(annualEstimate.gross) }}</h3>
                      <p>Annual Gross</p>
                    </v-card>
                  </v-col>
                  <v-col cols="12" md="3">
                    <v-card class="text-center pa-4" color="red lighten-5">
                      <h3>{{ formatCurrency(annualEstimate.taxes) }}</h3>
                      <p>Annual Taxes</p>
                    </v-card>
                  </v-col>
                  <v-col cols="12" md="3">
                    <v-card class="text-center pa-4" color="green lighten-5">
                      <h3>{{ formatCurrency(annualEstimate.net) }}</h3>
                      <p>Annual Net</p>
                    </v-card>
                  </v-col>
                  <v-col cols="12" md="3">
                    <v-card class="text-center pa-4" color="orange lighten-5">
                      <h3>{{ taxResult.effective_tax_rate.toFixed(1) }}%</h3>
                      <p>Tax Rate</p>
                    </v-card>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Tax Brackets Reference -->
        <v-row class="mt-4">
          <v-col cols="12">
            <v-card outlined>
              <v-card-title>
                Current Tax Brackets (2024)
                <v-spacer></v-spacer>
                <v-btn text @click="loadTaxBrackets">
                  <v-icon left>mdi-refresh</v-icon>
                  Refresh
                </v-btn>
              </v-card-title>
              <v-card-text>
                <v-data-table
                  :headers="bracketHeaders"
                  :items="taxBrackets"
                  :loading="loadingBrackets"
                  hide-default-footer
                >
                  <template v-slot:item.min_income="{ item }">
                    {{ formatCurrency(item.min_income) }}
                  </template>
                  <template v-slot:item.max_income="{ item }">
                    {{ item.max_income ? formatCurrency(item.max_income) : 'No limit' }}
                  </template>
                  <template v-slot:item.rate="{ item }">
                    {{ (parseFloat(item.rate) * 100).toFixed(1) }}%
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'TaxCalculator',
  data: () => ({
    formValid: false,
    calculating: false,
    loadingBrackets: false,
    taxResult: null,
    taxBrackets: [],
    taxRequest: {
      gross_pay: 5000,
      pay_period: 'bi_weekly',
      filing_status: 'SINGLE',
      allowances: 0,
      additional_withholding: 0,
      state: 'CA',
      year: 2024
    },
    payPeriods: [
      { title: 'Weekly', value: 'weekly' },
      { title: 'Bi-Weekly', value: 'bi_weekly' },
      { title: 'Semi-Monthly', value: 'semi_monthly' },
      { title: 'Monthly', value: 'monthly' },
      { title: 'Annual', value: 'annual' }
    ],
    filingStatuses: [
      { title: 'Single', value: 'SINGLE' },
      { title: 'Married Filing Jointly', value: 'MARRIED_JOINT' },
      { title: 'Married Filing Separately', value: 'MARRIED_SEPARATE' },
      { title: 'Head of Household', value: 'HEAD_OF_HOUSEHOLD' }
    ],
    states: [
      { title: 'California', value: 'CA' },
      { title: 'New York', value: 'NY' },
      { title: 'Texas', value: 'TX' },
      { title: 'Florida', value: 'FL' }
    ],
    bracketHeaders: [
      { title: 'Min Income', key: 'min_income' },
      { title: 'Max Income', key: 'max_income' },
      { title: 'Tax Rate', key: 'rate' },
      { title: 'Base Tax', key: 'base_tax' }
    ]
  }),

  computed: {
    annualEstimate() {
      if (!this.taxResult) return { gross: 0, taxes: 0, net: 0 }
      
      const multiplier = this.getAnnualMultiplier(this.taxRequest.pay_period)
      return {
        gross: this.taxResult.gross_pay * multiplier,
        taxes: this.taxResult.total_tax * multiplier,
        net: this.taxResult.net_pay * multiplier
      }
    }
  },

  mounted() {
    this.loadTaxBrackets()
  },

  methods: {
    async calculateTaxes() {
      if (!this.formValid) return
      
      this.calculating = true
      try {
        const response = await fetch('/api/payroll/tax-calculation/calculate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            ...this.taxRequest,
            employee_id: '00000000-0000-0000-0000-000000000000'
          })
        })
        
        if (response.ok) {
          this.taxResult = await response.json()
        }
      } catch (error) {
        console.error('Error calculating taxes:', error)
      } finally {
        this.calculating = false
      }
    },

    async loadTaxBrackets() {
      this.loadingBrackets = true
      try {
        const response = await fetch(`/api/payroll/tax-calculation/tax-brackets?filing_status=${this.taxRequest.filing_status}`)
        if (response.ok) {
          const data = await response.json()
          this.taxBrackets = data.brackets
        }
      } catch (error) {
        console.error('Error loading tax brackets:', error)
      } finally {
        this.loadingBrackets = false
      }
    },

    getAnnualMultiplier(payPeriod) {
      const multipliers = {
        'weekly': 52,
        'bi_weekly': 26,
        'semi_monthly': 24,
        'monthly': 12,
        'annual': 1
      }
      return multipliers[payPeriod] || 26
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }
  },

  watch: {
    'taxRequest.filing_status'() {
      this.loadTaxBrackets()
    }
  }
}
</script>

<style scoped>
.tax-calculator {
  padding: 16px;
}
</style>