<template>
  <div class="payment-method-selector">
    <label class="form-label">{{ label }} <span v-if="required" class="required">*</span></label>
    
    <div v-if="displayMode === 'dropdown'" class="method-dropdown">
      <select v-model="selectedMethod" @change="handleChange" :required="required" class="form-select">
        <option value="">{{ placeholder }}</option>
        <option v-for="method in filteredMethods" :key="method.value" :value="method.value">
          {{ method.icon }} {{ method.label }}
        </option>
      </select>
    </div>
    
    <div v-else-if="displayMode === 'cards'" class="method-cards">
      <div 
        v-for="method in filteredMethods" 
        :key="method.value"
        class="method-card"
        :class="{ active: selectedMethod === method.value }"
        @click="selectMethod(method.value)"
      >
        <div class="method-icon">{{ method.icon }}</div>
        <div class="method-info">
          <div class="method-name">{{ method.label }}</div>
          <div class="method-desc">{{ method.description }}</div>
          <div class="method-details">
            <span class="processing-time">{{ method.processingTime }}</span>
            <span class="fees">{{ method.fees }} fees</span>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="displayMode === 'grouped'" class="method-groups">
      <div v-for="(methods, category) in groupedMethods" :key="category" class="method-group">
        <h4 class="group-title">{{ formatCategoryName(category) }}</h4>
        <div class="group-methods">
          <label 
            v-for="method in methods" 
            :key="method.value"
            class="method-option"
            :class="{ active: selectedMethod === method.value }"
          >
            <input 
              type="radio" 
              :value="method.value" 
              v-model="selectedMethod"
              @change="handleChange"
              :required="required"
            >
            <div class="option-content">
              <span class="option-icon">{{ method.icon }}</span>
              <div class="option-info">
                <span class="option-name">{{ method.label }}</span>
                <span class="option-desc">{{ method.description }}</span>
              </div>
            </div>
          </label>
        </div>
      </div>
    </div>
    
    <!-- Selected Method Details -->
    <div v-if="selectedMethod && showDetails" class="selected-method-details">
      <div class="detail-card">
        <h5>Payment Details</h5>
        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">Processing Time:</span>
            <span class="detail-value">{{ selectedMethodInfo?.processingTime }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Fees:</span>
            <span class="detail-value">{{ selectedMethodInfo?.fees }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Category:</span>
            <span class="detail-value">{{ formatCategoryName(selectedMethodInfo?.category) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { paymentMethods, getPaymentMethodByValue, type PaymentMethod } from '@/utils/paymentMethods'

interface Props {
  modelValue?: string
  label?: string
  placeholder?: string
  required?: boolean
  displayMode?: 'dropdown' | 'cards' | 'grouped'
  categories?: string[]
  showDetails?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string, method: PaymentMethod | undefined): void
}

const props = withDefaults(defineProps<Props>(), {
  label: 'Payment Method',
  placeholder: 'Select Payment Method',
  required: false,
  displayMode: 'dropdown',
  categories: () => ['traditional', 'digital', 'mobile', 'crypto'],
  showDetails: false
})

const emit = defineEmits<Emits>()

const selectedMethod = ref(props.modelValue || '')

const filteredMethods = computed(() => {
  return paymentMethods.filter(method => 
    props.categories.includes(method.category)
  )
})

const groupedMethods = computed(() => {
  const groups: Record<string, PaymentMethod[]> = {}
  
  filteredMethods.value.forEach(method => {
    if (!groups[method.category]) {
      groups[method.category] = []
    }
    groups[method.category].push(method)
  })
  
  return groups
})

const selectedMethodInfo = computed(() => {
  return getPaymentMethodByValue(selectedMethod.value)
})

const formatCategoryName = (category: string) => {
  const names: Record<string, string> = {
    traditional: 'Traditional Banking',
    digital: 'Digital Payments',
    mobile: 'Mobile Payments',
    crypto: 'Cryptocurrency'
  }
  return names[category] || category
}

const selectMethod = (value: string) => {
  selectedMethod.value = value
  handleChange()
}

const handleChange = () => {
  emit('update:modelValue', selectedMethod.value)
  emit('change', selectedMethod.value, selectedMethodInfo.value)
}

watch(() => props.modelValue, (newValue) => {
  selectedMethod.value = newValue || ''
})
</script>

<style scoped>
.payment-method-selector {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.required {
  color: #ef4444;
}

/* Dropdown Style */
.form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Cards Style */
.method-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.method-card {
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.method-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.method-card.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.method-card .method-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.method-name {
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
}

.method-desc {
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.method-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
}

.processing-time {
  color: #059669;
  font-weight: 500;
}

.fees {
  color: #7c3aed;
  font-weight: 500;
}

/* Grouped Style */
.method-groups {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.method-group {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  background: white;
}

.group-title {
  margin: 0 0 16px 0;
  color: #111827;
  font-size: 1.1rem;
  font-weight: 600;
  border-bottom: 2px solid #f3f4f6;
  padding-bottom: 8px;
}

.group-methods {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.method-option {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.method-option:hover {
  background: #f9fafb;
  border-color: #3b82f6;
}

.method-option.active {
  background: #eff6ff;
  border-color: #3b82f6;
}

.method-option input[type="radio"] {
  margin-right: 12px;
}

.option-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.option-icon {
  font-size: 1.5rem;
}

.option-info {
  display: flex;
  flex-direction: column;
}

.option-name {
  font-weight: 500;
  color: #111827;
}

.option-desc {
  font-size: 0.9rem;
  color: #6b7280;
}

/* Selected Method Details */
.selected-method-details {
  margin-top: 16px;
}

.detail-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
}

.detail-card h5 {
  margin: 0 0 12px 0;
  color: #2d3748;
  font-size: 1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 0.8rem;
  color: #718096;
  font-weight: 500;
}

.detail-value {
  font-size: 0.9rem;
  color: #2d3748;
  font-weight: 500;
}

@media (max-width: 768px) {
  .method-cards {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .method-details {
    flex-direction: column;
    gap: 4px;
  }
}</style>