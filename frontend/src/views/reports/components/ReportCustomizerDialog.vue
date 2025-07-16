<template>
  <Dialog 
    v-model:visible="modelValue" 
    :header="`Customize: ${report?.name || 'Report'}`"
    :style="{ width: '80vw', maxWidth: '1200px' }"
    :modal="true"
    class="p-fluid"
    :closable="true"
    @hide="onHide"
  >
    <TabView>
      <!-- Parameters Tab -->
      <TabPanel header="Parameters">
        <div class="grid">
          <div class="col-12 md:col-6">
            <h4>Report Parameters</h4>
            <p class="text-500 text-sm mt-0 mb-4">Configure the data to include in your report</p>
            
            <div v-for="param in report?.parameters || []" :key="param.name" class="field">
              <label :for="param.name">{{ param.label || param.name }}</label>
              
              <!-- Text Input -->
              <InputText 
                v-if="param.type === 'text' || param.type === 'number'"
                v-model="parameters[param.name]"
                :type="param.type"
                class="w-full"
                :placeholder="param.placeholder || ''"
              />
              
              <!-- Date Picker -->
              <Calendar 
                v-else-if="param.type === 'date'"
                v-model="parameters[param.name]"
                :showIcon="true"
                dateFormat="yy-mm-dd"
                class="w-full"
                :showButtonBar="true"
              />
              
              <!-- Date Range Picker -->
              <div v-else-if="param.type === 'date-range'" class="p-inputgroup">
                <span class="p-inputgroup-addon">
                  <i class="pi pi-calendar"></i>
                </span>
                <InputText 
                  v-model="parameters[param.name]"
                  class="w-full"
                  :placeholder="'Select ' + (param.label || param.name)"
                  readonly
                />
                <Button 
                  icon="pi pi-calendar"
                  @click="showDateRangePicker(param.name)"
                />
              </div>
              
              <!-- Dropdown -->
              <Dropdown 
                v-else-if="param.type === 'select'"
                v-model="parameters[param.name]"
                :options="getParameterOptions(param)"
                optionLabel="label"
                optionValue="value"
                :placeholder="'Select ' + (param.label || param.name)"
                class="w-full"
              />
              
              <!-- Multi-Select -->
              <MultiSelect 
                v-else-if="param.type === 'multiselect'"
                v-model="parameters[param.name]"
                :options="getParameterOptions(param)"
                :optionLabel="'label'"
                :optionValue="'value'"
                :placeholder="'Select ' + (param.label || param.name)"
                display="chip"
                class="w-full"
              />
              
              <!-- Boolean Switch -->
              <InputSwitch 
                v-else-if="param.type === 'boolean'"
                v-model="parameters[param.name]"
              />
              
              <small v-if="param.description" class="text-500 block mt-1">{{ param.description }}</small>
            </div>
            
            <div v-if="!report?.parameters?.length" class="text-center p-5">
              <i class="pi pi-sliders-h text-6xl text-400 mb-3" />
              <h4>No Parameters Defined</h4>
              <p class="text-500">This report doesn't have any customizable parameters.</p>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <h4>Preview</h4>
            <p class="text-500 text-sm mt-0 mb-4">See how your parameters will affect the report</p>
            
            <div class="border-1 surface-border p-3 border-round" style="min-height: 300px;">
              <div v-if="!report" class="flex align-items-center justify-content-center h-full">
                <div class="text-center">
                  <i class="pi pi-eye text-6xl text-400 mb-3" />
                  <p class="text-500">Report preview will appear here</p>
                </div>
              </div>
              
              <div v-else class="p-3">
                <h5 class="mt-0">{{ report.name }}</h5>
                <p class="text-500">Generated with the following parameters:</p>
                
                <DataTable :value="getPreviewParameters()" class="p-datatable-sm" :showGridlines="true" :rows="10" :paginator="true">
                  <Column field="name" header="Parameter"></Column>
                  <Column field="value" header="Value"></Column>
                </DataTable>
              </div>
            </div>
            
            <div class="mt-4">
              <Button 
                label="Run Report" 
                icon="pi pi-play" 
                class="p-button-primary w-full"
                @click="onRun"
              />
            </div>
          </div>
        </div>
      </TabPanel>
      
      <!-- Display Options Tab -->
      <TabPanel header="Display">
        <div class="grid">
          <div class="col-12 md:col-6">
            <h4>Layout & Formatting</h4>
            <p class="text-500 text-sm mt-0 mb-4">Customize how the report looks</p>
            
            <div class="field">
              <label>Report Title</label>
              <InputText v-model="displayOptions.title" class="w-full" />
            </div>
            
            <div class="field">
              <label>Show Grid Lines</label>
              <InputSwitch v-model="displayOptions.showGridLines" />
            </div>
            
            <div class="field">
              <label>Show Row Numbers</label>
              <InputSwitch v-model="displayOptions.showRowNumbers" />
            </div>
            
            <div class="field">
              <label>Font Size</label>
              <Dropdown 
                v-model="displayOptions.fontSize" 
                :options="['Small', 'Normal', 'Large', 'Extra Large']"
                class="w-full"
              />
            </div>
            
            <div class="field">
              <label>Orientation</label>
              <div class="flex gap-3 mt-2">
                <div class="flex align-items-center">
                  <RadioButton 
                    id="orientation-portrait" 
                    v-model="displayOptions.orientation" 
                    value="portrait" 
                    name="orientation"
                  />
                  <label for="orientation-portrait" class="ml-2">Portrait</label>
                </div>
                <div class="flex align-items-center">
                  <RadioButton 
                    id="orientation-landscape" 
                    v-model="displayOptions.orientation" 
                    value="landscape" 
                    name="orientation"
                  />
                  <label for="orientation-landscape" class="ml-2">Landscape</label>
                </div>
              </div>
            </div>
            
            <div class="field">
              <label>Page Size</label>
              <Dropdown 
                v-model="displayOptions.pageSize" 
                :options="['Letter', 'Legal', 'A4', 'A3', 'Tabloid']"
                class="w-full"
              />
            </div>
            
            <div class="field">
              <label>Margins (inches)</label>
              <div class="grid">
                <div class="col-6">
                  <label class="block text-sm text-500 mb-1">Top</label>
                  <InputNumber v-model="displayOptions.margins.top" mode="decimal" :min="0.1" :max="2" :step="0.1" class="w-full" />
                </div>
                <div class="col-6">
                  <label class="block text-sm text-500 mb-1">Right</label>
                  <InputNumber v-model="displayOptions.margins.right" mode="decimal" :min="0.1" :max="2" :step="0.1" class="w-full" />
                </div>
                <div class="col-6">
                  <label class="block text-sm text-500 mb-1">Bottom</label>
                  <InputNumber v-model="displayOptions.margins.bottom" mode="decimal" :min="0.1" :max="2" :step="0.1" class="w-full" />
                </div>
                <div class="col-6">
                  <label class="block text-sm text-500 mb-1">Left</label>
                  <InputNumber v-model="displayOptions.margins.left" mode="decimal" :min="0.1" :max="2" :step="0.1" class="w-full" />
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <h4>Headers & Footers</h4>
            <p class="text-500 text-sm mt-0 mb-4">Customize report headers and footers</p>
            
            <div class="field">
              <label>Show Header</label>
              <InputSwitch v-model="displayOptions.showHeader" />
            </div>
            
            <div v-if="displayOptions.showHeader" class="field">
              <label>Header Content</label>
              <Textarea v-model="displayOptions.headerContent" rows="3" class="w-full" />
              <small class="text-500">Use placeholders like {page}, {pages}, {date}, {time}, {title}</small>
            </div>
            
            <div class="field">
              <label>Show Footer</label>
              <InputSwitch v-model="displayOptions.showFooter" />
            </div>
            
            <div v-if="displayOptions.showFooter" class="field">
              <label>Footer Content</label>
              <Textarea v-model="displayOptions.footerContent" rows="3" class="w-full" />
              <small class="text-500">Use placeholders like {page}, {pages}, {date}, {time}, {title}</small>
            </div>
            
            <div class="field">
              <label>Show Page Numbers</label>
              <InputSwitch v-model="displayOptions.showPageNumbers" />
            </div>
            
            <div v-if="displayOptions.showPageNumbers" class="field">
              <label>Page Number Format</label>
              <InputText v-model="displayOptions.pageNumberFormat" class="w-full" />
              <small class="text-500">Example: Page {page} of {pages}</small>
            </div>
            
            <div class="field">
              <label>Watermark</label>
              <InputText v-model="displayOptions.watermark" class="w-full" placeholder="e.g., DRAFT, CONFIDENTIAL" />
            </div>
          </div>
        </div>
      </TabPanel>
      
      <!-- Other tabs will be added in subsequent files -->
      
    </TabView>
    
    <template #footer>
      <div class="flex justify-content-between">
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="onCancel"
        />
        <div>
          <Button 
            label="Apply" 
            icon="pi pi-check" 
            class="p-button-primary"
            @click="onApply"
          />
          <Button 
            label="Save as Default" 
            icon="pi pi-save" 
            class="p-button-text"
            @click="onSaveAsDefault"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { PropType } from 'vue';
import type { Report, ReportParameter, ReportDisplayOptions } from '@/types/reports';

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  report: {
    type: Object as PropType<Report | null>,
    default: null,
  },
  initialParameters: {
    type: Object as PropType<Record<string, any>>,
    default: () => ({}),
  },
  initialDisplayOptions: {
    type: Object as PropType<ReportDisplayOptions>,
    default: () => ({
      title: '',
      showGridLines: true,
      showRowNumbers: true,
      fontSize: 'Normal',
      orientation: 'portrait',
      pageSize: 'Letter',
      margins: {
        top: 0.75,
        right: 0.5,
        bottom: 0.75,
        left: 0.5,
      },
      showHeader: true,
      headerContent: '{title}',
      showFooter: true,
      footerContent: 'Page {page} of {pages} | Generated on {date}',
      showPageNumbers: true,
      pageNumberFormat: 'Page {page} of {pages}',
      watermark: '',
    }),
  },
});

const emit = defineEmits([
  'update:modelValue',
  'apply',
  'cancel',
  'save-as-default',
]);

// Local state
const parameters = ref<Record<string, any>>({ ...props.initialParameters });
const displayOptions = ref<ReportDisplayOptions>({ ...props.initialDisplayOptions });

// Computed
const hasChanges = computed(() => {
  return (
    JSON.stringify(parameters.value) !== JSON.stringify(props.initialParameters) ||
    JSON.stringify(displayOptions.value) !== JSON.stringify(props.initialDisplayOptions)
  );
});

// Watchers
watch(() => props.initialParameters, (newVal) => {
  parameters.value = { ...newVal };
}, { deep: true });

watch(() => props.initialDisplayOptions, (newVal) => {
  displayOptions.value = { ...newVal };
}, { deep: true });

// Methods
const getParameterOptions = (param: ReportParameter) => {
  if (param.options) {
    return param.options;
  }
  
  // Default options for common parameter types
  switch (param.type) {
    case 'date-range':
      return [
        { label: 'Today', value: 'today' },
        { label: 'Yesterday', value: 'yesterday' },
        { label: 'This Week', value: 'this_week' },
        { label: 'Last Week', value: 'last_week' },
        { label: 'This Month', value: 'this_month' },
        { label: 'Last Month', value: 'last_month' },
        { label: 'This Quarter', value: 'this_quarter' },
        { label: 'Last Quarter', value: 'last_quarter' },
        { label: 'This Year', value: 'this_year' },
        { label: 'Last Year', value: 'last_year' },
        { label: 'Custom Range...', value: 'custom' },
      ];
    default:
      return [];
  }
};

const getPreviewParameters = () => {
  if (!props.report?.parameters?.length) {
    return [];
  }
  
  return props.report.parameters.map(param => ({
    name: param.label || param.name,
    value: parameters.value[param.name] !== undefined ? 
      String(parameters.value[param.name]) : 
      param.defaultValue ? 
        `Default: ${param.defaultValue}` : 
        'Not set',
  }));
};

const showDateRangePicker = (paramName: string) => {
  // Implementation for showing a date range picker
  console.log('Show date range picker for parameter:', paramName);
};

const onHide = () => {
  // Reset to initial values when dialog is hidden
  parameters.value = { ...props.initialParameters };
  displayOptions.value = { ...props.initialDisplayOptions };
  emit('update:modelValue', false);
};

const onCancel = () => {
  emit('cancel');
  emit('update:modelValue', false);
};

const onApply = () => {
  emit('apply', {
    parameters: { ...parameters.value },
    displayOptions: { ...displayOptions.value },
  });
  emit('update:modelValue', false);
};

const onSaveAsDefault = () => {
  emit('save-as-default', {
    parameters: { ...parameters.value },
    displayOptions: { ...displayOptions.value },
  });
};

const onRun = () => {
  emit('apply', {
    parameters: { ...parameters.value },
    displayOptions: { ...displayOptions.value },
  });
  emit('update:modelValue', false);
};
</script>

<style scoped>
.field {
  margin-bottom: 1.5rem;
}

:deep(.p-tabview-panels) {
  padding: 1rem 0;
}

:deep(.p-tabview-nav) {
  border-bottom: 1px solid var(--surface-d);
}

:deep(.p-tabview .p-tabview-nav li .p-tabview-nav-link) {
  padding: 1rem 1.5rem;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 1rem;
}
</style>
