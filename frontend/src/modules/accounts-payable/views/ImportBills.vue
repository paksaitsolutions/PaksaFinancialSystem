<template>
  <div class="import-bills">
    <h2>Import Bills</h2>
    <Card>
      <template #content>
        <div class="upload-area">
          <FileUpload 
            mode="basic" 
            name="bills[]" 
            :url="uploadUrl" 
            accept=".csv,.xlsx" 
            :maxFileSize="10000000"
            @upload="onUpload" 
            @error="onError"
            :auto="false"
            chooseLabel="Select File"
          />
          <p class="text-sm text-color-secondary mt-2">
            Supported formats: CSV, Excel (.xlsx)
          </p>
        </div>
        <Button label="Import" icon="pi pi-upload" @click="importBills" :loading="importing" />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const importing = ref(false)
const uploadUrl = '/api/v1/ap/import-bills'

const importBills = async () => {
  importing.value = true
  try {
    // Import logic here
    toast.add({ severity: 'success', summary: 'Success', detail: 'Bills imported successfully' })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to import bills' })
  } finally {
    importing.value = false
  }
}

const onUpload = () => {
  toast.add({ severity: 'success', summary: 'Success', detail: 'File uploaded' })
}

const onError = () => {
  toast.add({ severity: 'error', summary: 'Error', detail: 'Upload failed' })
}
</script>