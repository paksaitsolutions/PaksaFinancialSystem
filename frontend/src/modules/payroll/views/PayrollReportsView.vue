<template>
  <v-container fluid class="pa-6">
    <!-- Page Header -->
    <v-row class="mb-6" align="center">
      <v-col cols="12" sm="6" md="8">
        <h1 class="text-h4 font-weight-bold">Payroll Reports</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Generate and view payroll reports
        </p>
      </v-col>
      <v-col cols="12" sm="6" md="4" class="text-right">
        <v-btn
          color="primary"
          prepend-icon="mdi-refresh"
          variant="outlined"
          class="mr-2"
          @click="refreshReports"
          :loading="isLoading"
        >
          Refresh
        </v-btn>
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="showReportDialog = true"
        >
          New Report
        </v-btn>
      </v-col>
    </v-row>

    <!-- Report Templates -->
    <v-card class="mb-6">
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-file-document-multiple</v-icon>
        <span>Report Templates</span>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <v-row>
          <v-col
            v-for="template in reportTemplates"
            :key="template.id"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <v-card
              variant="outlined"
              class="h-100 d-flex flex-column"
              :disabled="template.disabled"
              :class="{ 'opacity-50': template.disabled }"
            >
              <v-card-item>
                <template v-slot:prepend>
                  <v-avatar :color="template.color" class="mr-4" size="large">
                    <v-icon :icon="template.icon" size="x-large"></v-icon>
                  </v-avatar>
                </template>
                <v-card-title class="text-subtitle-1 font-weight-bold">
                  {{ template.name }}
                </v-card-title>
                <v-card-subtitle class="text-caption">
                  {{ template.description }}
                </v-card-subtitle>
              </v-card-item>
              <v-divider></v-divider>
              <v-card-actions class="mt-auto">
                <v-spacer></v-spacer>
                <v-btn
                  variant="text"
                  color="primary"
                  size="small"
                  :loading="template.loading"
                  :disabled="template.disabled"
                  @click="generateReport(template)"
                >
                  Generate
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Recent Reports -->
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-history</v-icon>
        <span>Recent Reports</span>
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="Search reports"
          single-line
          hide-details
          variant="outlined"
          density="compact"
          class="mr-4"
          style="max-width: 300px;"
        ></v-text-field>
      </v-card-title>
      <v-divider></v-divider>
      <v-data-table
        :headers="headers"
        :items="recentReports"
        :search="search"
        :loading="isLoading"
        :items-per-page="10"
        class="elevation-1"
      >
        <template v-slot:item.type="{ item }">
          <v-chip :color="getReportColor(item.raw.type)" size="small">
            {{ formatReportType(item.raw.type) }}
          </v-chip>
        </template>
        <template v-slot:item.status="{ item }">
          <v-chip :color="getStatusColor(item.raw.status)" size="small">
            {{ formatStatus(item.raw.status) }}
          </v-chip>
        </template>
        <template v-slot:item.createdAt="{ item }">
          {{ formatDate(item.raw.createdAt) }}
        </template>
        <template v-slot:item.actions="{ item }">
          <v-tooltip text="View Report" location="top">
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                icon
                variant="text"
                size="small"
                color="primary"
                class="mr-1"
                @click="viewReport(item.raw)"
              >
                <v-icon>mdi-eye</v-icon>
              </v-btn>
            </template>
          </v-tooltip>
          <v-tooltip text="Download" location="top">
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                icon
                variant="text"
                size="small"
                color="primary"
                class="mr-1"
                @click="downloadReport(item.raw)"
                :loading="item.raw.downloading"
              >
                <v-icon>mdi-download</v-icon>
              </v-btn>
            </template>
          </v-tooltip>
          <v-tooltip text="Delete" location="top">
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                icon
                variant="text"
                size="small"
                color="error"
                @click="confirmDeleteReport(item.raw)"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </template>
          </v-tooltip>
        </template>
      </v-data-table>
    </v-card>

    <!-- Report Generation Dialog -->
    <v-dialog v-model="showReportDialog" max-width="800">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>Generate New Report</span>
          <v-btn icon @click="showReportDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pt-4">
          <v-form v-model="isFormValid" @submit.prevent="generateCustomReport">
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="newReport.type"
                  :items="reportTypes"
                  label="Report Type"
                  item-title="name"
                  item-value="id"
                  variant="outlined"
                  density="comfortable"
                  :rules="[v => !!v || 'Report type is required']"
                  required
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="newReport.format"
                  :items="['PDF', 'Excel', 'CSV']"
                  label="Format"
                  variant="outlined"
                  density="comfortable"
                  :rules="[v => !!v || 'Format is required']"
                  required
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-menu
                  v-model="showStartDatePicker"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  min-width="auto"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-bind="props"
                      v-model="newReport.dateRange[0]"
                      label="Start Date"
                      prepend-inner-icon="mdi-calendar"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || 'Start date is required']"
                      readonly
                      required
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="newReport.dateRange[0]"
                    @input="showStartDatePicker = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="12" md="6">
                <v-menu
                  v-model="showEndDatePicker"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  min-width="auto"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-bind="props"
                      v-model="newReport.dateRange[1]"
                      label="End Date"
                      prepend-inner-icon="mdi-calendar"
                      variant="outlined"
                      density="comfortable"
                      :rules="[v => !!v || 'End date is required', v => !v || v >= newReport.dateRange[0] || 'End date must be after start date']"
                      readonly
                      required
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="newReport.dateRange[1]"
                    :min="newReport.dateRange[0]"
                    @input="showEndDatePicker = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="newReport.notes"
                  label="Notes"
                  variant="outlined"
                  density="comfortable"
                  rows="2"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="px-4 py-3">
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="showReportDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            :loading="isGenerating"
            :disabled="!isFormValid || isGenerating"
            @click="generateCustomReport"
          >
            Generate Report
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6">Delete Report</v-card-title>
        <v-card-text>
          Are you sure you want to delete this report? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteReport">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useSnackbar } from '@/composables/useSnackbar';
import { format } from 'date-fns';

const { showSnackbar } = useSnackbar();
const router = useRouter();

// State
const isLoading = ref(false);
const isGenerating = ref(false);
const isFormValid = ref(false);
const showReportDialog = ref(false);
const showDeleteDialog = ref(false);
const showStartDatePicker = ref(false);
const showEndDatePicker = ref(false);
const search = ref('');
const reportToDelete = ref<any>(null);

// Form data
const newReport = ref({
  type: '',
  format: 'PDF',
  dateRange: [
    format(new Date(new Date().setDate(1)), 'yyyy-MM-dd'), // First day of current month
    format(new Date(), 'yyyy-MM-dd') // Today
  ],
  notes: ''
});

// Report templates
const reportTemplates = ref([
  {
    id: 'payroll-summary',
    name: 'Payroll Summary',
    description: 'Summary of all payroll transactions',
    icon: 'mdi-file-document-outline',
    color: 'primary',
    loading: false,
    disabled: false
  },
  {
    id: 'tax-report',
    name: 'Tax Report',
    description: 'Detailed tax information',
    icon: 'mdi-cash-multiple',
    color: 'success',
    loading: false,
    disabled: false
  },
  {
    id: 'employee-earnings',
    name: 'Employee Earnings',
    description: 'Detailed earnings by employee',
    icon: 'mdi-account-group',
    color: 'info',
    loading: false,
    disabled: false
  },
  {
    id: 'department-summary',
    name: 'Department Summary',
    description: 'Payroll costs by department',
    icon: 'mdi-office-building',
    color: 'warning',
    loading: false,
    disabled: true // Example of a disabled template
  }
]);

// Report types for dropdown
const reportTypes = [
  { id: 'payroll-summary', name: 'Payroll Summary' },
  { id: 'tax-report', name: 'Tax Report' },
  { id: 'employee-earnings', name: 'Employee Earnings' },
  { id: 'department-summary', name: 'Department Summary' },
  { id: 'custom', name: 'Custom Report' }
];

// Recent reports data
const recentReports = ref([
  {
    id: '1',
    name: 'Monthly Payroll Summary',
    type: 'payroll-summary',
    status: 'completed',
    format: 'PDF',
    createdAt: new Date('2023-05-15T10:30:00'),
    fileSize: '2.5 MB',
    downloading: false
  },
  {
    id: '2',
    name: 'Q2 Tax Report',
    type: 'tax-report',
    status: 'completed',
    format: 'Excel',
    createdAt: new Date('2023-04-30T14:45:00'),
    fileSize: '1.8 MB',
    downloading: false
  },
  {
    id: '3',
    name: 'April Employee Earnings',
    type: 'employee-earnings',
    status: 'failed',
    format: 'CSV',
    createdAt: new Date('2023-04-05T09:15:00'),
    fileSize: '3.2 MB',
    error: 'Processing timeout',
    downloading: false
  },
  {
    id: '4',
    name: 'March Payroll Summary',
    type: 'payroll-summary',
    status: 'completed',
    format: 'PDF',
    createdAt: new Date('2023-03-15T11:20:00'),
    fileSize: '2.3 MB',
    downloading: false
  },
  {
    id: '5',
    name: 'Q1 Tax Report',
    type: 'tax-report',
    status: 'completed',
    format: 'Excel',
    createdAt: new Date('2023-01-31T16:30:00'),
    fileSize: '1.7 MB',
    downloading: false
  }
]);

// Table headers
const headers = [
  { title: 'Report Name', key: 'name', sortable: true },
  { title: 'Type', key: 'type', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Format', key: 'format', sortable: true },
  { title: 'Created', key: 'createdAt', sortable: true },
  { title: 'Size', key: 'fileSize', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
];

// Methods
const refreshReports = async () => {
  try {
    isLoading.value = true;
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    showSnackbar('Reports refreshed successfully');
  } catch (error) {
    console.error('Error refreshing reports:', error);
    showSnackbar('Failed to refresh reports', 'error');
  } finally {
    isLoading.value = false;
  }
};

const generateReport = async (template: any) => {
  try {
    template.loading = true;
    // Simulate report generation
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Add to recent reports
    const newReport = {
      id: Date.now().toString(),
      name: `${template.name} - ${format(new Date(), 'MMM d, yyyy')}`,
      type: template.id,
      status: 'completed',
      format: 'PDF',
      createdAt: new Date(),
      fileSize: '1.2 MB',
      downloading: false
    };
    
    recentReports.value.unshift(newReport);
    showSnackbar(`${template.name} generated successfully`);
  } catch (error) {
    console.error('Error generating report:', error);
    showSnackbar(`Failed to generate ${template.name}`, 'error');
  } finally {
    template.loading = false;
  }
};

const generateCustomReport = async () => {
  if (!isFormValid.value) return;
  
  try {
    isGenerating.value = true;
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Add to recent reports
    const reportType = reportTypes.find(rt => rt.id === newReport.value.type)?.name || 'Custom Report';
    const newReportItem = {
      id: Date.now().toString(),
      name: `${reportType} - ${format(new Date(newReport.value.dateRange[0]), 'MMM d')} to ${format(newReport.value.dateRange[1], 'MMM d, yyyy')}`,
      type: newReport.value.type,
      status: 'completed',
      format: newReport.value.format,
      createdAt: new Date(),
      fileSize: '1.5 MB',
      downloading: false
    };
    
    recentReports.value.unshift(newReportItem);
    showReportDialog.value = false;
    showSnackbar('Report generated successfully');
    
    // Reset form
    newReport.value = {
      type: '',
      format: 'PDF',
      dateRange: [
        format(new Date(new Date().setDate(1)), 'yyyy-MM-dd'),
        format(new Date(), 'yyyy-MM-dd')
      ],
      notes: ''
    };
  } catch (error) {
    console.error('Error generating custom report:', error);
    showSnackbar('Failed to generate report', 'error');
  } finally {
    isGenerating.value = false;
  }
};

const viewReport = (report: any) => {
  // In a real app, this would open the report in a viewer or new tab
  showSnackbar(`Viewing report: ${report.name}`);
};

const downloadReport = async (report: any) => {
  try {
    report.downloading = true;
    // Simulate download
    await new Promise(resolve => setTimeout(resolve, 1000));
    showSnackbar(`Downloading ${report.name}...`);
    
    // In a real app, this would trigger a file download
    const link = document.createElement('a');
    link.href = '#'; // Replace with actual download URL
    link.download = `${report.name.toLowerCase().replace(/\s+/g, '-')}.${report.format.toLowerCase()}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error('Error downloading report:', error);
    showSnackbar('Failed to download report', 'error');
  } finally {
    report.downloading = false;
  }
};

const confirmDeleteReport = (report: any) => {
  reportToDelete.value = report;
  showDeleteDialog.value = true;
};

const deleteReport = () => {
  if (!reportToDelete.value) return;
  
  try {
    const index = recentReports.value.findIndex(r => r.id === reportToDelete.value.id);
    if (index !== -1) {
      recentReports.value.splice(index, 1);
      showSnackbar('Report deleted successfully');
    }
  } catch (error) {
    console.error('Error deleting report:', error);
    showSnackbar('Failed to delete report', 'error');
  } finally {
    showDeleteDialog.value = false;
    reportToDelete.value = null;
  }
};

// Formatting helpers
const formatDate = (date: Date) => {
  return format(new Date(date), 'MMM d, yyyy h:mm a');
};

const formatReportType = (type: string) => {
  const typeMap: Record<string, string> = {
    'payroll-summary': 'Payroll Summary',
    'tax-report': 'Tax Report',
    'employee-earnings': 'Employee Earnings',
    'department-summary': 'Dept. Summary',
    'custom': 'Custom'
  };
  return typeMap[type] || type;
};

const formatStatus = (status: string) => {
  return status.charAt(0).toUpperCase() + status.slice(1);
};

const getReportColor = (type: string) => {
  const colorMap: Record<string, string> = {
    'payroll-summary': 'primary',
    'tax-report': 'success',
    'employee-earnings': 'info',
    'department-summary': 'warning',
    'custom': 'secondary'
  };
  return colorMap[type] || 'grey';
};

const getStatusColor = (status: string) => {
  const colorMap: Record<string, string> = {
    'completed': 'success',
    'processing': 'info',
    'pending': 'warning',
    'failed': 'error'
  };
  return colorMap[status] || 'grey';
};

// Lifecycle hooks
onMounted(() => {
  // Load initial data
  refreshReports();
});
</script>

<style scoped>
.v-card {
  transition: opacity 0.3s ease;
}

.opacity-50 {
  opacity: 0.5;
}

.v-avatar {
  background: rgba(var(--v-theme-primary), 0.1);
}
</style>
