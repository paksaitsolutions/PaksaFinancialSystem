<template>
  <div class="vendors-advanced">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>Vendor Management</h1>
            <p>Advanced vendor management with AI insights and analytics</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-outline" @click="showBulkActions = !showBulkActions">
              Bulk Actions
            </button>
            <Button label="Export" icon="pi pi-download" class="p-button-outlined p-button-secondary" @click="showExportDialog = true" :disabled="vendors.length === 0" />
            <ExportDialog 
              v-model:visible="showExportDialog"
              :data="exportData"
              :columns="exportColumns"
              title="Export Vendors"
              description="Select the format and scope for exporting vendor data"
              @export="handleExport"
            />
            <button class="btn btn-primary" @click="showCreateModal = true">
              + Add Vendor
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Insights Panel -->
    <div class="container">
      <div class="ai-insights-panel" v-if="aiInsights.length > 0">
        <div class="insights-header">
          <h3>🤖 AI Insights</h3>
          <button class="btn-close" @click="dismissInsights">×</button>
        </div>
        <div class="insights-grid">
          <div v-for="insight in aiInsights" :key="insight.id" class="insight-card" :class="insight.priority">
            <div class="insight-icon">{{ insight.icon }}</div>
            <div class="insight-content">
              <h4>{{ insight.title }}</h4>
              <p>{{ insight.message }}</p>
              <button v-if="insight.action" class="btn-action" @click="executeInsightAction(insight)">
                {{ insight.actionText }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Advanced Filters -->
      <div class="filters-section">
        <div class="filters-header">
          <h3>Filters & Search</h3>
          <button class="btn btn-outline" @click="resetFilters">Reset</button>
        </div>
        <div class="filters-grid">
          <div class="filter-group">
            <label>Search</label>
            <input type="text" v-model="filters.search" placeholder="Search vendors..." class="filter-input">
          </div>
          <div class="filter-group">
            <label>Category</label>
            <select v-model="filters.category" class="filter-input">
              <option value="">All Categories</option>
              <option value="supplier">Supplier</option>
              <option value="contractor">Contractor</option>
              <option value="service_provider">Service Provider</option>
              <option value="consultant">Consultant</option>
              <option value="utility">Utility</option>
              <option value="government">Government</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Status</label>
            <select v-model="filters.status" class="filter-input">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="suspended">Suspended</option>
              <option value="pending_approval">Pending Approval</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Risk Level</label>
            <select v-model="filters.riskLevel" class="filter-input">
              <option value="">All Risk Levels</option>
              <option value="low">Low Risk</option>
              <option value="medium">Medium Risk</option>
              <option value="high">High Risk</option>
              <option value="critical">Critical Risk</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Payment Terms</label>
            <select v-model="filters.paymentTerms" class="filter-input">
              <option value="">All Terms</option>
              <option value="net15">Net 15</option>
              <option value="net30">Net 30</option>
              <option value="net45">Net 45</option>
              <option value="net60">Net 60</option>
              <option value="due_on_receipt">Due on Receipt</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Country</label>
            <select v-model="filters.country" class="filter-input">
              <option value="">All Countries</option>
              <option value="US">United States</option>
              <option value="CA">Canada</option>
              <option value="UK">United Kingdom</option>
              <option value="PK">Pakistan</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Bulk Actions Panel -->
      <div v-if="showBulkActions" class="bulk-actions-panel">
        <div class="bulk-header">
          <h3>Bulk Actions ({{ selectedVendors.length }} selected)</h3>
          <button class="btn-close" @click="showBulkActions = false">×</button>
        </div>
        <div class="bulk-actions">
          <button class="btn btn-outline" @click="bulkUpdateStatus" :disabled="selectedVendors.length === 0">
            Update Status
          </button>
          <button class="btn btn-outline" @click="bulkUpdateRisk" :disabled="selectedVendors.length === 0">
            Update Risk Level
          </button>
          <button class="btn btn-outline" @click="bulkExport" :disabled="selectedVendors.length === 0">
            Export Selected
          </button>
          <button class="btn btn-danger" @click="bulkDelete" :disabled="selectedVendors.length === 0">
            Delete Selected
          </button>
        </div>
      </div>

      <!-- Vendors Table -->
      <div class="table-card">
        <div class="table-header">
          <div class="table-title">
            <h3>Vendors ({{ filteredVendors.length }})</h3>
            <div class="view-options">
              <button class="view-btn" :class="{ active: viewMode === 'table' }" @click="viewMode = 'table'">
                📋 Table
              </button>
              <button class="view-btn" :class="{ active: viewMode === 'cards' }" @click="viewMode = 'cards'">
                🗃️ Cards
              </button>
            </div>
          </div>
          <div class="table-actions">
            <select v-model="sortBy" class="sort-select">
              <option value="name">Sort by Name</option>
              <option value="created_at">Sort by Date</option>
              <option value="outstanding_balance">Sort by Balance</option>
              <option value="risk_score">Sort by Risk Score</option>
            </select>
          </div>
        </div>
        
        <!-- Table View -->
        <div v-if="viewMode === 'table'" class="table-container">
          <table class="vendors-table">
            <thead>
              <tr>
                <th>
                  <input type="checkbox" @change="toggleSelectAll" :checked="allSelected">
                </th>
                <th>Vendor</th>
                <th>Category</th>
                <th>Contact</th>
                <th>Outstanding</th>
                <th>Risk Score</th>
                <th>Performance</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="vendor in paginatedVendors" :key="vendor.id" :class="{ selected: selectedVendors.includes(vendor.id) }">
                <td>
                  <input type="checkbox" :value="vendor.id" v-model="selectedVendors">
                </td>
                <td class="vendor-info">
                  <div class="vendor-main">
                    <span class="vendor-name">{{ vendor.name }}</span>
                    <span class="vendor-id">{{ vendor.vendorId }}</span>
                  </div>
                  <div class="vendor-meta">
                    <span class="location">{{ vendor.city }}, {{ vendor.country }}</span>
                  </div>
                </td>
                <td>
                  <span class="category-badge" :class="vendor.category">
                    {{ formatCategory(vendor.category) }}
                  </span>
                </td>
                <td class="contact-info">
                  <div>{{ vendor.contactPerson }}</div>
                  <div class="contact-details">{{ vendor.email }}</div>
                  <div class="contact-details">{{ vendor.phone }}</div>
                </td>
                <td class="amount" :class="{ 'high-amount': vendor.outstanding > 50000 }">
                  {{ formatCurrency(vendor.outstanding) }}
                </td>
                <td class="risk-score">
                  <div class="score-container">
                    <div class="score-bar">
                      <div class="score-fill" :style="{ width: vendor.aiRiskScore + '%' }" :class="getRiskClass(vendor.aiRiskScore)"></div>
                    </div>
                    <span class="score-text">{{ vendor.aiRiskScore }}%</span>
                  </div>
                </td>
                <td class="performance">
                  <div class="performance-indicators">
                    <div class="indicator" :class="getPerformanceClass(vendor.reliabilityScore)">
                      <span class="indicator-label">Reliability</span>
                      <span class="indicator-value">{{ vendor.reliabilityScore }}%</span>
                    </div>
                    <div class="indicator" :class="getPerformanceClass(vendor.paymentBehaviorScore)">
                      <span class="indicator-label">Payment</span>
                      <span class="indicator-value">{{ vendor.paymentBehaviorScore }}%</span>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="status-badge" :class="vendor.status">
                    {{ formatStatus(vendor.status) }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="btn-icon" @click="viewVendor(vendor)" title="View Details">👁️</button>
                    <button class="btn-icon" @click="editVendor(vendor)" title="Edit">✏️</button>
                    <button class="btn-icon" @click="viewAnalytics(vendor)" title="Analytics">📊</button>
                    <button class="btn-icon" @click="viewContracts(vendor)" title="Contracts">📄</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Cards View -->
        <div v-if="viewMode === 'cards'" class="cards-container">
          <div v-for="vendor in paginatedVendors" :key="vendor.id" class="vendor-card" :class="{ selected: selectedVendors.includes(vendor.id) }">
            <div class="card-header">
              <input type="checkbox" :value="vendor.id" v-model="selectedVendors">
              <div class="vendor-title">
                <h4>{{ vendor.name }}</h4>
                <span class="vendor-id">{{ vendor.vendorId }}</span>
              </div>
              <span class="status-badge" :class="vendor.status">{{ formatStatus(vendor.status) }}</span>
            </div>
            <div class="card-body">
              <div class="card-row">
                <span class="label">Category:</span>
                <span class="category-badge" :class="vendor.category">{{ formatCategory(vendor.category) }}</span>
              </div>
              <div class="card-row">
                <span class="label">Contact:</span>
                <span>{{ vendor.contactPerson }}</span>
              </div>
              <div class="card-row">
                <span class="label">Outstanding:</span>
                <span class="amount">{{ formatCurrency(vendor.outstanding) }}</span>
              </div>
              <div class="card-row">
                <span class="label">Risk Score:</span>
                <div class="risk-indicator" :class="getRiskClass(vendor.aiRiskScore)">
                  {{ vendor.aiRiskScore }}%
                </div>
              </div>
            </div>
            <div class="card-actions">
              <button class="btn btn-sm" @click="viewVendor(vendor)">View</button>
              <button class="btn btn-sm" @click="editVendor(vendor)">Edit</button>
              <button class="btn btn-sm" @click="viewAnalytics(vendor)">Analytics</button>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="pagination">
          <button class="btn btn-outline" @click="previousPage" :disabled="currentPage === 1">
            Previous
          </button>
          <span class="page-info">
            Page {{ currentPage }} of {{ totalPages }} ({{ filteredVendors.length }} vendors)
          </span>
          <button class="btn btn-outline" @click="nextPage" :disabled="currentPage === totalPages">
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Advanced Vendor Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content advanced-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingVendor ? 'Edit' : 'Create' }} Vendor</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        
        <div class="modal-tabs">
          <button class="tab-btn" :class="{ active: activeTab === 'basic' }" @click="activeTab = 'basic'">
            Basic Info
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'contact' }" @click="activeTab = 'contact'">
            Contact & Address
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'financial' }" @click="activeTab = 'financial'">
            Financial
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'compliance' }" @click="activeTab = 'compliance'">
            Compliance
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'ai' }" @click="activeTab = 'ai'">
            AI Insights
          </button>
        </div>
        
        <form @submit.prevent="saveVendor" class="vendor-form">
          <!-- Basic Info Tab -->
          <div v-if="activeTab === 'basic'" class="tab-content">
            <div class="form-grid">
              <div class="form-group">
                <label>Vendor Name *</label>
                <input type="text" v-model="vendorForm.name" required class="form-input">
              </div>
              <div class="form-group">
                <label>Legal Name</label>
                <input type="text" v-model="vendorForm.legalName" class="form-input">
              </div>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>Category *</label>
                <select v-model="vendorForm.category" required class="form-input">
                  <option value="">Select Category</option>
                  <option value="supplier">Supplier</option>
                  <option value="contractor">Contractor</option>
                  <option value="service_provider">Service Provider</option>
                  <option value="consultant">Consultant</option>
                  <option value="utility">Utility</option>
                  <option value="government">Government</option>
                </select>
              </div>
              <div class="form-group">
                <label>Subcategory</label>
                <input type="text" v-model="vendorForm.subcategory" class="form-input">
              </div>
            </div>
            <div class="form-group">
              <label>Website</label>
              <input type="url" v-model="vendorForm.website" class="form-input">
            </div>
            <div class="form-group">
              <label>Tags</label>
              <div class="tags-input">
                <span v-for="tag in vendorForm.tags" :key="tag" class="tag">
                  {{ tag }}
                  <button type="button" @click="removeTag(tag)">×</button>
                </span>
                <input type="text" @keyup.enter="addTag" placeholder="Add tag..." class="tag-input">
              </div>
            </div>
          </div>

          <!-- Contact & Address Tab -->
          <div v-if="activeTab === 'contact'" class="tab-content">
            <h4>Contact Information</h4>
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
                <label>Mobile</label>
                <input type="tel" v-model="vendorForm.mobile" class="form-input">
              </div>
            </div>
            
            <h4>Address Information</h4>
            <div class="form-group">
              <label>Billing Address</label>
              <textarea v-model="vendorForm.billingAddress" class="form-input" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label>Shipping Address</label>
              <textarea v-model="vendorForm.shippingAddress" class="form-input" rows="3"></textarea>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>City</label>
                <input type="text" v-model="vendorForm.city" class="form-input">
              </div>
              <div class="form-group">
                <label>State/Province</label>
                <input type="text" v-model="vendorForm.state" class="form-input">
              </div>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>Country</label>
                <select v-model="vendorForm.country" class="form-input">
                  <option value="">Select Country</option>
                  <option value="US">United States</option>
                  <option value="CA">Canada</option>
                  <option value="UK">United Kingdom</option>
                  <option value="PK">Pakistan</option>
                </select>
              </div>
              <div class="form-group">
                <label>Postal Code</label>
                <input type="text" v-model="vendorForm.postalCode" class="form-input">
              </div>
            </div>
          </div>

          <!-- Financial Tab -->
          <div v-if="activeTab === 'financial'" class="tab-content">
            <h4>Payment Terms</h4>
            <div class="form-grid">
              <div class="form-group">
                <label>Payment Terms</label>
                <select v-model="vendorForm.paymentTerms" class="form-input">
                  <option value="net15">Net 15</option>
                  <option value="net30">Net 30</option>
                  <option value="net45">Net 45</option>
                  <option value="net60">Net 60</option>
                  <option value="due_on_receipt">Due on Receipt</option>
                </select>
              </div>
              <div class="form-group">
                <label>Currency</label>
                <select v-model="vendorForm.currencyCode" class="form-input">
                  <option value="USD">USD - US Dollar</option>
                  <option value="EUR">EUR - Euro</option>
                  <option value="GBP">GBP - British Pound</option>
                  <option value="PKR">PKR - Pakistani Rupee</option>
                </select>
              </div>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>Credit Limit</label>
                <input type="number" v-model="vendorForm.creditLimit" class="form-input" step="0.01">
              </div>
              <div class="form-group">
                <label>Discount Percentage</label>
                <input type="number" v-model="vendorForm.discountPercentage" class="form-input" step="0.01" max="100">
              </div>
            </div>
            
            <h4>Banking Information</h4>
            <div class="form-grid">
              <div class="form-group">
                <label>Bank Name</label>
                <input type="text" v-model="vendorForm.bankName" class="form-input">
              </div>
              <div class="form-group">
                <label>Account Number</label>
                <input type="text" v-model="vendorForm.bankAccountNumber" class="form-input">
              </div>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>Routing Number</label>
                <input type="text" v-model="vendorForm.bankRoutingNumber" class="form-input">
              </div>
              <div class="form-group">
                <label>SWIFT Code</label>
                <input type="text" v-model="vendorForm.swiftCode" class="form-input">
              </div>
            </div>
          </div>

          <!-- Compliance Tab -->
          <div v-if="activeTab === 'compliance'" class="tab-content">
            <h4>Tax & Legal Information</h4>
            <div class="form-grid">
              <div class="form-group">
                <label>Tax ID</label>
                <input type="text" v-model="vendorForm.taxId" class="form-input">
              </div>
              <div class="form-group">
                <label>VAT Number</label>
                <input type="text" v-model="vendorForm.vatNumber" class="form-input">
              </div>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>Registration Number</label>
                <input type="text" v-model="vendorForm.registrationNumber" class="form-input">
              </div>
              <div class="form-group">
                <label>Business License</label>
                <input type="text" v-model="vendorForm.businessLicense" class="form-input">
              </div>
            </div>
            
            <h4>Risk & Compliance</h4>
            <div class="form-grid">
              <div class="form-group">
                <label>Risk Level</label>
                <select v-model="vendorForm.riskLevel" class="form-input">
                  <option value="low">Low Risk</option>
                  <option value="medium">Medium Risk</option>
                  <option value="high">High Risk</option>
                  <option value="critical">Critical Risk</option>
                </select>
              </div>
              <div class="form-group">
                <label>Status</label>
                <select v-model="vendorForm.status" class="form-input">
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="suspended">Suspended</option>
                  <option value="pending_approval">Pending Approval</option>
                </select>
              </div>
            </div>
            <div class="form-grid">
              <div class="form-group">
                <label>Last Audit Date</label>
                <input type="date" v-model="vendorForm.lastAuditDate" class="form-input">
              </div>
              <div class="form-group">
                <label>Next Audit Date</label>
                <input type="date" v-model="vendorForm.nextAuditDate" class="form-input">
              </div>
            </div>
          </div>

          <!-- AI Insights Tab -->
          <div v-if="activeTab === 'ai'" class="tab-content">
            <div class="ai-section">
              <h4>🤖 AI Risk Assessment</h4>
              <div class="ai-scores">
                <div class="score-card">
                  <div class="score-label">Overall Risk Score</div>
                  <div class="score-value risk" :class="getRiskClass(vendorForm.aiRiskScore)">
                    {{ vendorForm.aiRiskScore || 0 }}%
                  </div>
                </div>
                <div class="score-card">
                  <div class="score-label">Payment Behavior</div>
                  <div class="score-value" :class="getPerformanceClass(vendorForm.paymentBehaviorScore)">
                    {{ vendorForm.paymentBehaviorScore || 0 }}%
                  </div>
                </div>
                <div class="score-card">
                  <div class="score-label">Reliability Score</div>
                  <div class="score-value" :class="getPerformanceClass(vendorForm.reliabilityScore)">
                    {{ vendorForm.reliabilityScore || 0 }}%
                  </div>
                </div>
              </div>
              
              <div class="ai-recommendations" v-if="aiRecommendations.length > 0">
                <h5>AI Recommendations</h5>
                <div class="recommendations-list">
                  <div v-for="rec in aiRecommendations" :key="rec.id" class="recommendation-item" :class="rec.priority">
                    <div class="rec-icon">{{ rec.icon }}</div>
                    <div class="rec-content">
                      <div class="rec-title">{{ rec.title }}</div>
                      <div class="rec-message">{{ rec.message }}</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <button type="button" class="btn btn-outline" @click="runAIAnalysis">
                🔄 Run AI Analysis
              </button>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Vendor</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Snackbar -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ExportDialog from '@/components/common/ExportDialog.vue'
import { vendorsApi } from '@/services/api'
import { useLoadingState } from '@/composables/useStateManagement'

// Data
const router = useRouter()
const { setLoading, setError } = useLoadingState()
const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

const showSnackbar = (text: string, color = 'success') => {
  snackbarText.value = text
  snackbarColor.value = color
  snackbar.value = true
}

// Reactive data
const vendors = ref([])
const showCreateModal = ref(false)
const showExportDialog = ref(false)
const isExporting = ref(false)
const editingVendor = ref<boolean | null>(null)
const activeTab = ref('basic')
const viewMode = ref('table')
const currentPage = ref(1)
const itemsPerPage = ref(20)
const selectedVendors = ref([])

// Export functionality
const exportColumns = [
  { field: 'vendorId', header: 'Vendor ID' },
  { field: 'name', header: 'Name' },
  { field: 'category', header: 'Category' },
  { field: 'contactPerson', header: 'Contact Person' },
  { field: 'email', header: 'Email' },
  { field: 'phone', header: 'Phone' },
  { field: 'outstanding', header: 'Outstanding Balance' },
  { field: 'status', header: 'Status' },
  { field: 'riskLevel', header: 'Risk Level' },
  { field: 'lastOrderDate', header: 'Last Order' },
  { field: 'totalSpend', header: 'Total Spend' },
  { field: 'paymentTerms', header: 'Payment Terms' },
  { field: 'taxId', header: 'Tax ID' },
  { field: 'createdAt', header: 'Date Added' },
  { field: 'reliabilityScore', header: 'Reliability Score' }
]

const exportData = computed(() => {
  return vendors.value.map(vendor => ({
    ...vendor,
    outstanding: formatCurrency(vendor.outstanding || 0),
    totalSpend: formatCurrency(vendor.totalSpend || 0),
    lastOrderDate: vendor.lastOrderDate ? new Date(vendor.lastOrderDate).toLocaleDateString() : 'N/A',
    createdAt: vendor.createdAt ? new Date(vendor.createdAt).toLocaleDateString() : 'N/A',
    riskLevel: vendor.riskLevel?.charAt(0).toUpperCase() + vendor.riskLevel?.slice(1) || 'Medium'
  }))
})

// Fetch vendors from API
const fetchVendors = async () => {
  try {
    setLoading(true)
    const response = await vendorsApi.getAll()
    vendors.value = response.items || []
  } catch (error) {
    console.error('Error fetching vendors:', error)
    setError('Failed to load vendors')
  } finally {
    setLoading(false)
  }
}

// Load vendors on mount
onMounted(() => {
  fetchVendors()
})

const handleExport = async (format: string, options: any = {}) => {
  isExporting.value = true
  
  try {
    let dataToExport = exportData.value
    
    // Apply pagination if needed
    if (options.exportScope === 'currentPage') {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      dataToExport = dataToExport.slice(start, end)
    }
    
    // In a real app, this would be an API call
    // For now, we'll simulate a delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    showSnackbar(`Vendors exported successfully as ${format.toUpperCase()}`, 'success')
    
    return { success: true, data: dataToExport }
  } catch (error) {
    console.error('Export error:', error)
    showSnackbar('Failed to export vendors. Please try again.', 'error')
    return { success: false, error }
  } finally {
    isExporting.value = false
  }
}

// Legacy export function (keep for backward compatibility)
const exportVendors = () => {
  const csvData = exportData.value.map(vendor => ({
    'Vendor ID': vendor.vendorId,
    'Name': vendor.name,
    'Category': vendor.category,
    'Contact': vendor.contactPerson,
    'Email': vendor.email,
    'Phone': vendor.phone,
    'Outstanding': vendor.outstanding,
    'Status': vendor.status,
    'Risk Level': vendor.riskLevel,
    'Last Order': vendor.lastOrderDate,
    'Total Spend': vendor.totalSpend,
    'Payment Terms': vendor.paymentTerms,
    'Tax ID': vendor.taxId,
    'Date Added': vendor.createdAt,
    'Reliability Score': vendor.reliabilityScore
  }))
  
  const csv = convertToCSV(csvData)
  downloadCSV(csv, 'vendors-export.csv')
}

// ... rest of the code remains the same ...
</script>