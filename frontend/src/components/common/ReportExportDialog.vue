<template>
  <Dialog
    v-model:visible="visible"
    :style="{ width: '600px' }"
    header="Export Report"
    :modal="true"
    class="p-fluid"
  >
    <div class="field">
      <label for="format">Format</label>
      <Dropdown
        id="format"
        v-model="selectedFormat"
        :options="formats"
        optionLabel="name"
        placeholder="Select a format"
      />
    </div>

    <div class="field">
      <label for="scope">Export Scope</label>
      <SelectButton
        id="scope"
        v-model="exportScope"
        :options="exportScopes"
        optionLabel="label"
        aria-labelledby="basic"
      />
    </div>

    <div v-if="exportScope === 'range'" class="field">
      <label for="pageRange">Page Range</label>
      <div class="p-inputgroup">
        <span class="p-inputgroup-addon">Pages</span>
        <InputText
          id="pageRange"
          v-model="pageRange"
          placeholder="e.g. 1-5,8,11-13"
        />
      </div>
    </div>

    <template #footer>
      <Button
        label="Cancel"
        icon="pi pi-times"
        class="p-button-text"
        @click="close"
      />
      <Button
        label="Export"
        icon="pi pi-download"
        @click="exportReport"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref } from 'vue';
import Dialog from 'evue/dialog';
import Dropdown from 'pvue/dropdown';
import SelectButton from 'pvue/selectbutton';
import InputText from 'pvue/inputtext';
import Button from 'pvue/button';

const emit = defineEmits(['export']);

const visible = ref(false);
const selectedFormat = ref({ name: 'PDF', value: 'pdf' });
const exportScope = ref('current');
const pageRange = ref('');

const formats = [
  { name: 'PDF', value: 'pdf' },
  { name: 'Excel', value: 'xlsx' },
  { name: 'CSV', value: 'csv' },
  { name: 'HTML', value: 'html' },
];

const exportScopes = [
  { label: 'Current View', value: 'current' },
  { label: 'All Data', value: 'all' },
  { label: 'Page Range', value: 'range' },
];

const open = () => {
  visible.value = true;
};

const close = () => {
  visible.value = false;
};

const exportReport = () => {
  const options = {
    format: selectedFormat.value.value,
    scope: exportScope.value,
    pageRange: pageRange.value,
  };
  
  emit('export', options);
  close();
};

defineExpose({
  open,
  close,
});
</script>
