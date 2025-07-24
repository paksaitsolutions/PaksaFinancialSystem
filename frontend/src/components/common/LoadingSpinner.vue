<template>
  <div class="loading-spinner" :class="{ 'overlay': overlay }">
    <div class="spinner" :class="size">
      <div class="bounce1"></div>
      <div class="bounce2"></div>
      <div class="bounce3"></div>
    </div>
    <div v-if="message" class="loading-message">{{ message }}</div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: 'small' | 'medium' | 'large';
  overlay?: boolean;
  message?: string;
}

withDefaults(defineProps<Props>(), {
  size: 'medium',
  overlay: false,
  message: ''
});
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.loading-spinner.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  z-index: 9999;
}

.spinner {
  display: flex;
  gap: 0.2rem;
}

.spinner.small > div {
  width: 8px;
  height: 8px;
}

.spinner.medium > div {
  width: 12px;
  height: 12px;
}

.spinner.large > div {
  width: 16px;
  height: 16px;
}

.spinner > div {
  background-color: var(--primary-color);
  border-radius: 100%;
  animation: sk-bouncedelay 1.4s infinite ease-in-out both;
}

.spinner .bounce1 {
  animation-delay: -0.32s;
}

.spinner .bounce2 {
  animation-delay: -0.16s;
}

.loading-message {
  margin-top: 1rem;
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

@keyframes sk-bouncedelay {
  0%, 80%, 100% {
    transform: scale(0);
  } 40% {
    transform: scale(1.0);
  }
}
</style>