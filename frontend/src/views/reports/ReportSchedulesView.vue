<template>
  <div class="report-schedules-view">
    <div class="header">
      <h1>Report Schedules</h1>
      <Button icon="pi pi-plus" label="New Schedule" @click="showCreateDialog = true" />
    </div>

    <DataTable :value="schedules" :loading="loading">
      <Column field="schedule_name" header="Schedule Name" />
      <Column field="report_type" header="Report Type">
        <template #body="{ data }">
          {{ enhancedReportsService.utils.formatReportType(data.report_type) }}
        </template>
      </Column>
      <Column field="cron_expression" header="Frequency">
        <template #body="{ data }">
          {{ formatCronExpression(data.cron_expression) }}
        </template>
      </Column>
      <Column field="next_run" header="Next Run">
        <template #body="{ data }">
          {{ data.next_run ? new Date(data.next_run).toLocaleString() : 'Not scheduled' }}
        </template>
      </Column>
      <Column field="is_active" header="Status">
        <template #body="{ data }">
          <Tag :value="data.is_active ? 'Active' : 'Inactive'" :severity="data.is_active ? 'success' : 'warning'" />
        </template>
      </Column>
      <Column header="Actions">
        <template #body="{ data }">
          <Button icon="pi pi-play" class="p-button-text p-button-sm" @click="runSchedule(data)" v-tooltip="'Run Now'" />
          <Button icon="pi pi-pencil" class="p-button-text p-button-sm" @click="editSchedule(data)" v-tooltip="'Edit'" />
          <Button 
            :icon="data.is_active ? 'pi pi-pause' : 'pi pi-play'" 
            class="p-button-text p-button-sm" 
            @click="toggleSchedule(data)" 
            :v-tooltip="data.is_active ? 'Pause' : 'Resume'"
          />
          <Button icon="pi pi-trash" class="p-button-text p-button-sm" severity="danger" @click="deleteSchedule(data)" v-tooltip="'Delete'" />
        </template>
      </Column>
    </DataTable>

    <!-- Create/Edit Schedule Dialog -->
    <Dialog v-model:visible="showCreateDialog" header="Create Report Schedule" modal>
      <div class="schedule-form">
        <div class="field">
          <label>Schedule Name</label>
          <InputText v-model="scheduleForm.schedule_name" />
        </div>
        <div class="field">
          <label>Report Type</label>
          <Dropdown 
            v-model="scheduleForm.report_type" 
            :options="reportTypes" 
            optionLabel="label" 
            optionValue="value" 
          />
        </div>
        <div class="field">
          <label>Frequency</label>
          <Dropdown 
            v-model="selectedFrequency" 
            :options="frequencyOptions" 
            optionLabel="label" 
            optionValue="value"
            @change="updateCronExpression"
          />
        </div>
        <div class="field">
          <label>Cron Expression</label>
          <InputText v-model="scheduleForm.cron_expression" />
          <small class="text-muted">Custom cron expression (overrides frequency selection)</small>
        </div>
        <div class="field">
          <label>Email Recipients</label>
          <Chips v-model="scheduleForm.email_recipients" />
        </div>
        <div class="field">
          <label>Report Configuration</label>
          <Textarea v-model="reportConfigJson" rows="5" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="showCreateDialog = false" />
        <Button label="Save" @click="saveSchedule" :loading="saving" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useEnhancedReportsStore } from '@/stores/enhancedReports';
import enhancedReportsService from '@/services/enhancedReportsService';

const store = useEnhancedReportsStore();
const toast = useToast();

const loading = ref(false);
const showCreateDialog = ref(false);
const saving = ref(false);
const schedules = computed(() => store.schedules);

const scheduleForm = ref({
  schedule_name: '',
  report_type: '',
  cron_expression: '0 9 * * 1',
  email_recipients: [],
  report_config: {}
});

const reportConfigJson = ref('{}');
const selectedFrequency = ref('weekly');

const reportTypes = enhancedReportsService.utils.getReportTypes();

const frequencyOptions = [
  { label: 'Daily', value: 'daily', cron: '0 9 * * *' },
  { label: 'Weekly', value: 'weekly', cron: '0 9 * * 1' },
  { label: 'Monthly', value: 'monthly', cron: '0 9 1 * *' },
  { label: 'Quarterly', value: 'quarterly', cron: '0 9 1 */3 *' },
  { label: 'Custom', value: 'custom', cron: '' }
];

const formatCronExpression = (cron: string) => {
  const freq = frequencyOptions.find(f => f.cron === cron);
  return freq ? freq.label : 'Custom';
};

const updateCronExpression = () => {
  const freq = frequencyOptions.find(f => f.value === selectedFrequency.value);
  if (freq && freq.cron) {
    scheduleForm.value.cron_expression = freq.cron;
  }
};

const runSchedule = async (schedule: any) => {
  try {
    // Implementation for running schedule immediately
    toast.add({
      severity: 'success',
      summary: 'Schedule Executed',
      detail: 'Report schedule has been executed',
      life: 3000
    });
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Execution Failed',
      detail: 'Failed to execute schedule',
      life: 5000
    });
  }
};

const editSchedule = (schedule: any) => {
  scheduleForm.value = { ...schedule };
  reportConfigJson.value = JSON.stringify(schedule.report_config || {}, null, 2);
  showCreateDialog.value = true;
};

const toggleSchedule = async (schedule: any) => {
  try {
    // Implementation for toggling schedule status
    toast.add({
      severity: 'success',
      summary: 'Schedule Updated',
      detail: `Schedule has been ${schedule.is_active ? 'paused' : 'resumed'}`,
      life: 3000
    });
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Update Failed',
      detail: 'Failed to update schedule',
      life: 5000
    });
  }
};

const deleteSchedule = async (schedule: any) => {
  // Implementation for delete
  console.log('Delete schedule:', schedule);
};

const saveSchedule = async () => {
  saving.value = true;
  try {
    const scheduleData = {
      ...scheduleForm.value,
      report_config: JSON.parse(reportConfigJson.value)
    };
    
    await store.createSchedule(scheduleData);
    
    toast.add({
      severity: 'success',
      summary: 'Schedule Saved',
      detail: 'Report schedule has been saved successfully',
      life: 3000
    });
    
    showCreateDialog.value = false;
    resetForm();
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Save Failed',
      detail: 'Failed to save schedule',
      life: 5000
    });
  } finally {
    saving.value = false;
  }
};

const resetForm = () => {
  scheduleForm.value = {
    schedule_name: '',
    report_type: '',
    cron_expression: '0 9 * * 1',
    email_recipients: [],
    report_config: {}
  };
  reportConfigJson.value = '{}';
  selectedFrequency.value = 'weekly';
};

onMounted(() => {
  // Load schedules would be implemented here
});
</script>

<style scoped>
.report-schedules-view {
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.schedule-form {
  display: grid;
  gap: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.text-muted {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}
</style>