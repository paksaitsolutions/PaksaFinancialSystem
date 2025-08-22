<template>
  <v-container fluid>
    <v-card>
      <v-card-title>
        <v-icon left>mdi-calendar-check</v-icon>
        Period End Closing
      </v-card-title>
      
      <v-card-text>
        <v-stepper v-model="currentStep" vertical>
          <v-stepper-step :complete="currentStep > 1" step="1">
            Pre-Closing Checklist
          </v-stepper-step>
          
          <v-stepper-content step="1">
            <v-list>
              <v-list-item v-for="item in preClosingChecklist" :key="item.id">
                <template v-slot:prepend>
                  <v-checkbox v-model="item.completed" />
                </template>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
            
            <v-btn 
              color="primary" 
              @click="currentStep = 2"
              :disabled="!allPreClosingComplete"
            >
              Continue
            </v-btn>
          </v-stepper-content>
          
          <v-stepper-step :complete="currentStep > 2" step="2">
            Closing Entries
          </v-stepper-step>
          
          <v-stepper-content step="2">
            <v-data-table
              :headers="closingEntriesHeaders"
              :items="closingEntries"
              class="mb-4"
            >
              <template v-slot:item.status="{ item }">
                <v-chip :color="getStatusColor(item.status)" small>
                  {{ item.status }}
                </v-chip>
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn 
                  icon 
                  small 
                  @click="processClosingEntry(item)"
                  :disabled="item.status === 'completed'"
                >
                  <v-icon>mdi-play</v-icon>
                </v-btn>
              </template>
            </v-data-table>
            
            <v-btn 
              color="primary" 
              @click="currentStep = 3"
              :disabled="!allClosingEntriesComplete"
            >
              Continue
            </v-btn>
          </v-stepper-content>
          
          <v-stepper-step :complete="currentStep > 3" step="3">
            Final Review
          </v-stepper-step>
          
          <v-stepper-content step="3">
            <v-row>
              <v-col cols="12" md="6">
                <v-card outlined>
                  <v-card-title>Period Summary</v-card-title>
                  <v-card-text>
                    <v-simple-table>
                      <tbody>
                        <tr>
                          <td>Period:</td>
                          <td>{{ selectedPeriod }}</td>
                        </tr>
                        <tr>
                          <td>Total Revenue:</td>
                          <td>${{ formatCurrency(periodSummary.totalRevenue) }}</td>
                        </tr>
                        <tr>
                          <td>Total Expenses:</td>
                          <td>${{ formatCurrency(periodSummary.totalExpenses) }}</td>
                        </tr>
                        <tr>
                          <td>Net Income:</td>
                          <td>${{ formatCurrency(periodSummary.netIncome) }}</td>
                        </tr>
                      </tbody>
                    </v-simple-table>
                  </v-card-text>
                </v-card>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-card outlined>
                  <v-card-title>Closing Actions</v-card-title>
                  <v-card-text>
                    <v-btn 
                      color="success" 
                      block 
                      large 
                      @click="closePeriod"
                      :loading="closing"
                    >
                      Close Period
                    </v-btn>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-stepper-content>
        </v-stepper>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
export default {
  name: 'PeriodEndClosingView',
  
  data: () => ({
    currentStep: 1,
    closing: false,
    selectedPeriod: 'December 2024',
    
    preClosingChecklist: [
      {
        id: 1,
        title: 'Bank Reconciliations Complete',
        description: 'All bank accounts reconciled for the period',
        completed: false
      },
      {
        id: 2,
        title: 'Accounts Receivable Reviewed',
        description: 'AR aging reviewed and adjustments made',
        completed: false
      },
      {
        id: 3,
        title: 'Accounts Payable Reviewed',
        description: 'AP aging reviewed and accruals recorded',
        completed: false
      },
      {
        id: 4,
        title: 'Inventory Count Complete',
        description: 'Physical inventory count completed and reconciled',
        completed: false
      },
      {
        id: 5,
        title: 'Fixed Asset Depreciation',
        description: 'Depreciation calculated and recorded',
        completed: false
      }
    ],
    
    closingEntriesHeaders: [
      { text: 'Entry Type', value: 'type' },
      { text: 'Description', value: 'description' },
      { text: 'Amount', value: 'amount' },
      { text: 'Status', value: 'status' },
      { text: 'Actions', value: 'actions', sortable: false }
    ],
    
    closingEntries: [
      {
        id: 1,
        type: 'Revenue Closing',
        description: 'Close revenue accounts to income summary',
        amount: 150000,
        status: 'pending'
      },
      {
        id: 2,
        type: 'Expense Closing',
        description: 'Close expense accounts to income summary',
        amount: 120000,
        status: 'pending'
      },
      {
        id: 3,
        type: 'Income Summary',
        description: 'Close income summary to retained earnings',
        amount: 30000,
        status: 'pending'
      }
    ],
    
    periodSummary: {
      totalRevenue: 150000,
      totalExpenses: 120000,
      netIncome: 30000
    }
  }),
  
  computed: {
    allPreClosingComplete() {
      return this.preClosingChecklist.every(item => item.completed)
    },
    
    allClosingEntriesComplete() {
      return this.closingEntries.every(entry => entry.status === 'completed')
    }
  },
  
  methods: {
    getStatusColor(status) {
      switch (status) {
        case 'completed': return 'success'
        case 'processing': return 'warning'
        case 'pending': return 'grey'
        default: return 'grey'
      }
    },
    
    processClosingEntry(entry) {
      entry.status = 'processing'
      setTimeout(() => {
        entry.status = 'completed'
      }, 2000)
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US').format(amount)
    },
    
    async closePeriod() {
      this.closing = true
      try {
        // Simulate period closing
        await new Promise(resolve => setTimeout(resolve, 3000))
        console.log('Period closed successfully')
      } finally {
        this.closing = false
      }
    }
  }
}
</script>