export interface PaymentMethod {
  value: string;
  label: string;
  description: string;
  icon: string;
  category: 'traditional' | 'digital' | 'crypto' | 'mobile';
  processingTime: string;
  fees: string;
}

export const paymentMethods: PaymentMethod[] = [
  {
    value: 'check',
    label: 'Check',
    description: 'Traditional paper check payment',
    icon: '📝',
    category: 'traditional',
    processingTime: '3-5 business days',
    fees: 'Low'
  },
  {
    value: 'ach',
    label: 'ACH Transfer',
    description: 'Automated Clearing House electronic transfer',
    icon: '🏦',
    category: 'traditional',
    processingTime: '1-3 business days',
    fees: 'Low'
  },
  {
    value: 'wire_transfer',
    label: 'Wire Transfer',
    description: 'Direct bank-to-bank electronic transfer',
    icon: '⚡',
    category: 'traditional',
    processingTime: 'Same day',
    fees: 'High'
  },
  {
    value: 'ibft',
    label: 'IBFT',
    description: 'Interbank Fund Transfer (Pakistan)',
    icon: '🔄',
    category: 'traditional',
    processingTime: 'Instant',
    fees: 'Low'
  },
  {
    value: 'cash',
    label: 'Cash',
    description: 'Physical cash payment',
    icon: '💵',
    category: 'traditional',
    processingTime: 'Instant',
    fees: 'None'
  },
  {
    value: 'debit_card',
    label: 'Debit Card',
    description: 'Direct debit from bank account',
    icon: '💳',
    category: 'digital',
    processingTime: 'Instant',
    fees: 'Low'
  },
  {
    value: 'credit_card',
    label: 'Credit Card',
    description: 'Credit card payment processing',
    icon: '💎',
    category: 'digital',
    processingTime: 'Instant',
    fees: 'Medium'
  },
  {
    value: 'digital_wallet',
    label: 'Digital Wallet',
    description: 'PayPal, Stripe, Skrill, etc.',
    icon: '👛',
    category: 'digital',
    processingTime: 'Instant',
    fees: 'Medium'
  },
  {
    value: 'mobile_payment',
    label: 'Mobile Payment',
    description: 'Apple Pay, Google Pay, Samsung Pay',
    icon: '📱',
    category: 'mobile',
    processingTime: 'Instant',
    fees: 'Low'
  },
  {
    value: 'online_banking',
    label: 'Online Banking',
    description: 'Direct bank portal transfer',
    icon: '🌐',
    category: 'digital',
    processingTime: 'Instant',
    fees: 'Low'
  },
  {
    value: 'bank_transfer',
    label: 'Bank Transfer',
    description: 'Standard bank-to-bank transfer',
    icon: '🏛️',
    category: 'traditional',
    processingTime: '1-2 business days',
    fees: 'Low'
  },
  {
    value: 'crypto',
    label: 'Cryptocurrency',
    description: 'Bitcoin, Ethereum, USDC, etc.',
    icon: '₿',
    category: 'crypto',
    processingTime: '10-60 minutes',
    fees: 'Variable'
  }
];

export const getPaymentMethodByValue = (value: string): PaymentMethod | undefined => {
  return paymentMethods.find(method => method.value === value);
};

export const getPaymentMethodsByCategory = (category: string): PaymentMethod[] => {
  return paymentMethods.filter(method => method.category === category);
};

export const formatPaymentMethodLabel = (value: string): string => {
  const method = getPaymentMethodByValue(value);
  return method ? method.label : value.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
};

export const getPaymentMethodIcon = (value: string): string => {
  const method = getPaymentMethodByValue(value);
  return method ? method.icon : '💳';
};