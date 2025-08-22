<template>
  <div class="report-container">
    <!-- Report Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">{{ title }}</h1>
        <p class="text-gray-600 dark:text-gray-400">{{ description }}</p>
      </div>
      <div class="flex space-x-2">
        <Button 
          v-if="showExport"
          :label="exportLabel || 'Export'" 
          :icon="exportIcon || 'pi pi-download'"
          class="p-button-outlined"
          @click="handleExport" 
          :loading="exporting"
          :disabled="!canExport"
        />
        <Button 
          v-if="showPrint"
          label="Print" 
          icon="pi pi-print" 
          class="p-button-outlined"
          @click="handlePrint"
          :disabled="!canPrint" 
        />
        <Button 
          v-if="showSchedule"
          label="Schedule" 
          icon="pi pi-calendar" 
          class="p-button-outlined"
          @click="openScheduleDialog"
        />
      </div>
    </div>

    <!-- Report Filters -->
    <Card v-if="showFilters" class="mb-6">
      <template #title>
        <div class="flex justify-between items-center">
          <span>Filters</span>
          <div class="flex space-x-2">
            <Button 
              label="Reset" 
              icon="pi pi-refresh" 
              class="p-button-text"
              @click="resetFilters"
            />
            <Button 
              label="Apply" 
              icon="pi pi-check" 
              @click="applyFilters"
              :loading="loading"
            />
          </div>
        </div>
      </template>
      <template #content>
        <slot name="filters"></slot>
      </template>
    </Card>

    <!-- Report Content -->
    <div class="report-content">
      <!-- Loading State -->
      <div v-if="loading" class="flex flex-col items-center justify-center p-8">
        <ProgressSpinner />
        <p class="mt-4 text-gray-600 dark:text-gray-400">Generating report...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
        <div class="flex items-center">
          <i class="pi pi-exclamation-triangle text-red-500 mr-3"></i>
          <div>
            <h3 class="font-medium text-red-800 dark:text-red-200">Error Loading Report</h3>
            <p class="text-sm text-red-700 dark:text-red-300">{{ errorMessage || 'An error occurred while generating the report.' }}</p>
            <Button 
              label="Retry" 
              icon="pi pi-refresh" 
              class="p-button-text p-0 mt-2"
              @click="loadData"
            />
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="isEmpty" class="flex flex-col items-center justify-center p-8 text-center">
        <i class="pi pi-inbox text-5xl text-gray-300 mb-4"></i>
        <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-1">No Data Available</h3>
        <p class="text-gray-500 dark:text-gray-400 mb-4">Try adjusting your filters or check back later.</p>
        <Button 
          v-if="showResetOnEmpty"
          label="Reset Filters" 
          icon="pi pi-refresh" 
          @click="resetFilters"
        />
      </div>

      <!-- Report Content -->
      <template v-else>
        <!-- Summary Cards -->
        <div v-if="showSummaryCards" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <slot name="summary-cards"></slot>
        </div>

        <!-- Charts -->
        <div v-if="showCharts" class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <slot name="charts"></slot>
        </div>

        <!-- Main Content -->
        <slot></slot>
      </template>
    </div>

    <!-- Footer -->
    <div v-if="showFooter" class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-500 dark:text-gray-400">
      <div class="flex flex-col md:flex-row justify-between items-center">
        <div>Generated on {{ generatedDate }}</div>
        <div v-if="recordCount !== null">{{ recordCount }} records found</div>
      </div>
    </div>

    <!-- Schedule Dialog -->
    <Dialog 
      v-model:visible="scheduleDialogVisible" 
      header="Schedule Report" 
      :modal="true"
      :style="{ width: '500px' }"
    >
      <div class="p-fluid">
        <div class="field">
          <label for="frequency">Frequency</label>
          <Dropdown 
            id="frequency"
            v-model="schedule.frequency" 
            :options="frequencyOptions" 
            optionLabel="name" 
            optionValue="value"
            placeholder="Select Frequency"
          />
        </div>
        
        <div v-if="schedule.frequency === 'custom'" class="field">
          <label for="cron">Cron Expression</label>
          <InputText id="cron" v-model="schedule.cron" placeholder="0 0 * * * ?" />
          <small class="text-gray-500">Enter a valid cron expression</small>
        </div>
        
        <div class="field">
          <label for="email">Email Recipients</label>
          <Chips 
            id="email" 
            v-model="schedule.recipients" 
            separator=","
            placeholder="Enter email and press enter"
          />
          <small class="text-gray-500">Separate multiple emails with commas</small>
        </div>
        
        <div class="field-checkbox">
          <Checkbox 
            id="active" 
            v-model="schedule.active" 
            :binary="true"
          />
          <label for="active">Active</label>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text"
          @click="scheduleDialogVisible = false"
        />
        <Button 
          label="Save Schedule" 
          icon="pi pi-check" 
          @click="saveSchedule"
          :loading="savingSchedule"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { format } from 'date-fns';

const props = defineProps({
  // Basic Info
  title: { type: String, required: true },
  description: { type: String, default: '' },
  
  // Display Controls
  loading: { type: Boolean, default: false },
  error: { type: Boolean, default: false },
  errorMessage: { type: String, default: '' },
  isEmpty: { type: Boolean, default: false },
  recordCount: { type: Number, default: null },
  
  // Feature Toggles
  showFilters: { type: Boolean, default: true },
  showExport: { type: Boolean, default: true },
  showPrint: { type: Boolean, default: true },
  showSchedule: { type: Boolean, default: true },
  showSummaryCards: { type: Boolean, default: false },
  showCharts: { type: Boolean, default: false },
  showFooter: { type: Boolean, default: true },
  showResetOnEmpty: { type: Boolean, default: true },
  
  // Export Options
  exportLabel: { type: String, default: '' },
  exportIcon: { type: String, default: '' },
  canExport: { type: Boolean, default: true },
  canPrint: { type: Boolean, default: true },
  
  // Date
  generatedDate: { 
    type: String, 
    default: () => format(new Date(), 'yyyy-MM-dd HH:mm:ss') 
  },
});

const emit = defineEmits([
  'export',
  'print',
  'schedule',
  'apply-filters',
  'reset-filters',
]);

const { t } = useI18n();

// Schedule Dialog
const scheduleDialogVisible = ref(false);
const savingSchedule = ref(false);
const schedule = ref({
  frequency: 'weekly',
  cron: '',
  recipients: [],
  active: true,
});

const frequencyOptions = [
  { name: 'Daily', value: 'daily' },
  { name: 'Weekly', value: 'weekly' },
  { name: 'Monthly', value: 'monthly' },
  { name: 'Quarterly', value: 'quarterly' },
  { name: 'Yearly', value: 'yearly' },
  { name: 'Custom', value: 'custom' },
];

// Methods
const handleExport = (format = 'excel') => {
  emit('export', format);
};

const handlePrint = () => {
  emit('print');
};

const openScheduleDialog = () => {
  scheduleDialogVisible.value = true;
};

const saveSchedule = async () => {
  try {
    savingSchedule.value = true;
    // TODO: Implement schedule save logic
    emit('schedule', schedule.value);
    scheduleDialogVisible.value = false;
  } catch (error) {
    console.error('Error saving schedule:', error);
  } finally {
    savingSchedule.value = false;
  }
};

const applyFilters = () => {
  emit('apply-filters');
};

const resetFilters = () => {
  emit('reset-filters');
};

// Lifecycle
onMounted(() => {
  // Initialize any required data
});
</script>

<style scoped>
.report-container {
  @apply h-full flex flex-col;
}

.report-content {
  @apply flex-1 overflow-auto;
  min-height: 300px;
}

/* Print styles */
@media print {
  .report-container > :not(.report-content) {
    display: none !important;
  }
  
  .report-content {
    overflow: visible !important;
    height: auto !important;
  }
  
  body * {
    visibility: hidden;
  }
  
  .report-container, .report-container * {
    visibility: visible;
  }
  
  .report-container {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
  }
  
  .p-datatable {
    width: 100% !important;
  }
  
  .p-datatable .p-datatable-thead > tr > th,
  .p-datatable .p-datatable-tbody > tr > td {
    padding: 0.5rem !important;
    font-size: 12px !important;
  }
}
</style>
