<template>
  <teleport to="body">
    <div
      v-if="visible"
      class="modal-overlay"
      :class="{ 'modal-overlay-blur': blur }"
      @click="handleOverlayClick"
    >
      <div
        class="modal-container"
        :class="[
          `modal-${size}`,
          { 'modal-fullscreen': fullscreen }
        ]"
        @click.stop
      >
        <div class="modal-header" v-if="showHeader">
          <slot name="header">
            <h3 class="modal-title">{{ title }}</h3>
            <button
              v-if="closable"
              class="modal-close"
              @click="handleClose"
            >
              <i class="pi pi-times"></i>
            </button>
          </slot>
        </div>

        <div class="modal-content">
          <slot />
        </div>

        <div class="modal-footer" v-if="showFooter">
          <slot name="footer" :close="handleClose">
            <div class="modal-actions">
              <Button
                v-if="showCancel"
                label="Cancel"
                severity="secondary"
                @click="handleClose"
              />
              <Button
                v-if="showConfirm"
                :label="confirmLabel"
                @click="handleConfirm"
              />
            </div>
          </slot>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { watch, onMounted, onUnmounted } from 'vue'
import Button from 'primevue/button'

interface Props {
  visible: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  fullscreen?: boolean
  closable?: boolean
  closeOnOverlay?: boolean
  showHeader?: boolean
  showFooter?: boolean
  showCancel?: boolean
  showConfirm?: boolean
  confirmLabel?: string
  blur?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  fullscreen: false,
  closable: true,
  closeOnOverlay: true,
  showHeader: true,
  showFooter: false,
  showCancel: true,
  showConfirm: true,
  confirmLabel: 'Confirm',
  blur: true
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  close: []
  confirm: []
}>()

const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleConfirm = () => {
  emit('confirm')
}

const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    handleClose()
  }
}

const handleEscapeKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.visible && props.closable) {
    handleClose()
  }
}

// Prevent body scroll when modal is open
watch(() => props.visible, (visible) => {
  if (visible) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onMounted(() => {
  document.addEventListener('keydown', handleEscapeKey)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscapeKey)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: var(--spacing-lg);
  animation: modal-overlay-enter 0.2s ease-out;
}

.modal-overlay-blur {
  backdrop-filter: blur(4px);
}

.modal-container {
  background: var(--surface-0);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: modal-enter 0.3s ease-out;
}

.modal-sm {
  width: 100%;
  max-width: 400px;
}

.modal-md {
  width: 100%;
  max-width: 600px;
}

.modal-lg {
  width: 100%;
  max-width: 800px;
}

.modal-xl {
  width: 100%;
  max-width: 1200px;
}

.modal-fullscreen {
  width: 100vw;
  height: 100vh;
  max-width: none;
  max-height: none;
  border-radius: 0;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-xl) var(--spacing-xl) var(--spacing-lg);
  border-bottom: 1px solid var(--surface-200);
}

.modal-title {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: var(--text-color-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.modal-close:hover {
  background: var(--surface-100);
  color: var(--text-color);
}

.modal-content {
  flex: 1;
  padding: var(--spacing-xl);
  overflow-y: auto;
}

.modal-footer {
  padding: var(--spacing-lg) var(--spacing-xl) var(--spacing-xl);
  border-top: 1px solid var(--surface-200);
  background: var(--surface-50);
}

.modal-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
}

@keyframes modal-overlay-enter {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes modal-enter {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@media (max-width: 768px) {
  .modal-overlay {
    padding: var(--spacing-md);
  }
  
  .modal-container {
    width: 100%;
    max-width: none;
    max-height: 95vh;
  }
  
  .modal-header,
  .modal-content,
  .modal-footer {
    padding-left: var(--spacing-lg);
    padding-right: var(--spacing-lg);
  }
  
  .modal-actions {
    flex-direction: column-reverse;
  }
  
  .modal-actions .p-button {
    width: 100%;
  }
}
</style>