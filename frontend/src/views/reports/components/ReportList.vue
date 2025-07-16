<template>
  <div class="report-list-container">
    <!-- Search and Filter Bar -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div class="flex gap-2">
        <span class="p-input-icon-left w-20rem">
          <i class="pi pi-search" />
          <InputText 
            v-model="searchQuery" 
            placeholder="Search reports..." 
            class="w-full"
            @keyup.enter="applySearch"
          />
        </span>
        
        <Dropdown 
          v-model="selectedCategory" 
          :options="categories" 
          optionLabel="name"
          optionValue="id"
          placeholder="All Categories" 
          class="w-15rem"
          :showClear="true"
          @change="filterReports"
        />
        
        <MultiSelect 
          v-model="selectedTags" 
          :options="allTags" 
          placeholder="Filter by Tags"
          class="w-15rem"
          :showToggleAll="false"
          :maxSelectedLabels="1"
          @change="filterReports"
        />
      </div>
      
      <div class="flex gap-2">
        <Button 
          icon="pi pi-refresh" 
          class="p-button-rounded p-button-text" 
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
    
    <!-- View Toggle -->
    <div class="flex justify-content-end mb-3">
      <div class="flex border-1 surface-border border-round">
        <Button 
          icon="pi pi-th-large" 
          :class="['p-button-text', { 'p-button-secondary': viewMode === 'grid' }]"
          @click="viewMode = 'grid'"
        />
        <Button 
          icon="pi pi-list" 
          :class="['p-button-text', { 'p-button-secondary': viewMode === 'list' }]"
          @click="viewMode = 'list'"
        />
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading && reports.length === 0" class="flex justify-content-center p-5">
      <ProgressSpinner />
    </div>
    
    <!-- Empty State -->
    <div v-else-if="filteredReports.length === 0" class="flex flex-column align-items-center justify-content-center p-5">
      <i class="pi pi-inbox text-6xl text-400 mb-3" />
      <h3>No Reports Found</h3>
      <p class="text-500">Try adjusting your search or create a new report</p>
      <Button 
        label="Create Report" 
        icon="pi pi-plus" 
        class="mt-3"
        @click="openNewReportDialog"
      />
    </div>
    
    <!-- Grid View -->
    <div v-else-if="viewMode === 'grid'" class="grid">
      <div 
        v-for="report in filteredReports" 
        :key="report.id"
        class="col-12 md:col-6 lg:col-4 xl:col-3"
      >
        <ReportCard 
          :report="report" 
          :is-favorite="isFavorite(report.id)"
          @favorite="toggleFavorite(report.id)"
          @run="runReport(report)"
          @edit="editReport(report)"
          @delete="confirmDeleteReport(report)"
        />
      </div>
    </div>
    
    <!-- List View -->
    <DataTable 
      v-else
      :value="filteredReports"
      :paginator="true"
      :rows="10"
      :loading="loading"
      :scrollable="true"
      scrollHeight="flex"
      class="p-datatable-sm"
      responsiveLayout="scroll"
    >
      <Column field="name" header="Report Name" :sortable="true">
        <template #body="{ data }">
          <div class="flex align-items-center gap-2">
            <i :class="['pi', data.icon || 'pi-file', 'text-primary']" />
            <span class="font-medium">{{ data.name }}</span>
          </div>
        </template>
      </Column>
      
      <Column field="category" header="Category" :sortable="true">
        <template #body="{ data }">
          <Tag :value="getCategoryName(data.categoryId)" :severity="getCategorySeverity(data.categoryId)" />
        </template>
      </Column>
      
      <Column field="type" header="Type" :sortable="true">
        <template #body="{ data }">
          <Tag :value="formatReportType(data.type)" />
        </template>
      </Column>
      
      <Column field="lastRun" header="Last Run" :sortable="true">
        <template #body="{ data }">
          {{ formatDate(data.lastRun) }}
        </template>
      </Column>
      
      <Column header="Actions" :exportable="false" style="width: 12rem">
        <template #body="{ data }">
          <div class="flex gap-1">
            <Button 
              icon="pi pi-play" 
              class="p-button-rounded p-button-text p-button-sm"
              v-tooltip.top="'Run Report'"
              @click="runReport(data)"
            />
            <Button 
              icon="pi pi-star" 
              :class="['p-button-rounded p-button-text p-button-sm', { 'p-button-warning': isFavorite(data.id) }]"
              v-tooltip.top="isFavorite(data.id) ? 'Remove from Favorites' : 'Add to Favorites'"
              @click="toggleFavorite(data.id)"
            />
            <Button 
              icon="pi pi-pencil" 
              class="p-button-rounded p-button-text p-button-sm"
              v-tooltip.top="'Edit'"
              @click="editReport(data)"
            />
            <Button 
              icon="pi pi-trash" 
              class="p-button-rounded p-button-text p-button-sm p-button-danger"
              v-tooltip.top="'Delete'"
              @click="confirmDeleteReport(data)"
            />
          </div>
        </template>
      </Column>
    </DataTable>
    
    <!-- New/Edit Report Dialog -->
    <Dialog 
      v-model:visible="reportDialog.visible" 
      :header="reportDialog.mode === 'new' ? 'New Report' : 'Edit Report'" 
      :style="{ width: '50vw' }" 
      :modal="true"
      class="p-fluid"
    >
      <div class="field">
        <label for="name">Report Name</label>
        <InputText 
          id="name" 
          v-model="reportDialog.data.name" 
          required
          :class="{ 'p-invalid': submitted && !reportDialog.data.name }"
        />
        <small class="p-error" v-if="submitted && !reportDialog.data.name">Name is required.</small>
      </div>
      
      <div class="field">
        <label for="description">Description</label>
        <Textarea id="description" v-model="reportDialog.data.description" rows="3" />
      </div>
      
      <div class="formgrid grid">
        <div class="field col-6">
          <label for="category">Category</label>
          <Dropdown 
            id="category" 
            v-model="reportDialog.data.categoryId" 
            :options="categories" 
            optionLabel="name"
            optionValue="id"
            placeholder="Select a category"
            :class="{ 'p-invalid': submitted && !reportDialog.data.categoryId }"
          />
          <small class="p-error" v-if="submitted && !reportDialog.data.categoryId">Category is required.</small>
        </div>
        
        <div class="field col-6">
          <label for="type">Report Type</label>
          <Dropdown 
            id="type" 
            v-model="reportDialog.data.type" 
            :options="reportTypes" 
            optionLabel="label"
            optionValue="value"
            placeholder="Select a type"
          />
        </div>
      </div>
      
      <div class="field">
        <label for="dataSource">Data Source</label>
        <Dropdown 
          id="dataSource" 
          v-model="reportDialog.data.dataSource" 
          :options="dataSources" 
          optionLabel="name"
          optionValue="id"
          placeholder="Select a data source"
          :class="{ 'p-invalid': submitted && !reportDialog.data.dataSource }"
        />
        <small class="p-error" v-if="submitted && !reportDialog.data.dataSource">Data source is required.</small>
      </div>
      
      <div class="field">
        <label>Tags</label>
        <Chips v-model="reportDialog.data.tags" class="w-full" separator="," />
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="hideDialog"
        />
        <Button 
          :label="reportDialog.mode === 'new' ? 'Create' : 'Update'" 
          icon="pi pi-check" 
          class="p-button-primary" 
          @click="saveReport"
        />
      </template>
    </Dialog>
    
    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { useReportsStore } from '@/stores/reports';
import ReportCard from './ReportCard.vue';
import type { Report, ReportType } from '@/types/reports';

const emit = defineEmits(['run']);
const router = useRouter();
const confirm = useConfirm();
const toast = useToast();
const reportsStore = useReportsStore();

// State
const viewMode = ref<'grid' | 'list'>('grid');
const searchQuery = ref('');
const selectedCategory = ref<string | null>(null);
const selectedTags = ref<string[]>([]);
const submitted = ref(false);

// Report Dialog
const reportDialog = ref({
  visible: false,
  mode: 'new' as 'new' | 'edit',
  data: {
    id: '',
    name: '',
    description: '',
    categoryId: '',
    type: 'table' as ReportType,
    dataSource: '',
    tags: [] as string[],
  },
});

// Computed
const reports = computed(() => reportsStore.reports);
const loading = computed(() => reportsStore.loading);
const categories = computed(() => reportsStore.categories);
const favorites = computed(() => reportsStore.favorites);

const allTags = computed(() => {
  const tags = new Set<string>();
  reportsStore.reports.forEach(report => {
    if (report.tags) {
      report.tags.forEach(tag => tags.add(tag));
    }
  });
  return Array.from(tags);
});

const reportTypes = [
  { label: 'Table', value: 'table' },
  { label: 'Chart', value: 'chart' },
  { label: 'Pivot Table', value: 'pivot' },
  { label: 'Summary', value: 'summary' },
  { label: 'Matrix', value: 'matrix' },
  { label: 'Crosstab', value: 'crosstab' },
];

const dataSources = [
  { id: 'gl', name: 'General Ledger' },
  { id: 'ap', name: 'Accounts Payable' },
  { id: 'ar', name: 'Accounts Receivable' },
  { id: 'bank', name: 'Bank Transactions' },
  { id: 'inventory', name: 'Inventory' },
  { id: 'payroll', name: 'Payroll' },
  { id: 'fixed-assets', name: 'Fixed Assets' },
  { id: 'projects', name: 'Projects' },
];

const filteredReports = computed(() => {
  let result = [...reportsStore.reports];
  
  // Apply search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(
      report => 
        report.name.toLowerCase().includes(query) ||
        report.description?.toLowerCase().includes(query) ||
        (report.tags && report.tags.some(tag => tag.toLowerCase().includes(query)))
    );
  }
  
  // Apply category filter
  if (selectedCategory.value) {
    result = result.filter(report => report.categoryId === selectedCategory.value);
  }
  
  // Apply tags filter
  if (selectedTags.value.length > 0) {
    result = result.filter(
      report => report.tags && selectedTags.value.every(tag => report.tags?.includes(tag))
    );
  }
  
  return result;
});

// Methods
const formatDate = (dateString?: string) => {
  if (!dateString) return 'Never';
  return new Date(dateString).toLocaleString();
};

const formatReportType = (type: string) => {
  return type.charAt(0).toUpperCase() + type.slice(1);
};

const getCategoryName = (categoryId: string) => {
  const category = categories.value.find(c => c.id === categoryId);
  return category ? category.name : 'Uncategorized';
};

const getCategorySeverity = (categoryId: string) => {
  const categories = [
    { id: 'financial', severity: 'success' },
    { id: 'operational', severity: 'info' },
    { id: 'sales', severity: 'warning' },
    { id: 'inventory', severity: 'danger' },
    { id: 'hr', severity: 'help' },
  ];
  
  const category = categories.find(c => c.id === categoryId);
  return category ? category.severity : 'info';
};

const isFavorite = (reportId: string) => {
  return favorites.value.some(fav => fav.reportId === reportId);
};

const toggleFavorite = async (reportId: string) => {
  await reportsStore.toggleFavorite(reportId);
};

const runReport = (report: Report) => {
  emit('run', report);
};

const applySearch = () => {
  // Search is applied reactively via computed property
};

const filterReports = () => {
  // Filtering is applied reactively via computed property
};

const refreshReports = async () => {
  await reportsStore.fetchReports();
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: 'Reports refreshed',
    life: 3000,
  });
};

const openNewReportDialog = () => {
  reportDialog.value = {
    visible: true,
    mode: 'new',
    data: {
      id: '',
      name: '',
      description: '',
      categoryId: '',
      type: 'table',
      dataSource: '',
      tags: [],
    },
  };
  submitted.value = false;
};

const editReport = (report: Report) => {
  reportDialog.value = {
    visible: true,
    mode: 'edit',
    data: { ...report },
  };
  submitted.value = false;
};

const hideDialog = () => {
  reportDialog.value.visible = false;
  submitted.value = false;
};

const saveReport = async () => {
  submitted.value = true;
  
  // Validate
  if (!reportDialog.value.data.name || !reportDialog.value.data.categoryId || !reportDialog.value.data.dataSource) {
    return;
  }
  
  try {
    if (reportDialog.value.mode === 'new') {
      await reportsStore.createReport({
        ...reportDialog.value.data,
        createdBy: 'current-user-id', // This should come from auth store
      });
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Report created successfully',
        life: 3000,
      });
    } else {
      await reportsStore.updateReport(reportDialog.value.data.id, {
        ...reportDialog.value.data,
        modifiedBy: 'current-user-id', // This should come from auth store
      });
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Report updated successfully',
        life: 3000,
      });
    }
    
    reportDialog.value.visible = false;
  } catch (error) {
    console.error('Error saving report:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save report',
      life: 5000,
    });
  }
};

const confirmDeleteReport = (report: Report) => {
  confirm.require({
    message: `Are you sure you want to delete ${report.name}?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: () => deleteReport(report),
  });
};

const deleteReport = async (report: Report) => {
  try {
    await reportsStore.deleteReport(report.id);
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Report deleted successfully',
      life: 3000,
    });
  } catch (error) {
    console.error('Error deleting report:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete report',
      life: 5000,
    });
  }
};

// Lifecycle hooks
onMounted(async () => {
  await reportsStore.initialize();
});
</script>

<style scoped>
.report-list-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.p-datatable) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.p-datatable-wrapper) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.p-datatable-table) {
  flex: 1;
}
</style>
