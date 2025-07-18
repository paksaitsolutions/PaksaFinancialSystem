<template>
  <Dialog 
    :visible="modelValue" 
    @update:visible="$emit('update:modelValue', $event)"
    :header="report?.name || 'Run Report'" 
    :style="{ width: '90vw', maxWidth: '1400px', height: '90vh' }"
    :modal="true"
    class="p-fluid"
    :maximizable="true"
    :closable="true"
    @hide="onHide"
  >
    <div v-if="loading" class="flex justify-content-center p-5">
      <ProgressSpinner />
    </div>
    
    <div v-else-if="error" class="p-5 text-center">
      <i class="pi pi-exclamation-triangle text-6xl text-red-500 mb-3" />
      <h3>Error Loading Report</h3>
      <p class="text-500 mb-4">{{ error }}</p>
      <Button label="Retry" icon="pi pi-refresh" @click="$emit('refresh')" />
    </div>
    
    <div v-else class="h-full flex flex-column">
      <!-- Report Toolbar -->
      <div class="flex justify-content-between align-items-center mb-4">
        <div class="flex gap-2">
          <Button 
            icon="pi pi-refresh" 
            class="p-button-text" 
            label="Refresh" 
            @click="$emit('refresh')"
          />
          <SplitButton 
            label="Export" 
            icon="pi pi-download"
            :model="exportOptions"
            class="p-button-outlined"
            @click="onExport('pdf')"
          />
          <Button 
            icon="pi pi-calendar" 
            class="p-button-text" 
            label="Schedule" 
            @click="onSchedule"
          />
        </div>
        
        <div class="flex gap-2">
          <Button 
            :icon="isFavorite ? 'pi pi-star-fill' : 'pi pi-star'" 
            :class="['p-button-text', { 'p-button-warning': isFavorite }]"
            v-tooltip.top="isFavorite ? 'Remove from Favorites' : 'Add to Favorites'"
            @click="onToggleFavorite"
          />
          <Button 
            icon="pi pi-cog" 
            class="p-button-text" 
            label="Customize" 
            @click="onCustomize"
          />
        </div>
      </div>
      
      <!-- Report Content -->
      <div class="flex-grow-1 overflow-auto border-1 surface-border p-3">
        <div v-if="data && data.length > 0" class="report-content">
          <!-- Table Report -->
          <DataTable 
            v-if="report?.type === 'table'"
            :value="data"
            :paginator="true"
            :rows="20"
            :scrollable="true"
            scrollHeight="flex"
            class="p-datatable-sm"
            responsiveLayout="scroll"
            :loading="loading"
          >
            <Column 
              v-for="col in columns.filter(c => c.visible !== false)" 
              :key="col.field"
              :field="col.field" 
              :header="col.header || col.field" 
              :sortable="col.sortable !== false"
              :style="{ width: col.width ? col.width + 'px' : 'auto' }"
            />
          </DataTable>
          
          <!-- Chart Report -->
          <div v-else-if="report?.type === 'chart'" class="h-full flex align-items-center justify-content-center">
            <div class="text-center">
              <i class="pi pi-chart-bar text-6xl text-400 mb-3" />
              <h3>Chart Preview</h3>
              <p class="text-500">Chart visualization would be displayed here</p>
            </div>
          </div>
          
          <!-- Pivot Table Report -->
          <div v-else-if="report?.type === 'pivot'" class="h-full flex align-items-center justify-content-center">
            <div class="text-center">
              <i class="pi pi-table text-6xl text-400 mb-3" />
              <h3>Pivot Table</h3>
              <p class="text-500">Pivot table visualization would be displayed here</p>
            </div>
          </div>
          
          <!-- Other report types would be rendered here -->
          <div v-else class="h-full flex align-items-center justify-content-center">
            <div class="text-center">
              <i class="pi pi-file text-6xl text-400 mb-3" />
              <h3>Report Preview</h3>
              <p class="text-500">This is a preview of the selected report</p>
            </div>
          </div>
        </div>
        
        <div v-else class="h-full flex align-items-center justify-content-center">
          <div class="text-center">
            <i class="pi pi-info-circle text-6xl text-400 mb-3" />
            <h3>No Data Available</h3>
            <p class="text-500">Run the report to see the results</p>
            <Button 
              label="Run Report" 
              icon="pi pi-play" 
              class="mt-3"
              @click="$emit('refresh')"
            />
          </div>
        </div>
      </div>
      
      <!-- Report Footer -->
      <div class="flex justify-content-between align-items-center mt-2 text-sm text-500">
        <div>Last run: {{ formatDate(lastRun) }}</div>
        <div>Rows: {{ data?.length || 0 }}</div>
        <div>Generated: {{ formatDate(new Date().toISOString()) }}</div>
      </div>
    </div>
    
    <template #footer>
      <div class="flex justify-content-between">
        <Button 
          label="Close" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="onClose"
        />
        <Button 
          label="Run Again" 
          icon="pi pi-refresh" 
          class="p-button-primary"
          @click="onRefresh"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { PropType } from 'vue';
import type { Report } from '@/types/reports';

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  report: {
    type: Object as PropType<Report | null>,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String as PropType<string | null>,
    default: null,
  },
  data: {
    type: Array as PropType<any[] | null>,
    default: null,
  },
  columns: {
    type: Array as PropType<Array<{ field: string; header?: string; visible?: boolean; width?: number; sortable?: boolean }>>,
    default: () => [],
  },
  lastRun: {
    type: String as PropType<string | null>,
    default: null,
  },
  isFavorite: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  'update:modelValue',
  'refresh',
  'close',
  'export',
  'toggle-favorite',
  'schedule',
  'customize',
]);

// Computed
const exportOptions = computed(() => [
  { label: 'Export as PDF', icon: 'pi pi-file-pdf', command: () => onExport('pdf') },
  { label: 'Export as Excel', icon: 'pi pi-file-excel', command: () => onExport('excel') },
  { label: 'Export as CSV', icon: 'pi pi-file', command: () => onExport('csv') },
  { label: 'Export as JSON', icon: 'pi pi-code', command: () => onExport('json') },
]);

// Methods
const onHide = () => {
  emit('update:modelValue', false);
  emit('close');
};

const onClose = () => {
  emit('update:modelValue', false);
  emit('close');
};

const onRefresh = () => {
  emit('refresh');
};

const onExport = (format: string) => {
  emit('export', format);
};

const onToggleFavorite = () => {
  emit('toggle-favorite');
};

const onSchedule = () => {
  emit('schedule');
};

const onCustomize = () => {
  emit('customize');
};

const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return 'Never';
  
  const date = new Date(dateString);
  return date.toLocaleString();
};
</script>

<style scoped>
.report-content {
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