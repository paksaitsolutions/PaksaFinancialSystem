import type { Ref } from 'vue';
import type { RecurringJournal, RecurringJournalCreate, RecurringJournalUpdate } from '@/types/gl/recurringJournal';
import type { JournalEntryItem } from '@/types/gl/journalEntry';

/**
 * Form data structure for the RecurringJournalForm component
 */
export interface RecurringJournalFormData {
  id?: string;
  name: string;
  description: string;
  frequency: RecurringJournal['frequency'];
  interval: number;
  start_date: string;
  end_type: RecurringJournal['end_type'];
  end_date: string | null;
  end_after_occurrences: number | null;
  status: RecurringJournal['status'];
  company_id: string;
  template: {
    journal_date: string;
    reference: string;
    memo: string;
    currency: string;
    exchange_rate: number;
    items: JournalEntryItem[];
  };
}

/**
 * Props for the RecurringJournalForm component
 */
export interface RecurringJournalFormProps {
  dialog: boolean;
  journalId?: string;
  isEdit: boolean;
}

/**
 * Emits for the RecurringJournalForm component
 */
export interface RecurringJournalFormEmits {
  (e: 'update:dialog', value: boolean): void;
  (e: 'saved'): void;
  (e: 'cancelled'): void;
}

/**
 * Vuelidate validation schema for the form
 */
export interface RecurringJournalFormValidation {
  form: {
    name: { required: (value: string) => boolean; };
    description: { required: (value: string) => boolean; };
    frequency: { required: (value: string) => boolean; };
    interval: { 
      required: (value: number) => boolean;
      minValue: (value: number) => boolean;
    };
    start_date: { 
      required: (value: string) => boolean;
      validDate: (value: string) => boolean;
    };
    end_type: { required: (value: string) => boolean; };
    end_date: { 
      requiredIf: (value: string | null) => boolean;
      validDate: (value: string | null) => boolean;
      afterStartDate: (value: string | null) => boolean;
    };
    end_after_occurrences: { 
      requiredIf: (value: number | null) => boolean;
      minValue: (value: number) => boolean;
    };
    status: { required: (value: string) => boolean; };
    template: {
      journal_date: { 
        required: (value: string) => boolean;
        validDate: (value: string) => boolean;
      };
      reference: { required: (value: string) => boolean; };
      memo: { required: (value: string) => boolean; };
      items: { 
        required: (value: JournalEntryItem[]) => boolean;
        validItems: (value: JournalEntryItem[]) => boolean;
      };
    };
    $touch: () => void;
    $reset: () => void;
    $validate: () => Promise<boolean>;
    $errors: Array<{ $message: string }>;
    $invalid: boolean;
  };
}

/**
 * Refs and reactive state for the component
 */
export interface RecurringJournalFormState {
  loading: Ref<boolean>;
  saving: Ref<boolean>;
  step: Ref<number>;
  totalSteps: number;
  startDateMenu: Ref<boolean>;
  endDateMenu: Ref<boolean>;
  nextOccurrences: Ref<string[]>;
  journalFormValid: Ref<boolean>;
  formValid: Ref<boolean>;
  formData: RecurringJournalFormData;
  v: Ref<RecurringJournalFormValidation>;
}

/**
 * Frequency options for the form
 */
export interface FrequencyOption {
  value: RecurringJournal['frequency'];
  text: string;
  showInterval?: boolean;
}

/**
 * Status options for the form
 */
export interface StatusOption {
  value: RecurringJournal['status'];
  text: string;
  color: string;
}

/**
 * End type options for the form
 */
export interface EndTypeOption {
  value: RecurringJournal['end_type'];
  text: string;
}
