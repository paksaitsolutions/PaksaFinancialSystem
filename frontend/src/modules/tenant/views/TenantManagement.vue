<template>
  <div class="tenant-management">
    <!-- Header Section -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="text-2xl font-semibold text-900 m-0">Company Management</h2>
        <p class="text-600 mt-1 mb-0">Manage multi-tenant companies and their configurations</p>
      </div>
      <div class="flex gap-2">
        <Button 
          label="Company Selector" 
          icon="pi pi-building" 
          severity="secondary" 
          outlined 
          @click="showCompanySelector = true"
        />
        <Button 
          label="Register New Company" 
          icon="pi pi-plus" 
          @click="showAddCompany = true"
        />
      </div>
    </div>

    <!-- Current Active Company -->
    <Card class="mb-4" v-if="activeCompany">
      <template #title>
        <div class="flex align-items-center gap-3">
          <div class="company-logo">
            <img 
              v-if="activeCompany.logo" 
              :src="activeCompany.logo" 
              :alt="activeCompany.name" 
              class="w-3rem h-3rem border-circle"
            />
            <div v-else class="w-3rem h-3rem border-circle bg-primary flex align-items-center justify-content-center">
              <i class="pi pi-building text-white text-xl"></i>
            </div>
          </div>
          <div>
            <h3 class="m-0 text-primary">{{ activeCompany.name }}</h3>
            <p class="text-600 m-0 text-sm">Currently Active Company</p>
          </div>
          <Tag :value="activeCompany.status" :severity="getStatusSeverity(activeCompany.status)" class="ml-auto" />
        </div>
      </template>
      <template #content>
        <div class="flex flex-wrap gap-3">
          <div class="company-stat-card flex-1 min-w-15rem p-3 border-round bg-blue-50 border-1 border-blue-200">
            <div class="flex align-items-center gap-3">
              <div class="w-3rem h-3rem border-circle bg-blue-500 flex align-items-center justify-content-center">
                <i class="pi pi-users text-white text-xl"></i>
              </div>
              <div>
                <div class="text-2xl font-bold text-900">{{ activeCompany.users || 0 }}</div>
                <div class="text-600 text-sm">Active Users</div>
              </div>
            </div>
          </div>
          <div class="company-stat-card flex-1 min-w-15rem p-3 border-round bg-green-50 border-1 border-green-200">
            <div class="flex align-items-center gap-3">
              <div class="w-3rem h-3rem border-circle bg-green-500 flex align-items-center justify-content-center">
                <i class="pi pi-star text-white text-xl"></i>
              </div>
              <div>
                <div class="text-2xl font-bold text-900">{{ activeCompany.plan }}</div>
                <div class="text-600 text-sm">Subscription Plan</div>
              </div>
            </div>
          </div>
          <div class="company-stat-card flex-1 min-w-15rem p-3 border-round bg-purple-50 border-1 border-purple-200">
            <div class="flex align-items-center gap-3">
              <div class="w-3rem h-3rem border-circle bg-purple-500 flex align-items-center justify-content-center">
                <i class="pi pi-globe text-white text-xl"></i>
              </div>
              <div>
                <div class="text-lg font-bold text-900">{{ activeCompany.domain }}</div>
                <div class="text-600 text-sm">Domain</div>
              </div>
            </div>
          </div>
          <div class="company-stat-card flex-1 min-w-15rem p-3 border-round bg-orange-50 border-1 border-orange-200">
            <div class="flex align-items-center gap-3">
              <div class="w-3rem h-3rem border-circle bg-orange-500 flex align-items-center justify-content-center">
                <i class="pi pi-calendar text-white text-xl"></i>
              </div>
              <div>
                <div class="text-2xl font-bold text-900">{{ formatDate(activeCompany.createdAt) }}</div>
                <div class="text-600 text-sm">Created</div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Companies List -->
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <span>All Companies</span>
          <div class="flex gap-2">
            <InputText 
              v-model="searchTerm" 
              placeholder="Search companies..." 
              class="w-20rem"
            />
            <Dropdown 
              v-model="statusFilter" 
              :options="statusOptions" 
              optionLabel="label" 
              optionValue="value" 
              placeholder="Filter by Status"
              class="w-12rem"
            />
          </div>
        </div>
      </template>
      <template #content>
        <DataTable 
          :value="filteredCompanies" 
          :paginator="true" 
          :rows="10" 
          responsiveLayout="scroll"
          :loading="loading"
          dataKey="id"
        >
          <Column field="name" header="Company" sortable>
            <template #body="{ data }">
              <div class="flex align-items-center gap-2">
                <div class="company-logo-small">
                  <img 
                    v-if="data.logo" 
                    :src="data.logo" 
                    :alt="data.name" 
                    class="w-2rem h-2rem border-circle"
                  />
                  <div v-else class="w-2rem h-2rem border-circle bg-primary-100 flex align-items-center justify-content-center">
                    <i class="pi pi-building text-primary text-sm"></i>
                  </div>
                </div>
                <div>
                  <div class="font-semibold">{{ data.name }}</div>
                  <div class="text-sm text-600">{{ data.industry || 'General' }}</div>
                </div>
              </div>
            </template>
          </Column>
          <Column field="domain" header="Domain" sortable></Column>
          <Column field="plan" header="Plan" sortable>
            <template #body="{ data }">
              <Tag :value="data.plan" :severity="getPlanSeverity(data.plan)" />
            </template>
          </Column>
          <Column field="users" header="Users" sortable>
            <template #body="{ data }">
              <div class="text-center">
                <span class="font-semibold">{{ data.users || 0 }}</span>
                <span class="text-600"> / {{ data.maxUsers || 'Unlimited' }}</span>
              </div>
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column field="createdAt" header="Created" sortable>
            <template #body="{ data }">
              {{ formatDate(data.createdAt) }}
            </template>
          </Column>
          <Column header="Actions" :exportable="false">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button 
                  icon="pi pi-sign-in" 
                  class="p-button-text p-button-sm" 
                  v-tooltip="'Activate Company'"
                  @click="activateCompany(data)"
                  :disabled="data.id === activeCompany?.id"
                />
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-text p-button-sm" 
                  v-tooltip="'View Details'"
                  @click="viewCompany(data)"
                />
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-sm" 
                  v-tooltip="'Edit Company'"
                  @click="editCompany(data)"
                />
                <Button 
                  icon="pi pi-cog" 
                  class="p-button-text p-button-sm" 
                  v-tooltip="'Company Settings'"
                  @click="configureCompany(data)"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-danger" 
                  v-tooltip="'Delete Company'"
                  @click="confirmDelete(data)"
                  :disabled="data.id === activeCompany?.id"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Company Registration Dialog -->
    <Dialog 
      v-model:visible="showAddCompany" 
      header="Register New Company" 
      :style="{ width: '800px' }" 
      :modal="true"
      class="p-fluid"
    >
      <div class="grid">
        <!-- Company Information -->
        <div class="col-12">
          <h4 class="text-primary mb-3">Company Information</h4>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="companyName" class="font-semibold">Company Name *</label>
            <InputText 
              id="companyName" 
              v-model="newCompany.name" 
              class="w-full" 
              :class="{ 'p-invalid': !newCompany.name && submitted }"
              placeholder="Enter company name"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="companyCode" class="font-semibold">Company Code *</label>
            <InputText 
              id="companyCode" 
              v-model="newCompany.code" 
              class="w-full" 
              :class="{ 'p-invalid': !newCompany.code && submitted }"
              placeholder="e.g., ACME001"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="industry" class="font-semibold">Industry</label>
            <Dropdown 
              id="industry" 
              v-model="newCompany.industry" 
              :options="industries" 
              optionLabel="label" 
              optionValue="value"
              class="w-full" 
              placeholder="Select industry"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="companySize" class="font-semibold">Company Size</label>
            <Dropdown 
              id="companySize" 
              v-model="newCompany.size" 
              :options="companySizes" 
              optionLabel="label" 
              optionValue="value"
              class="w-full" 
              placeholder="Select company size"
            />
          </div>
        </div>
        
        <div class="col-12">
          <div class="field">
            <label for="companyAddress" class="font-semibold">Address</label>
            <Textarea 
              id="companyAddress" 
              v-model="newCompany.address" 
              rows="3" 
              class="w-full" 
              placeholder="Enter complete address"
            />
          </div>
        </div>
        
        <!-- Subscription & Configuration -->
        <div class="col-12">
          <h4 class="text-primary mb-3 mt-4">Subscription & Configuration</h4>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="subscriptionPlan" class="font-semibold">Subscription Plan *</label>
            <Dropdown 
              id="subscriptionPlan" 
              v-model="newCompany.plan" 
              :options="plans" 
              optionLabel="label" 
              optionValue="value"
              class="w-full" 
              :class="{ 'p-invalid': !newCompany.plan && submitted }"
              placeholder="Select plan"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="maxUsers" class="font-semibold">Maximum Users</label>
            <InputNumber 
              id="maxUsers" 
              v-model="newCompany.maxUsers" 
              class="w-full" 
              :min="1" 
              :max="1000"
              placeholder="Number of users"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="companyDomain" class="font-semibold">Subdomain</label>
            <div class="p-inputgroup">
              <InputText 
                id="companyDomain" 
                v-model="newCompany.subdomain" 
                placeholder="company-name"
              />
              <span class="p-inputgroup-addon">.paksa.com</span>
            </div>
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="timezone" class="font-semibold">Timezone</label>
            <Dropdown 
              id="timezone" 
              v-model="newCompany.timezone" 
              :options="timezones" 
              optionLabel="label" 
              optionValue="value"
              class="w-full" 
              placeholder="Select timezone"
              filter
            />
          </div>
        </div>
        
        <!-- Branding -->
        <div class="col-12">
          <h4 class="text-primary mb-3 mt-4">Branding & Customization</h4>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="primaryColor" class="font-semibold">Primary Color</label>
            <InputText 
              id="primaryColor" 
              v-model="newCompany.primaryColor" 
              class="w-full" 
              placeholder="#1976D2"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="logoUpload" class="font-semibold">Company Logo</label>
            <FileUpload 
              mode="basic" 
              name="logo" 
              :maxFileSize="1000000" 
              accept="image/*" 
              :auto="true" 
              chooseLabel="Choose Logo"
              class="w-full"
              @upload="onLogoUpload"
            />
          </div>
        </div>
        
        <!-- Admin User -->
        <div class="col-12">
          <h4 class="text-primary mb-3 mt-4">Administrator Account</h4>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="adminName" class="font-semibold">Admin Name *</label>
            <InputText 
              id="adminName" 
              v-model="newCompany.adminName" 
              class="w-full" 
              :class="{ 'p-invalid': !newCompany.adminName && submitted }"
              placeholder="Administrator full name"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="adminEmail" class="font-semibold">Admin Email *</label>
            <InputText 
              id="adminEmail" 
              v-model="newCompany.adminEmail" 
              class="w-full" 
              :class="{ 'p-invalid': !newCompany.adminEmail && submitted }"
              placeholder="admin@company.com"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="adminPassword" class="font-semibold">Admin Password *</label>
            <Password 
              id="adminPassword" 
              v-model="newCompany.adminPassword" 
              class="w-full" 
              :class="{ 'p-invalid': !newCompany.adminPassword && submitted }"
              placeholder="Secure password"
              toggleMask
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="adminPhone" class="font-semibold">Admin Phone</label>
            <InputText 
              id="adminPhone" 
              v-model="newCompany.adminPhone" 
              class="w-full" 
              placeholder="+1 (555) 123-4567"
            />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          @click="cancelAddCompany" 
          class="p-button-text" 
        />
        <Button 
          label="Register Company" 
          @click="registerCompany" 
          :loading="registering"
          icon="pi pi-check"
        />
      </template>
    </Dialog>

    <!-- Company Selector Dialog -->
    <Dialog 
      v-model:visible="showCompanySelector" 
      header="Select Active Company" 
      :style="{ width: '600px' }" 
      :modal="true"
    >
      <div class="company-selector-list">
        <div 
          v-for="company in companies" 
          :key="company.id" 
          class="company-selector-item p-3 border-1 border-200 border-round mb-2 cursor-pointer hover:bg-primary-50"
          :class="{ 'bg-primary-100 border-primary': company.id === activeCompany?.id }"
          @click="selectCompany(company)"
        >
          <div class="flex align-items-center gap-3">
            <div class="company-logo">
              <img 
                v-if="company.logo" 
                :src="company.logo" 
                :alt="company.name" 
                class="w-3rem h-3rem border-circle"
              />
              <div v-else class="w-3rem h-3rem border-circle bg-primary flex align-items-center justify-content-center">
                <i class="pi pi-building text-white"></i>
              </div>
            </div>
            <div class="flex-1">
              <div class="font-semibold text-lg">{{ company.name }}</div>
              <div class="text-600">{{ company.domain }}</div>
              <div class="flex gap-2 mt-1">
                <Tag :value="company.plan" :severity="getPlanSeverity(company.plan)" class="text-xs" />
                <Tag :value="company.status" :severity="getStatusSeverity(company.status)" class="text-xs" />
              </div>
            </div>
            <div v-if="company.id === activeCompany?.id" class="text-primary">
              <i class="pi pi-check-circle text-2xl"></i>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Close" 
          @click="showCompanySelector = false" 
          class="p-button-text" 
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation -->
    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import tenantService, { type TenantCompany, type CompanyRegistration } from '@/services/tenantService'

const toast = useToast()
const confirm = useConfirm()

const showAddCompany = ref(false)
const showCompanySelector = ref(false)
const loading = ref(false)
const registering = ref(false)
const submitted = ref(false)
const searchTerm = ref('')
const statusFilter = ref('')

const activeCompany = ref({
  id: 1,
  name: 'Paksa Financial System',
  domain: 'paksa.paksa.com',
  plan: 'Enterprise',
  users: 15,
  status: 'Active',
  createdAt: '2024-01-01',
  logo: null,
  industry: 'Financial Services'
})

const companies = ref<TenantCompany[]>([])

const newCompany = ref<CompanyRegistration>({
  name: '',
  code: '',
  industry: '',
  size: '',
  address: '',
  plan: '',
  max_users: 10,
  subdomain: '',
  timezone: 'UTC',
  language: 'en',
  currency: 'USD',
  date_format: 'MM/DD/YYYY',
  storage_limit_gb: 5,
  api_rate_limit: 1000,
  primary_color: '#1976D2',
  logo_url: undefined,
  admin_name: '',
  admin_email: '',
  admin_password: '',
  admin_phone: ''
})

const plans = [
  { label: 'Basic - $29/month (Up to 10 users)', value: 'Basic' },
  { label: 'Professional - $79/month (Up to 50 users)', value: 'Professional' },
  { label: 'Enterprise - $199/month (Up to 200 users)', value: 'Enterprise' },
  { label: 'Custom - Contact Sales', value: 'Custom' }
]

const industries = [
  { label: 'Financial Services', value: 'Financial Services' },
  { label: 'Manufacturing', value: 'Manufacturing' },
  { label: 'Technology', value: 'Technology' },
  { label: 'Healthcare', value: 'Healthcare' },
  { label: 'Retail', value: 'Retail' },
  { label: 'Construction', value: 'Construction' },
  { label: 'Education', value: 'Education' },
  { label: 'Non-Profit', value: 'Non-Profit' },
  { label: 'Other', value: 'Other' }
]

const companySizes = [
  { label: 'Small (1-50 employees)', value: 'Small' },
  { label: 'Medium (51-200 employees)', value: 'Medium' },
  { label: 'Large (201-1000 employees)', value: 'Large' },
  { label: 'Enterprise (1000+ employees)', value: 'Enterprise' }
]

const timezones = [
  { label: 'UTC', value: 'UTC' },
  { label: 'Eastern Time (ET)', value: 'America/New_York' },
  { label: 'Central Time (CT)', value: 'America/Chicago' },
  { label: 'Mountain Time (MT)', value: 'America/Denver' },
  { label: 'Pacific Time (PT)', value: 'America/Los_Angeles' },
  { label: 'London (GMT)', value: 'Europe/London' },
  { label: 'Paris (CET)', value: 'Europe/Paris' },
  { label: 'Tokyo (JST)', value: 'Asia/Tokyo' },
  { label: 'Sydney (AEST)', value: 'Australia/Sydney' },
  { label: 'Karachi (PKT)', value: 'Asia/Karachi' }
]

const statusOptions = [
  { label: 'All Statuses', value: '' },
  { label: 'Active', value: 'Active' },
  { label: 'Trial', value: 'Trial' },
  { label: 'Suspended', value: 'Suspended' },
  { label: 'Inactive', value: 'Inactive' }
]

const filteredCompanies = computed(() => {
  let filtered = companies.value
  
  if (searchTerm.value) {
    filtered = filtered.filter(company => 
      company.name.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
      company.domain.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
      company.code.toLowerCase().includes(searchTerm.value.toLowerCase())
    )
  }
  
  if (statusFilter.value) {
    filtered = filtered.filter(company => company.status === statusFilter.value)
  }
  
  return filtered
})

const getPlanSeverity = (plan: string) => {
  switch (plan) {
    case 'Enterprise': return 'success'
    case 'Professional': return 'warning'
    case 'Basic': return 'info'
    case 'Custom': return 'contrast'
    default: return 'secondary'
  }
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'Active': return 'success'
    case 'Trial': return 'warning'
    case 'Suspended': return 'danger'
    case 'Inactive': return 'secondary'
    default: return 'secondary'
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const activateCompany = async (company: TenantCompany) => {
  try {
    if (company.id) {
      const response = await tenantService.activateCompany(company.id)
      activeCompany.value = response.company
      
      toast.add({
        severity: 'success',
        summary: 'Company Activated',
        detail: response.message,
        life: 3000
      })
      
      // Apply company branding
      tenantService.applyCompanyBranding(response.company)
    }
  } catch (error: any) {
    console.error('Activation error:', error)
    const errorMessage = error.response?.data?.detail || 'Failed to activate company'
    toast.add({
      severity: 'error',
      summary: 'Activation Failed',
      detail: errorMessage,
      life: 3000
    })
  }
}

const applyCompanyBranding = (company: any) => {
  // Apply primary color
  if (company.primaryColor) {
    document.documentElement.style.setProperty('--primary-color', company.primaryColor)
  }
  
  // Update page title
  document.title = `${company.name} - Financial System`
  
  // Update favicon if company has logo
  if (company.logo) {
    const favicon = document.querySelector('link[rel="icon"]') as HTMLLinkElement
    if (favicon) {
      favicon.href = company.logo
    }
  }
}

const selectCompany = (company: any) => {
  activateCompany(company)
  showCompanySelector.value = false
}

const viewCompany = (company: any) => {
  // TODO: Implement company details view
  toast.add({
    severity: 'info',
    summary: 'View Company',
    detail: `Viewing details for ${company.name}`,
    life: 3000
  })
}

const editCompany = (company: any) => {
  // TODO: Implement company editing
  toast.add({
    severity: 'info',
    summary: 'Edit Company',
    detail: `Editing ${company.name}`,
    life: 3000
  })
}

const configureCompany = (company: any) => {
  // TODO: Navigate to company-specific settings
  toast.add({
    severity: 'info',
    summary: 'Company Settings',
    detail: `Configuring settings for ${company.name}`,
    life: 3000
  })
}

const confirmDelete = (company: any) => {
  confirm.require({
    message: `Are you sure you want to delete ${company.name}? This action cannot be undone.`,
    header: 'Delete Company',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: () => {
      deleteCompany(company)
    }
  })
}

const deleteCompany = async (company: TenantCompany) => {
  try {
    if (company.id) {
      await tenantService.deleteCompany(company.id)
      
      // Remove from local list
      const index = companies.value.findIndex(c => c.id === company.id)
      if (index > -1) {
        companies.value.splice(index, 1)
      }
      
      toast.add({
        severity: 'success',
        summary: 'Company Deleted',
        detail: `${company.name} has been deleted`,
        life: 3000
      })
      
      // If deleted company was active, switch to another
      if (activeCompany.value?.id === company.id && companies.value.length > 0) {
        await activateCompany(companies.value[0])
      }
    }
  } catch (error: any) {
    console.error('Delete error:', error)
    const errorMessage = error.response?.data?.detail || 'Failed to delete company'
    toast.add({
      severity: 'error',
      summary: 'Delete Failed',
      detail: errorMessage,
      life: 3000
    })
  }
}

const registerCompany = async () => {
  submitted.value = true
  
  // Validate required fields
  const validationErrors = tenantService.validateCompanyRegistration(newCompany.value)
  if (validationErrors.length > 0) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: validationErrors[0],
      life: 5000
    })
    return
  }
  
  registering.value = true
  
  try {
    // Auto-generate subdomain and code if not provided
    if (!newCompany.value.subdomain) {
      newCompany.value.subdomain = tenantService.generateSubdomain(newCompany.value.name)
    }
    if (!newCompany.value.code) {
      newCompany.value.code = tenantService.generateCompanyCode(newCompany.value.name)
    }
    
    const registeredCompany = await tenantService.registerCompany(newCompany.value)
    
    // Add to local list
    companies.value.push(registeredCompany)
    
    toast.add({
      severity: 'success',
      summary: 'Company Registered',
      detail: `${newCompany.value.name} has been successfully registered`,
      life: 5000
    })
    
    // Activate the new company
    await activateCompany(registeredCompany)
    
    cancelAddCompany()
  } catch (error: any) {
    console.error('Registration error:', error)
    const errorMessage = error.response?.data?.detail || 'Failed to register company. Please try again.'
    toast.add({
      severity: 'error',
      summary: 'Registration Failed',
      detail: errorMessage,
      life: 5000
    })
  } finally {
    registering.value = false
  }
}

const cancelAddCompany = () => {
  showAddCompany.value = false
  submitted.value = false
  newCompany.value = {
    name: '',
    code: '',
    industry: '',
    size: '',
    address: '',
    plan: '',
    max_users: 10,
    subdomain: '',
    timezone: 'UTC',
    language: 'en',
    currency: 'USD',
    date_format: 'MM/DD/YYYY',
    storage_limit_gb: 5,
    api_rate_limit: 1000,
    primary_color: '#1976D2',
    logo_url: undefined,
    admin_name: '',
    admin_email: '',
    admin_password: '',
    admin_phone: ''
  }
}

const onLogoUpload = (event: any) => {
  // TODO: Handle logo upload
  console.log('Logo uploaded:', event)
}

const loadCompanies = async () => {
  loading.value = true
  try {
    const companiesData = await tenantService.getCompanies({
      search: searchTerm.value,
      status: statusFilter.value || undefined
    })
    companies.value = companiesData
    
    // Set active company if not set
    if (!activeCompany.value && companiesData.length > 0) {
      activeCompany.value = companiesData[0]
      tenantService.applyCompanyBranding(activeCompany.value)
    }
  } catch (error) {
    console.error('Error loading companies:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load companies',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCompanies()
  
  // Load stored company context
  const storedCompany = tenantService.getStoredCompanyContext()
  if (storedCompany) {
    tenantService.applyCompanyBranding(storedCompany as TenantCompany)
  }
})
</script>

<style scoped>
.tenant-management {
  max-width: 1400px;
  margin: 0 auto;
}

.company-selector-item {
  transition: all 0.2s ease;
}

.company-selector-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.company-logo-small img,
.company-logo-small div {
  object-fit: cover;
}

.p-invalid {
  border-color: var(--red-500) !important;
}

.company-stat-card {
  transition: all 0.2s ease;
}

.company-stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .tenant-management {
    padding: 0 1rem;
  }
  
  .flex.gap-2 {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .w-20rem,
  .w-12rem {
    width: 100% !important;
  }
}
</style>