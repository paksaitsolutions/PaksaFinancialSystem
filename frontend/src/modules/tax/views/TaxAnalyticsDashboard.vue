<template>
  <v-container fluid class="pa-6">
    <!-- Page Header -->
    <v-row class="mb-6" align="center">
      <v-col cols="12" sm="6" md="8">
        <h1 class="text-h4 font-weight-bold">
          <v-tooltip bottom>
            <template v-slot:activator="{ props }">
              <span v-bind="props">Tax Analytics Dashboard</span>
            </template>
            <span>View comprehensive tax analysis, compliance metrics, and optimization recommendations</span>
          </v-tooltip>
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Analyze tax trends, compliance, and optimization opportunities
        </p>
      </v-col>
      <v-col cols="12" sm="6" md="4" class="d-flex justify-end align-center">
        <v-btn
          color="secondary"
          variant="text"
          class="mr-2"
          :loading="isLoading"
          @click="refreshData"
          :disabled="isLoading"
        >
          <v-icon start>mdi-refresh</v-icon>
          <span>Refresh</span>
          <v-tooltip bottom>
            <template v-slot:activator="{ props: tooltipProps }">
              <v-icon v-bind="tooltipProps" size="small" class="ml-1">mdi-information-outline</v-icon>
            </template>
            <span>Reload all tax analytics data from the server</span>
          </v-tooltip>
        </v-btn>
        
        <v-menu offset-y>
          <template v-slot:activator="{ props: menuProps }">
            <v-btn
              color="primary"
              v-bind="menuProps"
              :loading="isLoading"
              :disabled="isLoading"
            >
              <v-icon start>mdi-download</v-icon>
              <span>Export</span>
              <v-icon end>mdi-menu-down</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="downloadReport('csv')">
              <v-list-item-title>
                <v-icon start>mdi-file-document-outline</v-icon>
                Export as CSV
              </v-list-item-title>
            </v-list-item>
            <v-list-item @click="downloadReport('excel')">
              <v-list-item-title>
                <v-icon start>mdi-microsoft-excel</v-icon>
                Export as Excel
              </v-list-item-title>
            </v-list-item>
            <v-divider></v-divider>
            <v-list-item @click="downloadReport('pdf')">
              <v-list-item-title>
                <v-icon start>mdi-file-pdf-box</v-icon>
                Generate PDF Report
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-col>
    </v-row>

    <!-- Rest of the component content remains the same -->
    <!-- ... -->
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTaxAnalyticsStore } from '@/modules/tax/store/analytics';

const taxAnalyticsStore = useTaxAnalyticsStore();
const isLoading = ref(false);

const selectedPeriod = computed({
  get() {
    return taxAnalyticsStore.selectedPeriod;
  },
  set(value) {
    taxAnalyticsStore.setSelectedPeriod(value);
  }
});

const periodOptions = computed(() => taxAnalyticsStore.periodOptions);
const analyticsData = computed(() => taxAnalyticsStore.analyticsData);
const insights = computed(() => taxAnalyticsStore.insights);

async function fetchAnalytics() {
  try {
    isLoading.value = true;
    await taxAnalyticsStore.fetchAnalytics();
  } catch (error) {
    console.error('Error fetching tax analytics:', error);
  } finally {
    isLoading.value = false;
  }
}

function refreshData() {
  fetchAnalytics();
}

// Export functions
const exportInsights = async () => {
  try {
    loading.value = true;
    const response = await taxAnalyticsStore.exportAnalytics('csv');
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `tax-insights-${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error('Error exporting insights:', error);
  } finally {
    loading.value = false;
  }
};

const exportExcel = async () => {
  try {
    loading.value = true;
    const response = await taxAnalyticsStore.exportAnalytics('excel');
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `tax-report-${new Date().toISOString().split('T')[0]}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error('Error exporting to Excel:', error);
  } finally {
    loading.value = false;
  }
};

const exportPdf = async () => {
  try {
    loading.value = true;
    const response = await taxAnalyticsStore.exportAnalytics('pdf');
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    window.open(url, '_blank');
  } catch (error) {
    console.error('Error exporting to PDF:', error);
  } finally {
    loading.value = false;
  }
};

const downloadReport = (format: 'csv' | 'excel' | 'pdf') => {
  switch (format) {
    case 'csv':
      exportInsights();
      break;
    case 'excel':
      exportExcel();
      break;
    case 'pdf':
      exportPdf();
      break;
    default:
      console.warn('Unsupported export format:', format);
  }
};

onMounted(() => {
  fetchAnalytics();
});
</script>
