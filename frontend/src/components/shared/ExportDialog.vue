<template>
  <Dialog
    v-model:visible="modelValue"
    :style="{ width: '600px' }"
    :header="$t('common.exportData')"
    :modal="true"
    :closable="!loading"
    :close-on-escape="!loading"
  >
    <div class="export-dialog">
      <!-- Format Selection -->
      <div class="mb-4">
        <label class="block text-700 font-medium mb-2">{{ $t('common.format') }}</label>
        <div class="grid">
          <div 
            v-for="format in formats" 
            :key="format.value"
            class="col-6 md:col-4"
          >
            <div 
              class="p-3 border-round border-1 border-300 cursor-pointer hover:surface-100 transition-colors transition-duration-150"
              :class="{ 'border-primary-500 bg-primary-50': selectedFormat === format.value }"
              @click="selectedFormat = format.value"
            >
              <div class="flex align-items-center gap-3">
                <i :class="['text-2xl', format.icon || 'pi pi-file']" />
                <div>
                  <div class="font-medium">{{ format.label }}</div>
                  <div class="text-sm text-600">{{ getFormatDescription(format.value) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Export Options -->
      <div class="mb-4">
        <h4 class="mb-3">{{ $t('export.options') }}</h4>
        
        <!-- Scope Selection -->
        <div class="field mb-4">
          <label class="block text-700 font-medium mb-2">{{ $t('export.scope') }}</label>
          <div class="flex flex-wrap gap-3">
            <div class="flex align-items-center">
              <RadioButton 
                id="currentPage" 
                v-model="exportScope" 
                value="current" 
                :disabled="loading"
              />
              <label for="currentPage" class="ml-2">{{ $t('export.currentPage') }}</label>
            </div>
            <div class="flex align-items-center">
              <RadioButton 
                id="allPages" 
                v-model="exportScope" 
                value="all" 
                :disabled="loading"
              />
              <label for="allPages" class="ml-2">{{ $t('export.allData') }}</label>
            </div>
            <div class="flex align-items-center" v-if="hasPagination">
              <RadioButton 
                id="pageRange" 
                v-model="exportScope" 
                value="range" 
                :disabled="loading"
              />
              <label for="pageRange" class="ml-2">{{ $t('export.pageRange') }}</label>
            </div>
          </div>
        </div>

        <!-- Page Range (Conditional) -->
        <div v-if="exportScope === 'range'" class="field grid">
          <div class="col-12 md:col-6">
            <label for="startPage" class="block text-700 font-medium mb-2">{{ $t('export.startPage') }}</label>
            <InputNumber 
              id="startPage" 
              v-model="pageRange.start" 
              :min="1" 
              :max="totalPages" 
              :disabled="loading"
              show-buttons
              class="w-full"
            />
          </div>
          <div class="col-12 md:col-6">
            <label for="endPage" class="block text-700 font-medium mb-2">{{ $t('export.endPage') }}</label>
            <InputNumber 
              id="endPage" 
              v-model="pageRange.end" 
              :min="pageRange.start" 
              :max="totalPages" 
              :disabled="loading"
              show-buttons
              class="w-full"
            />
          </div>
        </div>

        <!-- Format-Specific Options -->
        <div v-if="selectedFormat === 'pdf'" class="field mt-4">
          <h5 class="mb-3">{{ $t('export.pdfOptions') }}</h5>
          <div class="grid">
            <div class="col-12 md:col-6">
              <label class="block text-700 font-medium mb-2">{{ $t('export.pageSize') }}</label>
              <Dropdown 
                v-model="pdfOptions.pageSize" 
                :options="pageSizes" 
                option-label="label" 
                option-value="value"
                :disabled="loading"
                class="w-full"
              />
            </div>
            <div class="col-12 md:col-6">
              <label class="block text-700 font-medium mb-2">{{ $t('export.orientation') }}</label>
              <div class="flex gap-3">
                <div class="flex align-items-center">
                  <RadioButton 
                    id="portrait" 
                    v-model="pdfOptions.orientation" 
                    value="portrait" 
                    :disabled="loading"
                  />
                  <label for="portrait" class="ml-2">{{ $t('export.portrait') }}</label>
                </div>
                <div class="flex align-items-center">
                  <RadioButton 
                    id="landscape" 
                    v-model="pdfOptions.orientation" 
                    value="landscape" 
                    :disabled="loading"
                  />
                  <label for="landscape" class="ml-2">{{ $t('export.landscape') }}</label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="selectedFormat === 'xlsx'" class="field mt-4">
          <h5 class="mb-3">{{ $t('export.excelOptions') }}</h5>
          <div class="flex flex-column gap-3">
            <div class="flex align-items-center">
              <Checkbox 
                id="includeFilters" 
                v-model="excelOptions.includeFilters" 
                :binary="true" 
                :disabled="loading"
              />
              <label for="includeFilters" class="ml-2">{{ $t('export.includeFilters') }}</label>
            </div>
            <div class="flex align-items-center">
              <Checkbox 
                id="freezeHeader" 
                v-model="excelOptions.freezeHeader" 
                :binary="true" 
                :disabled="loading"
              />
              <label for="freezeHeader" class="ml-2">{{ $t('export.freezeHeader') }}</label>
            </div>
          </div>
        </div>

        <div v-else-if="selectedFormat === 'csv'" class="field mt-4">
          <h5 class="mb-3">{{ $t('export.csvOptions') }}</h5>
          <div class="grid">
            <div class="col-12 md:col-6">
              <label class="block text-700 font-medium mb-2">{{ $t('export.delimiter') }}</label>
              <Dropdown 
                v-model="csvOptions.delimiter" 
                :options="delimiters" 
                option-label="label" 
                option-value="value"
                :disabled="loading"
                class="w-full"
              />
            </div>
            <div class="col-12 md:col-6">
              <label class="block text-700 font-medium mb-2">{{ $t('export.textQualifier') }}</label>
              <Dropdown 
                v-model="csvOptions.textQualifier" 
                :options="textQualifiers" 
                option-label="label" 
                option-value="value"
                :disabled="loading"
                class="w-full"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Progress Bar -->
      <div v-if="loading" class="mb-4">
        <div class="flex justify-content-between mb-2">
          <span>{{ $t('export.preparingExport') }}</span>
          <span>{{ progress }}%</span>
        </div>
        <ProgressBar :value="progress" :showValue="false" />
      </div>
    </div>

    <template #footer>
      <Button 
        :label="$t('common.cancel')" 
        class="p-button-text" 
        :disabled="loading"
        @click="$emit('update:modelValue', false)" 
      />
      <Button 
        :label="$t('common.export')" 
        icon="pi pi-download" 
        :loading="loading"
        @click="handleExport" 
      />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';

export default defineComponent({
  name: 'ExportDialog',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    formats: {
      type: Array,
      default: () => [
        { label: 'PDF', value: 'pdf', icon: 'pi pi-file-pdf' },
        { label: 'Excel', value: 'xlsx', icon: 'pi pi-file-excel' },
        { label: 'CSV', value: 'csv', icon: 'pi pi-file' }
      ]
    },
    hasPagination: {
      type: Boolean,
      default: true
    },
    totalPages: {
      type: Number,
      default: 1
    },
    loading: {
      type: Boolean,
      default: false
    },
    progress: {
      type: Number,
      default: 0
    }
  },
  emits: ['update:modelValue', 'export'],
  setup(props, { emit }) {
    // State
    const selectedFormat = ref(props.formats[0]?.value || 'pdf');
    const exportScope = ref('current');
    const pageRange = ref({
      start: 1,
      end: props.totalPages || 1
    });

    // PDF Options
    const pdfOptions = ref({
      pageSize: 'A4',
      orientation: 'portrait'
    });

    // Excel Options
    const excelOptions = ref({
      includeFilters: true,
      freezeHeader: true
    });

    // CSV Options
    const csvOptions = ref({
      delimiter: ',',
      textQualifier: '"'
    });

    // Available options
    const pageSizes = [
      { label: 'A4 (210 × 297 mm)', value: 'A4' },
      { label: 'Letter (8.5 × 11 in)', value: 'LETTER' },
      { label: 'Legal (8.5 × 14 in)', value: 'LEGAL' },
      { label: 'Tabloid (11 × 17 in)', value: 'TABLOID' }
    ];

    const delimiters = [
      { label: 'Comma (,)', value: ',' },
      { label: 'Semicolon (;)', value: ';' },
      { label: 'Tab (\t)', value: '\t' },
      { label: 'Pipe (|)', value: '|' }
    ];

    const textQualifiers = [
      { label: 'Double Quote (")', value: '"' },
      { label: 'Single Quote (\')', value: "'" },
      { label: 'None', value: '' }
    ];

    // Watchers
    watch(() => props.totalPages, (newVal) => {
      pageRange.value.end = Math.min(pageRange.value.end, newVal);
    });

    // Methods
    const getFormatDescription = (format: string) => {
      switch (format) {
        case 'pdf': return 'Portable Document Format';
        case 'xlsx': return 'Microsoft Excel';
        case 'csv': return 'Comma-Separated Values';
        default: return '';
      }
    };

    const handleExport = () => {
      const options: any = {
        format: selectedFormat.value,
        scope: exportScope.value,
        ...(exportScope.value === 'range' && {
          pageRange: {
            start: pageRange.value.start,
            end: pageRange.value.end
          }
        })
      };

      // Add format-specific options
      if (selectedFormat.value === 'pdf') {
        options.pdfOptions = pdfOptions.value;
      } else if (selectedFormat.value === 'xlsx') {
        options.excelOptions = excelOptions.value;
      } else if (selectedFormat.value === 'csv') {
        options.csvOptions = csvOptions.value;
      }

      emit('export', options);
    };

    return {
      // State
      selectedFormat,
      exportScope,
      pageRange,
      
      // Options
      pdfOptions,
      excelOptions,
      csvOptions,
      pageSizes,
      delimiters,
      textQualifiers,
      
      // Methods
      getFormatDescription,
      handleExport
    };
  }
});
</script>

<style scoped>
.export-dialog {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 0.5rem;
}

/* Custom scrollbar */
.export-dialog::-webkit-scrollbar {
  width: 8px;
}

.export-dialog::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.export-dialog::-webkit-scrollbar-thumb {
  background: #9e9e9e;
  border-radius: 4px;
}

.export-dialog::-webkit-scrollbar-thumb:hover {
  background: #757575;
}
</style>
