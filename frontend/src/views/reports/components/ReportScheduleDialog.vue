<template>
  <Dialog 
    v-model:visible="modelValue" 
    :header="`Schedule: ${report?.name || 'Report'}"
    :style="{ width: '600px' }"
    :modal="true"
    class="p-fluid"
    :closable="true"
    @hide="onHide"
  >
    <div v-if="loading" class="flex justify-content-center p-5">
      <ProgressSpinner />
    </div>
    
    <div v-else-if="error" class="p-5 text-center">
      <i class="pi pi-exclamation-triangle text-6xl text-red-500 mb-3" />
      <h3>Error Loading Schedule</h3>
      <p class="text-500 mb-4">{{ error }}</p>
      <Button label="Retry" icon="pi pi-refresh" @click="loadSchedule" />
    </div>
    
    <div v-else>
      <div class="field">
        <label>Schedule Name</label>
        <InputText v-model="schedule.name" class="w-full" />
        <small class="text-500">A descriptive name for this schedule</small>
      </div>
      
      <div class="field">
        <label>Description</label>
        <Textarea v-model="schedule.description" rows="2" class="w-full" />
        <small class="text-500">Optional description for this schedule</small>
      </div>
      
      <div class="field">
        <label>Frequency</label>
        <Dropdown 
          v-model="schedule.frequency" 
          :options="frequencyOptions"
          optionLabel="label"
          optionValue="value"
          class="w-full"
          @change="onFrequencyChange"
        />
      </div>
      
      <!-- Daily Options -->
      <div v-if="schedule.frequency === 'daily'" class="grid">
        <div class="col-12">
          <label>Run Time</label>
          <Calendar 
            v-model="schedule.time" 
            timeOnly 
            hourFormat="12"
            class="w-full"
          />
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox 
              id="weekdaysOnly" 
              v-model="schedule.weekdaysOnly" 
              :binary="true"
            />
            <label for="weekdaysOnly">Weekdays only (Monday - Friday)</label>
          </div>
        </div>
      </div>
      
      <!-- Weekly Options -->
      <div v-else-if="schedule.frequency === 'weekly'" class="grid">
        <div class="col-12 md:col-6">
          <label>Day of Week</label>
          <Dropdown 
            v-model="schedule.dayOfWeek" 
            :options="dayOfWeekOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full"
          />
        </div>
        <div class="col-12 md:col-6">
          <label>Run Time</label>
          <Calendar 
            v-model="schedule.time" 
            timeOnly 
            hourFormat="12"
            class="w-full"
          />
        </div>
      </div>
      
      <!-- Monthly Options -->
      <div v-else-if="schedule.frequency === 'monthly'" class="grid">
        <div class="col-12 md:col-6">
          <label>Day of Month</label>
          <Dropdown 
            v-model="schedule.dayOfMonth" 
            :options="dayOfMonthOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full"
          />
        </div>
        <div class="col-12 md:col-6">
          <label>Run Time</label>
          <Calendar 
            v-model="schedule.time" 
            timeOnly 
            hourFormat="12"
            class="w-full"
          />
        </div>
        <div class="col-12">
          <small class="text-500">Note: If the selected day doesn't exist in a month, the last day will be used.</small>
        </div>
      </div>
      
      <!-- Quarterly Options -->
      <div v-else-if="schedule.frequency === 'quarterly'" class="grid">
        <div class="col-12 md:col-6">
          <label>Month</label>
          <Dropdown 
            v-model="schedule.month" 
            :options="quarterlyMonthOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full"
          />
        </div>
        <div class="col-12 md:col-3">
          <label>Day</label>
          <InputNumber 
            v-model="schedule.day" 
            :min="1" 
            :max="31" 
            class="w-full"
          />
        </div>
        <div class="col-12 md:col-3">
          <label>Time</label>
          <Calendar 
            v-model="schedule.time" 
            timeOnly 
            hourFormat="12"
            class="w-full"
          />
        </div>
      </div>
      
      <!-- Yearly Options -->
      <div v-else-if="schedule.frequency === 'yearly'" class="grid">
        <div class="col-12 md:col-5">
          <label>Month</label>
          <Dropdown 
            v-model="schedule.month" 
            :options="monthOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full"
          />
        </div>
        <div class="col-12 md:col-3">
          <label>Day</label>
          <InputNumber 
            v-model="schedule.day" 
            :min="1" 
            :max="31" 
            class="w-full"
          />
        </div>
        <div class="col-12 md:col-4">
          <label>Time</label>
          <Calendar 
            v-model="schedule.time" 
            timeOnly 
            hourFormat="12"
            class="w-full"
          />
        </div>
      </div>
      
      <!-- Custom CRON Options -->
      <div v-else-if="schedule.frequency === 'custom'" class="grid">
        <div class="col-12">
          <label>CRON Expression</label>
          <div class="p-inputgroup">
            <InputText 
              v-model="schedule.cronExpression" 
              class="w-full"
              placeholder="e.g., 0 0 12 * * ?"
            />
            <Button 
              icon="pi pi-question-circle" 
              class="p-button-text"
              v-tooltip.top="'Enter a valid CRON expression (minute hour day-of-month month day-of-week year)'"
            />
          </div>
          <small class="text-500">
            Format: <code>second minute hour day-of-month month day-of-week year</code> (year is optional)
          </small>
        </div>
        <div class="col-12">
          <div class="p-3 border-1 border-round surface-border">
            <h4 class="mt-0">CRON Expression Examples</h4>
            <ul class="list-none p-0 m-0">
              <li class="mb-2"><code>0 0 12 * * ?</code> - Every day at noon</li>
              <li class="mb-2"><code>0 0 8 ? * MON-FRI</code> - Weekdays at 8 AM</li>
              <li class="mb-2"><code>0 0 9 1 * ?</code> - 9 AM on the 1st of every month</li>
              <li class="mb-2"><code>0 0 0 1 1/3 ?</code> - At midnight, on the 1st of every 3 months</li>
              <li class="mb-2"><code>0 0 10 ? * 6L</code> - 10 AM on the last Friday of every month</li>
            </ul>
          </div>
        </div>
      </div>
      
      <Divider />
      
      <div class="field">
        <label>Start Date/Time</label>
        <div class="grid">
          <div class="col-12 md:col-6">
            <Calendar 
              v-model="schedule.startDate" 
              dateFormat="yy-mm-dd" 
              :showIcon="true"
              :showButtonBar="true"
              class="w-full"
              :minDate="new Date()"
            />
          </div>
          <div class="col-12 md:col-6">
            <Calendar 
              v-model="schedule.startTime" 
              timeOnly 
              hourFormat="12"
              class="w-full"
            />
          </div>
        </div>
        <small class="text-500">When this schedule should start</small>
      </div>
      
      <div class="field">
        <label>End</label>
        <div class="grid">
          <div class="col-12 md:col-8">
            <div class="flex align-items-center">
              <div class="field-radiobutton mr-3">
                <RadioButton 
                  id="endNever" 
                  v-model="schedule.endType" 
                  value="never" 
                  name="endType"
                />
                <label for="endNever">Never</label>
              </div>
              <div class="field-radiobutton mr-3">
                <RadioButton 
                  id="endAfter" 
                  v-model="schedule.endType" 
                  value="after" 
                  name="endType"
                />
                <label for="endAfter">After</label>
              </div>
              <div class="field-radiobutton">
                <RadioButton 
                  id="endOnDate" 
                  v-model="schedule.endType" 
                  value="ondate" 
                  name="endType"
                />
                <label for="endOnDate">On Date</label>
              </div>
            </div>
          </div>
          <div v-if="schedule.endType === 'after'" class="col-12 md:col-4">
            <div class="p-inputgroup">
              <InputNumber 
                v-model="schedule.occurrences" 
                :min="1" 
                class="w-full"
              />
              <span class="p-inputgroup-addon">occurrences</span>
            </div>
          </div>
          <div v-else-if="schedule.endType === 'ondate'" class="col-12 md:col-4">
            <Calendar 
              v-model="schedule.endDate" 
              dateFormat="yy-mm-dd" 
              :showIcon="true"
              :showButtonBar="true"
              class="w-full"
              :minDate="schedule.startDate || new Date()"
            />
          </div>
        </div>
      </div>
      
      <Divider />
      
      <div class="field">
        <label>Export Format</label>
        <MultiSelect 
          v-model="schedule.formats" 
          :options="exportFormatOptions"
          optionLabel="label"
          optionValue="value"
          display="chip"
          class="w-full"
        />
      </div>
      
      <div class="field">
        <label>Email Notification</label>
        <div class="flex align-items-center">
          <InputText 
            v-model="schedule.notificationEmail" 
            class="w-full" 
            placeholder="Enter email address(es)"
          />
          <Button 
            icon="pi pi-users" 
            class="p-button-text"
            v-tooltip.top="'Select from address book'"
          />
        </div>
        <small class="text-500">Leave empty to use your account email. Multiple emails can be separated by commas.</small>
      </div>
      
      <div class="field">
        <label>Email Subject</label>
        <InputText v-model="schedule.emailSubject" class="w-full" />
      </div>
      
      <div class="field">
        <label>Email Message</label>
        <Textarea v-model="schedule.emailMessage" rows="3" class="w-full" />
        <small class="text-500">Use placeholders like {reportName}, {generatedDate}, {userName}</small>
      </div>
      
      <div class="field">
        <div class="field-checkbox">
          <Checkbox 
            id="includeLink" 
          v-model="schedule.includeLink" 
            :binary="true"
          />
          <label for="includeLink">Include link to report in email</label>
        </div>
      </div>
      
      <div class="field">
        <div class="field-checkbox">
          <Checkbox 
            id="attachFiles" 
            v-model="schedule.attachFiles" 
            :binary="true"
          />
          <label for="attachFiles">Attach report files to email</label>
        </div>
      </div>
      
      <Divider />
      
      <div class="field">
        <div class="flex align-items-center">
          <label class="mr-3">Status:</label>
          <InputSwitch v-model="schedule.isActive" />
          <span class="ml-2">{{ schedule.isActive ? 'Active' : 'Inactive' }}</span>
        </div>
        <small class="text-500">Inactive schedules won't run until activated</small>
      </div>
      
      <div class="mt-4 p-3 border-1 border-round surface-100">
        <h4 class="mt-0">Next 5 Runs</h4>
        <DataTable :value="nextRuns" class="p-datatable-sm" :showGridlines="true" :rows="5" :paginator="false">
          <Column field="date" header="Date" />
          <Column field="time" header="Time" />
        </DataTable>
      </div>
    </div>
    
    <template #footer>
      <div class="flex justify-content-between">
        <div>
          <Button 
            v-if="scheduleId"
            label="Delete" 
            icon="pi pi-trash" 
            class="p-button-text p-button-danger"
            @click="confirmDelete"
          />
        </div>
        <div>
          <Button 
            label="Cancel" 
            icon="pi pi-times" 
            class="p-button-text" 
            @click="onCancel"
          />
          <Button 
            :label="scheduleId ? 'Update' : 'Create'" 
            :icon="scheduleId ? 'pi pi-check' : 'pi pi-calendar-plus'" 
            class="p-button-primary"
            @click="onSave"
            :loading="saving"
          />
        </div>
      </div>
    </template>
  </Dialog>
  
  <!-- Delete Confirmation Dialog -->
  <Dialog 
    v-model:visible="showDeleteConfirm" 
    header="Confirm Delete" 
    :modal="true"
    :style="{ width: '450px' }"
  >
    <div class="flex align-items-center">
      <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem; color: var(--red-500)" />
      <span>Are you sure you want to delete this schedule?</span>
    </div>
    <template #footer>
      <Button 
        label="No" 
        icon="pi pi-times" 
        class="p-button-text" 
        @click="showDeleteConfirm = false"
      />
      <Button 
        label="Yes" 
        icon="pi pi-check" 
        class="p-button-danger" 
        @click="onDelete"
        :loading="deleting"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
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
  scheduleId: {
    type: String,
    default: '',
  },
});

const emit = defineEmits([
  'update:modelValue',
  'saved',
  'deleted',
  'cancel',
]);

// State
const loading = ref(false);
sconst saving = ref(false);
const deleting = ref(false);
const error = ref<string | null>(null);
const showDeleteConfirm = ref(false);

// Form data
const schedule = ref({
  id: '',
  name: '',
  description: '',
  reportId: '',
  frequency: 'daily',
  time: new Date(),
  dayOfWeek: '1',
  dayOfMonth: '1',
  month: '1',
  day: 1,
  cronExpression: '',
  startDate: new Date(),
  startTime: new Date(),
  endType: 'never',
  occurrences: 12,
  endDate: null as Date | null,
  weekdaysOnly: false,
  formats: ['pdf'],
  notificationEmail: '',
  emailSubject: '',
  emailMessage: 'Please find attached the scheduled report: {reportName}',
  includeLink: true,
  attachFiles: true,
  isActive: true,
  createdBy: '',
  createdAt: new Date(),
  updatedAt: new Date(),
});

// Options
const frequencyOptions = [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' },
  { label: 'Quarterly', value: 'quarterly' },
  { label: 'Yearly', value: 'yearly' },
  { label: 'Custom (CRON)', value: 'custom' },
];

const dayOfWeekOptions = [
  { label: 'Sunday', value: '0' },
  { label: 'Monday', value: '1' },
  { label: 'Tuesday', value: '2' },
  { label: 'Wednesday', value: '3' },
  { label: 'Thursday', value: '4' },
  { label: 'Friday', value: '5' },
  { label: 'Saturday', value: '6' },
];

const dayOfMonthOptions = Array.from({ length: 31 }, (_, i) => ({
  label: (i + 1).toString(),
  value: (i + 1).toString(),
}));

dayOfMonthOptions.push({ label: 'Last day of month', value: 'L' });

const quarterlyMonthOptions = [
  { label: 'January, April, July, October', value: '1,4,7,10' },
  { label: 'February, May, August, November', value: '2,5,8,11' },
  { label: 'March, June, September, December', value: '3,6,9,12' },
];

const monthOptions = [
  { label: 'January', value: '1' },
  { label: 'February', value: '2' },
  { label: 'March', value: '3' },
  { label: 'April', value: '4' },
  { label: 'May', value: '5' },
  { label: 'June', value: '6' },
  { label: 'July', value: '7' },
  { label: 'August', value: '8' },
  { label: 'September', value: '9' },
  { label: 'October', value: '10' },
  { label: 'November', value: '11' },
  { label: 'December', value: '12' },
];

const exportFormatOptions = [
  { label: 'PDF', value: 'pdf' },
  { label: 'Excel', value: 'xlsx' },
  { label: 'CSV', value: 'csv' },
  { label: 'HTML', value: 'html' },
  { label: 'Image (PNG)', value: 'png' },
];

// Computed
const nextRuns = computed(() => {
  // This would be calculated based on the schedule
  // For now, return mock data
  const now = new Date();
  return Array.from({ length: 5 }, (_, i) => {
    const date = new Date(now);
    date.setDate(date.getDate() + (i + 1));
    
    // Set time from schedule
    const time = new Date(schedule.value.time);
    date.setHours(time.getHours(), time.getMinutes(), 0, 0);
    
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
  });
});

// Watchers
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    loadSchedule();
  }
});

// Methods
const loadSchedule = async () => {
  if (!props.scheduleId) {
    // New schedule - set default values
    resetForm();
    return;
  }
  
  loading.value = true;
  error.value = null;
  
  try {
    // TODO: Fetch schedule by ID from API
    // const response = await reportService.getSchedule(props.scheduleId);
    // schedule.value = response.data;
    
    // Mock data for now
    setTimeout(() => {
      schedule.value = {
        ...schedule.value,
        id: props.scheduleId,
        name: `Schedule for ${props.report?.name || 'Report'}`,
        reportId: props.report?.id || '',
        description: `Automated schedule for ${props.report?.name || 'report'}`,
        emailSubject: `Scheduled Report: ${props.report?.name || ''}`,
        notificationEmail: 'user@example.com',
      };
      loading.value = false;
    }, 500);
  } catch (err) {
    console.error('Error loading schedule:', err);
    error.value = 'Failed to load schedule. Please try again.';
    loading.value = false;
  }
};

const resetForm = () => {
  schedule.value = {
    ...schedule.value,
    id: '',
    name: `Schedule for ${props.report?.name || 'Report'}`,
    description: `Automated schedule for ${props.report?.name || 'report'}`,
    reportId: props.report?.id || '',
    emailSubject: `Scheduled Report: ${props.report?.name || ''}`,
    startDate: new Date(),
    startTime: new Date(),
    endDate: null,
    endType: 'never',
    isActive: true,
  };
};

const onFrequencyChange = () => {
  // Reset dependent fields when frequency changes
  schedule.value.cronExpression = '';
};

const onHide = () => {
  emit('update:modelValue', false);
};

const onCancel = () => {
  emit('cancel');
  emit('update:modelValue', false);
};

const onSave = async () => {
  if (!validateForm()) {
    return;
  }
  
  saving.value = true;
  
  try {
    // TODO: Save schedule via API
    // const data = { ...schedule.value };
    // if (props.scheduleId) {
    //   await reportService.updateSchedule(props.scheduleId, data);
    // } else {
    //   await reportService.createSchedule(data);
    // }
    
    // Mock save
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    emit('saved', { ...schedule.value });
    emit('update:modelValue', false);
  } catch (err) {
    console.error('Error saving schedule:', err);
    // Show error message
  } finally {
    saving.value = false;
  }
};

const validateForm = () => {
  if (!schedule.value.name) {
    // Show error
    return false;
  }
  
  if (schedule.value.frequency === 'custom' && !schedule.value.cronExpression) {
    // Show error
    return false;
  }
  
  return true;
};

const confirmDelete = () => {
  showDeleteConfirm.value = true;
};

const onDelete = async () => {
  if (!props.scheduleId) {
    showDeleteConfirm.value = false;
    return;
  }
  
  deleting.value = true;
  
  try {
    // TODO: Delete schedule via API
    // await reportService.deleteSchedule(props.scheduleId);
    
    // Mock delete
    await new Promise(resolve => setTimeout(resolve, 500));
    
    emit('deleted', props.scheduleId);
    emit('update:modelValue', false);
    showDeleteConfirm.value = false;
  } catch (err) {
    console.error('Error deleting schedule:', err);
    // Show error message
  } finally {
    deleting.value = false;
  }
};

// Initialize
onMounted(() => {
  if (props.modelValue) {
    loadSchedule();
  }
});
</script>

<style scoped>
.field {
  margin-bottom: 1.5rem;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 1rem;
}

:deep(.p-calendar) {
  width: 100%;
}
</style>
