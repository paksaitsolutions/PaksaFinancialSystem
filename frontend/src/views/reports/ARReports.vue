<template>
  <div class="ar-reports">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>📊 AR Reports & Analytics</h1>
            <p>Comprehensive accounts receivable reporting</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-primary" @click="generateCustomerLedger">Generate Report</button>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Quick Reports -->
      <div class="quick-reports-section">
        <h3>🚀 Quick Reports</h3>
        <div class="reports-grid">
          <div v-for="report in quickReports" :key="report.id" class="report-card" @click="generateReport(report)">
            <div class="report-icon">{{ report.icon }}</div>
            <div class="report-content">
              <h4>{{ report.title }}</h4>
              <p>{{ report.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Customer Ledger Form -->
      <div class="advanced-report-card">
        <div class="report-header">
          <h4>👤 Customer Ledger</h4>
        </div>
        <div class="report-form">
          <div class="form-row">
            <select v-model="customerLedger.customerId" class="form-input">
              <option value="">Select Customer</option>
              <option v-for="customer in customers" :key="customer.id" :value="customer.id">
                {{ customer.name }}
              </option>
            </select>
            <input type="date" v-model="customerLedger.startDate" class="form-input">
            <input type="date" v-model="customerLedger.endDate" class="form-input">
          </div>
          <button class="btn btn-primary" @click="generateCustomerLedger">Generate Ledger</button>
        </div>
      </div>

      <!-- Report Results -->
      <div v-if="currentReport" class="report-results-section">
        <div class="results-header">
          <h3>📋 {{ currentReport.title }}</h3>
        </div>

        <div class="ledger-results">
          <div class="ledger-table">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Reference</th>
                  <th>Description</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="entry in currentReport.entries" :key="entry.id">
                  <td>{{ formatDate(entry.date) }}</td>
                  <td>{{ entry.reference }}</td>
                  <td>{{ entry.description }}</td>
                  <td class="amount">{{ formatCurrency(entry.amount) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const currentReport = ref(null)

const customerLedger = ref({
  customerId: '',
  startDate: '',
  endDate: ''
})

const quickReports = ref([
  {
    id: 'aging_summary',
    icon: '⏰',
    title: 'Aging Summary',
    description: 'Outstanding balances by age'
  },
  {
    id: 'top_customers',
    icon: '👑',
    title: 'Top Customers',
    description: 'Highest value customers'
  }
])

const customers = ref([
  { id: 1, name: 'ABC Corporation' },
  { id: 2, name: 'XYZ Retail Store' }
])

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const generateReport = (report: any) => {
  alert(`Generating ${report.title}...`)
}

const generateCustomerLedger = () => {
  currentReport.value = {
    title: 'Customer Ledger Report',
    entries: [
      {
        id: 1,
        date: '2024-01-01',
        reference: 'INV-001',
        description: 'Professional Services',
        amount: 15000
      },
      {
        id: 2,
        date: '2024-01-15',
        reference: 'PAY-001',
        description: 'Payment Received',
        amount: -10000
      }
    ]
  }
}

onMounted(() => {
  const today = new Date()
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1)
  
  customerLedger.value.startDate = firstDay.toISOString().split('T')[0]
  customerLedger.value.endDate = today.toISOString().split('T')[0]
})
</script>

<style>
@import '/src/assets/styles/ar-advanced.css';

.ar-reports {
  min-height: 100vh;
  background: #f8fafc;
}

.quick-reports-section {
  margin: 30px 0;
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.report-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 16px;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.1);
}

.report-icon {
  font-size: 2rem;
}

.report-content h4 {
  margin: 0 0 8px 0;
  color: #2d3748;
}

.advanced-report-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin: 20px 0;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.report-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.report-results-section {
  margin: 40px 0;
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.ledger-table table {
  width: 100%;
  border-collapse: collapse;
}

.ledger-table th,
.ledger-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.ledger-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #4a5568;
}

.amount {
  text-align: right;
  font-family: monospace;
}
</style>