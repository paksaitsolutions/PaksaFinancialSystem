<template>
  <div class="report-header">
    <div class="header-content">
      <div class="title-section">
        <h2>{{ title }}</h2>
        <p class="subtitle">{{ formatDateRange(dateRange) }}</p>
      </div>
      
      <div class="actions">
        <div class="date-range-picker">
          <label>Date Range:</label>
          <Calendar 
            v-model="dateRange" 
            selectionMode="range" 
            :showIcon="true"
            dateFormat="yy-mm-dd"
            :maxDate="new Date()"
            :manualInput="false"
            @date-select="handleDateChange"
            class="date-range-input"
          />
        </div>
        
        <div class="action-buttons">
          <Button 
            icon="pi pi-refresh" 
            :loading="loading"
            class="p-button-text"
            @click="handleRefresh"
            v-tooltip.top="'Refresh Data'"
          />
          
          <SplitButton 
            label="Export" 
            icon="pi pi-download"
            :model="exportOptions" 
            :loading="exportLoading"
            class="export-button"
            @click="handleExport('excel')"
          />
          
          <Button 
            icon="pi pi-filter" 
            class="p-button-text"
            @click="toggleFilters"
            :class="{ 'p-button-text': !showFilters, 'p-button-text p-button-success': showFilters }"
            v-tooltip.top="'Toggle Filters'"
          />
        </div>
      </div>
    </div>
    
    <Transition name="fade">
      <div v-if="showFilters" class="filters-panel">
        <slot name="filters"></slot>
      </div>
    </Transition>
    
    <Divider />
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from 'vue';
import { format } from 'date-fns';
import Calendar from 'vue/calendar';
import Button from 'vue/button';
import SplitButton from 'vue/splitbutton';
import Divider from 'vue/divider';
import { useToast } from 'vue/usetoast';

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  dateRange: {
    type: Object,
    required: true,
    validator: (value: any) => {
      return Array.isArray(value) || (value && value.startDate && value.endDate);
    }
  },
  loading: {
    type: Boolean,
    default: false
  },
  exportLoading: {
    type: Boolean,
    default: false
  },
  defaultExportFormat: {
    type: String,
    default: 'excel'
  }
});

const emit = defineEmits(['date-range-update', 'refresh', 'export']);
const toast = useToast();

const showFilters = ref(false);

const exportOptions = [
  {
    label: 'Export to Excel',
    icon: 'pi pi-file-excel',
    command: () => handleExport('excel')
  },
  {
    label: 'Export to PDF',
    icon: 'pi pi-file-pdf',
    command: () => handleExport('pdf')
  },
  {
    label: 'Export to CSV',
    icon: 'pi pi-file',
    command: () => handleExport('csv')
  },
  {
    label: 'Print Report',
    icon: 'pi pi-print',
    command: () => window.print()
  }
];

const formatDateRange = (range: any) => {
  if (!range || !range[0] || !range[1]) return 'Select date range';
  
  const start = format(new Date(range[0]), 'MMM d, yyyy');
  const end = format(new Date(range[1]), 'MMM d, yyyy');
  
  return `${start} - ${end}`;
};

const handleDateChange = (event: any) => {
  if (event.value && event.value[1]) {
    emit('date-range-update', event.value);
  }
};

const handleRefresh = () => {
  emit('refresh');
};

const handleExport = (format: string) => {
  emit('export', format);
};

const toggleFilters = () => {
  showFilters.value = !showFilters.value;
};

// Set default date range if not provided
watch(() => props.dateRange, (newVal) => {
  if (!newVal || (Array.isArray(newVal) && newVal.length === 0)) {
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - 1);
    emit('date-range-update', [start, end]);
  }
}, { immediate: true });
</script>

<style scoped>
.report-header {
  margin-bottom: 1.5rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.title-section h2 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.5rem;
  font-weight: 600;
}

.title-section .subtitle {
  margin: 0.25rem 0 0;
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.date-range-picker {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-right: 0.5rem;
}

.date-range-picker label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  white-space: nowrap;
}

.date-range-input {
  width: 240px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.export-button {
  min-width: 100px;
}

.filters-panel {
  background-color: var(--surface-50);
  border-radius: 6px;
  padding: 1rem;
  margin: 1rem 0;
  border: 1px solid var(--surface-200);
  transition: all 0.3s ease;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
  transform-origin: top;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scaleY(0.9);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }
  
  .date-range-picker {
    width: 100%;
    margin-bottom: 0.5rem;
  }
  
  .date-range-input {
    width: 100%;
  }
  
  .action-buttons {
    justify-content: flex-end;
  }
}
</style>
