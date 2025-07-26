<template>
  <Dialog
    v-model:visible="visible"
    :style="{ width: '600px', maxWidth: '95vw' }"
    :header="t('export.dialog.title')"
    :modal="true"
    :closable="!isExporting"
    :close-on-escape="!isExporting"
    class="export-dialog p-fluid"
  >
    <div v-if="isExporting" class="export-progress">
      <ProgressBar
        :value="exportProgress"
        :showValue="false"
        :class="{ 'export-complete': exportProgress >= 100 }"
      />
      <div class="flex align-items-center justify-content-between mt-2">
        <span>{{ t('export.status.exporting') }} ({{ exportProgress }}%)</span>
        <span v-if="exportProgress >= 100" class="text-green-500 font-medium">
          <i class="pi pi-check-circle mr-1"></i>
          {{ t('export.status.complete') }}
        </span>
      </div>
    </div>

    <div v-else>
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="exportFormat">{{ t('export.format.label') }}</label>
            <Dropdown
              id="exportFormat"
              v-model="selectedFormat"
              :options="formats"
              option-label="name"
              option-value="value"
              :placeholder="t('export.format.placeholder')"
              class="w-full"
              :disabled="isExporting"
            >
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex align-items-center">
                  <i :class="getFormatIcon(slotProps.value)" class="mr-2"></i>
                  <div>{{ getFormatName(slotProps.value) }}</div>
                </div>
                <span v-else>
                  {{ slotProps.placeholder }}
                </span>
              </template>
              <template #option="slotProps">
                <div class="flex align-items-center">
                  <i :class="getFormatIcon(slotProps.option.value)" class="mr-2"></i>
                  <div>{{ slotProps.option.name }}</div>
                </div>
              </template>
            </Dropdown>
          </div>
        </div>

        <div class="col-12 md:col-6">
          <div class="field">
            <label for="exportScope">{{ t('export.scope.label') }}</label>
            <SelectButton
              id="exportScope"
              v-model="exportScope"
              :options="exportScopes"
              option-label="label"
              option-value="value"
              class="w-full"
              :disabled="isExporting"
            />
          </div>
        </div>

        <div v-if="exportScope === 'range'" class="col-12">
          <div class="field">
            <label for="pageRange">{{ t('export.pageRange.label') }}</label>
            <InputText
              id="pageRange"
              v-model="pageRange"
              :placeholder="t('export.pageRange.placeholder')"
              :disabled="isExporting"
              class="w-full"
              :class="{ 'p-invalid': !isValidPageRange && pageRange }"
            />
            <small v-if="!isValidPageRange && pageRange" class="p-error">
              {{ t('export.pageRange.invalid') }}
            </small>
          </div>
        </div>

        <div v-if="showAdvancedOptions" class="col-12">
          <div class="border-top-1 border-300 mt-3 pt-3">
            <h4 class="text-sm font-medium mb-3">
              <i class="pi pi-cog mr-2"></i>
              {{ t('export.advancedOptions') }}
            </h4>
            
            <div class="grid">
              <div v-if="selectedFormat.value === 'pdf'" class="col-12 md:col-6">
                <div class="field">
                  <label for="pageSize">{{ t('export.pageSize') }}</label>
                  <Dropdown
                    id="pageSize"
                    v-model="options.pageSize"
                    :options="pageSizes"
                    option-label="label"
                    option-value="value"
                    class="w-full"
                    :disabled="isExporting"
                  />
                </div>
              </div>
              
              <div v-if="selectedFormat.value === 'pdf'" class="col-12 md:col-6">
                <div class="field">
                  <label for="orientation">{{ t('export.orientation') }}</label>
                  <SelectButton
                    id="orientation"
                    v-model="options.orientation"
                    :options="orientations"
                    option-label="label"
                    option-value="value"
                    class="w-full"
                    :disabled="isExporting"
                  />
                </div>
              </div>
              
              <div class="col-12">
                <div class="field-checkbox">
                  <Checkbox
                    id="includeHeader"
                    v-model="options.includeHeader"
                    :binary="true"
                    :disabled="isExporting"
                  />
                  <label for="includeHeader">{{ t('export.includeHeader') }}</label>
                </div>
              </div>
              
              <div v-if="selectedFormat.value === 'excel'" class="col-12">
                <div class="field-checkbox">
                  <Checkbox
                    id="freezeHeader"
                    v-model="options.freezeHeader"
                    :binary="true"
                    :disabled="isExporting"
                  />
                  <label for="freezeHeader">{{ t('export.freezeHeader') }}</label>
                </div>
              </div>
              
              <div class="col-12">
                <div class="field">
                  <label for="fileName">{{ t('export.fileName') }}</label>
                  <InputText
                    id="fileName"
                    v-model="options.fileName"
                    class="w-full"
                    :disabled="isExporting"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-content-between w-full">
        <div>
          <Button
            v-if="!isExporting"
            type="button"
            icon="pi pi-cog"
            :label="showAdvancedOptions ? t('common.hideOptions') : t('common.moreOptions')"
            class="p-button-text p-button-sm"
            @click="showAdvancedOptions = !showAdvancedOptions"
          />
        </div>
        <div class="flex gap-2">
          <Button
            :label="t('common.cancel')"
            icon="pi pi-times"
            class="p-button-text"
            :disabled="isExporting"
            @click="close"
          />
          <Button
            :label="t('common.export')"
            :icon="isExporting ? 'pi pi-spin pi-spinner' : 'pi pi-download'"
            :disabled="!isValid || isExporting"
            @click="handleExport"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useExport } from '@/core/utils/export';

// Vue components
import Dialog from 'vue/dialog';
import Dropdown from 'vue/dropdown';
import SelectButton from 'vue/selectbutton';
import InputText from 'vue/inputtext';
import Button from 'vue/button';
import Checkbox from 'vue/checkbox';
import ProgressBar from 'vue/progressbar';

const { t } = useI18n();
const emit = defineEmits(['export', 'error', 'success']);

// Refs
const visible = ref(false);
const showAdvancedOptions = ref(false);
const selectedFormat = ref('csv');
const exportScope = ref('current');
const pageRange = ref('');

// Export utility
const { isExporting, exportProgress, exportData } = useExport();

// Options
const options = ref({
  includeHeader: true,
  freezeHeader: true,
  pageSize: 'A4',
  orientation: 'portrait',
  fileName: '',
});

// Available formats
const formats = [
  { name: t('export.formats.excel'), value: 'excel' },
  { name: t('export.formats.csv'), value: 'csv' },
  { name: t('export.formats.pdf'), value: 'pdf' },
  { name: 'HTML', value: 'html' },
  { name: 'PNG', value: 'png' },
  { name: 'JPEG', value: 'jpeg' },
];

// Export scopes
const exportScopes = [
  { label: t('export.scopes.currentView'), value: 'current' },
  { label: t('export.scopes.allData'), value: 'all' },
  { label: t('export.scopes.pageRange'), value: 'range' },
];

// Page sizes for PDF
const pageSizes = [
  { label: 'A4', value: 'A4' },
  { label: 'Letter', value: 'letter' },
  { label: 'Legal', value: 'legal' },
  { label: 'A3', value: 'A3' },
];

// Orientations
const orientations = [
  { label: t('export.portrait'), value: 'portrait' },
  { label: t('export.landscape'), value: 'landscape' },
];

// Computed
const isValidPageRange = computed(() => {
  if (exportScope.value !== 'range') return true;
  if (!pageRange.value) return false;
  
  // Simple validation for page range format (e.g., 1-5,8,11-13)
  return /^(\d+(-\d+)?)(,\s*\d+(-\d+)?)*$/.test(pageRange.value);
});

const isValid = computed(() => {
  if (exportScope.value === 'range') {
    return isValidPageRange.value && pageRange.value.trim() !== '';
  }
  return true;
});

// Methods
const getFormatIcon = (format) => {
  const icons = {
    excel: 'pi pi-file-excel text-green-600',
    csv: 'pi pi-file',
    pdf: 'pi pi-file-pdf text-red-600',
    html: 'pi pi-code',
    png: 'pi pi-image',
    jpeg: 'pi pi-image',
  };
  return icons[format] || 'pi pi-file';
};

const getFormatName = (format) => {
  const formatObj = formats.find(f => f.value === format);
  return formatObj ? formatObj.name : format.toUpperCase();
};

const handleExport = async () => {
  if (!isValid.value) return;

  try {
    const exportOptions = {
      format: selectedFormat.value,
      scope: exportScope.value,
      pageRange: exportScope.value === 'range' ? pageRange.value : undefined,
      ...options.value,
    };
    
    // Emit the export event with options
    const result = await emit('export', exportOptions);
    
    // If the export was handled by the parent, don't proceed
    if (result === false) return;
    
    // Otherwise, use the default export behavior
    await exportData({
      data: [], // Empty data means parent should provide data
      ...exportOptions,
    });
    
    // Show success message
    emit('success', { format: selectedFormat.value });
    
    // Close the dialog after a short delay
    setTimeout(close, 1000);
  } catch (error) {
    console.error('Export error:', error);
    emit('error', error);
  }
};

const open = (initialOptions = {}) => {
  // Reset form
  resetForm();
  
  // Apply initial options
  if (initialOptions.format) {
    selectedFormat.value = initialOptions.format;
  }
  
  if (initialOptions.fileName) {
    options.value.fileName = initialOptions.fileName;
  } else {
    // Generate a default filename based on the current date and time
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0];
    const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '-');
    options.value.fileName = `export-${dateStr}-${timeStr}`;
  }
  
  visible.value = true;
};

const close = () => {
  // Only allow closing if not currently exporting
  if (!isExporting.value) {
    visible.value = false;
    resetForm();
  }
};

const resetForm = () => {
  selectedFormat.value = 'excel';
  exportScope.value = 'current';
  pageRange.value = '';
  showAdvancedOptions.value = false;
  options.value = {
    includeHeader: true,
    freezeHeader: true,
    pageSize: 'A4',
    orientation: 'portrait',
    fileName: '',
  };
};

// Watch for export completion
watch(isExporting, (newVal) => {
  if (!newVal && exportProgress.value >= 100) {
    // Auto-close after export completes
    setTimeout(close, 1500);
  }
});

// Expose methods
defineExpose({
  open,
  close,
  isExporting,
  exportProgress,
});
</script>

<style scoped>
.export-dialog :deep(.p-dialog-content) {
  overflow-y: visible;
}

.export-progress {
  padding: 1rem 0;
}

.export-complete :deep(.p-progressbar-value) {
  background-color: var(--green-500);
  transition: background-color 0.3s ease;
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 1rem 0;
}
</style>
