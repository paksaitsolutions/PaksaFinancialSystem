<template>
  <div class="multi-currency-input">
    <div class="flex flex-wrap items-center">
      <div class="w-full md:w-2/3 pr-2">
        <div class="relative rounded-md shadow-sm">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span class="text-gray-500 sm:text-sm">{{ currencySymbol }}</span>
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
          <div v-if="showOriginalValue && originalValue" class="absolute inset-y-0 right-0 pr-3 flex items-center text-sm text-gray-500">
            {{ originalCurrencySymbol }} {{ formatNumber(originalValue) }}
          </div>
        </div>
      </div>
      <div class="w-full md:w-1/3 mt-2 md:mt-0">
        <CurrencySelector
          v-model="selectedCurrency"
          :currencies="currencies"
          @change="handleCurrencyChange"
          :disabled="disabled"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import currencyService from '@/services/currencyService';

interface Currency {
  code: string;
  name: string;
  symbol: string;
  flag: string;
  decimalDigits: number;
  decimalSeparator: string;
  thousandsSeparator: string;
  symbolOnLeft: boolean;
  spaceBetweenAmountAndSymbol: boolean;
}

const props = defineProps({
  modelValue: {
    type: [Number, String],
    default: 0,
  },
  currency: {
    type: String,
    default: 'USD',
  },
  originalValue: {
    type: [Number, String],
    default: null,
  },
  originalCurrency: {
    type: String,
    default: null,
  },
  showOriginalValue: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  autoConvert: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(['update:modelValue', 'update:currency', 'blur', 'currency-change']);

const inputValue = ref(formatNumber(props.modelValue));
const selectedCurrency = ref(props.currency);
const currencies = ref<Currency[]>([
  {
    code: 'USD',
    name: 'US Dollar',
    symbol: '$',
    flag: 'fi-us',
    decimalDigits: 2,
    decimalSeparator: '.',
    thousandsSeparator: ',',
    symbolOnLeft: true,
    spaceBetweenAmountAndSymbol: false
  },
  {
    code: 'EUR',
    name: 'Euro',
    symbol: '€',
    flag: 'fi-eu',
    decimalDigits: 2,
    decimalSeparator: ',',
    thousandsSeparator: '.',
    symbolOnLeft: false,
    spaceBetweenAmountAndSymbol: true
  },
  {
    code: 'GBP',
    name: 'British Pound',
    symbol: '£',
    flag: 'fi-gb',
    decimalDigits: 2,
    decimalSeparator: '.',
    thousandsSeparator: ',',
    symbolOnLeft: true,
    spaceBetweenAmountAndSymbol: false
  },
  {
    code: 'PKR',
    name: 'Pakistani Rupee',
    symbol: '₨',
    flag: 'fi-pk',
    decimalDigits: 0,
    decimalSeparator: '.',
    thousandsSeparator: ',',
    symbolOnLeft: true,
    spaceBetweenAmountAndSymbol: false
  },
  {
    code: 'SAR',
    name: 'Saudi Riyal',
    symbol: '﷼',
    flag: 'fi-sa',
    decimalDigits: 2,
    decimalSeparator: '.',
    thousandsSeparator: ',',
    symbolOnLeft: true,
    spaceBetweenAmountAndSymbol: true
  },
  {
    code: 'AED',
    name: 'UAE Dirham',
    symbol: 'د.إ',
    flag: 'fi-ae',
    decimalDigits: 2,
    decimalSeparator: '.',
    thousandsSeparator: ',',
    symbolOnLeft: true,
    spaceBetweenAmountAndSymbol: true
  }
]);

// Load currencies from API
onMounted(async () => {
  try {
    const response = await currencyService.getAllCurrencies();
    if (response.data && Array.isArray(response.data)) {
      currencies.value = response.data.map(c => ({
        code: c.code,
        name: c.name,
        symbol: c.symbol || c.code,
        flag: `fi-${c.code.toLowerCase().substring(0, 2)}`,
        decimalDigits: c.decimal_places,
        decimalSeparator: '.',
        thousandsSeparator: ',',
        symbolOnLeft: true,
        spaceBetweenAmountAndSymbol: false
      }));
    }
  } catch (error) {
    console.error('Failed to load currencies:', error);
  }
});

const currencySymbol = computed(() => {
  const currency = currencies.value.find(c => c.code === selectedCurrency.value);
  return currency ? currency.symbol : selectedCurrency.value;
});

const originalCurrencySymbol = computed(() => {
  if (!props.originalCurrency) return '';
  const currency = currencies.value.find(c => c.code === props.originalCurrency);
  return currency ? currency.symbol : props.originalCurrency;
});

// Format number with thousand separators and decimal places
function formatNumber(value: number | string): string {
  // Convert string to number if needed
  const num = typeof value === 'string' ? parseFloat(value) || 0 : value;
  
  // Get decimal digits for the selected currency
  const currency = currencies.value.find(c => c.code === selectedCurrency.value);
  const decimalDigits = currency ? currency.decimalDigits : 2;
  
  // Format with appropriate decimal places and thousand separators
  return num.toLocaleString(undefined, {
    minimumFractionDigits: decimalDigits,
    maximumFractionDigits: decimalDigits,
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
  const isValid = /^\\d*\\.?\\d{0,2}$/.test(value.replace(/[^0-9.]/g, ''));
  
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
  
  // Format the number with appropriate decimal places
  inputValue.value = formatNumber(num);
  
  // Emit the formatted value and blur event
  emit('update:modelValue', num);
  emit('blur', event);
}

// Handle currency change
async function handleCurrencyChange(currency: Currency) {
  const oldCurrency = selectedCurrency.value;
  selectedCurrency.value = currency.code;
  emit('update:currency', currency.code);
  emit('currency-change', { from: oldCurrency, to: currency.code });
  
  // Auto-convert the amount if needed
  if (props.autoConvert && props.modelValue) {
    try {
      const response = await currencyService.convertCurrency({
        amount: parseNumber(inputValue.value),
        from_currency: oldCurrency,
        to_currency: currency.code
      });
      
      if (response.data && response.data.converted_amount) {
        const convertedAmount = parseFloat(response.data.converted_amount);
        inputValue.value = formatNumber(convertedAmount);
        emit('update:modelValue', convertedAmount);
      }
    } catch (error) {
      console.error('Failed to convert currency:', error);
    }
  }
}

// Watch for changes to the modelValue prop
watch(() => props.modelValue, (newValue) => {
  if (newValue !== parseNumber(inputValue.value)) {
    inputValue.value = formatNumber(newValue);
  }
});

// Watch for changes to the currency prop
watch(() => props.currency, (newValue) => {
  if (newValue !== selectedCurrency.value) {
    selectedCurrency.value = newValue;
  }
});

// Computed property for the formatted value
const formattedValue = computed(() => {
  return inputValue.value;
});
</script>

<style scoped>
.multi-currency-input {
  width: 100%;
}
</style>