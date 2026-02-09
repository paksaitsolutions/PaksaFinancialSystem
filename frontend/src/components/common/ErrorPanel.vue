<template>
  <div
    v-if="visible"
    class="error-panel"
    role="alert"
    aria-live="assertive"
    tabindex="0"
  >
    <div class="error-panel__header">
      <i class="pi pi-exclamation-triangle" aria-hidden="true"></i>
      <div>
        <h3 class="error-panel__title">{{ title }}</h3>
        <p class="error-panel__message">{{ message }}</p>
        <p v-if="requestId" class="error-panel__request">
          Correlation ID: <code>{{ requestId }}</code>
        </p>
      </div>
    </div>
    <ul v-if="details?.length" class="error-panel__details">
      <li v-for="detail in details" :key="detail">{{ detail }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
interface ErrorPanelProps {
  visible: boolean;
  title?: string;
  message: string;
  requestId?: string;
  details?: string[];
}

withDefaults(defineProps<ErrorPanelProps>(), {
  title: 'We hit a snag',
  details: () => []
});
</script>

<style scoped>
.error-panel {
  border: 1px solid #f5c2c7;
  background: #fff1f2;
  color: #991b1b;
  padding: 1rem 1.25rem;
  border-radius: 0.75rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
}

.error-panel__header {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.error-panel__title {
  margin: 0 0 0.35rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.error-panel__message {
  margin: 0;
  font-size: 0.95rem;
}

.error-panel__request {
  margin: 0.35rem 0 0 0;
  font-size: 0.85rem;
}

.error-panel__details {
  margin: 0.75rem 0 0 0;
  padding-left: 1.5rem;
  font-size: 0.9rem;
}
</style>
