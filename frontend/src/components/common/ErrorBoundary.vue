<template>
  <div v-if="hasError" class="error-boundary">
    <v-alert type="error" prominent>
      <v-row align="center">
        <v-col class="grow">
          <div class="text-h6">Something went wrong</div>
          <div class="text-body-2">{{ errorMessage }}</div>
        </v-col>
        <v-col class="shrink">
          <v-btn @click="retry" color="error" variant="outlined">
            <v-icon start>mdi-refresh</v-icon>
            Retry
          </v-btn>
        </v-col>
      </v-row>
    </v-alert>
    
    <v-expansion-panels v-if="showDetails" class="mt-4">
      <v-expansion-panel>
        <v-expansion-panel-title>Error Details</v-expansion-panel-title>
        <v-expansion-panel-text>
          <pre class="error-stack">{{ errorStack }}</pre>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </div>
  
  <slot v-else />
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'

interface Props {
  showDetails?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: false
})

const hasError = ref(false)
const errorMessage = ref('')
const errorStack = ref('')

onErrorCaptured((error: Error) => {
  hasError.value = true
  errorMessage.value = error.message || 'An unexpected error occurred'
  errorStack.value = error.stack || ''
  
  // Log error for monitoring
  console.error('Error caught by boundary:', error)
  
  return false // Prevent error from propagating
})

const retry = () => {
  hasError.value = false
  errorMessage.value = ''
  errorStack.value = ''
}
</script>

<style scoped>
.error-boundary {
  margin: 16px 0;
}

.error-stack {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}
</style>