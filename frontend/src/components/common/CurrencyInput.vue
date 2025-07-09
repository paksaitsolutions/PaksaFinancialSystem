<template>
  <div class="relative rounded-md shadow-sm">
    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
      <span class="text-gray-500 sm:text-sm">{{ currencySymbols[currency] || currency }}</span>
    </div>
    <input
      type="text"
      :value="formattedValue"
      @input="handleInput"
      @blur="handleBlur"
      :disabled="disabled"
      class="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-12 pr-12 sm:text-sm border-gray-300 rounded-md"
      :class="{ 'bg-gray-100': disabled }"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref, watch } from 'vue';

export default defineComponent({
  name: 'CurrencyInput',
  props: {
    modelValue: {
      type: [Number, String],
      default: 0,
    },
    currency: {
      type: String,
      default: 'PKR',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:modelValue', 'blur'],
  setup(props, { emit }) {
    const currencySymbols: Record<string, string> = {
      USD: '$',
      EUR: '€',
      GBP: '£',
      PKR: '₨',
      AED: 'د.إ',
      SAR: '﷼',
    };

    const inputValue = ref(formatNumber(props.modelValue));

    // Format number with thousand separators and decimal places
    function formatNumber(value: number | string): string {
      // Convert string to number if needed
      const num = typeof value === 'string' ? parseFloat(value) || 0 : value;
      
      // Format with 2 decimal places and thousand separators
      return num.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    }

    // Parse input string to number
    function parseNumber(value: string): number {
      // Remove all non-numeric characters except decimal point
      const numStr = value.replace(/[^0-9.]/g, '');
      return parseFloat(numStr) || 0;
    }

    // Handle input event
    function handleInput(event: Event) {
      const target = event.target as HTMLInputElement;
      const value = target.value;
      
      // Allow only numbers and one decimal point
      const isValid = /^\d*\.?\d{0,2}$/.test(value.replace(/[^0-9.]/g, ''));
      
      if (isValid) {
        inputValue.value = value;
        
        // Emit the parsed number
        const num = parseNumber(value);
        emit('update:modelValue', num);
      }
    }

    // Handle blur event to format the value
    function handleBlur(event: Event) {
      const target = event.target as HTMLInputElement;
      const num = parseNumber(target.value);
      
      // Format the number with 2 decimal places
      inputValue.value = formatNumber(num);
      
      // Emit the formatted value and blur event
      emit('update:modelValue', num);
      emit('blur', event);
    }

    // Watch for changes to the modelValue prop
    watch(() => props.modelValue, (newValue) => {
      if (newValue !== parseNumber(inputValue.value)) {
        inputValue.value = formatNumber(newValue);
      }
    });

    // Computed property for the formatted value
    const formattedValue = computed(() => {
      return inputValue.value;
    });

    return {
      currencySymbols,
      formattedValue,
      handleInput,
      handleBlur,
    };
  },
});
</script>
