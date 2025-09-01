<template>
  <div class="tax-compliance-dashboard">
    <!-- Page Header -->
    <div class="page-header">
      <h1>Tax Compliance Dashboard</h1>
      <div class="actions">
        <Button 
          icon="pi pi-refresh" 
          label="Refresh" 
          @click="refreshData" 
          :loading="isLoading"
          class="p-button-text"
        />
        <Button 
          icon="pi pi-file-export" 
          label="Export Report" 
          @click="exportReport" 
          :loading="isExporting"
          class="p-button-text"
        />
      </div>
    </div>

    <!-- Compliance Status Card -->
    <Card class="mb-4">
      <template #title>
        <div class="flex align-items-center">
          <i class="pi pi-shield mr-2" style="font-size: 1.5rem"></i>
          <span>Compliance Status</span>
        </div>
      </template>
      <template #content>
        <div v-if="hasComplianceData">
          <div class="compliance-overview mb-4">
            <div class="flex align-items-center justify-content-between">
              <div>
                <h3>Overall Status</h3>
                <Tag 
                  :severity="getComplianceStatusSeverity(complianceStatus.overall_status)"
                  :value="formatStatus(complianceStatus.overall_status)"
                  class="status-tag"
                />
                <p class="text-500 mt-2">Last updated: {{ formatDate(complianceStatus.last_updated) }}</p>
              </div>
              <div class="text-right">
                <div class="text-500 mb-2">Open Issues</div>
                <div class="text-2xl font-bold">{{ complianceStatus.open_issues?.length || 0 }}</div>
              </div>
            </div>
          </div>

          <Divider />

          <div class="compliance-details">
            <h4 class="mb-3">Status by Tax Type</h4>
            <div class="grid">
              <div 
                v-for="status in complianceStatus.status_by_tax_type" 
                :key="status.tax_type"
                class="col-12 md:col-6 lg:col-4 xl:col-3"
              >
                <div class="status-card p-3 mb-3 border-round">
                  <div class="flex justify-content-between align-items-center">
                    <div>
                      <div class="text-500">{{ status.tax_type_name || status.tax_type }}</div>
                      <div class="font-bold">
                        <Tag 
                          :severity="getComplianceStatusSeverity(status.status)"
                          :value="formatStatus(status.status)"
                          class="status-tag"
                        />
                      </div>
                    </div>
                    <div class="text-right">
                      <div class="text-500">Next Due</div>
                      <div class="font-bold">
                        {{ status.next_due_date ? formatDate(status.next_due_date, 'short') : 'N/A' }}
                        <span v-if="status.days_until_due !== undefined" 
                              :class="getDueDateClass(status.days_until_due)">
                          ({{ status.days_until_due }} days)
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center p-4">
          <ProgressSpinner v-if="isLoading" />
          <p v-else>No compliance data available</p>
        </div>
      </template>
    </Card>

    <!-- Upcoming Filings -->
    <div class="grid">
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-calendar mr-2" style="font-size: 1.5rem"></i>
              <span>Upcoming Tax Filings</span>
            </div>
          </template>
          <template #content>
            <div v-if="hasUpcomingFilings">
              <DataTable 
                :value="upcomingFilings" 
                :loading="isLoading"
                :paginator="upcomingFilings.length > 5"
                :rows="5"
                :rowsPerPageOptions="[5, 10, 25]"
                responsiveLayout="scroll"
              >
                <Column field="tax_type" header="Tax Type" :sortable="true">
                  <template #body="{ data }">
                    {{ data.tax_type_name || data.tax_type }}
                  </template>
                </Column>
                <Column field="jurisdiction_code" header="Jurisdiction" :sortable="true" />
                <Column field="due_date" header="Due Date" :sortable="true">
                  <template #body="{ data }">
                    <div>
                      <div>{{ formatDate(data.due_date, 'short') }}</div>
                      <small :class="getDueDateClass(data.days_until_due)">
                        ({{ data.days_until_due }} days)
                      </small>
                    </div>
                  </template>
                </Column>
                <Column field="frequency" header="Frequency" :sortable="true">
                  <template #body="{ data }">
                    <Tag :value="formatFrequency(data.frequency)" />
                  </template>
                </Column>
                <Column header="Actions" style="width: 100px">
                  <template #body="{ data }">
                    <Button 
                      icon="pi pi-eye" 
                      class="p-button-text p-button-sm" 
                      @click="viewFilingDetails(data)"
                      v-tooltip.top="'View Details'"
                    />
                    <Button 
                      icon="pi pi-file-edit" 
                      class="p-button-text p-button-sm" 
                      @click="prepareFiling(data)"
                      v-tooltip.top="'Prepare Filing'"
                    />
                  </template>
                </Column>
              </DataTable>
            </div>
            <div v-else class="text-center p-4">
              <ProgressSpinner v-if="isLoading" />
              <p v-else>No upcoming tax filings</p>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 lg:col-4">
        <Card>
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-exclamation-triangle mr-2" style="font-size: 1.5rem"></i>
              <span>Open Issues</span>
            </div>
          </template>
          <template #content>
            <div v-if="hasOpenIssues">
              <Timeline :value="complianceStatus.open_issues" layout="vertical" class="timeline-issues">
                <template #content="{ item }">
                  <div class="p-2 border-round" :class="getIssueSeverityClass(item)">
                    <div class="flex justify-content-between align-items-center">
                      <span class="font-bold">{{ item.title }}</span>
                      <Tag :severity="getIssueSeverity(item.severity)" :value="item.severity" />
                    </div>
                    <p class="m-0 text-sm">{{ item.description }}</p>
                    <div class="flex justify-content-between mt-2">
                      <small class="text-500">{{ formatDate(item.created_at, 'short') }}</small>
                      <Button 
                        label="View" 
                        icon="pi pi-arrow-right" 
                        class="p-button-text p-button-sm" 
                        @click="viewIssueDetails(item)"
                      />
                    </div>
                  </div>
                </template>
              </Timeline>
            </div>
            <div v-else class="text-center p-4">
              <i class="pi pi-check-circle text-green-500 text-5xl mb-3"></i>
              <p class="m-0">No open issues</p>
              <small class="text-500">You're all caught up!</small>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Recent Filings -->
    <Card class="mt-4">
      <template #title>
        <div class="flex align-items-center">
          <i class="pi pi-history mr-2" style="font-size: 1.5rem"></i>
          <span>Recent Tax Filings</span>
        </div>
      </template>
      <template #content>
        <div v-if="hasFilings">
          <DataTable 
            :value="filings" 
            :loading="isLoading"
            :paginator="true"
            :rows="5"
            :rowsPerPageOptions="[5, 10, 25]"
            responsiveLayout="scroll"
          >
            <Column field="tax_type" header="Tax Type" :sortable="true">
              <template #body="{ data }">
                {{ data.tax_type_name || data.tax_type }}
              </template>
            </Column>
            <Column field="jurisdiction_code" header="Jurisdiction" :sortable="true" />
            <Column field="period_start" header="Period" :sortable="true">
              <template #body="{ data }">
                {{ formatDate(data.period_start, 'short') }} - {{ formatDate(data.period_end, 'short') }}
              </template>
            </Column>
            <Column field="filing_date" header="Filed On" :sortable="true">
              <template #body="{ data }">
                {{ formatDate(data.filing_date, 'short') }}
              </template>
            </Column>
            <Column field="status" header="Status" :sortable="true">
              <template #body="{ data }">
                <Tag :value="formatStatus(data.status)" :severity="getFilingStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column field="total_amount" header="Amount" :sortable="true">
              <template #body="{ data }">
                {{ formatCurrency(data.total_amount, data.currency) }}
              </template>
            </Column>
            <Column header="Actions" style="width: 100px">
              <template #body="{ data }">
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-text p-button-sm" 
                  @click="viewFilingDetails(data)"
                  v-tooltip.top="'View Details'"
                />
                <Button 
                  icon="pi pi-download" 
                  class="p-button-text p-button-sm" 
                  @click="downloadFiling(data)"
                  v-tooltip.top="'Download'"
                />
              </template>
            </Column>
          </DataTable>
        </div>
        <div v-else class="text-center p-4">
          <ProgressSpinner v-if="isLoading" />
          <p v-else>No recent tax filings found</p>
        </div>
      </template>
    </Card>

    <!-- Export Dialog -->
    <Dialog 
      v-model:visible="showExportDialog" 
      header="Export Report" 
      :modal="true" 
      :dismissableMask="true"
      :style="{ width: '450px' }"
    >
      <div class="p-fluid">
        <div class="field">
          <label for="exportFormat">Format</label>
          <Dropdown 
            id="exportFormat" 
            v-model="exportFormat" 
            :options="['PDF', 'Excel', 'CSV']" 
            placeholder="Select a format"
          />
        </div>
        <div class="field">
          <label for="dateRange">Date Range</label>
          <Calendar 
            id="dateRange" 
            v-model="exportDateRange" 
            selectionMode="range" 
            :manualInput="false" 
            dateFormat="yy-mm-dd"
            showIcon
          />
        </div>
      </div>
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          @click="showExportDialog = false" 
          class="p-button-text"
        />
        <Button 
          label="Export" 
          icon="pi pi-download" 
          @click="confirmExport" 
          :loading="isExporting"
        />
      </template>
    </Dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
// Mock tax reporting composable
const useTaxReporting = () => ({
  generateReport: () => Promise.resolve({ success: true }),
  exportReport: () => Promise.resolve({ success: true })
});
import { formatDate, formatCurrency } from '@/utils/formatters';

export default defineComponent({
  name: 'TaxComplianceDashboard',
  setup() {
    const router = useRouter();
    const toast = useToast();
    const {
      // State
      isLoading,
      error,
      liabilityReport,
      complianceStatus,
      upcomingFilings,
      filings,
      
      // Computed
      hasComplianceData,
      hasUpcomingFilings,
      hasFilings,
      isCompliant,
      
      // Methods
      initialize,
      fetchTaxComplianceStatus,
      fetchUpcomingTaxFilings,
      fetchTaxFilings,
      exportTaxReport
    } = useTaxReporting();

    // Local state
    const isExporting = ref(false);
    const showExportDialog = ref(false);
    const exportFormat = ref('PDF');
    const exportDateRange = ref();

    // Computed
    const hasOpenIssues = computed(() => {
      return hasComplianceData.value && 
             complianceStatus.value?.open_issues && 
             complianceStatus.value.open_issues.length > 0;
    });

    // Methods
    const refreshData = async () => {
      try {
        await Promise.all([
          fetchTaxComplianceStatus(),
          fetchUpcomingTaxFilings(90),
          fetchTaxFilings({ limit: 5 })
        ]);
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Tax data refreshed',
          life: 3000
        });
      } catch (error) {
        console.error('Error refreshing tax data:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to refresh tax data',
          life: 5000
        });
      }
    };

    const exportReport = () => {
      showExportDialog.value = true;
    };

    const confirmExport = async () => {
      if (!exportFormat.value) {
        toast.add({
          severity: 'warn',
          summary: 'Warning',
          detail: 'Please select a format',
          life: 3000
        });
        return;
      }

      isExporting.value = true;
      
      try {
        const [startDate, endDate] = exportDateRange.value || [];
        const format = exportFormat.value.toLowerCase() as 'pdf' | 'excel' | 'csv';
        
        const filter = {
          start_date: startDate ? formatDate(startDate, 'yyyy-MM-dd') : '',
          end_date: endDate ? formatDate(endDate, 'yyyy-MM-dd') : ''
        };
        
        const blob = await exportTaxReport(format, filter);
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tax-report-${formatDate(new Date(), 'yyyyMMdd')}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Export started successfully',
          life: 3000
        });
        
        showExportDialog.value = false;
      } catch (error) {
        console.error('Error exporting report:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to export report',
          life: 5000
        });
      } finally {
        isExporting.value = false;
      }
    };

    const viewFilingDetails = (filing: any) => {
      router.push({ name: 'tax-filing-details', params: { id: filing.id } });
    };

    const prepareFiling = (filing: any) => {
      // Navigate to prepare filing page with pre-filled data
      router.push({
        name: 'prepare-tax-filing',
        query: {
          taxType: filing.tax_type,
          jurisdiction: filing.jurisdiction_code,
          periodStart: filing.period_start,
          periodEnd: filing.period_end
        }
      });
    };

    const downloadFiling = async (filing: any) => {
      try {
        // This would be implemented to download the filing document
        console.log('Download filing:', filing.id);
        // const blob = await downloadFilingDocument(filing.id, filing.document_id);
        // downloadFile(blob, `filing-${filing.id}.pdf`);
        
        toast.add({
          severity: 'info',
          summary: 'Info',
          detail: 'Download functionality will be implemented soon',
          life: 3000
        });
      } catch (error) {
        console.error('Error downloading filing:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to download filing',
          life: 5000
        });
      }
    };

    const viewIssueDetails = (issue: any) => {
      // Navigate to issue details page
      console.log('View issue:', issue.id);
      // router.push({ name: 'tax-issue-details', params: { id: issue.id } });
      
      toast.add({
        severity: 'info',
        summary: 'Info',
        detail: 'Issue details will be implemented soon',
        life: 3000
      });
    };

    // Formatting helpers
    const formatStatus = (status: string) => {
      if (!status) return '';
      return status.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');
    };

    const getComplianceStatusSeverity = (status: string) => {
      switch (status) {
        case 'compliant': return 'success';
        case 'warning': return 'warning';
        case 'non_compliant': return 'danger';
        default: return 'info';
      }
    };

    const getFilingStatusSeverity = (status: string) => {
      switch (status) {
        case 'draft': return 'info';
        case 'prepared': return 'warning';
        case 'submitted': return 'success';
        case 'accepted': return 'success';
        case 'rejected': return 'danger';
        case 'paid': return 'success';
        default: return 'info';
      }
    };

    const getIssueSeverity = (severity: string) => {
      switch (severity.toLowerCase()) {
        case 'low': return 'info';
        case 'medium': return 'warning';
        case 'high': return 'warning';
        case 'critical': return 'danger';
        default: return 'info';
      }
    };

    const getIssueSeverityClass = (issue: any) => {
      return `bg-${getIssueSeverity(issue.severity)}-100 border-${getIssueSeverity(issue.severity)}-500`;
    };

    const getDueDateClass = (daysUntilDue: number) => {
      if (daysUntilDue < 0) return 'text-red-500 font-bold';
      if (daysUntilDue <= 7) return 'text-orange-500 font-bold';
      if (daysUntilDue <= 30) return 'text-yellow-500';
      return 'text-green-500';
    };

    const formatFrequency = (frequency: string) => {
      if (!frequency) return '';
      return frequency
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    };

    // Lifecycle hooks
    onMounted(() => {
      initialize();
    });

    return {
      // State
      isLoading,
      isExporting,
      showExportDialog,
      exportFormat,
      exportDateRange,
      
      // Data
      liabilityReport,
      complianceStatus,
      upcomingFilings,
      filings,
      
      // Computed
      hasComplianceData,
      hasUpcomingFilings,
      hasFilings,
      isCompliant,
      hasOpenIssues,
      
      // Methods
      refreshData,
      exportReport,
      confirmExport,
      viewFilingDetails,
      prepareFiling,
      downloadFiling,
      viewIssueDetails,
      formatDate,
      formatCurrency,
      formatStatus,
      getComplianceStatusSeverity,
      getFilingStatusSeverity,
      getIssueSeverity,
      getIssueSeverityClass,
      getDueDateClass,
      formatFrequency
    };
  }
});
</script>

<style scoped>
.tax-compliance-dashboard {
  padding: 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-header h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-color);
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.compliance-overview {
  padding: 1rem;
  background-color: var(--surface-50);
  border-radius: var(--border-radius);
}

.status-tag {
  font-size: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 12px;
}

.status-card {
  background-color: var(--surface-50);
  border: 1px solid var(--surface-200);
  transition: all 0.3s ease;
}

.status-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.timeline-issues {
  margin-top: 1rem;
}

.timeline-issues .p-timeline-event-content {
  padding: 0.5rem 0;
}

.timeline-issues .p-timeline-event-opposite {
  display: none;
}

.timeline-issues .p-timeline-event-connector {
  background-color: var(--surface-200);
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .actions {
    width: 100%;
    justify-content: flex-end;
  }
}

@media (max-width: 640px) {
  .actions {
    flex-direction: column;
    width: 100%;
  }
  
  .actions .p-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
