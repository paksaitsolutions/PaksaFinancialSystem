import { ref, computed } from 'vue';
import { useForm, useField } from 'vee-validate';
import * as yup from 'yup';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';

export function useDeductionBenefitForm(initialValues: any = {}) {
  const { t } = useI18n();
  const toast = useToast();
  
  // Form schema validation
  const schema = yup.object({
    type: yup.string().required(t('validation.required', { field: t('deductionBenefit.type') })),
    name: yup.string()
      .required(t('validation.required', { field: t('deductionBenefit.name') }))
      .max(100, t('validation.maxLength', { field: t('deductionBenefit.name'), max: 100 })),
    description: yup.string()
      .max(500, t('validation.maxLength', { field: t('deductionBenefit.description'), max: 500 })),
    amount_type: yup.string()
      .required(t('validation.required', { field: t('deductionBenefit.amountType') }))
      .oneOf(['fixed', 'percentage'], t('validation.invalidSelection')),
    amount: yup.number()
      .required(t('validation.required', { field: t('deductionBenefit.amount') }))
      .min(0, t('validation.minValue', { field: t('deductionBenefit.amount'), min: 0 }))
      .when('amount_type', (amount_type, schema) => {
        if (amount_type === 'percentage') {
          return schema.max(100, t('validation.maxPercentage'));
        }
        return schema;
      })
      .typeError(t('validation.mustBeNumber')),
    taxable: yup.boolean(),
    active: yup.boolean()
  });

  // Initialize form with validation
  const { handleSubmit, resetForm, setFieldValue, setValues, errors, meta } = useForm({
    validationSchema: schema,
    initialValues: {
      type: '',
      name: '',
      description: '',
      amount_type: 'fixed',
      amount: 0,
      taxable: false,
      active: true,
      ...initialValues
    }
  });

  // Define form fields with validation
  const { value: type } = useField('type');
  const { value: name } = useField('name');
  const { value: description } = useField('description');
  const { value: amountType } = useField('amount_type');
  const { value: amount } = useField('amount');
  const { value: taxable } = useField('taxable');
  const { value: active } = useField('active');

  // Computed properties
  const isPercentage = computed(() => amountType.value === 'percentage');
  
  // Amount field suffix based on type
  const amountSuffix = computed(() => {
    if (amountType.value === 'percentage') return '%';
    return ''; // For fixed amounts, no suffix
  });

  // Handle form submission
  const onSubmit = handleSubmit(async (values) => {
    try {
      // Convert amount to number (in case it comes as string from form)
      const formData = {
        ...values,
        amount: parseFloat(values.amount as any)
      };
      
      return formData;
    } catch (error) {
      console.error('Form submission error:', error);
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: t('deductionBenefit.errors.submitFailed'),
        life: 5000
      });
      throw error;
    }
  });

  // Reset form to initial values
  const reset = () => {
    resetForm({
      values: {
        type: '',
        name: '',
        description: '',
        amount_type: 'fixed',
        amount: 0,
        taxable: false,
        active: true,
        ...initialValues
      }
    });
  };

  // Set form values (useful for edit mode)
  const setFormValues = (values: any) => {
    setValues({
      ...values,
      // Ensure amount is a number and handle potential null/undefined
      amount: values.amount || 0
    });
  };

  // Type options for the form
  const typeOptions = [
    { label: t('deductionBenefit.types.deduction'), value: 'deduction' },
    { label: t('deductionBenefit.types.benefit'), value: 'benefit' },
    { label: t('deductionBenefit.types.garnishment'), value: 'garnishment' },
    { label: t('deductionBenefit.types.loan'), value: 'loan' },
    { label: t('deductionBenefit.types.other'), value: 'other' }
  ];

  // Amount type options
  const amountTypeOptions = [
    { label: t('deductionBenefit.fixedAmount'), value: 'fixed' },
    { label: t('deductionBenefit.percentage'), value: 'percentage' }
  ];

  return {
    // Form state
    type,
    name,
    description,
    amountType,
    amount,
    taxable,
    active,
    errors,
    meta,
    
    // Computed
    isPercentage,
    amountSuffix,
    
    // Methods
    onSubmit,
    reset,
    setFormValues,
    
    // Options
    typeOptions,
    amountTypeOptions
  };
}

export default useDeductionBenefitForm;
