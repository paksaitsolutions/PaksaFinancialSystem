<script setup lang="ts">
import { ref, computed, reactive, watch, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useVuelidate } from '@vuelidate/core';
import { required, requiredIf, numeric, minValue, minLength, helpers } from '@vuelidate/validators';
import dayjs from 'dayjs';
import timezone from 'dayjs/plugin/timezone';
import utc from 'dayjs/plugin/utc';
import { useToast } from 'primevue/usetoast';
import type { JournalEntryItem as BaseJournalEntryItem } from '../../types/journalEntry';

declare module '@vuelidate/core' {
  interface ValidationArgs {
    $lazy?: boolean;
    $autoDirty?: boolean;
    $stopPropagation?: boolean;
    $each?: any;
    $invalid?: boolean;
    $errors?: any[];
    $error?: boolean;
  }
}

// Extend dayjs with plugins
dayjs.extend(utc);
dayjs.extend(timezone);

// Component props
const props = defineProps<{
  journal?: RecurringJournalTemplate;
  journalId?: string; // Add missing prop
  isEdit?: boolean;
  loading?: boolean;
  saving?: boolean;
  readonly?: boolean;
  modelValue?: boolean; // Add missing prop for v-model support
}>();

// Component emits
const emit = defineEmits<{
  (e: 'save', journal: RecurringJournalTemplate): void;
  (e: 'update:modelValue', value: boolean): void;
  (e: 'cancel'): void;
  (e: 'saved'): void; // Add missing event
  (e: 'update:journal', value: RecurringJournalTemplate): void; // Add missing event
}>();

// Types
type RecurrenceFrequency = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
type RecurrenceEndType = 'never' | 'on_date' | 'after_occurrences';
type RecurringJournalStatus = 'draft' | 'active' | 'paused' | 'completed' | 'cancelled';

// Define the base journal entry item interface
export interface BaseJournalEntryItem {
  id: string;
  account_id: string;
  account_name: string;
  description: string;
  amount: number;
  type: 'debit' | 'credit';
  cost_center_id?: string | null;
  department_id?: string | null;
  project_id?: string | null;
  tax_rate_id?: string | null;
  tax_amount?: number | null;
  line_item_order: number;
  currency?: string;
  exchange_rate?: number;
  metadata?: Record<string, any>;
}

// Extend the base JournalEntryItem with form-specific properties
interface JournalEntryItem extends Omit<BaseJournalEntryItem, 'type' | 'amount'> {
  debit: number | null;
  credit: number | null;
  account_id: string; // Make account_id required
}

interface RecurringJournalTemplate {
  id?: string;
  name: string;
  description: string;
  frequency: RecurrenceFrequency;
  interval: number;
  start_date: string;
  end_type: RecurrenceEndType;
  end_date: string | null;
  end_after_occurrences: number | null;
  status: RecurringJournalStatus;
  last_run_date: string | null;
  next_run_date: string | null;
  total_occurrences: number | null;
  processed_occurrences: number;
  template: {
    description: string;
    reference: string;
    journal_date: string;
    entries: JournalEntryItem[];
  };
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  updated_by?: string;
  timezone?: string;
}

interface RecurringJournalForm {
  name: string;
  description: string;
  frequency: RecurrenceFrequency;
  interval: number;
  start_date: string;
  end_type: RecurrenceEndType;
  end_date: string | null;
  end_after_occurrences: number | null;
  status: RecurringJournalStatus;
  template: {
    description: string;
    reference: string;
    journal_date: string;
    entries: JournalEntryItem[];
  };
  timezone?: string;
}

// Composition API
const { t } = useI18n();
const toast = useToast();

// API functions (mocked - should be imported from service)
const createRecurringJournal = async (data: RecurringJournalTemplate) => {
  // Implementation should be in a service
  console.log('Creating recurring journal:', data);
  return Promise.resolve({ data: { ...data, id: 'new-id' } });
};

const updateRecurringJournal = async (id: string, data: RecurringJournalTemplate) => {
  // Implementation should be in a service
  console.log('Updating recurring journal:', id, data);
  return Promise.resolve({ data: { ...data, id } });
};

// Form state with proper typing
const form = reactive<RecurringJournalForm>({
  name: '',
  description: '',
  frequency: 'monthly',
  interval: 1,
  start_date: dayjs().format('YYYY-MM-DD'),
  end_type: 'never',
  end_date: null,
  end_after_occurrences: null,
  status: 'draft',
  template: {
    description: '',
    reference: '',
    journal_date: dayjs().format('YYYY-MM-DD'),
    entries: [
      {
        id: `entry-${Date.now()}-1`,
        account_id: '',
        account_name: '',
        description: '',
        debit: null,
        credit: null,
        amount: 0,
        type: 'debit',
        line_item_order: 1,
        cost_center_id: null,
        department_id: null,
        project_id: null,
        tax_rate_id: null,
        tax_amount: null,
        currency: 'USD',
        exchange_rate: 1,
        metadata: {}
      }
    ]
  },
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
});

// Form state
const formValid = ref(false);
const step = ref(1);
const editable = computed(() => !props.readonly);
const isFormDirty = ref(false);
const generating = ref(false);
const showReportDialog = ref(false);

// Computed properties
const totalDebit = computed((): number => {
  return form.template.entries.reduce((sum: number, entry: JournalEntryItem) => {
    return sum + (entry.debit || 0);
  }, 0);
});

const totalCredit = computed((): number => {
  return form.template.entries.reduce((sum: number, entry: JournalEntryItem) => {
    return sum + (entry.credit || 0);
  }, 0);
});

const isBalanced = computed((): boolean => {
  return Math.abs(totalDebit.value - totalCredit.value) < 0.01; // Allow for floating point precision
});

// Next occurrence calculations
const nextOccurrences = computed(() => {
  if (form.start_date && form.frequency) {
    return calculateNextOccurrences();
  }
  return [];
});

// Vuelidate setup with proper typing
const rules = {
  $autoDirty: true,
  name: { required },
  description: { required },
  frequency: { required },
  interval: {
    required,
    numeric,
    minValue: minValue(1)
  },
  start_date: { required },
  end_type: { required },
  end_date: {
    required: requiredIf((form: RecurringJournalForm) => form.end_type === 'on_date'),
    validDate: (value: string | null) => {
      if (!value) return true;
      return !isPastDate(value);
    }
  },
  end_after_occurrences: {
    required: requiredIf((form: RecurringJournalForm) => form.end_type === 'after_occurrences'),
    numeric,
    minValue: minValue(1)
  },
  status: { required },
  template: {
    description: { required },
    reference: { required },
    journal_date: { required },
    entries: {
      required,
      minLength: minLength(1),
      $each: helpers.forEach({
        account_id: { required },
        description: { required },
        debit: {
          required: requiredIf((entry: JournalEntryItem) => !entry.credit || entry.credit <= 0),
          validAmount: (value: number | null, siblings: { credit: number | null }) => {
            if (value === null && siblings.credit === null) return false;
            if (value !== null && siblings.credit !== null) return false;
            if (value !== null && value < 0) return false;
            return true;
          }
        },
        credit: {
          required: requiredIf((entry: JournalEntryItem) => !entry.debit || entry.debit <= 0),
          validAmount: (value: number | null, siblings: { debit: number | null }) => {
            if (value === null && siblings.debit === null) return false;
            if (value !== null && siblings.debit !== null) return false;
            if (value !== null && value < 0) return false;
            return true;
          }
        }
      })
    }
  }
};

const v$ = useVuelidate(rules, form, { $autoDirty: true });

// Custom validation rules
const validEntry = (entry: JournalEntryItem) => {
  return (entry.debit !== null && entry.debit > 0) || (entry.credit !== null && entry.credit > 0);
};

const validAccount = (entry: JournalEntryItem) => {
  return !!entry.account_id;
};

const hasValidEntries = (entries: JournalEntryItem[]) => {
  return entries.some(entry => validEntry(entry));
};

// Error message formatter
const getErrorMessages = (errors: any[]): string => {
  return errors.map(err => err.$message).join(', ');
};

// Form submission handler
const submitForm = async () => {
  const isValid = await v$.value.$validate();
  if (!isValid) {
    const errorMessages = [];
    
    // Collect all validation errors
    if (v$.value.$errors.length) {
      v$.value.$errors.forEach(error => {
        errorMessages.push(`${error.$property}: ${error.$message}`);
      });
    }
    
    toast.error(`Please fix the following errors: ${errorMessages.join(', ')}`);
    return;
  }

  try {
    // Create a clean payload with only the necessary fields
    const payload: RecurringJournalTemplate = {
      ...form,
      id: props.journalId || undefined,
      template: {
        ...form.template,
        entries: form.template.entries.map((entry, index) => ({
          ...entry,
          amount: entry.debit || entry.credit || 0,
          type: entry.debit ? 'debit' : 'credit',
          line_item_order: index + 1,
          // Ensure all required fields are included
          account_name: entry.account_name || '',
          description: entry.description || '',
          cost_center_id: entry.cost_center_id || null,
          department_id: entry.department_id || null,
          project_id: entry.project_id || null,
          tax_rate_id: entry.tax_rate_id || null,
          tax_amount: entry.tax_amount || null,
          currency: entry.currency || 'USD',
          exchange_rate: entry.exchange_rate || 1,
          metadata: entry.metadata || {}
        }))
      }
    };

    if (props.journalId) {
      const response = await updateRecurringJournal(props.journalId, payload);
      toast.success('Recurring journal updated successfully');
      emit('update:journal', response.data);
    } else {
      const response = await createRecurringJournal(payload);
      toast.success('Recurring journal created successfully');
      emit('saved', response.data);
    }
    
    emit('update:modelValue', false);
  } catch (error) {
    console.error('Error saving recurring journal:', error);
    const errorMessage = error instanceof Error ? error.message : 'Failed to save recurring journal';
    toast.error(errorMessage);
  }
};

// Add a new journal entry
const addJournalEntry = () => {
  const newEntry: JournalEntryItem = {
    id: `entry-${Date.now()}-${form.template.entries.length}`,
    account_id: '',
    account_name: '',
    description: '',
    debit: null,
    credit: null,
    amount: 0,
    type: 'debit',
    line_item_order: form.template.entries.length + 1,
    cost_center_id: null,
    department_id: null,
    project_id: null,
    tax_rate_id: null,
    tax_amount: null,
    currency: 'USD',
    exchange_rate: 1,
    metadata: {}
  };
  form.template.entries.push(newEntry);
  isFormDirty.value = true;
};

// Remove a journal entry
const removeJournalEntry = (index: number) => {
  if (form.template.entries.length > 1) {
    form.template.entries.splice(index, 1);
    isFormDirty.value = true;
  } else {
    toast.warning('At least one journal entry is required');
  }
};

// Handle amount changes to ensure only one of debit/credit is set
const handleAmountChange = (entry: JournalEntryItem, field: 'debit' | 'credit') => {
  const value = parseFloat(entry[field] as any) || 0;
  
  if (field === 'debit' && value > 0) {
    entry.credit = null;
    entry.amount = value;
    entry.type = 'debit';
  } else if (field === 'credit' && value > 0) {
    entry.debit = null;
    entry.amount = value;
    entry.type = 'credit';
  } else {
    // If value is 0 or empty, clear both
    entry.debit = null;
    entry.credit = null;
    entry.amount = 0;
    entry.type = 'debit';
  }
  
  isFormDirty.value = true;
};

// Calculate next occurrences based on recurrence rules
const calculateNextOccurrences = () => {
  // Implementation should calculate next X occurrences based on frequency, interval, etc.
  // This is a simplified version
  const occurrences = [];
  let currentDate = dayjs(form.start_date);
  
  for (let i = 0; i < 5; i++) { // Show next 5 occurrences
    occurrences.push(currentDate.format('YYYY-MM-DD'));
    
    // Increment based on frequency
    switch (form.frequency) {
      case 'daily':
        currentDate = currentDate.add(form.interval, 'day');
        break;
      case 'weekly':
        currentDate = currentDate.add(form.interval, 'week');
        break;
      case 'monthly':
        currentDate = currentDate.add(form.interval, 'month');
        break;
      case 'quarterly':
        currentDate = currentDate.add(form.interval * 3, 'month');
        break;
      case 'yearly':
        currentDate = currentDate.add(form.interval, 'year');
        break;
    }
  }
  
  return occurrences;
};

// Check if a date is in the past
const isPastDate = (dateString: string): boolean => {
  return dayjs(dateString).isBefore(dayjs().startOf('day'));
};

// Initialize form when component is mounted or when journal prop changes
watch(() => props.journal, (newJournal: RecurringJournalTemplate | undefined) => {
  if (newJournal) {
    Object.assign(form, {
      ...newJournal,
      // Ensure all required fields are set
      template: {
        ...newJournal.template,
        entries: newJournal.template.entries.map(entry => ({
          ...entry,
          debit: entry.debit || null,
          credit: entry.credit || null
        }))
      }
    });
    
    // Recalculate next occurrences when journal is loaded
    calculateNextOccurrences();
  }
}, { immediate: true });

// Watch for form changes to update dirty state
watch(() => JSON.parse(JSON.stringify(form)), () => {
  isFormDirty.value = true;
}, { deep: true });

// Watch for changes that affect next occurrences
watch([
  () => form.start_date,
  () => form.frequency,
  () => form.interval,
  () => form.end_type,
  () => form.end_date,
  () => form.end_after_occurrences
], calculateNextOccurrences);

// Initialize next occurrences when component is mounted
onMounted(() => {
  calculateNextOccurrences();
});
</script>

<style scoped>
.v-stepper {
  background: transparent;
  box-shadow: none;
}

.v-stepper__step {
  padding: 12px 24px 12px 12px;
}

.v-stepper__step--complete {
  background-color: rgba(var(--v-primary-base), 0.1);
}

.v-stepper__step--editable {
  cursor: pointer;
}

.v-stepper__step--error {
  border-left: 4px solid var(--v-error-base);
}

.v-stepper__content {
  margin-left: 24px;
  padding-left: 20px;
  border-left: 1px dashed rgba(0, 0, 0, 0.12);
}

.v-stepper:not(.v-stepper--vertical) .v-stepper__label {
  display: flex;
  align-items: center;
}

.v-stepper__step__step {
  margin-right: 12px;
}

.v-stepper__step small {
  display: block;
  font-size: 0.75rem;
  color: rgba(0, 0, 0, 0.6);
  margin-top: 4px;
  white-space: normal;
  line-height: 1.2;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .v-stepper__step {
    padding: 8px 16px 8px 8px;
  }
  
  .v-stepper__content {
    margin-left: 16px;
    padding-left: 16px;
  }
}
</style>