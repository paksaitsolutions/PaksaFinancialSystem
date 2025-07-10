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

const securityStats = ref({
  events24h: 12,
  eventsTrend: -5,
  openFindings: 5,
  highRiskFindings: 2,
  mediumRiskFindings: 3,
  pendingApprovals: 4,
  urgentApprovals: 1,
  overdueApprovals: 1,
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

const getStatusSeverity = (status: string): 'success' | 'warning' | 'danger' | 'info' => {
  if (!status) return 'info';
  const statusLower = status.toLowerCase();
  if (statusLower.includes('compliant')) {
    return statusLower.startsWith('non') ? 'danger' : 'success';
  }
  if (statusLower.includes('progress')) return 'info';
  if (statusLower.includes('partial')) return 'warning';
  return 'info';
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
    case 'audit': return 'text-blue-500';
    case 'alert': return 'text-red-500';
    case 'approval': return 'text-green-500';
    case 'compliance': return 'text-purple-500';
    case 'user': return 'text-gray-500';
    default: return 'text-gray-400';
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
  },
  {
    id: 'pci-dss',
    name: 'PCI DSS',
    description: 'Payment Card Industry Data Security Standard',
    status: 'Partial',
    compliance: 75,
    lastAudit: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10), // 10 days ago
    nextAudit: new Date(Date.now() + 1000 * 60 * 60 * 24 * 80) // 80 days from now
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
  },
  {
    id: 'act-002',
    type: 'alert',
    title: 'Unusual Login Detected',
    description: 'A login from an unrecognized device was blocked.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    user: 'system'
  }
]);
</script>

<template>
  <div class="p-4 bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-800">Compliance Dashboard</h1>
        <p class="text-gray-500 mt-1">Overview of security, compliance, and system health.</p>
      </div>
      <div class="flex items-center gap-2">
        <Button icon="pi pi-sync" label="Refresh" class="p-button-outlined" :loading="loading" @click="fetchDashboardData" />
        <Button icon="pi pi-shield" label="Run Scan" class="p-button-secondary" @click="runSecurityScan" />
        <Button icon="pi pi-cog" class="p-button-text" @click="navigateTo('ComplianceSettings')" />
      </div>
    </header>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card>
        <template #title><span class="font-semibold">Compliance Score</span></template>
        <template #content>
          <div class="flex items-center justify-between">
            <div class="text-4xl font-bold text-blue-600">{{ stats.complianceScore }}%</div>
            <i class="pi pi-shield p-3 bg-blue-100 text-blue-600 rounded-full text-2xl"></i>
          </div>
          <div class="mt-3">
            <ProgressBar :value="stats.complianceScore" :show-value="false" style="height: 6px"></ProgressBar>
            <div class="text-sm text-gray-500 mt-2">Status: <span class="font-semibold text-green-600">Excellent</span></div>
          </div>
        </template>
      </Card>
      <Card>
        <template #title><span class="font-semibold">Security Events (24h)</span></template>
        <template #content>
          <div class="flex items-center justify-between">
            <div class="text-4xl font-bold text-orange-600">{{ securityStats.events24h }}</div>
            <i class="pi pi-exclamation-triangle p-3 bg-orange-100 text-orange-600 rounded-full text-2xl"></i>
          </div>
          <div class="mt-3 text-sm text-gray-500">
            <span :class="securityStats.eventsTrend < 0 ? 'text-green-500' : 'text-red-500'">
              <i :class="securityStats.eventsTrend < 0 ? 'pi pi-arrow-down' : 'pi pi-arrow-up'"></i>
              {{ Math.abs(securityStats.eventsTrend) }}%
            </span>
            vs. previous day
          </div>
        </template>
      </Card>
      <Card>
        <template #title><span class="font-semibold">Open Findings</span></template>
        <template #content>
          <div class="flex items-center justify-between">
            <div class="text-4xl font-bold text-red-600">{{ securityStats.openFindings }}</div>
            <i class="pi pi-bug p-3 bg-red-100 text-red-600 rounded-full text-2xl"></i>
          </div>
          <div class="mt-3 flex gap-2">
            <Tag severity="danger" :value="`${securityStats.highRiskFindings} High Risk`"></Tag>
            <Tag severity="warning" :value="`${securityStats.mediumRiskFindings} Medium`"></Tag>
          </div>
        </template>
      </Card>
      <Card>
        <template #title><span class="font-semibold">Pending Approvals</span></template>
        <template #content>
          <div class="flex items-center justify-between">
            <div class="text-4xl font-bold text-cyan-600">{{ securityStats.pendingApprovals }}</div>
            <i class="pi pi-check-square p-3 bg-cyan-100 text-cyan-600 rounded-full text-2xl"></i>
          </div>
          <div class="mt-3 flex gap-2">
             <Tag severity="danger" :value="`${securityStats.urgentApprovals} Urgent`"></Tag>
             <Tag severity="warning" :value="`${securityStats.overdueApprovals} Overdue`"></Tag>
          </div>
        </template>
      </Card>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Compliance Standards (Left) -->
      <div class="lg:col-span-2">
        <Card class="h-full">
          <template #title>
            <div class="flex justify-between items-center">
              <span class="font-semibold">Compliance Standards</span>
              <Button label="View All" class="p-button-text" @click="navigateTo('SecurityPolicies')" />
            </div>
          </template>
          <template #content>
            <DataTable :value="complianceStandards" :loading="loading" responsiveLayout="scroll" class="-m-4">
              <Column field="name" header="Standard" :sortable="true">
                <template #body="{ data }">
                  <div class="font-semibold">{{ data.name }}</div>
                  <div class="text-sm text-gray-500">{{ data.description }}</div>
                </template>
              </Column>
              <Column field="status" header="Status" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column header="Compliance" :sortable="true" sortField="compliance">
                <template #body="{ data }">
                  <div class="flex items-center gap-2">
                    <ProgressBar :value="data.compliance" :showValue="false" style="height: 8px; width: 100px"></ProgressBar>
                    <span class="font-medium">{{ data.compliance }}%</span>
                  </div>
                </template>
              </Column>
              <Column field="nextAudit" header="Next Audit" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.nextAudit) }}
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>

      <!-- Recent Activities (Right) -->
      <div class="lg:col-span-1">
        <Card class="h-full">
          <template #title>
            <div class="flex justify-between items-center">
              <span class="font-semibold">Recent Activities</span>
              <Button label="View All" class="p-button-text" @click="navigateTo('SecurityEvents')" />
            </div>
          </template>
          <template #content>
            <div class="space-y-4">
              <div v-for="activity in recentActivities" :key="activity.id" class="flex items-start gap-3">
                <div class="flex-shrink-0">
                  <span :class="getActivityColor(activity.type)" class="flex items-center justify-center h-8 w-8 rounded-full bg-gray-100">
                    <i :class="getActivityIcon(activity.type)"></i>
                  </span>
                </div>
                <div>
                  <p class="font-medium text-gray-800">{{ activity.title }}</p>
                  <p class="text-sm text-gray-500">{{ activity.description }}</p>
                  <div class="text-xs text-gray-400 mt-1">
                    <span>{{ formatTimeAgo(activity.timestamp) }}</span>
                    <span v-if="activity.user" class="mx-1">&middot;</span>
                    <span v-if="activity.user">{{ activity.user }}</span>
                  </div>
                </div>
              </div>
              <div v-if="!recentActivities.length" class="text-center text-gray-500 py-4">
                No recent activities.
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>
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
