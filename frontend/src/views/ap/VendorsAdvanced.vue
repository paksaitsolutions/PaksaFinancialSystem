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
            <button class="btn btn-secondary" @click="exportVendors">
              Export
            </button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive data
const showCreateModal = ref(false)
const showBulkActions = ref(false)
const editingVendor = ref(null)
const activeTab = ref('basic')
const viewMode = ref('table')
const currentPage = ref(1)
const itemsPerPage = ref(20)
const selectedVendors = ref([])
const sortBy = ref('name')

// Filters
const filters = ref({
  search: '',
  category: '',
  status: '',
  riskLevel: '',
  paymentTerms: '',
  country: ''
})

// AI Insights
const aiInsights = ref([
  {
    id: 1,
    icon: '⚠️',
    title: 'High Risk Vendor Alert',
    message: 'ABC Corp has exceeded credit limit by $15,000',
    priority: 'high',
    action: 'review_vendor',
    actionText: 'Review Now'
  },
  {
    id: 2,
    icon: '💡',
    title: 'Payment Optimization',
    message: '5 vendors offer early payment discounts this week',
    priority: 'medium',
    action: 'view_discounts',
    actionText: 'View Opportunities'
  }
])

const aiRecommendations = ref([])

// Form data
const vendorForm = ref({
  name: '',
  legalName: '',
  category: '',
  subcategory: '',
  contactPerson: '',
  email: '',
  phone: '',
  mobile: '',
  website: '',
  billingAddress: '',
  shippingAddress: '',
  city: '',
  state: '',
  country: '',
  postalCode: '',
  taxId: '',
  vatNumber: '',
  registrationNumber: '',
  businessLicense: '',
  paymentTerms: 'net30',
  creditLimit: 0,
  discountPercentage: 0,
  currencyCode: 'USD',
  bankName: '',
  bankAccountNumber: '',
  bankRoutingNumber: '',
  swiftCode: '',
  riskLevel: 'low',
  status: 'active',
  lastAuditDate: '',
  nextAuditDate: '',
  tags: [],
  aiRiskScore: 0,
  paymentBehaviorScore: 0,
  reliabilityScore: 0
})

// Mock vendor data
const vendors = ref([
  {
    id: 1,
    vendorId: 'V001',
    name: 'ABC Supplies Inc.',
    legalName: 'ABC Supplies Incorporated',
    category: 'supplier',
    contactPerson: 'John Smith',
    email: 'john@abcsupplies.com',
    phone: '555-0123',
    city: 'New York',
    country: 'US',
    outstanding: 15000,
    status: 'active',
    aiRiskScore: 25,
    paymentBehaviorScore: 85,
    reliabilityScore: 90
  },
  {
    id: 2,
    vendorId: 'V002',
    name: 'Tech Solutions LLC',
    category: 'service_provider',
    contactPerson: 'Sarah Johnson',
    email: 'sarah@techsolutions.com',
    phone: '555-0456',
    city: 'San Francisco',
    country: 'US',
    outstanding: 8500,
    status: 'active',
    aiRiskScore: 15,
    paymentBehaviorScore: 95,
    reliabilityScore: 88
  }
])

// Computed properties
const filteredVendors = computed(() => {
  let filtered = vendors.value
  
  if (filters.value.search) {
    const query = filters.value.search.toLowerCase()
    filtered = filtered.filter(vendor => 
      vendor.name.toLowerCase().includes(query) ||
      vendor.contactPerson.toLowerCase().includes(query) ||
      vendor.vendorId.toLowerCase().includes(query)
    )
  }
  
  if (filters.value.category) {
    filtered = filtered.filter(vendor => vendor.category === filters.value.category)
  }
  
  if (filters.value.status) {
    filtered = filtered.filter(vendor => vendor.status === filters.value.status)
  }
  
  // Sort
  filtered.sort((a, b) => {
    if (sortBy.value === 'name') return a.name.localeCompare(b.name)
    if (sortBy.value === 'outstanding_balance') return b.outstanding - a.outstanding
    if (sortBy.value === 'risk_score') return b.aiRiskScore - a.aiRiskScore
    return 0
  })
  
  return filtered
})

const paginatedVendors = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredVendors.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredVendors.value.length / itemsPerPage.value)
})

const allSelected = computed(() => {
  return paginatedVendors.value.length > 0 && 
         paginatedVendors.value.every(vendor => selectedVendors.value.includes(vendor.id))
})

// Methods
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

const getRiskClass = (score: number) => {
  if (score >= 80) return 'critical'
  if (score >= 60) return 'high'
  if (score >= 40) return 'medium'
  return 'low'
}

const getPerformanceClass = (score: number) => {
  if (score >= 90) return 'excellent'
  if (score >= 75) return 'good'
  if (score >= 60) return 'average'
  return 'poor'
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedVendors.value = []
  } else {
    selectedVendors.value = paginatedVendors.value.map(vendor => vendor.id)
  }
}

const resetFilters = () => {
  filters.value = {
    search: '',
    category: '',
    status: '',
    riskLevel: '',
    paymentTerms: '',
    country: ''
  }
}

const previousPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const addTag = (event: Event) => {
  const input = event.target as HTMLInputElement
  const tag = input.value.trim()
  if (tag && !vendorForm.value.tags.includes(tag)) {
    vendorForm.value.tags.push(tag)
    input.value = ''
  }
}

const removeTag = (tag: string) => {
  const index = vendorForm.value.tags.indexOf(tag)
  if (index > -1) {
    vendorForm.value.tags.splice(index, 1)
  }
}

const runAIAnalysis = () => {
  // Simulate AI analysis
  vendorForm.value.aiRiskScore = Math.floor(Math.random() * 100)
  vendorForm.value.paymentBehaviorScore = Math.floor(Math.random() * 100)
  vendorForm.value.reliabilityScore = Math.floor(Math.random() * 100)
  
  aiRecommendations.value = [
    {
      id: 1,
      icon: '💡',
      title: 'Credit Limit Recommendation',
      message: 'Based on payment history, consider increasing credit limit to $25,000',
      priority: 'medium'
    }
  ]
}

const dismissInsights = () => {
  aiInsights.value = []
}

const executeInsightAction = (insight: any) => {
  switch (insight.action) {
    case 'review_vendor':
      const vendor = vendors.value.find(v => v.outstanding > 50000)
      if (vendor) viewVendor(vendor)
      break
    case 'view_discounts':
      // Navigate to payments with discount filter
      const router = useRouter()
      router.push({ path: '/ap/payments', query: { filter: 'discounts' } })
      break
    default:
      alert('Action executed: ' + insight.title)
  }
}

const editVendor = (vendor: any) => {
  editingVendor.value = vendor
  vendorForm.value = { ...vendor }
  activeTab.value = 'basic'
  showCreateModal.value = true
}

const viewVendor = (vendor: any) => {
  // Navigate to vendor detail view
  window.open(`/ap/vendors/${vendor.id}`, '_blank')
}

const viewAnalytics = (vendor: any) => {
  // Navigate to analytics with vendor filter
  const router = useRouter()
  router.push({ path: '/ap/analytics', query: { vendor: vendor.id } })
}

const viewContracts = (vendor: any) => {
  // Navigate to contracts view
  window.open(`/ap/vendors/${vendor.id}/contracts`, '_blank')
}

const saveVendor = () => {
  console.log('Saving vendor:', vendorForm.value)
  closeModal()
}

const closeModal = () => {
  showCreateModal.value = false
  editingVendor.value = null
  activeTab.value = 'basic'
  vendorForm.value = {
    name: '',
    legalName: '',
    category: '',
    subcategory: '',
    contactPerson: '',
    email: '',
    phone: '',
    mobile: '',
    website: '',
    billingAddress: '',
    shippingAddress: '',
    city: '',
    state: '',
    country: '',
    postalCode: '',
    taxId: '',
    vatNumber: '',
    registrationNumber: '',
    businessLicense: '',
    paymentTerms: 'net30',
    creditLimit: 0,
    discountPercentage: 0,
    currencyCode: 'USD',
    bankName: '',
    bankAccountNumber: '',
    bankRoutingNumber: '',
    swiftCode: '',
    riskLevel: 'low',
    status: 'active',
    lastAuditDate: '',
    nextAuditDate: '',
    tags: [],
    aiRiskScore: 0,
    paymentBehaviorScore: 0,
    reliabilityScore: 0
  }
}

const exportVendors = () => {
  // Create CSV export
  const csvData = vendors.value.map(vendor => ({
    'Vendor ID': vendor.vendorId,
    'Name': vendor.name,
    'Category': vendor.category,
    'Contact': vendor.contactPerson,
    'Email': vendor.email,
    'Outstanding': vendor.outstanding,
    'Status': vendor.status
  }))
  
  const csv = convertToCSV(csvData)
  downloadCSV(csv, 'vendors-export.csv')
}

const bulkUpdateStatus = () => {
  const newStatus = prompt('Enter new status (active/inactive/suspended):')
  if (newStatus && ['active', 'inactive', 'suspended'].includes(newStatus)) {
    selectedVendors.value.forEach(vendorId => {
      const vendor = vendors.value.find(v => v.id === vendorId)
      if (vendor) vendor.status = newStatus
    })
    selectedVendors.value = []
    alert(`Updated ${selectedVendors.value.length} vendors`)
  }
}

const bulkUpdateRisk = () => {
  const newRisk = prompt('Enter new risk level (low/medium/high/critical):')
  if (newRisk && ['low', 'medium', 'high', 'critical'].includes(newRisk)) {
    selectedVendors.value.forEach(vendorId => {
      const vendor = vendors.value.find(v => v.id === vendorId)
      if (vendor) vendor.riskLevel = newRisk
    })
    selectedVendors.value = []
    alert(`Updated risk level for ${selectedVendors.value.length} vendors`)
  }
}

const bulkExport = () => {
  const selectedData = vendors.value.filter(v => selectedVendors.value.includes(v.id))
  const csv = convertToCSV(selectedData)
  downloadCSV(csv, 'selected-vendors.csv')
}

const bulkDelete = () => {
  if (confirm(`Delete ${selectedVendors.value.length} selected vendors?`)) {
    vendors.value = vendors.value.filter(v => !selectedVendors.value.includes(v.id))
    selectedVendors.value = []
    alert('Selected vendors deleted successfully')
  }
}

// Utility functions
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

onMounted(() => {
  // Load vendor data from API
  // loadVendors()
})
</script>