<template>
  <Dialog 
    v-model:visible="visible"
    :header="title || 'Export Report'"
    :modal="true"
    :style="{ width: '500px' }"
    @hide="handleClose"
  >
    <div class="export-options">
      <div class="field">
        <label>Export Format</label>
        <div class="flex flex-column gap-2">
          <div class="field-radiobutton">
            <RadioButton v-model="selectedFormat" inputId="pdf" value="pdf" />
            <label for="pdf" class="ml-2">PDF</label>
          </div>
          <div class="field-radiobutton">
            <RadioButton v-model="selectedFormat" inputId="excel" value="excel" />
            <label for="excel" class="ml-2">Excel (XLSX)</label>
          </div>
          <div class="field-radiobutton">
            <RadioButton v-model="selectedFormat" inputId="csv" value="csv" />
            <label for="csv" class="ml-2">CSV</label>
          </div>
        </div>
      </div>
      
      <div class="field">
        <label for="fileName">File Name</label>
        <InputText 
          id="fileName"
          v-model="fileName"
          class="w-full"
          placeholder="Enter file name"
        />
      </div>
      
      <div class="field-checkbox">
        <Checkbox v-model="includeHeaders" inputId="includeHeaders" binary />
        <label for="includeHeaders" class="ml-2">Include column headers</label>
      </div>
      
      <div class="field-checkbox">
        <Checkbox v-model="includeFilters" inputId="includeFilters" binary />
        <label for="includeFilters" class="ml-2">Include applied filters</label>
      </div>
      
      <div v-if="selectedFormat === 'pdf'" class="field">
        <label>Page Orientation</label>
        <div class="flex gap-4">
          <div class="field-radiobutton">
            <RadioButton v-model="pageOrientation" inputId="portrait" value="portrait" />
            <label for="portrait" class="ml-2">Portrait</label>
          </div>
          <div class="field-radiobutton">
            <RadioButton v-model="pageOrientation" inputId="landscape" value="landscape" />
            <label for="landscape" class="ml-2">Landscape</label>
          </div>
        </div>
      </div>
    </div>
    
    <template #footer>
      <Button 
        label="Cancel"
        class="p-button-text"
        @click="handleClose"
        :disabled="exporting"
      />
      <Button 
        label="Export"
        icon="pi pi-download"
        @click="handleExport"
        :loading="exporting"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface ExportOptions {
  format: string
  fileName: string
  includeHeaders: boolean
  includeFilters: boolean
  pageOrientation?: string
}

const props = defineProps<{
  visible: boolean
  title?: string
  defaultFileName?: string
  loading?: boolean
}>()

const emit = defineEmits(['update:visible', 'export'])

const selectedFormat = ref('pdf')
const fileName = ref('')
const includeHeaders = ref(true)
const includeFilters = ref(false)
const pageOrientation = ref('portrait')
const exporting = ref(false)

const handleExport = async () => {
  exporting.value = true
  
  try {
    const options: ExportOptions = {
      format: selectedFormat.value,
      fileName: fileName.value || 'report',
      includeHeaders: includeHeaders.value,
      includeFilters: includeFilters.value
    }
    
    if (selectedFormat.value === 'pdf') {
      options.pageOrientation = pageOrientation.value
    }
    
    emit('export', options)
    
    // Simulate export delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    handleClose()
  } finally {
    exporting.value = false
  }
}

const handleClose = () => {
  emit('update:visible', false)
}

// Watch for visibility changes to reset form
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    fileName.value = props.defaultFileName || 'report'
    selectedFormat.value = 'pdf'
    includeHeaders.value = true
    includeFilters.value = false
    pageOrientation.value = 'portrait'
  }
})

// Watch for loading prop
watch(() => props.loading, (newLoading) => {
  exporting.value = newLoading || false
})
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color-secondary);
}

.field-radiobutton {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.field-checkbox {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.export-options {
  padding: 1rem 0;
}
</style>