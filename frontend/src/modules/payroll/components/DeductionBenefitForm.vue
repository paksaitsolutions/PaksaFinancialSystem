<template>
  <form @submit.prevent="handleSubmit" class="p-fluid">
    <div class="grid">
      <!-- Type (Deduction/Benefit) -->
      <div class="field col-12 md:col-6">
        <label for="type" class="font-medium text-900">{{ $t('payroll.deductionBenefit.type') }} *</label>
        <Dropdown
          id="type"
          v-model="formData.type"
          :options="deductionTypes"
          option-label="label"
          option-value="value"
          :class="{ 'p-invalid': v$.type.$error }"
          :disabled="isEdit"
          class="w-full"
        />
        <small v-if="v$.type.$error" class="p-error">
          {{ v$.type.$errors[0].$message }}
        </small>
      </div>

      <!-- Code -->
      <div class="field col-12 md:col-6">
        <label for="code" class="font-medium text-900">{{ $t('common.code') }}</label>
        <InputText
          id="code"
          v-model="formData.code"
          :class="{ 'p-invalid': v$.code.$error }"
          :disabled="isEdit"
          class="w-full"
        />
        <small v-if="v$.code.$error" class="p-error">
          {{ v$.code.$errors[0].$message }}
        </small>
      </div>

      <!-- Name -->
      <div class="field col-12">
        <label for="name" class="font-medium text-900">{{ $t('common.name') }} *</label>
        <InputText
          id="name"
          v-model="formData.name"
          :class="{ 'p-invalid': v$.name.$error }"
          class="w-full"
        />
        <small v-if="v$.name.$error" class="p-error">
          {{ v$.name.$errors[0].$message }}
        </small>
      </div>

      <!-- Description -->
      <div class="field col-12">
        <label for="description" class="font-medium text-900">{{ $t('common.description') }}</label>
        <Textarea
          id="description"
          v-model="formData.description"
          rows="3"
          :class="{ 'p-invalid': v$.description.$error }"
          class="w-full"
        />
        <small v-if="v$.description.$error" class="p-error">
          {{ v$.description.$errors[0].$message }}
        </small>
      </div>

      <!-- Amount Type and Amount/Percentage -->
      <div class="field col-12 md:col-6">
        <label for="amountType" class="font-medium text-900">{{ $t('payroll.deductionBenefit.amountType') }} *</label>
        <Dropdown
          id="amountType"
          v-model="formData.amountType"
          :options="amountTypes"
          option-label="label"
          option-value="value"
          :class="{ 'p-invalid': v$.amountType.$error }"
          class="w-full"
          @change="onAmountTypeChange"
        />
        <small v-if="v$.amountType.$error" class="p-error">
          {{ v$.amountType.$errors[0].$message }}
        </small>
      </div>

      <div class="field col-12 md:col-6">
        <label for="amount" class="font-medium text-900">
          {{ formData.amountType === 'percentage' ? $t('payroll.deductionBenefit.percentage') : $t('payroll.deductionBenefit.amount') }} *
        </label>
        <div class="p-inputgroup">
          <InputNumber
            id="amount"
            v-model="formData.amount"
            :mode="formData.amountType === 'percentage' ? 'decimal' : 'currency'"
            :min="0"
            :max="formData.amountType === 'percentage' ? 100 : null"
            :fraction-digits="formData.amountType === 'percentage' ? 2 : 2"
            :currency="currency"
            :suffix="formData.amountType === 'percentage' ? '%' : ''"
            :class="{ 'p-invalid': v$.amount.$error }"
            class="w-full"
          />
        </div>
        <small v-if="v$.amount.$error" class="p-error">
          {{ v$.amount.$errors[0].$message }}
        </small>
      </div>

      <!-- Tax Settings -->
      <div class="field col-12 md:col-6">
        <label for="isTaxable" class="font-medium text-900">{{ $t('payroll.deductionBenefit.taxSettings') }}</label>
        <div class="flex align-items-center mt-2">
          <Checkbox
            id="isTaxable"
            v-model="formData.isTaxable"
            :binary="true"
            :class="{ 'p-invalid': v$.isTaxable.$error }"
          />
          <label for="isTaxable" class="ml-2">{{ $t('payroll.deductionBenefit.isTaxable') }}</label>
        </div>
        <small v-if="v$.isTaxable.$error" class="p-error">
          {{ v$.isTaxable.$errors[0].$message }}
        </small>
      </div>

      <!-- Status -->
      <div class="field col-12 md:col-6">
        <label for="isActive" class="font-medium text-900">{{ $t('common.status') }}</label>
        <div class="flex align-items-center mt-2">
          <InputSwitch
            id="isActive"
            v-model="formData.isActive"
            :class="{ 'p-invalid': v$.isActive.$error }"
          />
          <span class="ml-2">
            {{ formData.isActive ? $t('common.active') : $t('common.inactive') }}
          </span>
        </div>
        <small v-if="v$.isActive.$error" class="p-error">
          {{ v$.isActive.$errors[0].$message }}
        </small>
      </div>

      <!-- Effective Date -->
      <div class="field col-12 md:col-6">
        <label for="effectiveDate" class="font-medium text-900">{{ $t('payroll.deductionBenefit.effectiveDate') }} *</label>
        <Calendar
          id="effectiveDate"
          v-model="formData.effectiveDate"
          :show-icon="true"
          :show-button-bar="true"
          :class="{ 'p-invalid': v$.effectiveDate.$error }"
          class="w-full"
          date-format="yy-mm-dd"
        />
        <small v-if="v$.effectiveDate.$error" class="p-error">
          {{ v$.effectiveDate.$errors[0].$message }}
        </small>
      </div>

      <!-- Expiry Date -->
      <div class="field col-12 md:col-6">
        <label for="expiryDate" class="font-medium text-900">{{ $t('payroll.deductionBenefit.expiryDate') }}</label>
        <Calendar
          id="expiryDate"
          v-model="formData.expiryDate"
          :show-icon="true"
          :show-button-bar="true"
          :class="{ 'p-invalid': v$.expiryDate.$error }"
          class="w-full"
          date-format="yy-mm-dd"
          :min-date="formData.effectiveDate"
        />
        <small v-if="v$.expiryDate.$error" class="p-error">
          {{ v$.expiryDate.$errors[0].$message }}
        </small>
      </div>

      <!-- GL Account Mapping -->
      <div class="field col-12">
        <label class="font-medium text-900">{{ $t('payroll.deductionBenefit.glAccountMapping') }}</label>
        <div class="grid">
          <div class="field col-12 md:col-6">
            <label for="debitAccountId" class="block mb-2">{{ $t('payroll.deductionBenefit.debitAccount') }}</label>
            <Dropdown
              id="debitAccountId"
              v-model="formData.debitAccountId"
              :options="glAccounts"
              option-label="name"
              option-value="id"
              :filter="true"
              :class="{ 'p-invalid': v$.debitAccountId.$error }"
              class="w-full"
              :placeholder="$t('common.selectAccount')"
            />
            <small v-if="v$.debitAccountId.$error" class="p-error">
              {{ v$.debitAccountId.$errors[0].$message }}
            </small>
          </div>
          <div class="field col-12 md:col-6">
            <label for="creditAccountId" class="block mb-2">{{ $t('payroll.deductionBenefit.creditAccount') }}</label>
            <Dropdown
              id="creditAccountId"
              v-model="formData.creditAccountId"
              :options="glAccounts"
              option-label="name"
              option-value="id"
              :filter="true"
              :class="{ 'p-invalid': v$.creditAccountId.$error }"
              class="w-full"
              :placeholder="$t('common.selectAccount')"
            />
            <small v-if="v$.creditAccountId.$error" class="p-error">
              {{ v$.creditAccountId.$errors[0].$message }}
            </small>
          </div>
        </div>
      </div>
    </div>

    <!-- Form Actions -->
    <div class="flex justify-content-end gap-2 mt-4">
      <Button
        type="button"
        :label="$t('common.cancel')"
        class="p-button-text"
        @click="$emit('cancel')"
      />
      <Button
        type="submit"
        :label="isEdit ? $t('common.update') : $t('common.save')"
        :icon="isEdit ? 'pi pi-check' : 'pi pi-save'"
        :loading="loading"
      />
    </div>
  </form>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useVuelidate } from '@vuelidate/core';
import { required, minLength, maxLength, decimal, numeric, helpers } from '@vuelidate/validators';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';

export default defineComponent({
  name: 'DeductionBenefitForm',
  props: {
    initialData: {
      type: Object,
      default: () => ({})
    },
    isEdit: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    currency: {
      type: String,
      default: 'PKR'
    },
    glAccounts: {
      type: Array,
      default: () => []
    }
  },
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    const { t } = useI18n();
    const toast = useToast();

    // Form data with default values
    const formData = ref({
      type: props.initialData.type || 'deduction',
      code: props.initialData.code || '',
      name: props.initialData.name || '',
      description: props.initialData.description || '',
      amountType: props.initialData.amountType || 'fixed',
      amount: props.initialData.amount || 0,
      isTaxable: props.initialData.isTaxable !== undefined ? props.initialData.isTaxable : false,
      isActive: props.initialData.isActive !== undefined ? props.initialData.isActive : true,
      effectiveDate: props.initialData.effectiveDate ? new Date(props.initialData.effectiveDate) : new Date(),
      expiryDate: props.initialData.expiryDate ? new Date(props.initialData.expiryDate) : null,
      debitAccountId: props.initialData.debitAccountId || null,
      creditAccountId: props.initialData.creditAccountId || null,
    });

    // Validation rules
    const rules = {
      type: { required: helpers.withMessage(t('validation.required', { field: t('payroll.deductionBenefit.type') }), required) },
      code: {
        required: helpers.withMessage(t('validation.required', { field: t('common.code') }), required),
        minLength: helpers.withMessage(t('validation.minLength', { field: t('common.code'), min: 3 }), minLength(3)),
        maxLength: helpers.withMessage(t('validation.maxLength', { field: t('common.code'), max: 20 }), maxLength(20))
      },
      name: {
        required: helpers.withMessage(t('validation.required', { field: t('common.name') }), required),
        minLength: helpers.withMessage(t('validation.minLength', { field: t('common.name'), min: 3 }), minLength(3)),
        maxLength: helpers.withMessage(t('validation.maxLength', { field: t('common.name'), max: 100 }), maxLength(100))
      },
      description: {
        maxLength: helpers.withMessage(t('validation.maxLength', { field: t('common.description'), max: 500 }), maxLength(500))
      },
      amountType: { 
        required: helpers.withMessage(t('validation.required', { field: t('payroll.deductionBenefit.amountType') }), required) 
      },
      amount: {
        required: helpers.withMessage(t('validation.required', { field: t('payroll.deductionBenefit.amount') }), required),
        decimal: helpers.withMessage(t('validation.decimal', { field: t('payroll.deductionBenefit.amount') }), decimal),
        minValue: helpers.withMessage(t('validation.minValue', { field: t('payroll.deductionBenefit.amount'), min: 0 }), (value: number) => value >= 0),
        maxValue: helpers.withMessage(
          t('validation.maxValue', { field: t('payroll.deductionBenefit.amount'), max: 100 }), 
          (value: number) => formData.value.amountType === 'percentage' ? value <= 100 : true
        )
      },
      isTaxable: {},
      isActive: {},
      effectiveDate: { 
        required: helpers.withMessage(t('validation.required', { field: t('payroll.deductionBenefit.effectiveDate') }), required) 
      },
      expiryDate: {
        validDate: helpers.withMessage(
          t('validation.dateAfter', { 
            field: t('payroll.deductionBenefit.expiryDate'), 
            after: t('payroll.deductionBenefit.effectiveDate') 
          }), 
          (value: Date | null) => {
            if (!value) return true;
            return value >= formData.value.effectiveDate;
          }
        )
      },
      debitAccountId: {},
      creditAccountId: {}
    };

    const v$ = useVuelidate(rules, formData);

    // Dropdown options
    const deductionTypes = [
      { label: t('payroll.deductionBenefit.types.deduction'), value: 'deduction' },
      { label: t('payroll.deductionBenefit.types.benefit'), value: 'benefit' }
    ];

    const amountTypes = [
      { label: t('payroll.deductionBenefit.amountTypes.fixed'), value: 'fixed' },
      { label: t('payroll.deductionBenefit.amountTypes.percentage'), value: 'percentage' }
    ];

    // Handle form submission
    const handleSubmit = async () => {
      const isValid = await v$.value.$validate();
      
      if (!isValid) {
        toast.add({
          severity: 'error',
          summary: t('common.error'),
          detail: t('validation.formValidationError'),
          life: 5000
        });
        return;
      }

      // Prepare the data for submission
      const submissionData = {
        ...formData.value,
        // Convert dates to ISO string for API
        effectiveDate: formData.value.effectiveDate.toISOString().split('T')[0],
        expiryDate: formData.value.expiryDate ? formData.value.expiryDate.toISOString().split('T')[0] : null
      };

      emit('submit', submissionData);
    };

    // Handle amount type change
    const onAmountTypeChange = () => {
      // Reset amount when switching between fixed and percentage
      formData.value.amount = 0;
    };

    return {
      formData,
      v$,
      deductionTypes,
      amountTypes,
      handleSubmit,
      onAmountTypeChange
    };
  }
});
</script>

<style scoped>
.field {
  margin-bottom: 1.5rem;
}

.p-inputgroup {
  width: 100%;
}

/* Responsive adjustments */
@media screen and (max-width: 960px) {
  .p-fluid .p-field {
    margin-bottom: 1.5rem;
  }
}
</style>
