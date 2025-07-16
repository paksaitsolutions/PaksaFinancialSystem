<template>
  <Dialog 
    v-model:visible="modelValue" 
    :header="`Export: ${report?.name || 'Report'}"
    :style="{ width: '600px' }"
    :modal="true"
    class="p-fluid"
    :closable="true"
    @hide="onHide"
  >
    <div v-if="exporting" class="flex flex-column align-items-center justify-content-center p-5">
      <ProgressSpinner />
      <p class="mt-3">Preparing export, please wait...</p>
      <div class="w-full mt-3">
        <ProgressBar :value="exportProgress" :showValue="false" />
        <div class="flex justify-content-between mt-2">
          <small class="text-500">{{ exportStatus }}</small>
          <small class="text-500">{{ exportProgress }}%</small>
        </div>
      </div>
    </div>
    
    <div v-else>
      <div class="field">
        <label>Export Format</label>
        <div class="grid">
          <div 
            v-for="format in exportFormats" 
            :key="format.value" 
            class="col-6 md:col-4 p-2"
          >
            <div 
              class="border-1 surface-border border-round p-3 flex flex-column align-items-center cursor-pointer hover:surface-100 transition-colors transition-duration-150"
              :class="{ 'border-primary': selectedFormat === format.value, 'surface-50': selectedFormat === format.value }"
              @click="selectedFormat = format.value"
            >
              <i :class="format.icon" class="text-4xl mb-2" :class="format.color || 'text-700'" />
              <div class="font-medium">{{ format.label }}</div>
              <small class="text-500">{{ format.extension }}</small>
            </div>
          </div>
        </div>
      </div>
      
      <template v-if="selectedFormat">
        <Divider />
        
        <div class="field">
          <label>File Name</label>
          <div class="p-inputgroup">
            <InputText 
              v-model="fileName" 
              class="w-full" 
              placeholder="Enter file name"
            />
            <span class="p-inputgroup-addon">
              .{{ getFormatExtension(selectedFormat) }}
            </span>
          </div>
        </div>
        
        <div v-if="hasExportOptions" class="field">
          <label>Options</label>
          
          <!-- PDF Options -->
          <div v-if="selectedFormat === 'pdf'" class="grid">
            <div class="col-12 md:col-6">
              <div class="field-checkbox">
                <Checkbox 
                  id="landscape" 
                  v-model="exportOptions.pdf.landscape" 
                  :binary="true"
                />
                <label for="landscape">Landscape Orientation</label>
              </div>
              
              <div class="field-checkbox">
                <Checkbox 
                  id="includeHeaderFooter" 
                  v-model="exportOptions.pdf.includeHeaderFooter" 
                  :binary="true"
                />
                <label for="includeHeaderFooter">Include Header & Footer</label>
              </div>
              
              <div class="field-checkbox">
                <Checkbox 
                  id="printBackground" 
                  v-model="exportOptions.pdf.printBackground" 
                  :binary="true"
                />
                <label for="printBackground">Print Background</label>
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Page Size</label>
                <Dropdown 
                  v-model="exportOptions.pdf.pageSize" 
                  :options="pageSizes"
                  optionLabel="label"
                  optionValue="value"
                  class="w-full"
                />
              </div>
              
              <div class="field">
                <label>Scale</label>
                <div class="p-inputgroup">
                  <InputNumber 
                    v-model="exportOptions.pdf.scale" 
                    :min="0.1" 
                    :max="2" 
                    :step="0.1"
                    class="w-full"
                  />
                  <span class="p-inputgroup-addon">x</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Excel Options -->
          <div v-else-if="selectedFormat === 'xlsx'" class="grid">
            <div class="col-12">
              <div class="field-checkbox">
                <Checkbox 
                  id="includeFilters" 
                  v-model="exportOptions.excel.includeFilters" 
                  :binary="true"
                />
                <label for="includeFilters">Include Filters</label>
              </div>
              
              <div class="field-checkbox">
                <Checkbox 
                  id="includeFormulas" 
                  v-model="exportOptions.excel.includeFormulas" 
                  :binary="true"
                />
                <label for="includeFormulas">Include Formulas</label>
              </div>
              
              <div class="field">
                <label>Freeze Panes</label>
                <div class="flex align-items-center">
                  <InputNumber 
                    v-model="exportOptions.excel.freezeRows" 
                    :min="0" 
                    :max="10" 
                    class="w-6rem"
                    placeholder="Rows"
                  />
                  <span class="mx-2">x</span>
                  <InputNumber 
                    v-model="exportOptions.excel.freezeColumns" 
                    :min="0" 
                    :max="10" 
                    class="w-6rem"
                    placeholder="Columns"
                  />
                </div>
              </div>
            </div>
          </div>
          
          <!-- CSV Options -->
          <div v-else-if="selectedFormat === 'csv'" class="grid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Field Delimiter</label>
                <InputText 
                  v-model="exportOptions.csv.delimiter" 
                  class="w-full" 
                  maxlength="1"
                />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Text Qualifier</label>
                <Dropdown 
                  v-model="exportOptions.csv.qualifier" 
                  :options="textQualifiers"
                  optionLabel="label"
                  optionValue="value"
                  class="w-full"
                />
              </div>
            </div>
            <div class="col-12">
              <div class="field-checkbox">
                <Checkbox 
                  id="includeHeader" 
                  v-model="exportOptions.csv.includeHeader" 
                  :binary="true"
                />
                <label for="includeHeader">Include Column Headers</label>
              </div>
              
              <div class="field-checkbox">
                <Checkbox 
                  id="useTextQualifier" 
                  v-model="exportOptions.csv.useTextQualifier" 
                  :binary="true"
                />
                <label for="useTextQualifier">Use Text Qualifier</label>
              </div>
            </div>
          </div>
          
          <!-- Image Options -->
          <div v-else-if="selectedFormat === 'png' || selectedFormat === 'jpg'" class="grid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Quality</label>
                <InputNumber 
                  v-model="exportOptions.image.quality" 
                  :min="0.1" 
                  :max="1" 
                  :step="0.1"
                  class="w-full"
                />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Scale</label>
                <InputNumber 
                  v-model="exportOptions.image.scale" 
                  :min="0.1" 
                  :max="3" 
                  :step="0.1"
                  class="w-full"
                />
              </div>
            </div>
          </div>
        </div>
        
        <Divider />
        
        <div class="field">
          <label>What to Export</label>
          <div class="flex flex-column gap-2">
            <div class="flex align-items-center">
              <RadioButton 
                id="exportCurrent" 
                v-model="exportWhat" 
                value="current" 
                name="exportWhat" 
                class="mr-2"
              />
              <label for="exportCurrent">Current view only</label>
            </div>
            <div class="flex align-items-center">
              <RadioButton 
                id="exportAll" 
                v-model="exportWhat" 
                value="all" 
                name="exportWhat" 
                class="mr-2"
              />
              <label for="exportAll">All data ({{ totalRows }} rows)</label>
            </div>
            <div v-if="totalPages > 1" class="flex align-items-center">
              <RadioButton 
                id="exportRange" 
                v-model="exportWhat" 
                value="range" 
                name="exportWhat" 
                class="mr-2"
              />
              <label for="exportRange">Pages</label>
              <div v-if="exportWhat === 'range'" class="flex align-items-center ml-3">
                <InputNumber 
                  v-model="exportPageFrom" 
                  :min="1" 
                  :max="exportPageTo || totalPages" 
                  class="w-4rem"
                />
                <span class="mx-2">to</span>
                <InputNumber 
                  v-model="exportPageTo" 
                  :min="exportPageFrom || 1" 
                  :max="totalPages" 
                  class="w-4rem"
                />
                <span class="ml-2">of {{ totalPages }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <Divider />
        
        <div class="field">
          <label>After Export</label>
          <div class="flex flex-column gap-2">
            <div class="flex align-items-center">
              <RadioButton 
                id="actionDownload" 
                v-model="afterExport" 
                value="download" 
                name="afterExport" 
                class="mr-2"
              />
              <label for="actionDownload">Download file</label>
            </div>
            <div class="flex align-items-center">
              <RadioButton 
                id="actionEmail" 
                v-model="afterExport" 
                value="email" 
                name="afterExport" 
                class="mr-2"
              />
              <label for="actionEmail">Email to</label>
              <InputText 
                v-if="afterExport === 'email'" 
                v-model="emailAddress" 
                class="ml-2 flex-grow-1" 
                placeholder="email@example.com"
              />
            </div>
            <div class="flex align-items-center">
              <RadioButton 
                id="actionSave" 
                v-model="afterExport" 
                value="save" 
                name="afterExport" 
                class="mr-2"
              />
              <label for="actionSave">Save to Documents</label>
              <Dropdown 
                v-if="afterExport === 'save'" 
                v-model="saveFolder" 
                :options="folders" 
                optionLabel="name" 
                optionValue="id" 
                placeholder="Select folder" 
                class="ml-2 flex-grow-1"
              />
            </div>
          </div>
        </div>
      </template>
    </div>
    
    <template #footer>
      <div class="flex justify-content-between">
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="onCancel"
          :disabled="exporting"
        />
        <div>
          <Button 
            label="Export" 
            :icon="exportIcon" 
            class="p-button-primary"
            @click="onExport"
            :disabled="!selectedFormat || exporting"
            :loading="exporting"
          />
          <Button 
            v-if="selectedFormat"
            label="Schedule..." 
            icon="pi pi-calendar" 
            class="p-button-text"
            @click="onSchedule"
            :disabled="exporting"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
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
  totalRows: {
    type: Number,
    default: 0,
  },
  totalPages: {
    type: Number,
    default: 1,
  },
  currentPage: {
    type: Number,
    default: 1,
  },
});

const emit = defineEmits([
  'update:modelValue',
  'export',
  'schedule',
  'cancel',
]);

// State
const exporting = ref(false);
const exportProgress = ref(0);
const exportStatus = ref('Preparing export...');
const selectedFormat = ref('pdf');
const fileName = ref('');
const exportWhat = ref('current');
const exportPageFrom = ref(1);
const exportPageTo = ref(1);
const afterExport = ref('download');
const emailAddress = ref('');
const saveFolder = ref('');

// Options
const exportFormats = [
  { label: 'PDF', value: 'pdf', extension: '.pdf', icon: 'pi pi-file-pdf', color: 'text-red-500' },
  { label: 'Excel', value: 'xlsx', extension: '.xlsx', icon: 'pi pi-file-excel', color: 'text-green-600' },
  { label: 'CSV', value: 'csv', extension: '.csv', icon: 'pi pi-file', color: 'text-blue-500' },
  { label: 'HTML', value: 'html', extension: '.html', icon: 'pi pi-code', color: 'text-orange-500' },
  { label: 'Image (PNG)', value: 'png', extension: '.png', icon: 'pi pi-image', color: 'text-purple-500' },
  { label: 'Image (JPEG)', value: 'jpg', extension: '.jpg', icon: 'pi pi-image', color: 'text-teal-500' },
];

const pageSizes = [
  { label: 'Letter (8.5" x 11")', value: 'Letter' },
  { label: 'Legal (8.5" x 14")', value: 'Legal' },
  { label: 'A4 (210mm x 297mm)', value: 'A4' },
  { label: 'A3 (297mm x 420mm)', value: 'A3' },
  { label: 'Tabloid (11" x 17")', value: 'Tabloid' },
];

const textQualifiers = [
  { label: 'Double Quote ( ")', value: '"' },
  { label: "Single Quote ( ' )", value: "'" },
  { label: 'None', value: '' },
];

const folders = [
  { id: 'reports', name: 'Reports' },
  { id: 'exports', name: 'Exports' },
  { id: 'shared', name: 'Shared' },
  { id: 'personal', name: 'My Documents' },
];

const exportOptions = ref({
  pdf: {
    landscape: false,
    includeHeaderFooter: true,
    printBackground: true,
    pageSize: 'A4',
    scale: 1,
  },
  excel: {
    includeFilters: true,
    includeFormulas: true,
    freezeRows: 1,
    freezeColumns: 1,
  },
  csv: {
    delimiter: ',',
    qualifier: '"',
    includeHeader: true,
    useTextQualifier: true,
  },
  image: {
    quality: 0.8,
    scale: 1,
  },
});

// Computed
const hasExportOptions = computed(() => {
  return ['pdf', 'xlsx', 'csv', 'png', 'jpg'].includes(selectedFormat.value);
});

const exportIcon = computed(() => {
  const format = exportFormats.find(f => f.value === selectedFormat.value);
  return format ? `pi ${format.icon}` : 'pi pi-download';
});

// Watchers
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    resetForm();
  }
});

watch(() => props.currentPage, (newVal) => {
  if (exportWhat.value === 'current') {
    exportPageFrom.value = newVal;
    exportPageTo.value = newVal;
  }
});

// Methods
const getFormatExtension = (format: string) => {
  const found = exportFormats.find(f => f.value === format);
  return found ? found.extension.substring(1) : '';
};

const resetForm = () => {
  selectedFormat.value = 'pdf';
  fileName.value = props.report ? `${props.report.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${new Date().toISOString().split('T')[0]}` : 'report';
  exportWhat.value = 'current';
  exportPageFrom.value = props.currentPage;
  exportPageTo.value = props.currentPage;
  afterExport.value = 'download';
  emailAddress.value = '';
  saveFolder.value = 'reports';
  exportProgress.value = 0;
  exportStatus.value = 'Preparing export...';
};

const onHide = () => {
  emit('update:modelValue', false);
};

const onCancel = () => {
  emit('cancel');
  emit('update:modelValue', false);
};

const onExport = async () => {
  if (!selectedFormat.value) {
    // Show error
    return;
  }
  
  // Prepare export options
  const options = {
    format: selectedFormat.value,
    fileName: `${fileName.value}.${getFormatExtension(selectedFormat.value)}`,
    what: exportWhat.value,
    pageFrom: exportPageFrom.value,
    pageTo: exportPageTo.value,
    afterExport: afterExport.value,
    email: afterExport.value === 'email' ? emailAddress.value : undefined,
    folder: afterExport.value === 'save' ? saveFolder.value : undefined,
    options: { ...exportOptions.value[selectedFormat.value as keyof typeof exportOptions.value] },
  };
  
  // Simulate export progress
  exporting.value = true;
  exportProgress.value = 0;
  exportStatus.value = 'Preparing data...';
  
  // Simulate progress updates
  const progressInterval = setInterval(() => {
    if (exportProgress.value < 90) {
      exportProgress.value += 10;
      exportStatus.value = `Exporting... (${exportProgress.value}%)`;
    }
  }, 300);
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Complete progress
    clearInterval(progressInterval);
    exportProgress.value = 100;
    exportStatus.value = 'Export complete!';
    
    // Emit export event
    emit('export', options);
    
    // Close dialog after a short delay
    setTimeout(() => {
      emit('update:modelValue', false);
    }, 1000);
  } catch (err) {
    console.error('Export failed:', err);
    // Show error message
  } finally {
    exporting.value = false;
    clearInterval(progressInterval);
  }
};

const onSchedule = () => {
  // Close this dialog and open schedule dialog
  emit('schedule', {
    format: selectedFormat.value,
    fileName: `${fileName.value}.${getFormatExtension(selectedFormat.value)}`,
    options: { ...exportOptions.value[selectedFormat.value as keyof typeof exportOptions.value] },
  });
  emit('update:modelValue', false);
};
</script>

<style scoped>
.field {
  margin-bottom: 1.5rem;
}

:deep(.p-dialog-content) {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
