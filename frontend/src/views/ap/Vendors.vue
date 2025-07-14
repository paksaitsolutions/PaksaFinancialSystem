<template>
  <div class="vendors">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>Vendors</h1>
            <p>Manage vendor information and relationships</p>
          </div>
          <button class="btn btn-primary" @click="showCreateModal = true">
            + Add Vendor
          </button>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Filters -->
      <div class="filters-section">
        <div class="filters-grid">
          <input type="text" v-model="searchQuery" placeholder="Search vendors..." class="filter-input">
          <select v-model="selectedStatus" class="filter-input">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <select v-model="selectedCategory" class="filter-input">
            <option value="">All Categories</option>
            <option value="supplier">Supplier</option>
            <option value="contractor">Contractor</option>
            <option value="service">Service Provider</option>
          </select>
        </div>
      </div>

      <!-- Vendors Table -->
      <div class="table-card">
        <div class="table-header">
          <h3>Vendors ({{ filteredVendors.length }})</h3>
          <div class="table-actions">
            <button class="btn btn-outline">Export</button>
            <button class="btn btn-outline">Import</button>
          </div>
        </div>
        
        <div class="table-container">
          <table class="vendors-table">
            <thead>
              <tr>
                <th>Vendor ID</th>
                <th>Name</th>
                <th>Contact</th>
                <th>Category</th>
                <th>Outstanding</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="vendor in filteredVendors" :key="vendor.id">
                <td class="vendor-id">{{ vendor.vendorId }}</td>
                <td class="vendor-name">{{ vendor.name }}</td>
                <td>
                  <div class="contact-info">
                    <div>{{ vendor.contactPerson }}</div>
                    <div class="contact-details">{{ vendor.email }}</div>
                  </div>
                </td>
                <td>
                  <span class="category-badge" :class="vendor.category">
                    {{ vendor.category }}
                  </span>
                </td>
                <td class="amount">{{ formatCurrency(vendor.outstanding) }}</td>
                <td>
                  <span class="status-badge" :class="vendor.status">
                    {{ vendor.status }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="btn-icon" @click="editVendor(vendor)" title="Edit">✏️</button>
                    <button class="btn-icon" @click="viewInvoices(vendor)" title="Invoices">📄</button>
                    <button class="btn-icon" @click="viewPayments(vendor)" title="Payments">💰</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingVendor ? 'Edit' : 'Create' }} Vendor</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="saveVendor" class="vendor-form">
          <div class="form-grid">
            <div class="form-group">
              <label>Vendor Name *</label>
              <input type="text" v-model="vendorForm.name" required class="form-input">
            </div>
            <div class="form-group">
              <label>Category *</label>
              <select v-model="vendorForm.category" required class="form-input">
                <option value="">Select Category</option>
                <option value="supplier">Supplier</option>
                <option value="contractor">Contractor</option>
                <option value="service">Service Provider</option>
              </select>
            </div>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label>Contact Person</label>
              <input type="text" v-model="vendorForm.contactPerson" class="form-input">
            </div>
            <div class="form-group">
              <label>Email</label>
              <input type="email" v-model="vendorForm.email" class="form-input">
            </div>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label>Phone</label>
              <input type="tel" v-model="vendorForm.phone" class="form-input">
            </div>
            <div class="form-group">
              <label>Tax ID</label>
              <input type="text" v-model="vendorForm.taxId" class="form-input">
            </div>
          </div>
          
          <div class="form-group">
            <label>Address</label>
            <textarea v-model="vendorForm.address" class="form-input" rows="3"></textarea>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label>Payment Terms</label>
              <select v-model="vendorForm.paymentTerms" class="form-input">
                <option value="net30">Net 30</option>
                <option value="net15">Net 15</option>
                <option value="due_on_receipt">Due on Receipt</option>
                <option value="net60">Net 60</option>
              </select>
            </div>
            <div class="form-group">
              <label>Status</label>
              <select v-model="vendorForm.status" class="form-input">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Vendor</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const showCreateModal = ref(false)
const editingVendor = ref(null)
const searchQuery = ref('')
const selectedStatus = ref('')
const selectedCategory = ref('')

const vendorForm = ref({
  name: '',
  category: '',
  contactPerson: '',
  email: '',
  phone: '',
  taxId: '',
  address: '',
  paymentTerms: 'net30',
  status: 'active'
})

const vendors = ref([
  {
    id: 1,
    vendorId: 'V001',
    name: 'ABC Supplies Inc.',
    contactPerson: 'John Smith',
    email: 'john@abcsupplies.com',
    phone: '555-0123',
    category: 'supplier',
    outstanding: 15000,
    status: 'active'
  },
  {
    id: 2,
    vendorId: 'V002',
    name: 'Tech Solutions LLC',
    contactPerson: 'Sarah Johnson',
    email: 'sarah@techsolutions.com',
    phone: '555-0456',
    category: 'service',
    outstanding: 8500,
    status: 'active'
  },
  {
    id: 3,
    vendorId: 'V003',
    name: 'Construction Pro',
    contactPerson: 'Mike Wilson',
    email: 'mike@constructionpro.com',
    phone: '555-0789',
    category: 'contractor',
    outstanding: 25000,
    status: 'active'
  }
])

const filteredVendors = computed(() => {
  let filtered = vendors.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(vendor => 
      vendor.name.toLowerCase().includes(query) ||
      vendor.contactPerson.toLowerCase().includes(query) ||
      vendor.vendorId.toLowerCase().includes(query)
    )
  }
  
  if (selectedStatus.value) {
    filtered = filtered.filter(vendor => vendor.status === selectedStatus.value)
  }
  
  if (selectedCategory.value) {
    filtered = filtered.filter(vendor => vendor.category === selectedCategory.value)
  }
  
  return filtered
})

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const editVendor = (vendor: any) => {
  editingVendor.value = vendor
  vendorForm.value = { ...vendor }
  showCreateModal.value = true
}

const viewInvoices = (vendor: any) => {
  console.log('Viewing invoices for vendor:', vendor.name)
}

const viewPayments = (vendor: any) => {
  console.log('Viewing payments for vendor:', vendor.name)
}

const saveVendor = () => {
  if (editingVendor.value) {
    const index = vendors.value.findIndex(v => v.id === editingVendor.value.id)
    if (index > -1) {
      vendors.value[index] = { ...vendorForm.value, id: editingVendor.value.id }
    }
  } else {
    const newVendor = {
      ...vendorForm.value,
      id: Math.max(...vendors.value.map(v => v.id)) + 1,
      vendorId: `V${String(Math.max(...vendors.value.map(v => parseInt(v.vendorId.slice(1)))) + 1).padStart(3, '0')}`,
      outstanding: 0
    }
    vendors.value.push(newVendor)
  }
  closeModal()
}

const closeModal = () => {
  showCreateModal.value = false
  editingVendor.value = null
  vendorForm.value = {
    name: '',
    category: '',
    contactPerson: '',
    email: '',
    phone: '',
    taxId: '',
    address: '',
    paymentTerms: 'net30',
    status: 'active'
  }
}
</script>

<style scoped>
.vendors {
  min-height: 100vh;
  background: #f5f7fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e0e6ed;
  padding: 20px 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.header-content p {
  color: #718096;
  margin: 5px 0 0 0;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #1976D2;
  color: white;
}

.btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-outline {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #4a5568;
}

.filters-section {
  margin: 20px 0;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.filter-input {
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
}

.table-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.table-header h3 {
  margin: 0;
  color: #2d3748;
}

.table-actions {
  display: flex;
  gap: 12px;
}

.vendors-table {
  width: 100%;
  border-collapse: collapse;
}

.vendors-table th,
.vendors-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f7fafc;
}

.vendors-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #4a5568;
}

.vendor-id {
  font-family: monospace;
  font-weight: 600;
  color: #2d3748;
}

.vendor-name {
  font-weight: 500;
  color: #2d3748;
}

.contact-info {
  font-size: 0.9rem;
}

.contact-details {
  color: #718096;
  font-size: 0.8rem;
}

.amount {
  text-align: right;
  font-weight: 500;
  color: #e53e3e;
}

.category-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.category-badge.supplier {
  background: #e3f2fd;
  color: #1565c0;
}

.category-badge.contractor {
  background: #fff3e0;
  color: #ef6c00;
}

.category-badge.service {
  background: #f3e5f5;
  color: #7b1fa2;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.active {
  background: #c6f6d5;
  color: #22543d;
}

.status-badge.inactive {
  background: #fed7d7;
  color: #742a2a;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.btn-icon:hover {
  background: #f7fafc;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.vendor-form {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #4a5568;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>