import { ref, computed } from 'vue';
import { useLocalStorage } from '@vueuse/core';

const currentLocale = useLocalStorage('locale', 'en');
const translations = ref<Record<string, Record<string, string>>>({});

export function useI18n() {
  const locale = computed({
    get: () => currentLocale.value,
    set: (value: string) => {
      currentLocale.value = value;
    }
  });

  const t = (key: string, params?: Record<string, any>): string => {
    const translation = translations.value[locale.value]?.[key] || key;
    
    if (params) {
      return translation.replace(/\{(\w+)\}/g, (match, param) => {
        return params[param] || match;
      });
    }
    
    return translation;
  };

  const setTranslations = (localeCode: string, localeTranslations: Record<string, string>) => {
    if (!translations.value[localeCode]) {
      translations.value[localeCode] = {};
    }
    Object.assign(translations.value[localeCode], localeTranslations);
  };

  const formatCurrency = (amount: number, currency: string = 'USD'): string => {
    const currencyMap: Record<string, { symbol: string; position: 'before' | 'after' }> = {
      'USD': { symbol: '$', position: 'before' },
      'EUR': { symbol: '€', position: 'after' },
      'GBP': { symbol: '£', position: 'before' }
    };

    const config = currencyMap[currency] || { symbol: currency, position: 'before' };
    const formatted = amount.toLocaleString(locale.value, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    return config.position === 'before' ? `${config.symbol}${formatted}` : `${formatted} ${config.symbol}`;
  };

  const formatDate = (date: Date | string, format: 'short' | 'long' = 'short'): string => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    const options: Intl.DateTimeFormatOptions = format === 'long' 
      ? { year: 'numeric', month: 'long', day: 'numeric' }
      : { year: 'numeric', month: '2-digit', day: '2-digit' };

    return dateObj.toLocaleDateString(locale.value, options);
  };

  const formatNumber = (number: number): string => {
    return number.toLocaleString(locale.value);
  };

  return {
    locale,
    t,
    setTranslations,
    formatCurrency,
    formatDate,
    formatNumber
  };
}