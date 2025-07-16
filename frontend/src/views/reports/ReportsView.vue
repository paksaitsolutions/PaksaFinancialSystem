<template>
  <div class="reports-view">
    <Toast position="top-right" />
    
    <div class="flex flex-column h-full">
      <!-- Header -->
      <div class="flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="m-0">Reports</h1>
          <Breadcrumb :home="breadcrumbHome" :model="breadcrumbItems" class="p-0 border-none" />
        </div>
        <div class="flex gap-2">
          <Button 
            label="Refresh" 
            icon="pi pi-refresh" 
            class="p-button-text"
            :loading="loading"
            @click="refreshReports"
          />
          <Button 
            label="New Report" 
            icon="pi pi-plus" 
            class="p-button-primary"
            @click="openNewReportDialog"
          />
        </div>
      </div>
      
      <!-- Main Content -->
      <div class="flex flex-grow-1 gap-4 h-0">
        <!-- Sidebar -->
        <div class="w-3 border-right-1 surface-border p-3 overflow-y-auto" style="min-width: 250px;">
          <div class="mb-4">
            <h3 class="text-lg font-medium mb-2">Categories</h3>
            <div class="flex flex-column gap-1">
              <Button 
                v-for="category in categories" 
                :key="category.id"
                :label="category.name" 
                :icon="category.icon || 'pi pi-folder'"
                :class="['p-button-text p-button-sm text-left justify-content-start', 
                        { 'p-highlight': selectedCategoryId === category.id }]"
                @click="selectCategory(category.id)"
              >
                <span class="ml-2">{{ category.name }}</span>
                <Tag :value="category.count" severity="info" class="ml-auto" />
              </Button>
            </div>
          </div>
          
          <Divider />
          
          <div class="mb-4">
            <div class="flex justify-content-between align-items-center mb-2">
              <h3 class="text-lg font-medium m-0">Favorites</h3>
              <i class="pi pi-star-fill text-yellow-500" />
            </div>
            <div v-if="favoriteReports.length > 0" class="flex flex-column gap-1">
              <Button 
                v-for="report in favoriteReports" 
                :key="report.id"
                :label="report.name" 
                icon="pi pi-star-fill"
                class="p-button-text p-button-sm text-left justify-content-start p-0"
                @click="runReport(report)"
              >
                <span class="ml-2">{{ report.name }}</span>
              </Button>
            </div>
            <div v-else class="text-500 text-sm">
              No favorite reports yet. Click the star icon on a report to add it to favorites.
            </div>
          </div>
          
          <Divider />
          
          <div>
            <div class="flex justify-content-between align-items-center mb-2">
              <h3 class="text-lg font-medium m-0">Recent</h3>
              <i class="pi pi-history" />
            </div>
            <div v-if="recentReports.length > 0" class="flex flex-column gap-1">
              <Button 
                v-for="report in recentReports" 
                :key="report.id"
                :label="report.name" 
                icon="pi pi-clock"
                class="p-button-text p-button-sm text-left justify-content-start p-0"
                @click="runReport(report)"
              >
                <span class="ml-2">{{ report.name }}</span>
              </Button>
            </div>
            <div v-else class="text-500 text-sm">
              No recent reports. Run a report to see it here.
            </div>
          </div>
        </div>
        
        <!-- Main Content Area -->
        <div class="flex-grow-1 p-3 overflow-y-auto">
          <ReportList 
            ref="reportListRef"
            @run="runReport"
          />
        </div>
      </div>
    </div>
    
    <!-- Report Runner Dialog -->
    <ReportRunnerDialog 
      v-model:visible="reportRunner.visible"
      :report="reportRunner.report"
      :loading="reportRunner.loading"
      :error="reportRunner.error"
      :data="reportRunner.data"
      :columns="reportRunner.columns"
      :last-run="reportRunner.lastRun"
      :is-favorite="isFavorite"
      @refresh="loadReportData"
      @close="closeReportRunner"
      @export="exportReport"
      @toggle-favorite="toggleFavorite"
      @schedule="openScheduleDialog"
      @customize="openCustomizeDialog"
    />
    
    <!-- Schedule Report Dialog -->
    <Dialog 
      v-model:visible="scheduleDialog.visible" 
      header="Schedule Report" 
      :style="{ width: '500px' }"
      :modal="true"
      class="p-fluid"
    >
      <div class="field">
        <label for="scheduleName">Schedule Name</label>
        <InputText id="scheduleName" v-model="scheduleDialog.name" class="w-full" />
      </div>
      
      <div class="field">
        <label>Frequency</label>
        <div class="flex flex-wrap gap-3">
          <div class="flex align-items-center">
            <RadioButton 
              id="frequency1" 
              name="frequency" 
              value="daily" 
              v-model="scheduleDialog.frequency"
            />
            <label for="frequency1" class="ml-2">Daily</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="frequency2" 
              name="frequency" 
              value="weekly" 
              v-model="scheduleDialog.frequency"
            />
            <label for="frequency2" class="ml-2">Weekly</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="frequency3" 
              name="frequency" 
              value="monthly" 
              v-model="scheduleDialog.frequency"
            />
            <label for="frequency3" class="ml-2">Monthly</label>
          </div>
        </div>
      </div>
      
      <div class="field">
        <label for="time">Time</label>
        <Calendar 
          id="time" 
          v-model="scheduleDialog.time" 
          timeOnly 
          hourFormat="12" 
          class="w-full"
        />
      </div>
      
      <div class="field">
        <label for="recipients">Recipients</label>
        <Chips id="recipients" v-model="scheduleDialog.recipients" class="w-full" />
      </div>
      
      <div class="field">
        <label for="format">Format</label>
        <Dropdown 
          id="format" 
          v-model="scheduleDialog.format" 
          :options="['PDF', 'Excel', 'CSV']" 
          class="w-full"
        />
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="scheduleDialog.visible = false"
        />
        <Button 
          label="Save Schedule" 
          icon="pi pi-check" 
          class="p-button-primary"
          @click="saveSchedule"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useReportsStore } from '@/stores/reports';
import ReportList from './components/ReportList.vue';
import ReportRunnerDialog from './components/ReportRunnerDialog.vue';
import type { Report } from '@/types/reports';

const router = useRouter();
const reportsStore = useReportsStore();
const reportListRef = ref<InstanceType<typeof ReportList>>();

// Breadcrumb
const breadcrumbHome = {
  icon: 'pi pi-home',
  to: '/',
};

const breadcrumbItems = [
  { label: 'Reports' },
];

// State
const selectedCategoryId = ref<string | null>(null);
const loading = ref(false);

// Report Runner
const reportRunner = ref({
  visible: false,
  loading: false,
  error: null as string | null,
  report: null as Report | null,
  data: null as any[] | null,
  columns: [] as Array<{ field: string; header: string; visible: boolean; width?: number; sortable?: boolean }>,
  lastRun: null as string | null,
});

// Schedule Dialog
const scheduleDialog = ref({
  visible: false,
  name: '',
  frequency: 'daily',
  time: new Date(),
  recipients: [] as string[],
  format: 'PDF',
});

// Computed
const categories = computed(() => reportsStore.categories);
const favoriteReports = computed(() => reportsStore.favoriteReports);
const recentReports = computed(() => reportsStore.recentReports);
const isFavorite = computed(() => {
  if (!reportRunner.value.report) return false;
  return reportsStore.favorites.some(fav => fav.reportId === reportRunner.value.report?.id);
});

// Methods
const refreshReports = async () => {
  loading.value = true;
  try {
    await reportsStore.fetchReports();
  } finally {
    loading.value = false;
  }
};

const selectCategory = (categoryId: string) => {
  selectedCategoryId.value = selectedCategoryId.value === categoryId ? null : categoryId;
  // Filter reports by category
  if (reportListRef.value) {
    // @ts-ignore - We know this method exists on the ref
    reportListRef.value.filterByCategory(selectedCategoryId.value);
  }
};

const runReport = async (report: Report) => {
  reportRunner.value = {
    ...reportRunner.value,
    visible: true,
    loading: true,
    report,
    error: null,
  };
  
  await loadReportData();
};

const loadReportData = async () => {
  if (!reportRunner.value.report) return;
  
  reportRunner.value.loading = true;
  reportRunner.value.error = null;
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock data based on report type
    const mockData = generateMockData(reportRunner.value.report);
    
    reportRunner.value.data = mockData.data;
    reportRunner.value.columns = mockData.columns.map((col: string) => ({
      field: col,
      header: col.split(/(?=[A-Z])/).join(' ').replace(/^./, str => str.toUpperCase()),
      visible: true,
      sortable: true,
    }));
    
    reportRunner.value.lastRun = new Date().toISOString();
  } catch (error) {
    console.error('Error loading report data:', error);
    reportRunner.value.error = 'Failed to load report data. Please try again.';
  } finally {
    reportRunner.value.loading = false;
  }
};

const closeReportRunner = () => {
  reportRunner.value.visible = false;
  // Small delay to allow animation to complete before resetting
  setTimeout(() => {
    reportRunner.value = {
      visible: false,
      loading: false,
      error: null,
      report: null,
      data: null,
      columns: [],
      lastRun: null,
    };
  }, 300);
};

const exportReport = async (format: string) => {
  if (!reportRunner.value.report) return;
  
  try {
    await reportsStore.exportReport(reportRunner.value.report.id, format as any);
  } catch (error) {
    console.error('Error exporting report:', error);
  }
};

const toggleFavorite = async () => {
  if (!reportRunner.value.report) return;
  
  try {
    await reportsStore.toggleFavorite(reportRunner.value.report.id);
  } catch (error) {
    console.error('Error toggling favorite:', error);
  }
};

const openNewReportDialog = () => {
  // Implementation for new report dialog
  console.log('Open new report dialog');
};

const openScheduleDialog = () => {
  if (!reportRunner.value.report) return;
  
  scheduleDialog.value = {
    visible: true,
    name: `${reportRunner.value.report.name} Schedule`,
    frequency: 'daily',
    time: new Date(),
    recipients: [],
    format: 'PDF',
  };
};

const saveSchedule = async () => {
  if (!reportRunner.value.report) return;
  
  try {
    // In a real app, this would save the schedule to the backend
    console.log('Saving schedule:', {
      reportId: reportRunner.value.report.id,
      ...scheduleDialog.value,
    });
    
    scheduleDialog.value.visible = false;
    
    // Show success message
    // @ts-ignore - We know this exists from PrimeVue
    useToast().add({
      severity: 'success',
      summary: 'Schedule Saved',
      detail: 'The report schedule has been saved successfully.',
      life: 3000,
    });
  } catch (error) {
    console.error('Error saving schedule:', error);
    
    // Show error message
    // @ts-ignore - We know this exists from PrimeVue
    useToast().add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save schedule. Please try again.',
      life: 5000,
    });
  }
};

const openCustomizeDialog = () => {
  // Implementation for customize dialog
  console.log('Open customize dialog');
};

// Helper function to generate mock data for the report
const generateMockData = (report: Report) => {
  // This is just a simple example - in a real app, this would come from an API
  const mockTemplates: Record<string, { columns: string[]; data: any[] }> = {
    'financial': {
      columns: ['date', 'account', 'debit', 'credit', 'balance'],
      data: Array.from({ length: 50 }, (_, i) => ({
        id: i + 1,
        date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        account: `Account ${Math.floor(Math.random() * 10) + 1}`,
        description: `Transaction ${i + 1}`,
        debit: Math.random() > 0.3 ? (Math.random() * 1000).toFixed(2) : null,
        credit: Math.random() > 0.7 ? (Math.random() * 1000).toFixed(2) : null,
        balance: (Math.random() * 10000 - 2000).toFixed(2),
      })),
    },
    'inventory': {
      columns: ['item', 'category', 'quantity', 'unitPrice', 'totalValue'],
      data: Array.from({ length: 50 }, (_, i) => ({
        id: i + 1,
        item: `Item ${String.fromCharCode(65 + (i % 26))}${Math.floor(i / 26) + 1}`,
        category: ['Electronics', 'Clothing', 'Food', 'Office', 'Other'][Math.floor(Math.random() * 5)],
        quantity: Math.floor(Math.random() * 100) + 1,
        unitPrice: (Math.random() * 100 + 1).toFixed(2),
        totalValue: (Math.random() * 10000 + 1).toFixed(2),
        lastUpdated: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
      })),
    },
    'sales': {
      columns: ['orderId', 'customer', 'product', 'quantity', 'price', 'total', 'date'],
      data: Array.from({ length: 50 }, (_, i) => ({
        id: i + 1,
        orderId: `ORD-${1000 + i}`,
        customer: `Customer ${String.fromCharCode(65 + (i % 10))}`,
        product: ['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard', 'Mouse', 'Headphones', 'Charger', 'Case', 'Stand'][i % 10],
        quantity: Math.floor(Math.random() * 5) + 1,
        price: [999.99, 699.99, 399.99, 249.99, 129.99, 49.99, 199.99, 29.99, 39.99, 59.99][i % 10],
        total: 0, // Will be calculated
        date: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
      })).map(item => ({
        ...item,
        total: (item.quantity * item.price).toFixed(2),
      })),
    },
  };
  
  // Default template if no match found
  const defaultTemplate = {
    columns: ['id', 'name', 'value', 'date'],
    data: Array.from({ length: 20 }, (_, i) => ({
      id: i + 1,
      name: `Item ${i + 1}`,
      value: (Math.random() * 1000).toFixed(2),
      date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    })),
  };
  
  // Try to find a matching template based on report name or category
  const templateKey = Object.keys(mockTemplates).find(key => 
    report.name.toLowerCase().includes(key) || 
    report.categoryId?.toLowerCase().includes(key)
  );
  
  return templateKey ? mockTemplates[templateKey] : defaultTemplate;
};

// Lifecycle hooks
onMounted(async () => {
  await reportsStore.initialize();
});
</script>

<style scoped>
.reports-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.p-breadcrumb) {
  background: transparent;
  border: none;
  padding: 0.5rem 0;
}
</style>
