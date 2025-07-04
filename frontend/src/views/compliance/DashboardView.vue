<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { format } from 'date-fns';

// Router and toast
const router = useRouter();
const toast = useToast();

// State
const loading = ref<boolean>(false);
const stats = ref({
  complianceScore: 92,
  securityScore: 88,
  auditScore: 95,
  dataPrivacyScore: 90,
  lastUpdated: new Date()
});

    // Helper functions
    const formatDate = (date: Date | string | null | undefined): string => {
      if (!date) return 'N/A';
      try {
        return format(new Date(date), 'MMM d, yyyy');
      } catch (e) {
        console.error('Error formatting date:', e);
        return 'Invalid date';
      }
    };

    const formatTimeAgo = (date: Date | string | null | undefined): string => {
      if (!date) return 'Just now';
      try {
        const now = new Date();
        const diffInSeconds = Math.floor((now.getTime() - new Date(date).getTime()) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
      } catch (e) {
        console.error('Error formatting time ago:', e);
        return 'Just now';
      }
    };

    const getAlertSeverity = (severity: string): string => {
      if (!severity) return 'info';
      const severityLower = severity.toLowerCase();
      if (severityLower.includes('high') || severityLower.includes('critical')) return 'danger';
      if (severityLower.includes('medium')) return 'warning';
      if (severityLower.includes('low')) return 'info';
      return 'info';
    };

    const getComplianceScoreColor = (score: number): string => {
      if (score >= 90) return 'bg-green-100 text-green-600';
      if (score >= 70) return 'bg-blue-100 text-blue-600';
      if (score >= 50) return 'bg-amber-100 text-amber-600';
      return 'bg-red-100 text-red-600';
    };

    const getStatusSeverity = (status: string): string => {
      if (!status) return 'info';
      const statusLower = status.toLowerCase();
      if (statusLower.includes('compliant')) {
        return statusLower.startsWith('non') ? 'danger' : 'success';
      }
      if (statusLower.includes('progress') || statusLower === 'in progress') return 'info';
      if (statusLower.includes('warning') || statusLower.includes('partial')) return 'warning';
      return 'info';
    };

    const getProgressBarClass = (status: string): string => {
      switch (status.toLowerCase()) {
        case 'compliant': return 'progress-bar-success';
        case 'partial': return 'progress-bar-warning';
        case 'in-progress': return 'progress-bar-info';
        case 'non-compliant': return 'progress-bar-danger';
        default: return '';
      }
    };

    const getActivityIcon = (type: string): string => {
      switch (type) {
        case 'audit': return 'pi pi-file-edit';
        case 'alert': return 'pi pi-exclamation-triangle';
        case 'approval': return 'pi pi-check-circle';
        case 'compliance': return 'pi pi-shield';
        case 'user': return 'pi pi-user';
        default: return 'pi pi-info-circle';
      }
    };

    const getActivityColor = (type: string): string => {
      switch (type) {
        case 'audit': return '#3b82f6';
        case 'alert': return '#ef4444';
        case 'approval': return '#10b981';
        case 'compliance': return '#8b5cf6';
        case 'user': return '#6b7280';
        default: return '#9ca3af';
      }
    };

    // Navigation helper
    const navigateTo = (routeName: string): void => {
      router.push({ name: routeName });
    };

    // Fetch dashboard data
    const fetchDashboardData = async (): Promise<void> => {
      loading.value = true;
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        toast.add({
          severity: 'success',
          summary: 'Dashboard Updated',
          detail: 'Dashboard data has been refreshed',
          life: 3000
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        loading.value = false;
      }
    };

    // Handle activity actions
    const handleActivityAction = (activity: any): void => {
      if (activity.action === 'review-policy') {
        router.push({ name: 'security-policies' });
      }
    };

    // Run security scan
    const runSecurityScan = async (): Promise<void> => {
      loading.value = true;
      try {
        await new Promise(resolve => setTimeout(resolve, 1500));
        toast.add({
          severity: 'success',
          summary: 'Security Scan',
          detail: 'Security scan completed successfully',
          life: 3000
        });
      } catch (error) {
        console.error('Error running security scan:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to run security scan. Please try again.',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };

    // View alert details
    const viewAlertDetails = (alert: any): void => {
      // Implementation for viewing alert details
      console.log('Viewing alert:', alert);
    };

    // Lifecycle hooks
    onMounted(() => {
      fetchDashboardData();
    });

// Mock data (move to API calls in production)
const complianceStandards = ref([
  {
    id: 'gdpr',
    name: 'GDPR',
    description: 'General Data Protection Regulation',
    status: 'Compliant',
    compliance: 95,
    lastAudit: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30), // 30 days ago
    nextAudit: new Date(Date.now() + 1000 * 60 * 60 * 24 * 60) // 60 days from now
  }
]);

const recentActivities = ref([
  {
    id: 'act-001',
    type: 'audit',
    title: 'Security Policy Updated',
    description: 'Password policy has been updated to meet new requirements',
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
    user: 'admin@example.com'
  }
]);

const securityAlerts = ref([
  {
    id: 1,
    title: 'Multiple Failed Login Attempts',
    description: '5 failed login attempts detected for user admin@example.com',
    severity: 'high',
    timestamp: new Date(Date.now() - 1000 * 60 * 15), // 15 minutes ago
    resolved: false
  }
]);
</script>

<template>
  <div class="compliance-dashboard">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Compliance & Security Dashboard</h1>
        <p class="text-gray-600">Comprehensive overview of security status, compliance metrics, and system health</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <Button 
          icon="pi pi-sync" 
          label="Refresh Data" 
          class="p-button-outlined p-button-sm"
          :loading="loading"
          @click="fetchDashboardData"
          v-tooltip="'Refresh dashboard data'"
        />
        <Button 
          icon="pi pi-shield" 
          label="Run Security Scan" 
          class="p-button-outlined p-button-sm p-button-help"
          @click="runSecurityScan"
          v-tooltip="'Run a full system security scan'"
        />
        <Button 
          icon="pi pi-cog" 
          label="Settings" 
          class="p-button-outlined p-button-sm"
          v-tooltip="'Configure dashboard settings'"
          @click="$router.push({ name: 'compliance-settings' })"
        />
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <!-- Compliance Score -->
      <div class="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">Compliance Score</p>
            <div class="flex items-baseline mt-1">
              <span class="text-2xl font-semibold">{{ stats.complianceScore }}</span>
              <span class="ml-1 text-sm text-gray-500">/ 100</span>
              <span 
                :class="[
                  'ml-2 text-xs font-medium px-2 py-0.5 rounded-full',
                  stats.complianceScore >= 90 ? 'bg-green-100 text-green-800' :
                  stats.complianceScore >= 75 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                ]"
              >
                {{ stats.complianceScore >= 90 ? 'Excellent' : stats.complianceScore >= 75 ? 'Good' : 'Needs Attention' }}
              </span>
            </div>
          </div>
          <div class="p-3 rounded-full bg-blue-50">
            <i class="pi pi-shield text-blue-600 text-xl"></i>
          </div>
        </div>
        <div class="mt-3">
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div 
              class="h-2 rounded-full" 
              :class="[
                stats.complianceScore >= 90 ? 'bg-green-500' :
                  stats.complianceScore >= 75 ? 'bg-yellow-500' : 'bg-red-500'
              ]"
            </div>
          </div>
          <span class="text-green-500 font-medium">+5% </span>
          <span class="text-500">since last month</span>
        </div>
      </div>
      
      <!-- Security Events Card -->
      <div class="col-12 md:col-6 xl:col-3">
        <div class="card mb-0">
          <div class="flex justify-content-between mb-3">
            <div>
              <span class="block text-500 font-medium mb-3">Security Events (24h)</span>
              <div class="text-900 font-medium text-xl">{{ securityStats.events24h }}</div>
            </div>
            <div class="flex align-items-center justify-content-center bg-orange-100 border-round" style="width:2.5rem;height:2.5rem">
              <i class="pi pi-exclamation-triangle text-orange-500 text-xl"></i>
            </div>
          </div>
          <span :class="securityStats.eventsTrend < 0 ? 'text-green-500' : 'text-red-500'" class="font-medium">
            {{ securityStats.eventsTrend > 0 ? '+' : '' }}{{ securityStats.eventsTrend }}% 
          </span>
          <span class="text-500">from yesterday</span>
        </div>
      </div>
      
      <!-- Open Findings Card -->
      <div class="col-12 md:col-6 xl:col-3">
        <div class="card mb-0">
          <div class="flex justify-content-between mb-3">
            <div>
              <span class="block text-500 font-medium mb-3">Open Findings</span>
              <div class="text-900 font-medium text-xl">{{ securityStats.openFindings }}</div>
            </div>
            <div class="flex align-items-center justify-content-center bg-red-100 border-round" style="width:2.5rem;height:2.5rem">
              <i class="pi pi-bug text-red-500 text-xl"></i>
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <Tag severity="danger" :value="`${securityStats.highRiskFindings} High`" />
            <Tag severity="warning" :value="`${securityStats.mediumRiskFindings} Medium`" />
          </div>
        </div>
      </div>
      
      <!-- Pending Approvals Card -->
      <div class="col-12 md:col-6 xl:col-3">
        <div class="card mb-0">
          <div class="flex justify-content-between mb-3">
            <div>
              <span class="block text-500 font-medium mb-3">Pending Approvals</span>
              <div class="text-900 font-medium text-xl">{{ securityStats.pendingApprovals }}</div>
            </div>
            <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width:2.5rem;height:2.5rem">
              <i class="pi pi-check-square text-cyan-500 text-xl"></i>
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <Tag severity="danger" :value="`${securityStats.urgentApprovals} Urgent`" />
            <Tag severity="warning" :value="`${securityStats.overdueApprovals} Overdue`" />
          </div>
        </div>
      </div>
      
      <!-- Compliance Standards -->
      <div class="col-12 xl:col-8">
        <div class="card">
          <div class="flex justify-content-between align-items-center mb-4">
            <h5 class="m-0">Compliance Standards</h5>
            <Button label="View All" icon="pi pi-list" class="p-button-text" @click="navigateTo('compliance-standards')" />
          </div>
          <DataTable :value="complianceStandards" :loading="loading" responsiveLayout="scroll">
            <Column field="name" header="Standard" :sortable="true">
              <template #body="{ data }">
                <div class="flex flex-column">
                  <span class="font-medium">{{ data.name }}</span>
                  <span class="text-500 text-sm">{{ data.description }}</span>
                </div>
              </template>
            </Column>
            <Column field="status" header="Status" :sortable="true">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column header="Compliance" :sortable="true" sortField="compliance">
              <template #body="{ data }">
                <div class="flex align-items-center">
                  <ProgressBar :value="data.compliance" :showValue="false" :style="{ height: '6px' }" :class="getProgressBarClass(data.status)" />
                  <span class="ml-2">{{ data.compliance }}%</span>
                </div>
              </template>
            </Column>
            <Column field="lastAudit" header="Last Audit" :sortable="true">
              <template #body="{ data }">
                {{ formatDate(data.lastAudit) }}
              </template>
            </Column>
            <Column field="nextAudit" header="Next Audit" :sortable="true">
              <template #body="{ data }">
                {{ formatDate(data.nextAudit) }}
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
      
      <!-- Recent Activities -->
      <div class="col-12 xl:col-4">
        <div class="card h-full">
          <div class="flex justify-content-between align-items-center mb-4">
            <h5 class="m-0">Recent Activities</h5>
            <Button label="View All" icon="pi pi-list" class="p-button-text" @click="navigateTo('audit-logs')" />
          </div>
          
          <div class="activity-timeline">
            <div v-for="(activity, index) in recentActivities" :key="activity.id" class="activity-item">
              <div class="activity-marker" :class="getActivityColor(activity.type)">
                <i :class="getActivityIcon(activity.type)"></i>
              </div>
              <div class="activity-content">
                <div class="flex justify-content-between align-items-start">
                  <div>
                    <div class="font-medium">{{ activity.user }}</div>
                    <div class="text-600 text-sm">{{ activity.description }}</div>
                    <div v-if="activity.tags && activity.tags.length" class="mt-2">
                      <Tag v-for="tag in activity.tags" :key="tag" :value="tag" class="mr-2 mb-1" />
                    </div>
                  </div>
                  <div class="text-500 text-sm">{{ formatTimeAgo(activity.timestamp) }}</div>
                </div>
                <div v-if="activity.action" class="mt-2">
                  <Button :label="activity.action.label" icon="pi pi-arrow-right" class="p-button-text p-button-sm" @click="handleActivityAction(activity)" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Security Alerts -->
      <div class="col-12 xl:col-8">
        <div class="card">
          <div class="flex justify-content-between align-items-center mb-4">
            <h5 class="m-0">Security Alerts</h5>
            <div>
              <Button label="Run Security Scan" icon="pi pi-search" class="p-button-outlined p-button-secondary mr-2" @click="runSecurityScan" :loading="loading" />
              <Button label="View All" icon="pi pi-list" class="p-button-text" @click="navigateTo('security-alerts')" />
              <div class="flex justify-between items-center mt-2 text-xs">
                <span class="text-gray-500">{{ formatTimeAgo(alert.timestamp) }}</span>
                <div class="space-x-2">
                  <Button 
                    v-if="!alert.resolved"
                    icon="pi pi-check" 
                    class="p-button-text p-button-sm"
                    label="Resolve"
                    @click="resolveAlert(alert.id)"
                  />
                  <Button 
                    icon="pi pi-eye" 
                    class="p-button-text p-button-sm"
                    @click="viewAlertDetails(alert)"
                  />
                </div>
              </div>
            </div>
          </div>
          <div class="text-center mt-4">
            <Button 
              label="View All Alerts" 
              class="p-button-text" 
              icon="pi pi-shield"
              @click="$router.push({ name: 'security-events' })"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Import components and utilities
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { format, subDays } from 'date-fns';
import { useToast } from 'primevue/usetoast';

// Types
type SeverityLevel = 'critical' | 'high' | 'medium' | 'low';
type SeverityDisplay = 'Critical' | 'High' | 'Medium' | 'Low';

interface SecurityStats {
  events24h: number;
  eventsTrend: number;
  criticalEvents: number;
  warningEvents: number;
  openFindings: number;
  findingsTrend: number;
  highRiskFindings: number;
  mediumRiskFindings: number;
  pendingApprovals: number;
  approvalsTrend: number;
  urgentApprovals: number;
  overdueApprovals: number;
}

interface ComplianceStandard {
  id: string;
  name: string;
  description: string;
  status: string;
  compliance: number;
  lastAudit: Date;
  nextAudit: Date;
  progress?: number;
}

interface SecurityAlert {
  id: string;
  title: string;
  description: string;
  severity: SeverityLevel;
  timestamp: Date;
  status: string;
  type: string;
}

interface Activity {
  id: string;
  type: string;
  user: string;
  timestamp: Date;
  description: string;
  action?: {
    label: string;
    route: string;
  };
  status?: string;
  highlight?: boolean;
  tags?: string[];
}

interface QuickAction {
  id: string;
  label: string;
  icon: string;
  action: string;
  class: string;
}

interface SystemHealthItem {
  name: string;
  status: string;
  usage: number;
  details: string;
  threshold: number;
}

// Router and services
const router = useRouter();
const toast = useToast();

// State
const loading = ref<boolean>(false);
const stats = ref({
  complianceScore: 92,
  securityScore: 88,
  auditScore: 94,
  dataPrivacyScore: 89,
  lastUpdated: new Date()
});

// Compliance frameworks data
const complianceFrameworks = ref([
  { id: 'iso27001', name: 'ISO 27001', status: 'Compliant', progress: 95 },
  { id: 'gdpr', name: 'GDPR', status: 'Partially Compliant', progress: 85 },
  { id: 'pci-dss', name: 'PCI DSS', status: 'Compliant', progress: 92 },
  { id: 'hipaa', name: 'HIPAA', status: 'In Progress', progress: 75 }
]);

// Security stats
const securityStats = ref<SecurityStats>({
  events24h: 24,
  eventsTrend: -12,
  criticalEvents: 3,
  warningEvents: 8,
  openFindings: 15,
  findingsTrend: -5,
  highRiskFindings: 4,
  mediumRiskFindings: 7,
  pendingApprovals: 8,
  approvalsTrend: 25,
  urgentApprovals: 2,
  overdueApprovals: 1
});

// Compliance standards
const complianceStandards = ref<ComplianceStandard[]>([
  {
    id: 'gdpr',
    name: 'GDPR',
    description: 'General Data Protection Regulation',
    status: 'Compliant',
    compliance: 98,
    lastAudit: subDays(new Date(), 30),
    nextAudit: new Date('2025-08-15')
  },
  {
    id: 'iso27001',
    name: 'ISO 27001',
    description: 'Information Security Management',
    status: 'In Progress',
    compliance: 85,
    lastAudit: subDays(new Date(), 60),
    nextAudit: new Date('2025-09-20')
  },
  {
    id: 'pci-dss',
    name: 'PCI DSS',
    status: 'non-compliant',
    progress: 30,
    lastAssessed: new Date('2025-03-01'),
    completedControls: 6,
    totalControls: 20
  }
]);

const recentActivities = ref<Activity[]>([
  {
    id: 'act-001',
    type: 'policy',
    user: 'admin',
    timestamp: subDays(new Date(), 0.1),
    description: 'Updated password policy to require 12 characters',
    action: { label: 'View Policy', route: '/compliance/policies/123' },
    status: 'Completed',
    highlight: true,
    tags: ['Security', 'Policy']
  },
  {
    id: 'act-002',
    type: 'user',
    user: 'johndoe',
    timestamp: subDays(new Date(), 0.5),
    description: 'Changed user role from Editor to Admin',
    action: { label: 'View User', route: '/users/johndoe' },
    status: 'Completed',
    tags: ['User Management']
  },
  {
    id: 'act-003',
    type: 'system',
    user: 'system',
    timestamp: subDays(new Date(), 1),
    description: 'Nightly backup completed successfully',
    action: { label: 'View Logs', route: '/system/backups' },
    status: 'Completed'
  }
]);

const securityAlerts = ref([
  {
    id: 1,
    title: 'Multiple Failed Login Attempts',
    description: '5 failed login attempts detected for user admin@example.com',
    severity: 'high',
    timestamp: new Date(Date.now() - 1000 * 60 * 15), // 15 minutes ago
    resolved: false
  },
  {
    id: 2,
    title: 'Outdated Security Policy',
    description: 'Password policy has not been updated in 90 days',
    severity: 'medium',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5), // 5 hours ago
    resolved: false
  },
  {
    id: 3,
    title: 'New Security Patch Available',
    description: 'Update to version 2.5.3 includes critical security fixes',
    severity: 'medium',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
    resolved: false
  },
  {
    id: 4,
    title: 'Unusual API Activity',
    description: 'Unusual API call pattern detected from IP 192.168.1.100',
    severity: 'high',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
  }
]);

// Format date helper
const formatDate = (date: Date | string | null | undefined): string => {
  if (!date) return 'N/A';
  try {
    return format(new Date(date), 'MMM d, yyyy');
  } catch (e) {
    console.error('Error formatting date:', e);
    return 'Invalid date';
  }
};

// Format time ago helper
const formatTimeAgo = (date: Date | string | null | undefined): string => {
  if (!date) return 'Just now';
  try {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - new Date(date).getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  } catch (e) {
    console.error('Error formatting time ago:', e);
    return 'Just now';
  }
};

// Get alert severity helper
const getAlertSeverity = (severity: string): 'success' | 'info' | 'warning' | 'danger' | 'secondary' | 'contrast' => {
  if (!severity) return 'info';
  const severityLower = severity.toLowerCase();
  if (severityLower.includes('high') || severityLower.includes('critical')) return 'danger';
  if (severityLower.includes('medium')) return 'warning';
  if (severityLower.includes('low')) return 'info';
  return 'info';
};

// Get compliance score color class
const getComplianceScoreColor = (score: number): string => {
  if (score >= 90) return 'bg-green-100 text-green-600';
  if (score >= 70) return 'bg-blue-100 text-blue-600';
  if (score >= 50) return 'bg-amber-100 text-amber-600';
  return 'bg-red-100 text-red-600';
};

// Fetch dashboard data
const fetchDashboardData = async (): Promise<void> => {
  loading.value = true;
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    // In a real app, you would fetch data from your API
    // const response = await api.get('/compliance/dashboard');
    // dashboardData.value = response.data;
    toast.add({
      severity: 'success',
      summary: 'Dashboard Updated',
      detail: 'Dashboard data has been refreshed',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};

const handleActivityAction = (activity: any) => {
  if (activity.action === 'review-policy') {
    router.push({ name: 'security-policies' });
  }
};

const runSecurityScan = () => {
  toast.add({
    severity: 'info',
    summary: 'Compliance Scan',
    detail: 'Compliance scan has been queued. You will be notified when complete.',
    life: 5000
  });
};

const resolveAlert = (alertId: number) => {
  const alert = securityAlerts.value.find(a => a.id === alertId);
  if (alert) {
    alert.resolved = true;
    toast.add({
      severity: 'success',
      summary: 'Alert Resolved',
      detail: 'The security alert has been marked as resolved.',
      life: 3000
    });
  }
};

const viewAlertDetails = (alert: SecurityAlert) => {
  // Navigate to alert details page or show in a dialog
  console.log('Viewing alert:', alert);
  // Example: router.push({ name: 'alert-details', params: { id: alert.id } });
};

// Lifecycle hooks
onMounted(() => {
  fetchDashboardData();
});

// Component name
defineOptions({
  name: 'ComplianceDashboard'
});
</script>

<template>
  <div class="compliance-dashboard">
    <!-- Header -->
    <div class="flex justify-content-between align-items-center mb-4">
      <h1 class="text-2xl font-bold">Compliance & Security Dashboard</h1>
      <Button 
        label="Run Security Scan" 
        icon="pi pi-shield" 
        :loading="loading"
        @click="runSecurityScan"
      />
    </div>

    <!-- Stats Overview -->
    <div class="grid">
      <div class="card">
        <h3 class="text-lg font-semibold mb-2">Compliance Score</h3>
        <div class="flex items-center">
          <div class="text-3xl font-bold mr-3">{{ stats.complianceScore }}%</div>
          <div class="flex-1">
            <ProgressBar 
              :model-value="stats.complianceScore" 
              :class="getProgressBarClass(stats.complianceScore)"
              :show-value="false"
            />
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="text-lg font-semibold mb-2">Security Score</h3>
        <div class="flex items-center">
          <div class="text-3xl font-bold mr-3">{{ stats.securityScore }}%</div>
          <div class="flex-1">
            <ProgressBar 
              :model-value="stats.securityScore" 
              :class="getProgressBarClass(stats.securityScore)"
              :show-value="false"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activities -->
    <div class="card">
      <h3 class="text-lg font-semibold mb-4">Recent Activities</h3>
      <ul class="activity-timeline">
        <li v-for="activity in recentActivities" :key="activity.id" class="activity-item">
          <div class="activity-marker" :style="{ backgroundColor: getActivityColor(activity.type) }">
            <i :class="getActivityIcon(activity.type)"></i>
          </div>
          <div class="activity-content">
            <div class="font-medium">{{ activity.title }}</div>
            <p class="text-sm text-gray-600">{{ activity.description }}</p>
            <div class="text-xs text-gray-500 mt-1">
              {{ formatTimeAgo(activity.timestamp) }} by {{ activity.user }}
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';
import { formatDistanceToNow } from 'date-fns';

// Toast
const toast = useToast();

// State
const loading = ref<boolean>(false);
const stats = ref({
  complianceScore: 92,
  securityScore: 88,
  auditScore: 95,
  dataPrivacyScore: 90,
  lastUpdated: new Date()
});

// Mock data for recent activities
const recentActivities = ref([
  {
    id: 'act-001',
    type: 'audit',
    title: 'Security Policy Updated',
    description: 'Password policy has been updated to meet new requirements',
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
    user: 'admin@example.com'
  },
  {
    id: 'act-002',
    type: 'login',
    title: 'User Login',
    description: 'User logged in from 192.168.1.100',
    timestamp: new Date(Date.now() - 1000 * 60 * 120), // 2 hours ago
    user: 'user@example.com'
  }
]);

// Helper functions
const formatTimeAgo = (date: Date | string): string => {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
};

const getProgressBarClass = (score: number): string => {
  if (score >= 90) return 'progress-bar-success';
  if (score >= 70) return 'progress-bar-warning';
  return 'progress-bar-danger';
};

const getActivityIcon = (type: string): string => {
  const icons: Record<string, string> = {
    audit: 'pi pi-shield',
    login: 'pi pi-sign-in',
    update: 'pi pi-pencil',
    alert: 'pi pi-exclamation-triangle'
  };
  return icons[type] || 'pi pi-info-circle';
};

const getActivityColor = (type: string): string => {
  const colors: Record<string, string> = {
    audit: '#3b82f6',
    login: '#10b981',
    update: '#f59e0b',
    alert: '#ef4444'
  };
  return colors[type] || '#6b7280';
};

const runSecurityScan = async (): Promise<void> => {
  loading.value = true;
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    toast.add({
      severity: 'success',
      summary: 'Scan Complete',
      detail: 'Security scan completed successfully',
      life: 3000
    });
  } catch (error) {
    console.error('Security scan failed:', error);
    toast.add({
      severity: 'error',
      summary: 'Scan Failed',
      detail: 'Failed to complete security scan',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};

// Lifecycle hooks can be added here when needed
</script>

<style scoped>
/* Component styles */
.compliance-dashboard {
  padding: 1.5rem;
}

/* Responsive grid for stats */
.grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  margin-bottom: 1.5rem;
}

/* Card styles */
.card {
  background: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

/* Activity timeline */
.activity-timeline {
  position: relative;
  padding-left: 1.5rem;
  margin: 0;
  list-style: none;
}

.activity-timeline::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0.5rem;
  width: 2px;
  background-color: #e2e8f0;
}

.activity-item {
  position: relative;
  padding-bottom: 1.5rem;
  padding-left: 1.5rem;
  border-left: 1px solid #e2e8f0;
}

.activity-item:last-child {
  padding-bottom: 0;
  border-left-color: transparent;
}

.activity-marker {
  position: absolute;
  left: -0.5rem;
  top: 0.25rem;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
}

.activity-content {
  padding: 0.5rem 0;
}

/* Progress bar styles */
:deep(.p-progressbar) {
  height: 0.5rem;
  border-radius: 0.25rem;
  background-color: #e5e7eb;
}

:deep(.p-progressbar-value) {
  border-radius: 0.25rem;
}

.progress-bar-success :deep(.p-progressbar-value) {
  background-color: #10b981;
}

.progress-bar-warning :deep(.p-progressbar-value) {
  background-color: #f59e0b;
}

.progress-bar-danger :deep(.p-progressbar-value) {
  background-color: #ef4444;
}

.progress-bar-info :deep(.p-progressbar-value) {
  background-color: #3b82f6;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .compliance-dashboard {
    padding: 1rem;
  }
  
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
