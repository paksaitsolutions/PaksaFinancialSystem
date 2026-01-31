<template>
  <div class="error-container">
    <div class="error-content">
      <div class="error-icon">
        <i class="pi pi-exclamation-triangle"></i>
      </div>
      <h1 class="error-title">500 - Server Error</h1>
      <p class="error-message">
        Oops! Something went wrong on our end. Our team has been notified and we're working to fix it.
      </p>
      
      <!-- Module-specific error guidance -->
      <div v-if="currentModule" class="module-guidance">
        <h3>Module: {{ formatModuleName(currentModule) }}</h3>
        <p v-if="moduleGuidance">{{ moduleGuidance }}</p>
      </div>

      <div class="error-actions">
        <Button 
          label="Go to Dashboard" 
          icon="pi pi-home" 
          class="p-button-primary"
          @click="goToDashboard"
        />
        <Button 
          label="Try Again" 
          icon="pi pi-refresh" 
          class="p-button-outlined p-button-secondary"
          @click="reloadPage"
        />
        <Button 
          v-if="shouldShowSupport"
          label="Contact Support" 
          icon="pi pi-question-circle" 
          class="p-button-text"
          @click="contactSupport"
        />
      </div>

      <!-- Technical details (collapsible) -->
      <div class="technical-details" v-if="showTechnicalDetails">
        <Divider />
        <div class="flex justify-content-between align-items-center mb-3">
          <h4>Technical Details</h4>
          <Button 
            icon="pi pi-times" 
            class="p-button-text p-button-sm" 
            @click="toggleTechnicalDetails" 
          />
        </div>
        <pre class="error-details">{{ errorDetails }}</pre>
      </div>
      <div v-else class="show-details">
        <Button 
          label="Show Technical Details" 
          icon="pi pi-info-circle" 
          class="p-button-text p-button-sm" 
          @click="toggleTechnicalDetails"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

// Module-specific guidance messages
const moduleGuidanceMap: Record<string, string> = {
  'general-ledger': 'There was an issue processing your request in the General Ledger module. Please try again or contact support if the problem persists.',
  'accounts-payable': 'We encountered an issue with the Accounts Payable module. Your invoice or payment data may not have been processed.',
  'accounts-receivable': 'An error occurred while processing your Accounts Receivable request. Please verify the customer information and try again.',
  'cash-management': 'We could not complete your Cash Management operation. Please check your bank connections and try again.',
  'fixed-assets': 'There was an error processing your Fixed Assets request. The asset details may not have been saved.',
  'payroll': 'An error occurred in the Payroll module. Please verify the employee data and try again.',
  'inventory': 'We encountered an issue with the Inventory module. Your stock levels may not have been updated.',
  'purchasing': 'There was a problem processing your purchase order. Please verify the details and try again.',
  'sales': 'An error occurred while processing your sales transaction. Please try again or contact support.',
  'reporting': 'We could not generate your report. Please try again with different parameters or contact support.',
  'settings': 'An error occurred while updating your settings. Your changes may not have been saved.'
};

// Get current module from route
const currentModule = computed(() => {
  const path = route.path.split('/')[1];
  return path || null;
});

// Get module-specific guidance
const moduleGuidance = computed(() => {
  return currentModule.value ? moduleGuidanceMap[currentModule.value] || '' : '';
});

// Error details from route or default
const errorDetails = ref({
  timestamp: new Date().toISOString(),
  errorId: generateErrorId(),
  path: route.path,
  module: currentModule.value,
  message: 'An unexpected error occurred while processing your request.'
});

// UI State
const showTechnicalDetails = ref(false);
const shouldShowSupport = ref(true);

// Methods
const goToDashboard = () => {
  router.push('/dashboard');
};

const reloadPage = () => {
  window.location.reload();
};

const contactSupport = () => {
  // Implement contact support logic
  window.open('mailto:support@paksa.com?subject=Error%20' + errorDetails.value.errorId, '_blank');
};

const toggleTechnicalDetails = () => {
  showTechnicalDetails.value = !showTechnicalDetails.value;
};

// Helper functions
function generateErrorId(): string {
  return 'ERR-' + Math.random().toString(36).substr(2, 9).toUpperCase();
}

function formatModuleName(module: string): string {
  return module
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Lifecycle hooks
onMounted(() => {
  // Log the error to your error tracking service
  console.error('Server Error:', errorDetails.value);
  
  // Hide support button if in development
  if (import.meta.env.DEV) {
    shouldShowSupport.value = false;
  }
});
</script>

<style scoped>
.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
  background-color: var(--surface-ground);
}

.error-content {
  text-align: center;
  max-width: 600px;
  width: 100%;
  background: var(--surface-card);
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.error-icon {
  font-size: 5rem;
  color: var(--red-500);
  margin-bottom: 1.5rem;
}

.error-title {
  font-size: 2.5rem;
  color: var(--text-color);
  margin-bottom: 1rem;
}

.error-message {
  color: var(--text-color-secondary);
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.module-guidance {
  background-color: var(--surface-100);
  border-left: 4px solid var(--primary-color);
  padding: 1rem;
  margin: 1.5rem 0;
  text-align: left;
  border-radius: 0 4px 4px 0;
}

.module-guidance h3 {
  color: var(--primary-color);
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin: 2rem 0;
  flex-wrap: wrap;
}

.technical-details {
  margin-top: 2rem;
  text-align: left;
  background-color: var(--surface-50);
  padding: 1rem;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.error-details {
  font-family: monospace;
  font-size: 0.85rem;
  color: var(--text-color-secondary);
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}

.show-details {
  margin-top: 1rem;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .error-content {
    padding: 2rem 1.5rem;
  }
  
  .error-title {
    font-size: 2rem;
  }
  
  .error-message {
    font-size: 1rem;
  }
  
  .error-actions {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .error-actions .p-button {
    width: 100%;
  }
}
</style>
