import { ref, computed } from 'vue'

interface Currency {
  id: number
  code: string
  name: string
  symbol: string
  rate: number
  isBase: boolean
  status: string
}

const currencies = ref<Currency[]>([
  {
    id: 1,
    code: 'USD',
    name: 'US Dollar',
    symbol: '$',
    rate: 1.0000,
    isBase: true,
    status: 'Active'
  },
  {
    id: 2,
    code: 'EUR',
    name: 'Euro',
    symbol: '€',
    rate: 0.8500,
    isBase: false,
    status: 'Active'
  }
])

export const useCurrency = () => {
  const baseCurrency = computed(() => currencies.value.find(c => c.isBase))
  const activeCurrencies = computed(() => currencies.value.filter(c => c.status === 'Active'))

  const formatCurrency = (amount: number, currencyCode?: string) => {
    const currency = currencyCode 
      ? currencies.value.find(c => c.code === currencyCode)
      : baseCurrency.value
    
    if (!currency) return amount.toString()
    
    return `${currency.symbol}${amount.toLocaleString('en-US', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    })}`
  }

  const convertCurrency = (amount: number, fromCode: string, toCode: string) => {
    const fromCurrency = currencies.value.find(c => c.code === fromCode)
    const toCurrency = currencies.value.find(c => c.code === toCode)
    
    if (!fromCurrency || !toCurrency) return amount
    
    const baseAmount = amount / fromCurrency.rate
    return baseAmount * toCurrency.rate
  }

  return {
    currencies,
    baseCurrency,
    activeCurrencies,
    formatCurrency,
    convertCurrency
  }
}