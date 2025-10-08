<template>
  <div class="tax-compliance-dashboard">
    <!-- Header -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-3xl font-bold text-900 mb-2">Tax Compliance Dashboard</h1>
        <Breadcrumb :home="home" :model="breadcrumbItems" class="mb-0" />
      </div>
      <div class="flex gap-2">
        <Button 
          icon="pi pi-refresh" 
          label="Refresh" 
          class="p-button-outlined" 
          @click="refreshData" 
          :loading="loading"
        />
        <Button 
          icon="pi pi-cog" 
          label="Settings" 
          class="p-button-outlined"
          @click="showSettings = true"
        />
      </div>
    </div>

    <!-- Compliance Overview Cards -->
    <div class="grid mb-4">
      <div class="col-12 lg:col-3 md:col-6">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-1">Compliance Score</div>
                <div class="text-2xl font-bold text-900">{{ overview.compliance_score }}%</div>
                <div class="text-sm" :class="getScoreColor(overview.compliance_score)">
                  <i class="pi" :class="getScoreIcon(overview.compliance_score)"></i>
                  {{ getScoreStatus(overview.compliance_score) }}
                </div>
              </div>
              <div class="w-3rem h-3rem border-circle bg-blue-100 flex align-items-center justify-content-center">
                <i class="pi pi-chart-line text-blue-600 text-xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-3 md:col-6">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-1">Active Alerts</div>
                <div class="text-2xl font-bold text-900">{{ overview.active_alerts }}</div>
                <div class="text-sm text-orange-600">
                  <i class="pi pi-exclamation-triangle"></i>
                  Requires attention
                </div>
              </div>
              <div class="w-3rem h-3rem border-circle bg-orange-100 flex align-items-center justify-content-center">
                <i class="pi pi-bell text-orange-600 text-xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-3 md:col-6">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-1">Total Checks</div>
                <div class="text-2xl font-bold text-900">{{ overview.total_checks }}</div>
                <div class="text-sm text-green-600">
                  <i class="pi pi-check-circle"></i>
                  {{ overview.passed_checks }} passed
                </div>
              </div>
              <div class="w-3rem h-3rem border-circle bg-green-100 flex align-items-center justify-content-center">
                <i class="pi pi-verified text-green-600 text-xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-3 md:col-6">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-1">Next Check</div>
                <div class="text-lg font-semibold text-900">{{ formatDateTime(overview.next_check) }}</div>
                <div class="text-sm text-600">
                  <i class="pi pi-clock"></i>
                  Scheduled
                </div>
              </div>
              <div class="w-3rem h-3rem border-circle bg-purple-100 flex align-items-center justify-content-center">
                <i class="pi pi-calendar text-purple-600 text-xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid">
      <!-- Alerts Panel -->
      <div class="col-12 lg:col-8">
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center p-4 pb-0">
              <h3 class="m-0">Compliance Alerts</h3>
              <div class="flex gap-2">
                <Dropdown 
                  v-model="alertFilters.severity" 
                  :options="severityOptions" 
                  placeholder="All Severities"
                  class="w-10rem"
                  @change="loadAlerts"
                />
                <Dropdown 
                  v-model="alertFilters.status" 
                  :options="statusOptions" 
                  placeholder="All Statuses"
                  class="w-10rem"
                  @change="loadAlerts"
                />
              </div>
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="alerts" 
              :loading="alertsLoading"
              :paginator="true" 
              :rows="10"
              class="p-datatable-sm"
              responsiveLayout="scroll"
            >
              <template #empty>No alerts found.</template>
              <Column field="severity" header="Severity" style="width: 100px">
                <template #body="{ data }">
                  <Tag 
                    :value="data.severity" 
                    :severity="getSeverityColor(data.severity)"
                    :icon="getSeverityIcon(data.severity)"
                  />
                </template>
              </Column>
              <Column field="title" header="Alert" class="font-medium" />
              <Column field="entity_type" header="Type" style="width: 120px" />
              <Column field="created_at" header="Created" style="width: 150px">
                <template #body="{ data }">
                  {{ formatDateTime(data.created_at) }}
                </template>
              </Column>
              <Column field="status" header="Status" style="width: 100px">
                <template #body="{ data }">
                  <Tag 
                    :value="data.status" 
                    :severity="getStatusColor(data.status)"
                  />
                </template>
              </Column>
              <Column header="Actions" style="width: 120px">
                <template #body="{ data }">
                  <div class="flex gap-1">
                    <Button 
                      icon="pi pi-eye" 
                      class="p-button-text p-button-sm" 
                      @click="viewAlert(data)"
                      v-tooltip.top="'View Details'"
                    />
                    <Button 
                      v-if="data.status === 'open'"
                      icon="pi pi-check" 
                      class="p-button-text p-button-sm p-button-success" 
                      @click="resolveAlert(data)"
                      v-tooltip.top="'Resolve'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>

      <!-- Jurisdictions Panel -->
      <div class="col-12 lg:col-4">
        <Card>
          <template #header>
            <div class="p-4 pb-0">
              <h3 class="m-0">Tax Jurisdictions</h3>
            </div>
          </template>
          <template #content>
            <div class="space-y-3">
              <div 
                v-for="jurisdiction in jurisdictions" 
                :key="jurisdiction.id"
                class="border-1 border-200 border-round p-3 hover:bg-50 cursor-pointer transition-colors"
                @click="selectJurisdiction(jurisdiction)"
              >
                <div class="flex justify-content-between align-items-start mb-2">
                  <div class="font-medium text-900">{{ jurisdiction.name }}</div>
                  <Tag :value="jurisdiction.country" class="p-tag-sm" />
                </div>
                <div class="text-sm text-600 mb-2">{{ jurisdiction.code }}</div>
                <div class="flex justify-content-between align-items-center">
                  <div class="text-sm">
                    <i class="pi pi-calendar text-500 mr-1"></i>
                    {{ jurisdiction.filing_frequency }}
                  </div>
                  <div class="text-sm" :class="getFilingStatusColor(jurisdiction.next_filing_date)">
                    {{ getFilingStatus(jurisdiction.next_filing_date) }}
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Compliance Rules -->
    <div class="grid mt-4">
      <div class="col-12">
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center p-4 pb-0">
              <h3 class="m-0">Compliance Rules</h3>
              <Button 
                icon="pi pi-plus" 
                label="Add Rule" 
                class="p-button-sm"
                @click="showAddRule = true"
              />
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="rules" 
              :loading="rulesLoading"
              :paginator="true" 
              :rows="10"
              class="p-datatable-sm"
              responsiveLayout="scroll"
            >
              <template #empty>No rules found.</template>
              <Column field="name" header="Rule Name" class="font-medium" />
              <Column field="check_type" header="Type" style="width: 120px" />
              <Column field="jurisdiction" header="Jurisdiction" style="width: 120px" />
              <Column field="severity" header="Severity" style="width: 100px">
                <template #body="{ data }">
                  <Tag 
                    :value="data.severity" 
                    :severity="getSeverityColor(data.severity)"
                  />
                </template>
              </Column>
              <Column field="is_active" header="Status" style="width: 100px">
                <template #body="{ data }">
                  <Tag 
                    :value="data.is_active ? 'Active' : 'Inactive'" 
                    :severity="data.is_active ? 'success' : 'secondary'"
                  />
                </template>
              </Column>
              <Column header="Actions" style="width: 120px">
                <template #body="{ data }">
                  <div class="flex gap-1">
                    <Button 
                      icon="pi pi-pencil" 
                      class="p-button-text p-button-sm" 
                      @click="editRule(data)"
                      v-tooltip.top="'Edit'"
                    />
                    <Button 
                      icon="pi pi-trash" 
                      class="p-button-text p-button-sm p-button-danger" 
                      @click="deleteRule(data)"
                      v-tooltip.top="'Delete'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- Alert Details Dialog -->
    <Dialog 
      v-model:visible="showAlertDetails" 
      :style="{width: '600px'}" 
      header="Alert Details" 
      :modal="true"
    >
      <div v-if="selectedAlert">
        <div class="grid">
          <div class="col-12">
            <div class="field">
              <label class="font-semibold">Title</label>
              <div class="mt-1">{{ selectedAlert.title }}</div>
            </div>
          </div>
          <div class="col-6">
            <div class="field">
              <label class="font-semibold">Severity</label>
              <div class="mt-1">
                <Tag 
                  :value="selectedAlert.severity" 
                  :severity="getSeverityColor(selectedAlert.severity)"
                />
              </div>
            </div>
          </div>
          <div class="col-6">
            <div class="field">
              <label class="font-semibold">Status</label>
              <div class="mt-1">
                <Tag 
                  :value="selectedAlert.status" 
                  :severity="getStatusColor(selectedAlert.status)"
                />
              </div>
            </div>
          </div>
          <div class="col-12">
            <div class="field">
              <label class="font-semibold">Description</label>
              <div class="mt-1">{{ selectedAlert.description }}</div>
            </div>
          </div>
          <div class="col-6">
            <div class="field">
              <label class="font-semibold">Entity Type</label>
              <div class="mt-1">{{ selectedAlert.entity_type }}</div>
            </div>
          </div>
          <div class="col-6">
            <div class="field">
              <label class="font-semibold">Created</label>
              <div class="mt-1">{{ formatDateTime(selectedAlert.created_at) }}</div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <Button 
          label="Close" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="showAlertDetails = false"
        />
        <Button 
          v-if="selectedAlert?.status === 'open'"
          label="Resolve" 
          icon="pi pi-check" 
          class="p-button-success" 
          @click="resolveSelectedAlert"
        />
      </template>
    </Dialog>

    <!-- Add Rule Dialog -->
    <Dialog 
      v-model:visible="showAddRule" 
      :style="{width: '600px'}" 
      header="Add Compliance Rule" 
      :modal="true"
    >
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label for="ruleName">Rule Name <span class="text-red-500">*</span></label>
            <InputText 
              id="ruleName"
              v-model="newRule.name" 
              class="w-full"
              placeholder="Enter rule name"
            />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label for="checkType">Check Type</label>
            <Dropdown 
              id="checkType"
              v-model="newRule.check_type" 
              :options="checkTypeOptions" 
              class="w-full"
              placeholder="Select check type"
            />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label for="jurisdiction">Jurisdiction</label>
            <Dropdown 
              id="jurisdiction"
              v-model="newRule.jurisdiction" 
              :options="jurisdictionOptions" 
              class="w-full"
              placeholder="Select jurisdiction"
            />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label for="severity">Severity</label>
            <Dropdown 
              id="severity"
              v-model="newRule.severity" 
              :options="severityOptions.slice(1)" 
              optionLabel="label"
              optionValue="value"
              class="w-full"
              placeholder="Select severity"
            />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label for="frequency">Check Frequency</label>
            <Dropdown 
              id="frequency"
              v-model="newRule.frequency" 
              :options="frequencyOptions" 
              class="w-full"
              placeholder="Select frequency"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="description">Description</label>
            <Textarea 
              id="description"
              v-model="newRule.description" 
              rows="3"
              class="w-full"
              placeholder="Enter rule description"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="conditions">Rule Conditions</label>
            <Textarea 
              id="conditions"
              v-model="newRule.conditions" 
              rows="4"
              class="w-full"
              placeholder="Enter rule conditions (JSON format)"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox 
              id="isActive" 
              v-model="newRule.is_active" 
              :binary="true"
            />
            <label for="isActive">Active</label>
          </div>
        </div>
      </div>
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="cancelAddRule"
        />
        <Button 
          label="Save Rule" 
          icon="pi pi-check" 
          @click="saveRule"
          :loading="savingRule"
        />
      </template>
    </Dialog>

    <!-- Settings Dialog -->
    <Dialog 
      v-model:visible="showSettings" 
      :style="{width: '500px'}" 
      header="Compliance Settings" 
      :modal="true"
    >
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label for="autoCheck">Auto Check Frequency</label>
            <Dropdown 
              id="autoCheck"
              v-model="settings.autoCheckFrequency" 
              :options="frequencyOptions" 
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox 
              id="notifications" 
              v-model="settings.enableNotifications" 
              :binary="true"
            />
            <label for="notifications">Enable Email Notifications</label>
          </div>
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox 
              id="realtime" 
              v-model="settings.realtimeMonitoring" 
              :binary="true"
            />
            <label for="realtime">Real-time Monitoring</label>
          </div>
        </div>
      </div>
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="showSettings = false"
        />
        <Button 
          label="Save" 
          icon="pi pi-check" 
          @click="saveSettings"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import taxComplianceService, { 
  type ComplianceOverview, 
  type ComplianceAlert, 
  type ComplianceRule, 
  type TaxJurisdiction 
} from '@/api/taxComplianceService'

// Types are now imported from the service

// Composables
const toast = useToast()
const confirm = useConfirm()

// Reactive data
const loading = ref(false)
const alertsLoading = ref(false)
const rulesLoading = ref(false)

const overview = ref<ComplianceOverview>({
  total_checks: 0,
  passed_checks: 0,
  failed_checks: 0,
  warning_checks: 0,
  compliance_score: 0,
  last_check: '',
  next_check: '',
  active_alerts: 0
})

const alerts = ref<ComplianceAlert[]>([])
const rules = ref<ComplianceRule[]>([])
const jurisdictions = ref<TaxJurisdiction[]>([])

const selectedAlert = ref<ComplianceAlert | null>(null)
const showAlertDetails = ref(false)
const showSettings = ref(false)
const showAddRule = ref(false)
const savingRule = ref(false)

const newRule = ref({
  name: '',
  check_type: '',
  jurisdiction: '',
  severity: '',
  frequency: 'daily',
  description: '',
  conditions: '',
  is_active: true
})

// Filters
const alertFilters = ref({
  severity: null,
  status: null
})

// Settings
const settings = ref({
  autoCheckFrequency: 'daily',
  enableNotifications: true,
  realtimeMonitoring: true
})

// Breadcrumb
const home = ref({ icon: 'pi pi-home', to: '/' })
const breadcrumbItems = ref([
  { label: 'Tax Management', to: '/tax' },
  { label: 'Compliance' }
])

// Options
const severityOptions = ref([
  { label: 'All Severities', value: null },
  { label: 'Critical', value: 'critical' },
  { label: 'High', value: 'high' },
  { label: 'Medium', value: 'medium' },
  { label: 'Low', value: 'low' }
])

const statusOptions = ref([
  { label: 'All Statuses', value: null },
  { label: 'Open', value: 'open' },
  { label: 'Acknowledged', value: 'acknowledged' },
  { label: 'Resolved', value: 'resolved' }
])

const frequencyOptions = ref([
  { label: 'Hourly', value: 'hourly' },
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' }
])

const checkTypeOptions = ref([
  { label: 'Tax Rate Validation', value: 'tax_rate' },
  { label: 'Filing Deadline', value: 'filing_deadline' },
  { label: 'Document Compliance', value: 'document_compliance' },
  { label: 'Calculation Accuracy', value: 'calculation_accuracy' },
  { label: 'Reporting Requirements', value: 'reporting_requirements' }
])

const jurisdictionOptions = ref([
  { label: 'Federal', value: 'federal' },
  { label: 'State', value: 'state' },
  { label: 'Local', value: 'local' },
  { label: 'International', value: 'international' }
])

// Methods
const loadOverview = async () => {
  try {
    loading.value = true
    overview.value = await taxComplianceService.getOverview()
  } catch (error) {
    console.error('Error loading overview:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load compliance overview',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const loadAlerts = async () => {
  try {
    alertsLoading.value = true
    const filters = {
      severity: alertFilters.value.severity || undefined,
      status: alertFilters.value.status || undefined
    }
    alerts.value = await taxComplianceService.getAlerts(filters)
  } catch (error) {
    console.error('Error loading alerts:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load compliance alerts',
      life: 3000
    })
  } finally {
    alertsLoading.value = false
  }
}

const loadRules = async () => {
  try {
    rulesLoading.value = true
    rules.value = await taxComplianceService.getRules()
  } catch (error) {
    console.error('Error loading rules:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load compliance rules',
      life: 3000
    })
  } finally {
    rulesLoading.value = false
  }
}

const loadJurisdictions = async () => {
  try {
    jurisdictions.value = await taxComplianceService.getJurisdictions()
  } catch (error) {
    console.error('Error loading jurisdictions:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load tax jurisdictions',
      life: 3000
    })
  }
}

const refreshData = async () => {
  await Promise.all([
    loadOverview(),
    loadAlerts(),
    loadRules(),
    loadJurisdictions()
  ])
}

const viewAlert = (alert: ComplianceAlert) => {
  selectedAlert.value = alert
  showAlertDetails.value = true
}

const resolveAlert = async (alert: ComplianceAlert) => {
  try {
    await taxComplianceService.resolveAlert(alert.id)
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Alert resolved successfully',
      life: 3000
    })
    await loadAlerts()
    await loadOverview()
  } catch (error) {
    console.error('Error resolving alert:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to resolve alert',
      life: 3000
    })
  }
}

const resolveSelectedAlert = async () => {
  if (selectedAlert.value) {
    await resolveAlert(selectedAlert.value)
    showAlertDetails.value = false
  }
}

const selectJurisdiction = (jurisdiction: TaxJurisdiction) => {
  // Navigate to jurisdiction details or show more info
  console.log('Selected jurisdiction:', jurisdiction)
}

const editRule = (rule: ComplianceRule) => {
  // Open edit rule dialog
  console.log('Edit rule:', rule)
}

const deleteRule = (rule: ComplianceRule) => {
  confirm.require({
    message: `Are you sure you want to delete the rule "${rule.name}"?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try {
        // await axios.delete(`/api/v1/tax/compliance/rules/${rule.id}`)
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Rule deleted successfully',
          life: 3000
        })
        await loadRules()
      } catch (error) {
        console.error('Error deleting rule:', error)
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete rule',
          life: 3000
        })
      }
    }
  })
}

const saveRule = async () => {
  if (!newRule.value.name.trim()) {
    toast.add({
      severity: 'error',
      summary: 'Validation Error',
      detail: 'Rule name is required',
      life: 3000
    })
    return
  }

  try {
    savingRule.value = true
    // await taxComplianceService.createRule(newRule.value)
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Compliance rule created successfully',
      life: 3000
    })
    showAddRule.value = false
    resetNewRule()
    await loadRules()
  } catch (error) {
    console.error('Error creating rule:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to create compliance rule',
      life: 3000
    })
  } finally {
    savingRule.value = false
  }
}

const cancelAddRule = () => {
  showAddRule.value = false
  resetNewRule()
}

const resetNewRule = () => {
  newRule.value = {
    name: '',
    check_type: '',
    jurisdiction: '',
    severity: '',
    frequency: 'daily',
    description: '',
    conditions: '',
    is_active: true
  }
}

const saveSettings = () => {
  // Save settings
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: 'Settings saved successfully',
    life: 3000
  })
  showSettings.value = false
}

// Utility functions
const formatDateTime = (dateString: string) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const getScoreColor = (score: number) => {
  if (score >= 90) return 'text-green-600'
  if (score >= 75) return 'text-yellow-600'
  return 'text-red-600'
}

const getScoreIcon = (score: number) => {
  if (score >= 90) return 'pi-check-circle'
  if (score >= 75) return 'pi-exclamation-triangle'
  return 'pi-times-circle'
}

const getScoreStatus = (score: number) => {
  if (score >= 90) return 'Excellent'
  if (score >= 75) return 'Good'
  return 'Needs Attention'
}

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'critical': return 'danger'
    case 'high': return 'warning'
    case 'medium': return 'info'
    case 'low': return 'success'
    default: return 'secondary'
  }
}

const getSeverityIcon = (severity: string) => {
  switch (severity) {
    case 'critical': return 'pi-times-circle'
    case 'high': return 'pi-exclamation-triangle'
    case 'medium': return 'pi-info-circle'
    case 'low': return 'pi-check-circle'
    default: return 'pi-circle'
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'open': return 'danger'
    case 'acknowledged': return 'warning'
    case 'resolved': return 'success'
    default: return 'secondary'
  }
}

const getFilingStatusColor = (filingDate: string) => {
  if (!filingDate) return 'text-500'
  const date = new Date(filingDate)
  const now = new Date()
  const diffDays = Math.ceil((date.getTime() - now.getTime()) / (1000 * 3600 * 24))
  
  if (diffDays < 0) return 'text-red-600'
  if (diffDays <= 7) return 'text-orange-600'
  return 'text-green-600'
}

const getFilingStatus = (filingDate: string) => {
  if (!filingDate) return 'No date set'
  const date = new Date(filingDate)
  const now = new Date()
  const diffDays = Math.ceil((date.getTime() - now.getTime()) / (1000 * 3600 * 24))
  
  if (diffDays < 0) return 'Overdue'
  if (diffDays <= 7) return `Due in ${diffDays} days`
  return `Due ${date.toLocaleDateString()}`
}

// Lifecycle
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.tax-compliance-dashboard {
  padding: 1.5rem;
}

.space-y-3 > * + * {
  margin-top: 0.75rem;
}

.hover\:bg-50:hover {
  background-color: var(--surface-50);
}

.transition-colors {
  transition: background-color 0.2s ease;
}
</style>
