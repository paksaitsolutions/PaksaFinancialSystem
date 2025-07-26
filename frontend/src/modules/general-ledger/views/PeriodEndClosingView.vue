<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Period-End Closing</h1>
        
        <v-stepper v-model="currentStep" alt-labels>
          <v-stepper-header>
            <v-stepper-item
              :complete="currentStep > 1"
              :value="1"
              title="Pre-Closing Checks"
            />
            <v-divider />
            <v-stepper-item
              :complete="currentStep > 2"
              :value="2"
              title="Trial Balance Review"
            />
            <v-divider />
            <v-stepper-item
              :complete="currentStep > 3"
              :value="3"
              title="Adjusting Entries"
            />
            <v-divider />
            <v-stepper-item
              :complete="currentStep > 4"
              :value="4"
              title="Final Closing"
            />
          </v-stepper-header>
          
          <v-stepper-window>
            <v-stepper-window-item :value="1">
              <v-card>
                <v-card-title>Pre-Closing Validation</v-card-title>
                <v-card-text>
                  <v-list>
                    <v-list-item
                      v-for="check in preClosingChecks"
                      :key="check.id"
                      :prepend-icon="check.passed ? 'mdi-check-circle' : 'mdi-alert-circle'"
                      :class="check.passed ? 'text-success' : 'text-error'"
                    >
                      <v-list-item-title>{{ check.description }}</v-list-item-title>
                      <v-list-item-subtitle v-if="!check.passed">
                        {{ check.issue }}
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                  
                  <v-btn
                    @click="runPreClosingChecks"
                    color="primary"
                    :loading="runningChecks"
                    class="mt-4"
                  >
                    Run Validation Checks
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-stepper-window-item>
            
            <v-stepper-window-item :value="2">
              <v-card>
                <v-card-title>Trial Balance Review</v-card-title>
                <v-card-text>
                  <v-data-table
                    :headers="trialBalanceHeaders"
                    :items="trialBalanceData"
                    :loading="loadingTrialBalance"
                  >
                    <template v-slot:item.debit="{ item }">
                      {{ formatCurrency(item.debit) }}
                    </template>
                    <template v-slot:item.credit="{ item }">
                      {{ formatCurrency(item.credit) }}
                    </template>
                  </v-data-table>
                  
                  <v-row class="mt-4">
                    <v-col cols="6">
                      <v-card outlined>
                        <v-card-text class="text-center">
                          <div class="text-h6">Total Debits</div>
                          <div class="text-h4 text-success">{{ formatCurrency(totalDebits) }}</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="6">
                      <v-card outlined>
                        <v-card-text class="text-center">
                          <div class="text-h6">Total Credits</div>
                          <div class="text-h4 text-success">{{ formatCurrency(totalCredits) }}</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-stepper-window-item>
            
            <v-stepper-window-item :value="3">
              <v-card>
                <v-card-title>Adjusting Entries</v-card-title>
                <v-card-text>
                  <v-btn @click="showAdjustingEntryDialog = true" color="primary" class="mb-4">
                    Add Adjusting Entry
                  </v-btn>
                  
                  <v-data-table
                    :headers="adjustingEntryHeaders"
                    :items="adjustingEntries"
                  >
                    <template v-slot:item.amount="{ item }">
                      {{ formatCurrency(item.amount) }}
                    </template>
                    <template v-slot:item.actions="{ item }">
                      <v-btn icon small @click="editAdjustingEntry(item)">
                        <v-icon>mdi-pencil</v-icon>
                      </v-btn>
                      <v-btn icon small @click="deleteAdjustingEntry(item)">
                        <v-icon>mdi-delete</v-icon>
                      </v-btn>
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>
            </v-stepper-window-item>
            
            <v-stepper-window-item :value="4">
              <v-card>
                <v-card-title>Final Period Closing</v-card-title>
                <v-card-text>
                  <v-alert type="warning" class="mb-4">
                    <strong>Warning:</strong> Once you close this period, no further entries can be made.
                    Please ensure all transactions are complete and accurate.
                  </v-alert>
                  
                  <v-row>
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="closingPeriod.name"
                        label="Period Name"
                        readonly
                      />
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="closingPeriod.endDate"
                        label="Period End Date"
                        readonly
                      />
                    </v-col>
                    <v-col cols="12">
                      <v-textarea
                        v-model="closingNotes"
                        label="Closing Notes"
                        rows="3"
                      />
                    </v-col>
                  </v-row>
                  
                  <v-btn
                    @click="closePeriod"
                    color="error"
                    :loading="closingPeriod.loading"
                    :disabled="!canClosePeriod"
                  >
                    Close Period
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-stepper-window-item>
          </v-stepper-window>
          
          <v-stepper-actions
            @click:next="nextStep"
            @click:prev="prevStep"
            :disabled="!canProceedToNextStep"
          />
        </v-stepper>
      </v-col>
    </v-row>
    
    <!-- Adjusting Entry Dialog -->
    <adjusting-entry-dialog
      v-model="showAdjustingEntryDialog"
      :entry="selectedAdjustingEntry"
      @save="saveAdjustingEntry"
    />
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdjustingEntryDialog from '../components/AdjustingEntryDialog.vue'
import { usePeriodClosingStore } from '../store/period-closing'

const periodClosingStore = usePeriodClosingStore()
const currentStep = ref(1)
const runningChecks = ref(false)
const loadingTrialBalance = ref(false)
const showAdjustingEntryDialog = ref(false)
const selectedAdjustingEntry = ref(null)
const closingNotes = ref('')

const preClosingChecks = ref([
  { id: 1, description: 'All journal entries posted', passed: false, issue: 'Found 3 unposted entries' },
  { id: 2, description: 'Bank reconciliations complete', passed: false, issue: 'Main account not reconciled' },
  { id: 3, description: 'Trial balance balanced', passed: false, issue: 'Out of balance by $150.00' },
  { id: 4, description: 'No pending approvals', passed: false, issue: '2 entries awaiting approval' }
])

const trialBalanceHeaders = [
  { title: 'Account', key: 'accountName' },
  { title: 'Account Code', key: 'accountCode' },
  { title: 'Debit', key: 'debit' },
  { title: 'Credit', key: 'credit' }
]

const adjustingEntryHeaders = [
  { title: 'Date', key: 'date' },
  { title: 'Description', key: 'description' },
  { title: 'Account', key: 'account' },
  { title: 'Amount', key: 'amount' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const trialBalanceData = ref([])
const adjustingEntries = ref([])

const closingPeriod = ref({
  name: 'December 2023',
  endDate: '2023-12-31',
  loading: false
})

const totalDebits = computed(() => 
  trialBalanceData.value.reduce((sum, item) => sum + (item.debit || 0), 0)
)

const totalCredits = computed(() => 
  trialBalanceData.value.reduce((sum, item) => sum + (item.credit || 0), 0)
)

const canProceedToNextStep = computed(() => {
  switch (currentStep.value) {
    case 1: return preClosingChecks.value.every(check => check.passed)
    case 2: return Math.abs(totalDebits.value - totalCredits.value) < 0.01
    case 3: return true
    case 4: return true
    default: return false
  }
})

const canClosePeriod = computed(() => 
  canProceedToNextStep.value && currentStep.value === 4
)

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount || 0)
}

const runPreClosingChecks = async () => {
  runningChecks.value = true
  try {
    const results = await periodClosingStore.runPreClosingValidation()
    preClosingChecks.value = results
  } finally {
    runningChecks.value = false
  }
}

const loadTrialBalance = async () => {
  loadingTrialBalance.value = true
  try {
    trialBalanceData.value = await periodClosingStore.getTrialBalance()
  } finally {
    loadingTrialBalance.value = false
  }
}

const nextStep = () => {
  if (canProceedToNextStep.value && currentStep.value < 4) {
    currentStep.value++
    if (currentStep.value === 2) {
      loadTrialBalance()
    }
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const editAdjustingEntry = (entry) => {
  selectedAdjustingEntry.value = entry
  showAdjustingEntryDialog.value = true
}

const deleteAdjustingEntry = async (entry) => {
  await periodClosingStore.deleteAdjustingEntry(entry.id)
  loadAdjustingEntries()
}

const saveAdjustingEntry = async (entry) => {
  await periodClosingStore.saveAdjustingEntry(entry)
  showAdjustingEntryDialog.value = false
  selectedAdjustingEntry.value = null
  loadAdjustingEntries()
}

const loadAdjustingEntries = async () => {
  adjustingEntries.value = await periodClosingStore.getAdjustingEntries()
}

const closePeriod = async () => {
  closingPeriod.value.loading = true
  try {
    await periodClosingStore.closePeriod({
      periodId: closingPeriod.value.id,
      notes: closingNotes.value
    })
    // Show success message and redirect
  } finally {
    closingPeriod.value.loading = false
  }
}

onMounted(() => {
  loadAdjustingEntries()
})
</script>