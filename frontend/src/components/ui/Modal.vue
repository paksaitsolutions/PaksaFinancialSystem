<template>
  <teleport to="body">
    <transition name="modal-fade">
      <div v-if="isOpen" class="modal-overlay" @click.self="handleOverlayClick">
        <div 
          class="modal" 
          :class="[
            `modal-${size}`,
            { 'modal-centered': centered },
            { 'modal-scrollable': scrollable }
          ]"
          role="dialog"
          :aria-labelledby="titleId"
          aria-modal="true"
        >
          <div class="modal-header" v-if="showHeader">
            <h5 :id="titleId" class="modal-title">
              <slot name="title">{{ title }}</slot>
            </h5>
            <button 
              v-if="showClose" 
              type="button" 
              class="modal-close" 
              @click="close"
              aria-label="Close"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          
          <div class="modal-body">
            <slot></slot>
          </div>
          
          <div v-if="showFooter" class="modal-footer">
            <slot name="footer">
              <Button @click="close" :disabled="loading">
                {{ cancelText }}
              </Button>
              <Button 
                v-if="showConfirm" 
                @click="handleConfirm" 
                :variant="confirmVariant"
                :loading="loading"
              >
                {{ confirmText }}
              </Button>
            </slot>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script lang="ts">
import { defineComponent, ref, watch, computed, onMounted, onUnmounted } from 'vue';
import Button from './Button.vue';

export default defineComponent({
  name: 'Modal',
  
  components: {
    Button,
  },
  
  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
    title: {
      type: String,
      default: '',
    },
    size: {
      type: String,
      default: 'md',
      validator: (value: string) => ['sm', 'md', 'lg', 'xl'].includes(value),
    },
    centered: {
      type: Boolean,
      default: false,
    },
    scrollable: {
      type: Boolean,
      default: false,
    },
    showClose: {
      type: Boolean,
      default: true,
    },
    showHeader: {
      type: Boolean,
      default: true,
    },
    showFooter: {
      type: Boolean,
      default: true,
    },
    showConfirm: {
      type: Boolean,
      default: true,
    },
    confirmText: {
      type: String,
      default: 'Confirm',
    },
    confirmVariant: {
      type: String,
      default: 'primary',
    },
    cancelText: {
      type: String,
      default: 'Cancel',
    },
    loading: {
      type: Boolean,
      default: false,
    },
    closeOnBackdrop: {
      type: Boolean,
      default: true,
    },
    closeOnEsc: {
      type: Boolean,
      default: true,
    },
  },
  
  emits: ['update:modelValue', 'close', 'confirm'],
  
  setup(props, { emit }) {
    const isOpen = ref(props.modelValue);
    const titleId = computed(() => `modal-title-${Math.random().toString(36).substr(2, 9)}`);
    
    // Handle keyboard events
    const handleKeydown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && props.closeOnEsc) {
        close();
      }
    };
    
    // Add/remove event listeners when modal opens/closes
    watch(() => props.modelValue, (newVal) => {
      isOpen.value = newVal;
      
      if (newVal) {
        // Add event listeners when modal opens
        document.body.style.overflow = 'hidden';
        document.addEventListener('keydown', handleKeydown);
      } else {
        // Remove event listeners when modal closes
        document.body.style.overflow = '';
        document.removeEventListener('keydown', handleKeydown);
      }
    }, { immediate: true });
    
    // Clean up event listeners when component is unmounted
    onUnmounted(() => {
      document.body.style.overflow = '';
      document.removeEventListener('keydown', handleKeydown);
    });
    
    const close = () => {
      if (props.loading) return;
      
      isOpen.value = false;
      emit('update:modelValue', false);
      emit('close');
    };
    
    const handleConfirm = () => {
      emit('confirm');
    };
    
    const handleOverlayClick = () => {
      if (props.closeOnBackdrop) {
        close();
      }
    };
    
    return {
      isOpen,
      titleId,
      close,
      handleConfirm,
      handleOverlayClick,
    };
  },
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
  padding: 1rem;
  overflow-y: auto;
}

.modal {
  position: relative;
  width: 100%;
  background-color: #fff;
  border-radius: 0.3rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 2rem);
  overflow: hidden;
}

.modal-centered {
  align-items: center;
}

.modal-scrollable {
  max-height: calc(100vh - 2rem);
}

.modal-sm {
  max-width: 400px;
}

.modal-md {
  max-width: 600px;
}

.modal-lg {
  max-width: 800px;
}

.modal-xl {
  max-width: 1140px;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  border-top-left-radius: calc(0.3rem - 1px);
  border-top-right-radius: calc(0.3rem - 1px);
}

.modal-title {
  margin: 0;
  line-height: 1.5;
  font-size: 1.25rem;
  font-weight: 500;
}

.modal-close {
  padding: 0.5rem;
  margin: -0.5rem -0.5rem -0.5rem auto;
  background-color: transparent;
  border: 0;
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1;
  color: #000;
  text-shadow: 0 1px 0 #fff;
  opacity: 0.5;
  cursor: pointer;
  transition: opacity 0.15s ease-in-out;
}

.modal-close:hover {
  opacity: 0.75;
  text-decoration: none;
}

.modal-body {
  position: relative;
  flex: 1 1 auto;
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  border-bottom-right-radius: calc(0.3rem - 1px);
  border-bottom-left-radius: calc(0.3rem - 1px);
  gap: 0.5rem;
}

/* Modal Animation */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.15s ease-in-out;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal,
.modal-fade-leave-active .modal {
  transition: transform 0.15s ease-out, opacity 0.15s ease-out;
}

.modal-fade-enter-from .modal,
.modal-fade-leave-to .modal {
  transform: translateY(-50px);
  opacity: 0;
}
</style>
