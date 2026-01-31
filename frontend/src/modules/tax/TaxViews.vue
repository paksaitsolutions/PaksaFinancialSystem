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
      <v-col cols="12" sm="6" md="4" class="text-right">
        <v-btn
          color="primary"
          prepend-icon="mdi-refresh"
          :loading="isLoading"
          @click="refreshData"
          :disabled="isLoading"
        >
          <v-tooltip bottom>
            <template v-slot:activator="{ props }">
              <span v-bind="props">Refresh Data</span>
            </template>
            <span>Reload all tax analytics data from the server</span>
          </v-tooltip>
        </v-btn>
      </v-col>
    </v-row>

    <!-- Date Range Filter -->
    <v-card class="mb-6">
      <v-card-title class="text-subtitle-1 font-weight-bold">
        Date Range
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-select
              v-model="selectedPeriod"
              :items="periodOptions"
              label="Select Period"
              density="compact"
              variant="outlined"
              :loading="isLoading"
              @update:model-value="fetchAnalytics"
            >
              <template v-slot:prepend>
                <v-tooltip bottom>
                  <template v-slot:activator="{ props }">
                    <v-icon v-bind="props">mdi-calendar</v-icon>
                  </template>
                  <span>Select the time period for analysis</span>
                </v-tooltip>
              </template>
            </v-select>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- AI Insights Section -->
    <v-card class="mb-6">
      <v-card-title class="text-subtitle-1 font-weight-bold">
        AI Insights & Recommendations
      </v-card-title>
      <v-card-text>
        <v-tabs v-model="activeTab" class="mb-4">
          <v-tab value="compliance">
            <v-tooltip bottom>
              <template v-slot:activator="{ props }">
                <span v-bind="props">Compliance Analysis</span>
              </template>
              <span>View AI-generated analysis of tax compliance metrics</span>
            </v-tooltip>
          </v-tab>
          <v-tab value="optimization">
            <v-tooltip bottom>
              <template v-slot:activator="{ props }">
                <span v-bind="props">Optimization Recommendations</span>
              </template>
              <span>Get AI-powered suggestions for tax optimization</span>
            </v-tooltip>
          </v-tab>
          <v-tab value="risk">
            <v-tooltip bottom>
              <template v-slot:activator="{ props }">
                <span v-bind="props">Risk Assessment</span>
              </template>
              <span>Analyze tax compliance and audit risk using AI</span>
            </v-tooltip>
          </v-tab>
        </v-tabs>
        
        <div v-if="insights[activeTab]">
          <v-card-text class="text-body-1">
            {{ insights[activeTab] }}
          </v-card-text>
          <v-card-actions>
            <v-btn
              color="primary"
              prepend-icon="mdi-download"
              :loading="exportService.loading"
              @click="exportInsights"
            >
              Export Insights
            </v-btn>
          </v-card-actions>
        </div>
        <div v-else>
          <v-card-text>
            <v-skeleton-loader
              type="text@3"
              class="mb-4"
            ></v-skeleton-loader>
            <v-skeleton-loader
              type="text@2"
            ></v-skeleton-loader>
          </v-card-text>
        </div>
      </v-card-text>
    </v-card>

    <!-- Analytics Cards -->
    <v-row>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <v-card-title class="text-h6">
            <v-tooltip bottom>
              <template v-slot:activator="{ props }">
                <span v-bind="props">Total Tax Amount</span>
              </template>
              <span>Total tax liability across all jurisdictions</span>
            </v-tooltip>
          </v-card-title>
          <v-card-text class="text-h4 font-weight-bold">
            {{ formatCurrency(totalTax) }}
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <v-card-title class="text-h6">
            <v-tooltip bottom>
              <template v-slot:activator="{ props }">
                <span v-bind="props">Average Tax per Employee</span>
              </template>
              <span>Average tax contribution per employee</span>
            </v-tooltip>
          </v-card-title>
          <v-card-text class="text-h4 font-weight-bold">
            {{ formatCurrency(avgTaxPerEmployee) }}
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <v-card-title class="text-h6">
            <v-tooltip bottom>
              <template v-slot:activator="{ props }">
                <span v-bind="props">Tax Compliance Rate</span>
              </template>
              <span>Percentage of tax obligations met on time</span>
            </v-tooltip>
          </v-card-title>
          <v-card-text class="text-h4 font-weight-bold">
            {{ complianceRate }}%
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="pa-4">
          <v-card-title class="text-h6">
            <v-tooltip bottom>
              <template v-slot:activator="{ props }">
                <span v-bind="props">Exemption Usage</span>
              </template>
              <span>Total value of tax exemptions claimed</span>
            </v-tooltip>
          </v-card-title>
          <v-card-text class="text-h4 font-weight-bold">
            {{ formatCurrency(totalExemptions) }}
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts Section -->
    <v-row>
      <v-col cols="12" sm="12" md="6">
        <v-card class="mb-6">
          <v-card-title class="text-subtitle-1 font-weight-bold">
            <v-tooltip bottom>
              <template v-slot:activator="{ props }">
                <span v-bind="props">Tax Distribution by Jurisdiction</span>
              </template>
              <span>Breakdown of tax liability across different tax jurisdictions</span>
            </v-tooltip>
          </v-card-title>
          <v-card-text>
            <v-skeleton-loader
              v-if="isLoading"
              type="image"
              class="mb-4"
            ></v-skeleton-loader>
            <v-chart v-else :options="jurisdictionChart" />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="12" md="6">
        <v-card class="mb-6">
          <v-card-title class="text-subtitle-1 font-weight-bold">
            <v-tooltip bottom>
              <template v-slot:activator="{ props }">
                <span v-bind="props">Exemption Utilization</span>
              </template>
              <span>Usage of different tax exemptions by category</span>
            </v-tooltip>
          </v-card-title>
          <v-card-text>
            <v-skeleton-loader
              v-if="isLoading"
              type="image"
              class="mb-4"
            ></v-skeleton-loader>
            <v-chart v-else :options="exemptionChart" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Advanced Analytics Section -->
    <v-card class="mb-6">
      <v-card-title class="text-subtitle-1 font-weight-bold">
        Advanced Analytics
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="12" md="6">
            <v-card class="mb-4">
              <v-card-title class="text-subtitle-2">
                <v-tooltip bottom>
                  <template v-slot:activator="{ props }">
                    <span v-bind="props">Tax Trend Analysis</span>
                  </template>
                  <span>Historical analysis of tax trends and seasonality</span>
                </v-tooltip>
              </v-card-title>
              <v-card-text>
                <v-skeleton-loader
                  v-if="isLoading"
                  type="image"
                  class="mb-4"
                ></v-skeleton-loader>
                <v-chart v-else :options="trendChart" />
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="12" md="6">
            <v-card>
              <v-card-title class="text-subtitle-2">
                <v-tooltip bottom>
                  <template v-slot:activator="{ props }">
                    <span v-bind="props">Compliance Risk Matrix</span>
                  </template>
                  <span>Analysis of tax compliance risks and exposure</span>
                </v-tooltip>
              </v-card-title>
              <v-card-text>
                <v-skeleton-loader
                  v-if="isLoading"
                  type="image"
                  class="mb-4"
                ></v-skeleton-loader>
                <v-chart v-else :options="riskMatrixChart" />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Export & Actions -->
    <v-card>
      <v-card-title class="text-subtitle-1 font-weight-bold">
        Export & Actions
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="12" md="4">
            <v-btn
              block
              color="primary"
              prepend-icon="mdi-file-excel"
              :loading="exportService.loading"
              @click="exportExcel"
            >
              Export to Excel
            </v-btn>
          </v-col>
          <v-col cols="12" sm="12" md="4">
            <v-btn
              block
              color="primary"
              prepend-icon="mdi-file-pdf"
              :loading="exportService.loading"
              @click="exportPdf"
            >
              Export to PDF
            </v-btn>
          </v-col>
          <v-col cols="12" sm="12" md="4">
            <v-btn
              block
              color="primary"
              prepend-icon="mdi-chart-box"
              :loading="exportService.loading"
              @click="downloadReport"
            >
              Download Report
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTaxAnalyticsStore } from '@/modules/tax/store/analytics';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { useExportService } from '@/services/export';

const taxAnalyticsStore = useTaxAnalyticsStore();
const exportService = useExportService();

const activeTab = ref('compliance');

const selectedPeriod = computed({
  get: () => taxAnalyticsStore.selectedPeriod,
  set: (value) => {
    taxAnalyticsStore.selectedPeriod = value;
  }
});

const periodOptions = computed(() => taxAnalyticsStore.periodOptions);
const analyticsData = computed(() => taxAnalyticsStore.analyticsData);
const insights = computed(() => taxAnalyticsStore.insights);
const isLoading = computed(() => taxAnalyticsStore.isLoading);

const totalTax = computed(() => analyticsData.value.totalTax);
const avgTaxPerEmployee = computed(() => analyticsData.value.avgTaxPerEmployee);
const complianceRate = computed(() => analyticsData.value.complianceRate);
const totalExemptions = computed(() => analyticsData.value.totalExemptions);

const jurisdictionChart = computed(() => ({
  xAxis: [],
  yAxis: [],
  series: [{
    type: 'pie',
    data: Object.entries(analyticsData.value.jurisdictionalBreakdown).map(([key, value]) => ({
      name: key,
      value: value
    }))
  }],
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  }
}));

const exemptionChart = computed(() => ({
  xAxis: {
    type: 'category',
    data: Object.keys(analyticsData.value.exemptionUsage)
  },
  yAxis: {
    type: 'value'
  },
  series: [{
    type: 'bar',
    data: Object.values(analyticsData.value.exemptionUsage)
  }],
  tooltip: {
    trigger: 'axis'
  }
}));

const trendChart = computed(() => ({
  xAxis: {
    type: 'category',
    data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  },
  yAxis: {
    type: 'value'
  },
  series: [{
    type: 'line',
    data: [820, 932, 901, 934, 1290, 1330]
  }],
  tooltip: {
    trigger: 'axis'
  }
}));

const riskMatrixChart = computed(() => ({
  xAxis: {
    type: 'category',
    data: ['Low', 'Medium', 'High']
  },
  yAxis: {
    type: 'value'
  },
  series: [{
    type: 'bar',
    stack: 'total',
    data: [300, 500, 700]
  }, {
    type: 'bar',
    stack: 'total',
    data: [200, 300, 400]
  }],
  tooltip: {
    trigger: 'axis'
  }
}));

const fetchAnalytics = async () => {
  try {
    await taxAnalyticsStore.fetchAnalytics();
  } catch (error) {
    console.error('Error fetching analytics:', error);
    // Add error handling here
  }
};

const refreshData = async () => {
  if (isLoading.value) return;
  
  try {
    await fetchAnalytics();
  } catch (error) {
    console.error('Error refreshing data:', error);
    // Add error handling here
  }
};

const exportInsights = async () => {
  if (exportService.loading) return;
  
  try {
    await exportService.exportText(
      'tax_insights.txt',
      insights.value[activeTab.value]
    );
  } catch (error) {
    console.error('Error exporting insights:', error);
    // Add error handling here
  }
};

const exportExcel = async () => {
  if (exportService.loading) return;
  
  try {
    await exportService.exportExcel(
      'tax_analytics',
      analyticsData.value
    );
  } catch (error) {
    console.error('Error exporting Excel:', error);
    // Add error handling here
  }
};

const exportPdf = async () => {
  if (exportService.loading) return;
  
  try {
    await exportService.exportPdf(
      'tax_analytics',
      analyticsData.value
    );
  } catch (error) {
    console.error('Error exporting PDF:', error);
    // Add error handling here
  }
};

const downloadReport = async () => {
  if (exportService.loading) return;
  
  try {
    await exportService.downloadReport(
      'tax_analytics',
      analyticsData.value,
      insights.value
    );
  } catch (error) {
    console.error('Error downloading report:', error);
    // Add error handling here
  }
};

onMounted(() => {
  fetchAnalytics();
});
</script>          <v-card-title class="text-subtitle-1 font-weight-bold">
            Exemption Usage Trends
          </v-card-title>
          <v-card-text>
            <v-chart :options="exemptionChart" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- AI Insights -->
    <v-card class="mb-6">
      <v-card-title class="text-subtitle-1 font-weight-bold">
        AI Tax Insights
      </v-card-title>
      <v-card-text>
        <v-expansion-panels>
          <v-expansion-panel>
            <v-expansion-panel-title>
              Tax Compliance Analysis
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <pre>{{ insights.compliance }}</pre>
            </v-expansion-panel-text>
          </v-expansion-panel>
          <v-expansion-panel>
            <v-expansion-panel-title>
              Tax Optimization Recommendations
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <pre>{{ insights.optimization }}</pre>
            </v-expansion-panel-text>
          </v-expansion-panel>
          <v-expansion-panel>
            <v-expansion-panel-title>
              Risk Assessment
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <pre>{{ insights.risk }}</pre>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTaxAnalyticsService } from '@/services/analytics/taxAnalyticsService';

const taxAnalyticsService = useTaxAnalyticsService();

const selectedPeriod = ref('current_month');
const periodOptions = [
  { text: 'Current Month', value: 'current_month' },
  { text: 'Current Quarter', value: 'current_quarter' },
  { text: 'Current Year', value: 'current_year' },
  { text: 'Custom Range', value: 'custom' }
];

const analytics = ref({
  totalTax: 0,
  avgTaxPerEmployee: 0,
  complianceRate: 0,
  totalExemptions: 0,
  jurisdictionalBreakdown: {},
  exemptionUsage: {}
});

const insights = ref({
  compliance: '',
  optimization: '',
  risk: ''
});

const jurisdictionChart = computed(() => ({
  title: { text: 'Tax by Jurisdiction' },
  series: [{
    type: 'pie',
    data: Object.entries(analytics.value.jurisdictionalBreakdown).map(([key, value]) => ({
      name: key,
      value: value
    }))
  }]
}));

const exemptionChart = computed(() => ({
  title: { text: 'Exemption Usage' },
  xAxis: { type: 'category' },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar',
    data: Object.entries(analytics.value.exemptionUsage).map(([key, value]) => ({
      name: key,
      value: value
    }))
  }]
}));

const totalTax = computed(() => analytics.value.totalTax);
const avgTaxPerEmployee = computed(() => analytics.value.avgTaxPerEmployee);
const complianceRate = computed(() => analytics.value.complianceRate.toFixed(2));
const totalExemptions = computed(() => analytics.value.totalExemptions);

async function fetchAnalytics() {
  try {
    const { trends, analysis } = await taxAnalyticsService.analyzeTaxTrends(selectedPeriod.value);
    analytics.value = trends;
    insights.value = analysis;
  } catch (error) {
    console.error('Error fetching analytics:', error);
  }
}

async function refreshData() {
  await fetchAnalytics();
}

onMounted(() => {
  fetchAnalytics();
});
</script>
