<template>
  <div class="unified-loading" :class="loadingClasses">
    <div v-if="type === 'spinner'" class="loading-spinner">
      <div class="spinner"></div>
      <p v-if="message" class="loading-message">{{ message }}</p>
    </div>
    
    <div v-else-if="type === 'skeleton'" class="loading-skeleton">
      <div class="skeleton-item" v-for="n in skeletonLines" :key="n"></div>
    </div>
    
    <div v-else-if="type === 'dots'" class="loading-dots">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>
    
    <div v-else-if="type === 'progress'" class="loading-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
      </div>
      <p v-if="message" class="loading-message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'spinner' | 'skeleton' | 'dots' | 'progress'
  size?: 'sm' | 'md' | 'lg'
  message?: string
  overlay?: boolean
  skeletonLines?: number
  progress?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'spinner',
  size: 'md',
  overlay: false,
  skeletonLines: 3,
  progress: 0
})

const loadingClasses = computed(() => ({
  [`loading-${props.size}`]: true,
  'loading-overlay': props.overlay
}))
</script>

<style scoped>
.unified-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  z-index: 9999;
}

/* Spinner Loading */
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--surface-200);
  border-top: 3px solid var(--primary-500);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-sm .spinner {
  width: 24px;
  height: 24px;
  border-width: 2px;
}

.loading-lg .spinner {
  width: 56px;
  height: 56px;
  border-width: 4px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Skeleton Loading */
.loading-skeleton {
  width: 100%;
  max-width: 400px;
}

.skeleton-item {
  height: 16px;
  background: linear-gradient(90deg, var(--surface-200) 25%, var(--surface-100) 50%, var(--surface-200) 75%);
  background-size: 200% 100%;
  border-radius: var(--border-radius);
  margin-bottom: var(--spacing-sm);
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-item:last-child {
  margin-bottom: 0;
  width: 60%;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Dots Loading */
.loading-dots {
  display: flex;
  gap: var(--spacing-sm);
}

.dot {
  width: 8px;
  height: 8px;
  background: var(--primary-500);
  border-radius: 50%;
  animation: dot-bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

.loading-sm .dot {
  width: 6px;
  height: 6px;
}

.loading-lg .dot {
  width: 12px;
  height: 12px;
}

@keyframes dot-bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* Progress Loading */
.loading-progress {
  width: 100%;
  max-width: 300px;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: var(--surface-200);
  border-radius: var(--border-radius);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-500);
  border-radius: var(--border-radius);
  transition: width var(--transition-normal);
}

.loading-message {
  margin: var(--spacing-md) 0 0 0;
  font-size: var(--font-size-sm);
  color: var(--text-color-secondary);
  text-align: center;
}
</style>