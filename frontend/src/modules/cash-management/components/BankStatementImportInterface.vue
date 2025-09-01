<template>
  <div class="bank-statement-import">
    <Card>
      <template #title>Bank Statement Import</template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="bankAccount">Select Bank Account</label>
              <Dropdown 
                id="bankAccount"
                v-model="selectedAccount"
                :options="bankAccounts"
                optionLabel="name"
                optionValue="id"
                placeholder="Choose account"
                class="w-full"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="fileFormat">File Format</label>
              <Dropdown 
                id="fileFormat"
                v-model="selectedFormat"
                :options="fileFormats"
                optionLabel="label"
                optionValue="value"
                placeholder="Select format"
                class="w-full"
              />
            </div>
          </div>
        </div>
        
        <div class="field">
          <label>Upload Statement File</label>
          <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
            <input 
              ref="fileInput"
              type="file" 
              @change="handleFileSelect"
              accept=".csv,.xlsx,.xls,.ofx,.qfx"
              style="display: none"
            />
            <div class="text-center p-4">
              <i class="pi pi-cloud-upload text-4xl text-primary mb-3"></i>
              <p class="mb-2">Drag and drop your statement file here</p>
              <p class="text-sm text-500 mb-3">or</p>
              <Button 
                label="Choose File" 
                icon="pi pi-folder-open"
                @click="$refs.fileInput.click()"
                class="p-button-outlined"
              />
            </div>
          </div>
        </div>
        
        <div v-if="selectedFile" class="selected-file mt-3">
          <Card>
            <template #content>
              <div class="flex align-items-center justify-content-between">
                <div class="flex align-items-center">
                  <i class="pi pi-file text-2xl text-primary mr-3"></i>
                  <div>
                    <div class="font-medium">{{ selectedFile.name }}</div>
                    <div class="text-sm text-500">{{ formatFileSize(selectedFile.size) }}</div>
                  </div>
                </div>
                <Button 
                  icon="pi pi-times" 
                  class="p-button-text p-button-rounded"
                  @click="removeFile"
                />
              </div>
            </template>
          </Card>
        </div>
        
        <div class="flex justify-content-end mt-4">
          <Button 
            label="Import Statement" 
            icon="pi pi-upload"
            @click="importStatement"
            :disabled="!selectedFile || !selectedAccount"
            :loading="importing"
          />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const selectedAccount = ref(null)
const selectedFormat = ref('csv')
const selectedFile = ref<File | null>(null)
const importing = ref(false)

const bankAccounts = ref([
  { id: 1, name: 'Main Business Account - HBL' },
  { id: 2, name: 'Savings Account - Meezan Bank' },
  { id: 3, name: 'USD Account - HBL' }
])

const fileFormats = ref([
  { label: 'CSV', value: 'csv' },
  { label: 'Excel (XLSX)', value: 'xlsx' },
  { label: 'OFX', value: 'ofx' },
  { label: 'QFX', value: 'qfx' }
])

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    selectedFile.value = event.dataTransfer.files[0]
  }
}

const removeFile = () => {
  selectedFile.value = null
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const importStatement = async () => {
  importing.value = true
  try {
    // Mock import process
    await new Promise(resolve => setTimeout(resolve, 2000))
    console.log('Importing statement:', {
      account: selectedAccount.value,
      format: selectedFormat.value,
      file: selectedFile.value?.name
    })
    // Reset form
    selectedFile.value = null
    selectedAccount.value = null
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.upload-area {
  border: 2px dashed var(--surface-border);
  border-radius: 6px;
  background: var(--surface-50);
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: var(--primary-color);
  background: var(--primary-50);
}

.selected-file {
  border: 1px solid var(--surface-border);
  border-radius: 6px;
  padding: 1rem;
}
</style>