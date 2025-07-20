<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import ProgressBar from 'primevue/progressbar';
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import FileUpload from 'primevue/fileupload';
import Dropdown from 'primevue/dropdown';
import Checkbox from 'primevue/checkbox';
import useGlImportExport from '../composables/useGlImportExport';

const props = defineProps<{
  visible: boolean;
  filters?: Record<string, any>;
}>();

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void;
  (e: 'import-complete'): void;
}>();

const { t } = useI18n();
const toast = useToast();

const {
  isExporting,
  isImporting,
  importProgress,
  importErrors,
  exportAccounts,
  importAccounts,
  downloadTemplate
} = useGlImportExport();

const activeTab = ref(0);
const selectedFormat = ref<'csv' | 'xlsx' | 'pdf'>('xlsx');
const updateExisting = ref(false);
const fileInput = ref<File | null>(null);
const showImportSuccess = ref(false);
const importResult = ref<{
  imported: number;
  updated: number;
  errors: string[];
} | null>(null);

const exportFormats = [
  { label: 'Excel (.xlsx)', value: 'xlsx' },
  { label: 'CSV (.csv)', value: 'csv' },
  { label: 'PDF (.pdf)', value: 'pdf' },
];

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files.length > 0) {
    fileInput.value = input.files[0];
  } else {
    fileInput.value = null;
  }
};

const handleImport = async () => {
  if (!fileInput.value) {
    toast.add({
      severity: 'warn',
      summary: 'No File Selected',
      detail: 'Please select a file to import.',
      life: 5000
    });
    return;
  }

  try {
    const result = await importAccounts(fileInput.value, updateExisting.value);
    importResult.value = result;
    showImportSuccess.value = true;
    emit('import-complete');
  } catch (error) {
    console.error('Import failed:', error);
  }
};

const handleExport = async () => {
  try {
    await exportAccounts(selectedFormat.value, props.filters);
  } catch (error) {
    console.error('Export failed:', error);
  }
};

const handleDownloadTemplate = async () => {
  await downloadTemplate('xlsx');
};

const resetForm = () => {
  fileInput.value = null;
  updateExisting.value = false;
  importProgress.value = 0;
  importResult.value = null;
  showImportSuccess.value = false;
};

watch(
  () => props.visible,
  (newVal) => {
    if (!newVal) {
      // Reset form when dialog is closed
      resetForm();
    }
  }
);
</script>

<template>
  <Dialog
    v-model:visible="visible"
    :modal="true"
    :style="{ width: '600px' }"
    header="Import/Export GL Accounts"
    @update:visible="(val) => $emit('update:visible', val)"
  >
    <TabView v-model:activeIndex="activeTab" class="mb-4">
      <!-- Import Tab -->
      <TabPanel header="Import">
        <div v-if="!showImportSuccess" class="flex flex-column gap-4">
          <div class="field">
            <label for="importFile" class="block mb-2">
              Select file to import (.xlsx, .csv)
            </label>
            <FileUpload
              mode="basic"
              :auto="true"
              :multiple="false"
              :showUploadButton="false"
              :showCancelButton="false"
              accept=".xlsx,.csv"
              @select="handleFileSelect"
            >
              <template #content>
                <div v-if="fileInput" class="p-3 border-round border-1 border-300">
                  <i class="pi pi-file-excel mr-2" />
                  {{ fileInput.name }}
                  <small class="block text-500">
                    {{ (fileInput.size / 1024).toFixed(2) }} KB
                  </small>
                </div>
                <div v-else class="p-3 text-center border-round border-1 border-300 border-dashed">
                  <i class="pi pi-cloud-upload text-4xl text-400 mb-2 block" />
                  <span class="text-600">Click or drag file to upload</span>
                </div>
              </template>
            </FileUpload>
          </div>

          <div class="field-checkbox">
            <Checkbox
              id="updateExisting"
              v-model="updateExisting"
              :binary="true"
            />
            <label for="updateExisting">
              Update existing accounts with matching account codes
            </label>
          </div>

          <div class="flex justify-content-between align-items-center mt-4">
            <Button
              label="Download Template"
              icon="pi pi-download"
              class="p-button-outlined p-button-sm"
              @click="handleDownloadTemplate"
            />
            <div>
              <Button
                label="Cancel"
                class="p-button-text p-button-sm mr-2"
                @click="$emit('update:visible', false)"
              />
              <Button
                label="Import"
                icon="pi pi-upload"
                :loading="isImporting"
                :disabled="!fileInput || isImporting"
                @click="handleImport"
              />
            </div>
          </div>

          <ProgressBar
            v-if="isImporting"
            :value="importProgress"
            showValue
            class="mt-4"
          />
        </div>

        <!-- Import Success -->
        <div v-else class="text-center p-4">
          <i class="pi pi-check-circle text-6xl text-green-500 mb-4" />
          <h3 class="text-xl font-semibold mb-2">Import Completed Successfully</h3>
          <p class="text-600 mb-4">
            Imported {{ importResult?.imported || 0 }} accounts, updated {{ importResult?.updated || 0 }} accounts.
          </p>
          
          <div v-if="importResult?.errors?.length" class="text-left mb-4">
            <h4 class="font-semibold mb-2 text-red-500">
              {{ importResult.errors.length }} errors occurred:
            </h4>
            <div class="border-round border-1 border-300 p-3" style="max-height: 200px; overflow-y: auto">
              <div v-for="(error, index) in importResult.errors" :key="index" class="text-sm mb-1">
                {{ error }}
              </div>
            </div>
          </div>

          <div class="flex justify-content-center gap-2 mt-4">
            <Button
              label="Close"
              class="p-button-text"
              @click="$emit('update:visible', false)"
            />
            <Button
              label="Import Another"
              icon="pi pi-upload"
              @click="resetForm"
            />
          </div>
        </div>
      </TabPanel>

      <!-- Export Tab -->
      <TabPanel header="Export">
        <div class="flex flex-column gap-4">
          <div class="field">
            <label for="exportFormat" class="block mb-2">
              Select export format
            </label>
            <Dropdown
              id="exportFormat"
              v-model="selectedFormat"
              :options="exportFormats"
              option-label="label"
              option-value="value"
              class="w-full"
            />
          </div>

          <div class="flex justify-content-end gap-2 mt-4">
            <Button
              label="Cancel"
              class="p-button-text"
              @click="$emit('update:visible', false)"
            />
            <Button
              label="Export"
              icon="pi pi-download"
              :loading="isExporting"
              @click="handleExport"
            />
          </div>
        </div>
      </TabPanel>
    </TabView>
  </Dialog>
</template>
