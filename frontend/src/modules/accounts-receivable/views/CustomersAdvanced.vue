<template>
  <div class="customers-advanced">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>Customer Management</h1>
            <p>Advanced customer management with AI insights</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-secondary" @click="exportCustomers">Export</button>
            <button class="btn btn-primary" @click="showCreateModal = true">+ Add Customer</button>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Customers Table -->
      <div class="table-card">
        <div class="table-header">
          <h3>Customers ({{ customers.length }})</h3>
        </div>
        
        <div class="table-container">
          <table class="customers-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Category</th>
                <th>Contact</th>
                <th>Outstanding</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="customer in customers" :key="customer.id">
                <td class="customer-info">
                  <div class="customer-main">
                    <span class="customer-name">{{ customer.name }}</span>
                    <span class="customer-id">{{ customer.customerId }}</span>
                  </div>
                </td>
                <td>
                  <span class="category-badge" :class="customer.category">
                    {{ formatCategory(customer.category) }}
                  </span>
                </td>
                <td class="contact-info">
                  <div>{{ customer.contactPerson }}</div>
                  <div class="contact-details">{{ customer.email }}</div>
                </td>
                <td class="amount">{{ formatCurrency(customer.outstanding) }}</td>
                <td>
                  <span class="status-badge" :class="customer.status">
                    {{ formatStatus(customer.status) }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="btn-icon" @click="viewCustomer(customer)" title="View">👁️</button>
                    <button class="btn-icon" @click="editCustomer(customer)" title="Edit">✏️</button>
                    <button class="btn-icon" @click="viewInvoices(customer)" title="Invoices">📄</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingCustomer ? 'Edit' : 'Create' }} Customer</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="saveCustomer" class="customer-form">
          <div class="form-grid">
            <div class="form-group">
              <label>Customer Name *</label>
              <input type="text" v-model="customerForm.name" required class="form-input">
            </div>
            <div class="form-group">
              <label>Category *</label>
              <select v-model="customerForm.category" required class="form-input">
                <option value="">Select Category</option>
                <option value="individual">Individual</option>
                <option value="business">Business</option>
                <option value="government">Government</option>
                <option value="reseller">Reseller</option>
              </select>
            </div>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label>Contact Person</label>
              <input type="text" v-model="customerForm.contactPerson" class="form-input">
            </div>
            <div class="form-group">
              <label>Email</label>
              <input type="email" v-model="customerForm.email" class="form-input">
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label>Phone</label>
              <input type="tel" v-model="customerForm.phone" class="form-input">
            </div>
            <div class="form-group">
              <label>Credit Limit</label>
              <input type="number" v-model="customerForm.creditLimit" class="form-input" step="0.01">
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Customer</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showCreateModal = ref(false)
const editingCustomer = ref(null)

const customerForm = ref({
  name: '',
  category: '',
  contactPerson: '',
  email: '',
  phone: '',
  creditLimit: 0
})

const customers = ref([
  {
    id: 1,
    customerId: 'C001',
    name: 'ABC Corporation',
    category: 'business',
    contactPerson: 'John Smith',
    email: 'john@abccorp.com',
    phone: '555-0123',
    outstanding: 25000,
    status: 'active'
  },
  {
    id: 2,
    customerId: 'C002',
    name: 'XYZ Retail Store',
    category: 'retail',
    contactPerson: 'Sarah Johnson',
    email: 'sarah@xyzretail.com',
    phone: '555-0456',
    outstanding: 12000,
    status: 'active'
  }
])

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const formatCategory = (category: string) => {
  return category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatStatus = (status: string) => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const viewCustomer = (customer: any) => {
  window.open(`/ar/customers/${customer.id}`, '_blank')
}

const editCustomer = (customer: any) => {
  editingCustomer.value = customer
  customerForm.value = { ...customer }
  showCreateModal.value = true
}

const viewInvoices = (customer: any) => {
  router.push({ path: '/ar/invoices', query: { customer: customer.id } })
}

const saveCustomer = () => {
  if (!customerForm.value.name || !customerForm.value.category) {
    alert('Please fill in required fields')
    return
  }
  
  if (editingCustomer.value) {
    const index = customers.value.findIndex(c => c.id === editingCustomer.value.id)
    if (index > -1) {
      customers.value[index] = { ...customers.value[index], ...customerForm.value }
    }
    alert('Customer updated successfully')
  } else {
    const newCustomer = {
      id: Math.max(...customers.value.map(c => c.id)) + 1,
      customerId: `C${String(Math.max(...customers.value.map(c => parseInt(c.customerId.substring(1)))) + 1).padStart(3, '0')}`,
      ...customerForm.value,
      outstanding: 0,
      status: 'active'
    }
    customers.value.push(newCustomer)
    alert('Customer created successfully')
  }
  
  closeModal()
}

const closeModal = () => {
  showCreateModal.value = false
  editingCustomer.value = null
  customerForm.value = {
    name: '',
    category: '',
    contactPerson: '',
    email: '',
    phone: '',
    creditLimit: 0
  }
}

const exportCustomers = () => {
  const csvData = customers.value.map(customer => ({
    'Customer ID': customer.customerId,
    'Name': customer.name,
    'Category': customer.category,
    'Contact': customer.contactPerson,
    'Email': customer.email,
    'Outstanding': customer.outstanding
  }))
  
  const csv = convertToCSV(csvData)
  downloadCSV(csv, 'customers-export.csv')
}

const convertToCSV = (data: any[]) => {
  if (!data.length) return ''
  
  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
  ].join('\n')
  
  return csvContent
}

const downloadCSV = (csv: string, filename: string) => {
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(url)
}
</script>

<style>
@import '/src/assets/styles/ar-advanced.css';
</style>