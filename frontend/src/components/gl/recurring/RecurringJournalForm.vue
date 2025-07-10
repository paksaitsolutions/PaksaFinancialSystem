<template>
  <v-form
    ref="form"
    v-model="formValid"
    lazy-validation
    @submit.prevent="handleSubmit"
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon left>mdi-calendar-refresh</v-icon>
        {{ isEdit ? $t('gl.recurring_journals.edit_title') : $t('gl.recurring_journals.create_title') }}
      </v-card-title>

      <v-card-text>
        <v-stepper v-model="step" vertical>
          <v-stepper-step
            :complete="step > 1"
            step="1"
            :editable="editable"
            :rules="[() => !v$.name.$error]"
          >
            {{ $t('gl.recurring_journals.steps.basic_info') }}
            <small v-if="step > 1">{{ formData.name }}</small>
          </v-stepper-step>

          <v-stepper-content step="1">
            <v-row>
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="formData.name"
                  :label="$t('gl.recurring_journals.fields.name')"
                  :error-messages="getErrorMessages(v$.name)"
                  :disabled="!editable"
                  required
                  outlined
                  dense
                  @input="v$.name.$touch()"
                  @blur="v$.name.$touch()"
                ></v-text-field>
              </v-col>

              <v-col cols="12" md="4">
                <v-select
                  v-model="formData.status"
                  :items="statusOptions"
                  :label="$t('gl.recurring_journals.fields.status')"
                  :error-messages="getErrorMessages(v$.status)"
                  :disabled="!editable || isEdit"
                  item-text="text"
                  item-value="value"
                  outlined
                  dense
                  @input="v$.status.$touch()"
                  @blur="v$.status.$touch()"
                ></v-select>
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="formData.description"
                  :label="$t('gl.recurring_journals.fields.description')"
                  :error-messages="getErrorMessages(v$.description)"
                  :disabled="!editable"
                  rows="2"
                  outlined
                  auto-grow
                  @input="v$.description.$touch()"
                  @blur="v$.description.$touch()"
                ></v-textarea>
              </v-col>
            </v-row>

            <v-btn
              color="primary"
              @click="step = 2"
              :disabled="v$.$invalid"
            >
              {{ $t('common.next') }}
              <v-icon right>mdi-arrow-right</v-icon>
            </v-btn>
          </v-stepper-content>

          <v-stepper-step
            :complete="step > 2"
            step="2"
            :editable="editable"
            :rules="[() => !v$.frequency.$error && !v$.start_date.$error]"
          >
            {{ $t('gl.recurring_journals.steps.schedule') }}
            <small v-if="step > 2">
              {{ formatScheduleSummary }}
            </small>
          </v-stepper-step>

          <v-stepper-content step="2">
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="formData.frequency"
                  :items="frequencyOptions"
                  :label="$t('gl.recurring_journals.fields.frequency')"
                  :error-messages="getErrorMessages(v$.frequency)"
                  :disabled="!editable"
                  item-text="text"
                  item-value="value"
                  outlined
                  dense
                  @change="onFrequencyChange"
                ></v-select>
              </v-col>

              <v-col cols="12" md="6" v-if="showInterval">
                <v-text-field
                  v-model.number="formData.interval"
                  :label="$t('gl.recurring_journals.fields.interval')"
                  :error-messages="getErrorMessages(v$.interval)"
                  :disabled="!editable"
                  type="number"
                  min="1"
                  outlined
                  dense
                  @input="v$.interval.$touch()"
                  @blur="v$.interval.$touch()"
                ></v-text-field>
              </v-col>

              <v-col cols="12" md="6">
                <v-menu
                  v-model="startDateMenu"
                  :close-on-content-click="false"
                  :nudge-right="40"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field
                      v-model="formData.start_date"
                      :label="$t('gl.recurring_journals.fields.start_date')"
                      :error-messages="getErrorMessages(v$.start_date)"
                      :disabled="!editable"
                      prepend-inner-icon="mdi-calendar"
                      readonly
                      outlined
                      dense
                      v-bind="attrs"
                      v-on="on"
                      @input="v$.start_date.$touch()"
                      @blur="v$.start_date.$touch()"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="formData.start_date"
                    @input="startDateMenu = false"
                    :min="$dayjs().format('YYYY-MM-DD')"
                  ></v-date-picker>
                </v-menu>
              </v-col>

              <v-col cols="12" md="6">
                <v-select
                  v-model="formData.end_type"
                  :items="endTypeOptions"
                  :label="$t('gl.recurring_journals.fields.end_type')"
                  :error-messages="getErrorMessages(v$.end_type)"
                  :disabled="!editable"
                  item-text="text"
                  item-value="value"
                  outlined
                  dense
                  @change="onEndTypeChange"
                ></v-select>
              </v-col>

              <v-col cols="12" md="6" v-if="formData.end_type === 'on_date'">
                <v-menu
                  v-model="endDateMenu"
                  :close-on-content-click="false"
                  :nudge-right="40"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field
                      v-model="formData.end_date"
                      :label="$t('gl.recurring_journals.fields.end_date')"
                      :error-messages="getErrorMessages(v$.end_date)"
                      :disabled="!editable"
                      prepend-inner-icon="mdi-calendar"
                      readonly
                      outlined
                      dense
                      v-bind="attrs"
                      v-on="on"
                      @input="v$.end_date.$touch()"
                      @blur="v$.end_date.$touch()"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="formData.end_date"
                    @input="endDateMenu = false"
                    :min="formData.start_date || $dayjs().format('YYYY-MM-DD')"
                  ></v-date-picker>
                </v-menu>
              </v-col>

              <v-col cols="12" md="6" v-if="formData.end_type === 'after_occurrences'">
                <v-text-field
                  v-model.number="formData.end_after_occurrences"
                  :label="$t('gl.recurring_journals.fields.end_after_occurrences')"
                  :error-messages="getErrorMessages(v$.end_after_occurrences)"
                  :disabled="!editable"
                  type="number"
                  min="1"
                  outlined
                  dense
                  @input="v$.end_after_occurrences.$touch()"
                  @blur="v$.end_after_occurrences.$touch()"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-alert
              v-if="nextOccurrences.length > 0"
              type="info"
              outlined
              dense
              class="mb-4"
            >
              <div class="d-flex align-center">
                <v-icon left>mdi-information</v-icon>
                <span>{{ $t('gl.recurring_journals.next_occurrences') }}:</span>
              </div>
              <v-chip
                v-for="(date, index) in nextOccurrences"
                :key="index"
                small
                class="ma-1"
                :color="isPastDate(date) ? 'grey lighten-2' : 'primary lighten-4'"
              >
                {{ formatReadableDate(date) }}
              </v-chip>
              <span v-if="nextOccurrences.length >= 5" class="caption ml-2">
                {{ $t('gl.recurring_journals.and_more', { count: nextOccurrences.length - 5 }) }}
              </span>
            </v-alert>

            <div class="d-flex justify-space-between">
              <v-btn text @click="step = 1">
                <v-icon left>mdi-arrow-left</v-icon>
                {{ $t('common.back') }}
              </v-btn>
              <v-btn
                color="primary"
                @click="step = 3"
                :disabled="v$.$invalid"
              >
                {{ $t('common.next') }}
                <v-icon right>mdi-arrow-right</v-icon>
              </v-btn>
            </div>
          </v-stepper-content>

          <v-stepper-step
            :complete="step > 3"
            step="3"
            :editable="editable"
            :rules="[() => !v$.template.journal_date.$error && !v$.template.reference.$error && !v$.template.items.$error]"
          >
            {{ $t('gl.recurring_journals.steps.journal_template') }}
            <small v-if="step > 3">{{ journalTemplateSummary }}</small>
          </v-stepper-step>

          <v-stepper-content step="3">
            <journal-entry-form
              ref="journalForm"
              v-model="formData.template"
              :editable="editable"
              :show-actions="false"
              @valid="onJournalFormValid"
            />

            <div class="d-flex justify-space-between mt-4">
              <v-btn text @click="step = 2">
                <v-icon left>mdi-arrow-left</v-icon>
                {{ $t('common.back') }}
              </v-btn>
              <div>
                <v-btn
                  text
                  @click="saveDraft"
                  :loading="saving"
                  class="mr-2"
                  v-if="!isEdit"
                >
                  {{ $t('common.save_draft') }}
                </v-btn>
                <v-btn
                  color="primary"
                  @click="handleSubmit"
                  :loading="saving"
                  :disabled="!journalFormValid || v$.$invalid"
                >
                  {{ isEdit ? $t('common.save') : $t('common.create') }}
                </v-btn>
              </div>
            </div>
          </v-stepper-content>
        </v-stepper>
      </v-card-text>
    </v-card>
  </v-form>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch, onMounted, defineProps, defineEmits, withDefaults } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import { useToast } from 'vue-toastification';
import useVuelidate from '@vuelidate/core';
import type { ValidationRule } from '@vuelidate/core';
import { 
  required, 
  minLength, 
  maxLength, 
  minValue, 
  maxValue, 
  numeric, 
  helpers 
} from '@vuelidate/validators';
import dayjs from 'dayjs';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import JournalEntryForm from '@/components/gl/JournalEntryForm.vue';

// Configure dayjs plugins
dayjs.extend(customParseFormat);
dayjs.extend(utc);
dayjs.extend(timezone);

// Import types
import type { 
  RecurrenceFrequency, 
  RecurrenceEndType, 
  RecurringJournalStatus as RJStatus,
  RecurringJournal as RecurringJournalType,
  JournalEntryItem
} from '@/types/gl/recurringJournal';

// Re-export types for external use
export type { JournalEntryItem };

type EndType = 'never' | 'on_date' | 'after_occurrences';
type FrequencyType = 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom';

// Define FrequencyOption interface
interface FrequencyOption {
  text: string;
  value: RecurrenceFrequency;
  description: string;
}

// Define StatusOption interface
interface StatusOption {
  text: string;
  value: string;
  color: string;
}

// Define WeeklyDayOption interface
interface WeeklyDayOption {
  text: string;
  value: number;
  abbr: string;
}

// Define MonthlyOption interface
interface MonthlyOption {
  text: string;
  value: 'day' | 'first' | 'last' | 'weekday' | 'weekend_day';
}

// Define WeekdayOption interface
interface WeekdayOption {
  text: string;
  value: number;
  abbr: string;
}

// Define JournalEntryTemplate interface
export interface JournalEntryTemplate {
  id?: string;
  name: string;
  description?: string | null;
  status: 'active' | 'inactive' | 'draft';
  template_data: {
    entry_date: string;
    reference: string;
    currency: string;
    exchange_rate: number;
    memo?: string;
    items: JournalEntryItem[];
  };
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  updated_by?: string;
  company_id?: string;
  is_recurring: boolean;
  recurring_settings?: RecurringSettings;
}

// Define RecurringSettings interface
export interface RecurringSettings {
  frequency: RecurrenceFrequency;
  interval: number;
  start_date: string;
  end_type: EndType;
  end_date?: string | null;
  end_after_occurrences?: number | null;
  week_days?: number[];
  month_day?: number;
  month_week?: number;
  month_weekday?: number;
  last_occurrence?: string | null;
  next_occurrence?: string | null;
  timezone: string;
  created_at?: string;
  updated_at?: string;
}

// Define form data interface
export interface FormData {
  id?: string;
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'draft';
  frequency: RecurrenceFrequency;
  interval: number;
  start_date: string;
  end_type: EndType;
  end_date: string | null;
  end_after_occurrences: number | null;
  week_days: number[];
  month_day: number | null;
  month_week: number | null;
  month_weekday: number | null;
  timezone: string;
  template: JournalEntryTemplate | null;
  created_at?: string;
}

// Component props
const props = withDefaults(defineProps<{
  journalId?: string;
  isEdit?: boolean;
  initialData?: Partial<FormData>;
  loading?: boolean;
  saving?: boolean;
  readonly?: boolean;
  disabled?: boolean;
}>(), {
  isEdit: false,
  loading: false,
  saving: false,
  readonly: false,
  disabled: false
});

// Component emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: Partial<FormData>): void;
  (e: 'submit', value: FormData): void;
  (e: 'cancel'): void;
  (e: 'update:step', step: number): void;
  (e: 'update:editable', editable: boolean): void;
  (e: 'update:form-valid', isValid: boolean): void;
}>();

// Form validation rules using Vuelidate's helpers.withMessage for i18n
const { t } = useI18n();
const store = useStore();
const router = useRouter();
const toast = useToast();
  };

  return {
    name: {
      required: withMessage(t('validation.required', { field: t('gl.recurring_journals.fields.name') }), required),
      minLength: withMessage(
        t('validation.min_length', { field: t('gl.recurring_journals.fields.name'), min: 3 }),
        minLength(3)
      ),
      maxLength: withMessage(
        t('validation.max_length', { field: t('gl.recurring_journals.fields.name'), max: 100 }),
        maxLength(100)
      )
    },
    description: {
      maxLength: withMessage(
        t('validation.max_length', { field: t('gl.recurring_journals.fields.description'), max: 500 }),
        maxLength(500)
      )
    },
    frequency: {
      required: withMessage(t('validation.required', { field: t('gl.recurring_journals.fields.frequency') }), required)
    },
    interval: {
      required: withMessage(t('validation.required', { field: t('gl.recurring_journals.fields.interval') }), required),
      minValue: withMessage(
        t('validation.min_value', { field: t('gl.recurring_journals.fields.interval'), min: 1 }),
        minValue(1)
      ),
      maxValue: withMessage(
        t('validation.max_value', { field: t('gl.recurring_journals.fields.interval'), max: 366 }),
        maxValue(366)
      )
    },
    start_date: {
      required: helpers.withMessage(t('validation.required', { field: t('gl.recurring_journals.fields.start_date') }), required),
      validDate: helpers.withMessage(
        t('validation.invalid_date'),
        (value: string) => !value || dayjs(value).isValid()
      )
    },
    end_date: {
      required: withMessage(
        t('validation.required_if', {
          field: t('gl.recurring_journals.fields.end_date'),
          other: t('gl.recurring_journals.fields.end_type'),
          value: t('gl.recurring_journals.end_types.on_date')
        }),
        (value: string | null, siblings: any) => {
          return siblings.end_type !== 'on_date' || !!value;
        }
      ),
      isFutureDate: withMessage(
        t('validation.future_date', { field: t('gl.recurring_journals.fields.end_date') }),
        (value: string | null, siblings: any) => {
          if (!value || siblings.end_type !== 'on_date') return true;
          return new Date(value) > new Date();
        }
      ),
      afterStartDate: withMessage(
        t('validation.after_date', {
          field: t('gl.recurring_journals.fields.end_date'),
          other: t('gl.recurring_journals.fields.start_date')
        }),
        (value: string | null, siblings: any) => {
          if (!value || !siblings.start_date || siblings.end_type !== 'on_date') return true;
          return new Date(value) > new Date(siblings.start_date);
        }
      )
    },
    end_after_occurrences: {
      required: withMessage(
        t('validation.required_if', {
          field: t('gl.recurring_journals.fields.end_after_occurrences'),
          other: t('gl.recurring_journals.fields.end_type'),
          value: t('gl.recurring_journals.end_types.after_occurrences')
        }),
        (value: number | null, siblings: any) => {
          return siblings.end_type !== 'after_occurrences' || value !== null;
        }
      ),
      minValue: withMessage(
        t('validation.min_value', { field: t('gl.recurring_journals.fields.end_after_occurrences'), min: 1 }),
        (value: number | null, siblings: any) => {
          if (siblings.end_type !== 'after_occurrences' || value === null) return true;
          return value >= 1;
        }
      ),
      maxValue: withMessage(
        t('validation.max_value', { field: t('gl.recurring_journals.fields.end_after_occurrences'), max: 999 }),
        (value: number | null, siblings: any) => {
          if (siblings.end_type !== 'after_occurrences' || value === null) return true;
          return value <= 999;
        }
      )
    },
    template: {
      journal_date: {
        required: helpers.withMessage(t('validation.required', { field: t('gl.journal_entries.fields.journal_date') }), required),
        validDate: helpers.withMessage(t('validation.invalid_date'), (value: string) => !value || dayjs(value).isValid())
      },
      reference: {
        required: helpers.withMessage(t('validation.required', { field: t('gl.journal_entries.fields.reference') }), required),
        maxLength: helpers.withMessage(
          t('validation.max_length', { field: t('gl.journal_entries.fields.reference'), max: 50 }),
          maxLength(50)
        )
      },
      memo: {
        maxLength: helpers.withMessage(
          t('validation.max_length', { field: t('gl.journal_entries.fields.memo'), max: 255 }),
          maxLength(255)
        )
      },
      items: {
        required: helpers.withMessage(t('validation.required', { field: t('gl.journal_entries.fields.items') }), (items: JournalEntryItem[]) => items && items.length > 0),
        minLength: helpers.withMessage(
          t('validation.min_items', { field: t('gl.journal_entries.fields.items'), min: 2 }),
          (items: JournalEntryItem[]) => items.length >= 2
        ),
        validItems: helpers.withMessage(
          t('gl.journal_entries.validation.balanced_entries'),
          (items: JournalEntryItem[]) => {
            if (!items || items.length < 2) return false;
          required: helpers.withMessage(t('validation.required', { field: t('gl.journal_entries.fields.reference') }), required),
          maxLength: helpers.withMessage(
            t('validation.max_length', { field: t('gl.journal_entries.fields.reference'), max: 50 }),
            maxLength(50)
          )
        },
        memo: {
          maxLength: helpers.withMessage(
            t('validation.max_length', { field: t('gl.journal_entries.fields.memo'), max: 255 }),
            maxLength(255)
          )
        },
        items: {
          required: helpers.withMessage(t('validation.required', { field: t('gl.journal_entries.fields.items') }), (items: JournalEntryItem[]) => items && items.length > 0),
          minLength: helpers.withMessage(
            t('validation.min_items', { field: t('gl.journal_entries.fields.items'), min: 2 }),
            (items: JournalEntryItem[]) => items.length >= 2
          ),
          validItems: helpers.withMessage(
            t('gl.journal_entries.validation.balanced_entries'),
            (items: JournalEntryItem[]) => {
              if (!items || items.length < 2) return false;

              const totalDebit = items
                .filter(item => item.type === 'debit')
                .reduce((sum, item) => sum + (Number(item.amount) || 0), 0);

              const totalCredit = items
                .filter(item => item.type === 'credit')
                .reduce((sum, item) => sum + (Number(item.amount) || 0), 0);

              return Math.abs(totalDebit - totalCredit) < 0.01;
            }
          ),
          $each: helpers.forEach({ // Apply rules to each item in the array
            account_id: {
              required: helpers.withMessage(t('validation.required', { field: t('gl.journal_entries.fields.account') }), required)
            },
            amount: {
              required: helpers.withMessage(t('validation.required', { field: t('gl.journal_entries.fields.amount') }), required),
              numeric: helpers.withMessage(t('validation.numeric', { field: t('gl.journal_entries.fields.amount') }), numeric),
              minValue: helpers.withMessage(t('validation.minValue', { field: t('gl.journal_entries.fields.amount'), min: 0.01 }), minValue(0.01))
            },
            description: {
              maxLength: helpers.withMessage(
                t('validation.max_length', { field: t('gl.journal_entries.fields.description'), max: 255 }),
                maxLength(255)
              )
            }
          })
        }
      }
    });

    const rules = computed(() => createRules(t));
    const v$ = useVuelidate(rules, formData);

    // Options for form dropdowns
    // Explicitly type the array elements to match RecurrenceFrequency
    const frequencyOptions = computed<Array<{ text: string; value: RecurrenceFrequency }>>(() => [
      { text: t('gl.recurring_journals.frequencies.daily'), value: 'daily' },
      { text: t('gl.recurring_journals.frequencies.weekly'), value: 'weekly' },
      { text: t('gl.recurring_journals.frequencies.biweekly'), value: 'biweekly' },
      { text: t('gl.recurring_journals.frequencies.monthly'), value: 'monthly' },
</script>

<style scoped>
/* Add component-specific styles here if needed */
</style>