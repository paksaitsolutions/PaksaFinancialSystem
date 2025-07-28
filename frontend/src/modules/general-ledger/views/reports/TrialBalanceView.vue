<template>
  <v-container fluid class="trial-balance-container">
    <v-card class="trial-balance-card" elevation="4">
      <!-- Header Section -->
      <v-card-title class="header-section">
        <div class="d-flex align-center w-100">
          <v-avatar color="primary" size="48" class="mr-4">
            <v-icon color="white" size="24">mdi-scale-balance</v-icon>
          </v-avatar>
          <div>
            <h1 class="text-h4 font-weight-bold">Trial Balance</h1>
            <p class="text-subtitle-1 text-medium-emphasis">Advanced Financial Reporting</p>
          </div>
          <v-spacer />
          <v-chip :color="isBalanced ? 'success' : 'error'" variant="flat" size="large">
            <v-icon start>{{ isBalanced ? 'mdi-check-circle' : 'mdi-alert-circle' }}</v-icon>
            {{ isBalanced ? 'Balanced' : 'Out of Balance' }}
          </v-chip>
        </div>
      </v-card-title>

      <!-- Controls Section -->
      <v-card-text class="controls-section">
        <v-row>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filters.startDate"
              type="date"
              label="Start Date"
              prepend-inner-icon="mdi-calendar"
              variant="outlined"
              density="comfortable"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filters.endDate"
              type="date"
              label="End Date"
              prepend-inner-icon="mdi-calendar"
              variant="outlined"
              density="comfortable"
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-select
              v-model="filters.accountType"
              :items="accountTypes"
              label="Account Type"
              prepend-inner-icon="mdi-filter"
              variant="outlined"
              density="comfortable"
              clearable
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-switch
              v-model="filters.includeZeros"
              label="Include Zero Balances"
              color="primary"
              inset
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-btn
              color="primary"
              size="large"
              block
              :loading="loading"
              @click="generateReport"
            >
              <v-icon start>mdi-refresh</v-icon>
              Generate
            </v-btn>
          </v-col>
        </v-row>

        <!-- Action Buttons -->
        <v-row class="mt-4">
          <v-col cols="12">
            <div class="d-flex gap-3">
              <v-btn
                color="success"
                variant="outlined"
                :disabled="!trialBalance"
                @click="exportToExcel"
              >
                <v-icon start>mdi-microsoft-excel</v-icon>
                Export Excel
              </v-btn>
              <v-btn
                color="error"
                variant="outlined"
                :disabled="!trialBalance"
                @click="exportToPDF"
              >
                <v-icon start>mdi-file-pdf-box</v-icon>
                Export PDF
              </v-btn>
              <v-btn
                color="info"
                variant="outlined"
                :disabled="!trialBalance"
                @click="printReport"
              >
                <v-icon start>mdi-printer</v-icon>
                Print
              </v-btn>
              <v-spacer />
              <v-text-field
                v-model="searchQuery"
                placeholder="Search accounts..."
                prepend-inner-icon="mdi-magnify"
                variant="outlined"
                density="compact"
                style="max-width: 300px;"
                clearable
              />
            </div>
          </v-col>
        </v-row>
      </v-card-text>

      <!-- Summary Cards -->
      <v-card-text v-if="trialBalance" class="summary-section">
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <v-card class="summary-card" color="primary" variant="tonal">
              <v-card-text class="text-center">
                <v-icon size="32" class="mb-2">mdi-plus-circle</v-icon>
                <div class="text-h5 font-weight-bold">{{ formatCurrency(totalDebits) }}</div>
                <div class="text-caption">Total Debits</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="summary-card" color="secondary" variant="tonal">
              <v-card-text class="text-center">
                <v-icon size="32" class="mb-2">mdi-minus-circle</v-icon>
                <div class="text-h5 font-weight-bold">{{ formatCurrency(totalCredits) }}</div>
                <div class="text-caption">Total Credits</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="summary-card" :color="isBalanced ? 'success' : 'error'" variant="tonal">
              <v-card-text class="text-center">
                <v-icon size="32" class="mb-2">{{ isBalanced ? 'mdi-check-circle' : 'mdi-alert-circle' }}</v-icon>
                <div class="text-h5 font-weight-bold">{{ formatCurrency(Math.abs(difference)) }}</div>
                <div class="text-caption">{{ isBalanced ? 'Balanced' : 'Difference' }}</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="summary-card" color="info" variant="tonal">
              <v-card-text class="text-center">
                <v-icon size="32" class="mb-2">mdi-account-multiple</v-icon>
                <div class="text-h5 font-weight-bold">{{ filteredEntries.length }}</div>
                <div class="text-caption">Total Accounts</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>

      <!-- Data Table -->
      <v-card-text class="table-section">
        <v-data-table
          v-if="trialBalance"
          :headers="headers"
          :items="filteredEntries"
          :loading="loading"
          :search="searchQuery"
          class="advanced-table"
          density="comfortable"
          :items-per-page="25"
          :items-per-page-options="[10, 25, 50, 100, -1]"
        >
          <template #item.accountCode="{ item }">
            <v-chip size="small" color="primary" variant="outlined">
              {{ item.accountCode }}
            </v-chip>
          </template>

          <template #item.accountType="{ item }">
            <v-chip 
              size="small" 
              :color="getAccountTypeColor(item.accountType)"
              variant="flat"
            >
              {{ item.accountType }}
            </v-chip>
          </template>

          <template #item.debitAmount="{ item }">
            <div class="text-right font-weight-bold" :class="item.debitAmount > 0 ? 'text-success' : ''">
              {{ item.debitAmount > 0 ? formatCurrency(item.debitAmount) : '-' }}
            </div>
          </template>

          <template #item.creditAmount="{ item }">
            <div class="text-right font-weight-bold" :class="item.creditAmount > 0 ? 'text-error' : ''">
              {{ item.creditAmount > 0 ? formatCurrency(item.creditAmount) : '-' }}
            </div>
          </template>

          <template #item.balance="{ item }">
            <div class="text-right font-weight-bold" :class="getBalanceClass(item.balance)">
              {{ formatCurrency(Math.abs(item.balance)) }}
            </div>
          </template>

          <template #bottom>
            <div class="totals-row pa-4">
              <v-row class="font-weight-bold text-h6">
                <v-col cols="6" class="text-right">TOTALS:</v-col>
                <v-col cols="2" class="text-right text-success">{{ formatCurrency(totalDebits) }}</v-col>
                <v-col cols="2" class="text-right text-error">{{ formatCurrency(totalCredits) }}</v-col>
                <v-col cols="2" class="text-right" :class="isBalanced ? 'text-success' : 'text-error'">
                  {{ formatCurrency(Math.abs(difference)) }}
                </v-col>
              </v-row>
            </div>
          </template>
        </v-data-table>

        <!-- Loading State -->
        <div v-else-if="loading" class="text-center pa-8">
          <v-progress-circular indeterminate color="primary" size="64" />
          <div class="mt-4 text-h6">Generating Trial Balance...</div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center pa-8">
          <v-icon size="64" color="grey">mdi-file-document-outline</v-icon>
          <div class="mt-4 text-h6">No Data Available</div>
          <div class="text-body-1 text-medium-emphasis">Click Generate to create your trial balance</div>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const loading = ref(false)
const trialBalance = ref<any>(null)
const searchQuery = ref('')

const filters = ref({
  startDate: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0],
  endDate: new Date().toISOString().split('T')[0],
  accountType: null,
  includeZeros: false
})

const accountTypes = ['Asset', 'Liability', 'Equity', 'Revenue', 'Expense']

const headers = [
  { title: 'Account Code', key: 'accountCode', width: '120px' },
  { title: 'Account Name', key: 'accountName', width: '300px' },
  { title: 'Type', key: 'accountType', width: '120px' },
  { title: 'Debit Amount', key: 'debitAmount', align: 'end', width: '150px' },
  { title: 'Credit Amount', key: 'creditAmount', align: 'end', width: '150px' },
  { title: 'Balance', key: 'balance', align: 'end', width: '150px' }
]

const filteredEntries = computed(() => {
  if (!trialBalance.value?.entries) return []
  
  let entries = trialBalance.value.entries
  
  if (filters.value.accountType) {
    entries = entries.filter((entry: any) => entry.accountType === filters.value.accountType)
  }
  
  if (!filters.value.includeZeros) {
    entries = entries.filter((entry: any) => entry.debitAmount !== 0 || entry.creditAmount !== 0)
  }
  
  return entries
})

const totalDebits = computed(() => {
  return filteredEntries.value.reduce((sum: number, entry: any) => sum + entry.debitAmount, 0)
})

const totalCredits = computed(() => {
  return filteredEntries.value.reduce((sum: number, entry: any) => sum + entry.creditAmount, 0)
})

const difference = computed(() => totalDebits.value - totalCredits.value)
const isBalanced = computed(() => Math.abs(difference.value) < 0.01)

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const getAccountTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    'Asset': 'success',
    'Liability': 'error',
    'Equity': 'info',
    'Revenue': 'primary',
    'Expense': 'warning'
  }
  return colors[type] || 'grey'
}

const getBalanceClass = (balance: number) => {
  return balance > 0 ? 'text-success' : balance < 0 ? 'text-error' : 'text-grey'
}

const generateReport = async () => {
  loading.value = true
  try {
    const response = await api.get('/api/v1/gl/reports/trial-balance', {
      params: {
        start_date: filters.value.startDate,
        end_date: filters.value.endDate,
        include_zeros: filters.value.includeZeros
      }
    })
    trialBalance.value = response.data
  } catch (error) {
    console.error('Error generating trial balance:', error)
    // Show user-friendly error message
    trialBalance.value = null
  } finally {
    loading.value = false
  }
}

const exportToExcel = () => {
  console.log('Exporting to Excel...')
}

const exportToPDF = () => {
  console.log('Exporting to PDF...')
}

const printReport = () => {
  window.print()
}

onMounted(() => {
  generateReport()
})
</script>

<style scoped>
.trial-balance-container {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  min-height: 100vh;
  padding: 24px;
}

.trial-balance-card {
  border-radius: 20px;
  overflow: hidden;
}

.header-section {
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, rgb(var(--v-theme-secondary)) 100%);
  color: white;
  padding: 32px;
}

.controls-section {
  background: rgba(var(--v-theme-surface), 0.8);
  backdrop-filter: blur(10px);
}

.summary-section {
  background: rgba(var(--v-theme-primary), 0.02);
}

.summary-card {
  border-radius: 16px;
  transition: all 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
}

.advanced-table {
  border-radius: 12px;
  overflow: hidden;
}

.totals-row {
  background: rgba(var(--v-theme-primary), 0.05);
  border-top: 2px solid rgb(var(--v-theme-primary));
}

:deep(.v-data-table__wrapper) {
  border-radius: 12px;
}

:deep(.v-data-table-header) {
  background: rgba(var(--v-theme-primary), 0.1);
}

:deep(.v-data-table-header th) {
  font-weight: 600;
  color: rgb(var(--v-theme-primary));
}
</style>