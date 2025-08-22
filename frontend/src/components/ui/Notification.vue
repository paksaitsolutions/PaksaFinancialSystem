<template>
  <transition name="notification-slide">
    <div 
      v-if="isVisible" 
      class="notification" 
      :class="[type, position]"
      :style="{ '--notification-bg': getBackgroundColor, '--notification-color': getTextColor }"
    >
      <div class="notification-content">
        <div v-if="icon" class="notification-icon">
          <i :class="icon"></i>
        </div>
        <div class="notification-message">
          <div v-if="title" class="notification-title">{{ title }}</div>
          <div class="notification-text">
            <slot>{{ message }}</slot>
          </div>
        </div>
      </div>
      <button v-if="dismissible" class="notification-close" @click="dismiss">
        &times;
      </button>
    </div>
  </transition>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted } from 'vue';

type NotificationType = 'success' | 'error' | 'info' | 'warning';
type NotificationPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';

export default defineComponent({
  name: 'Notification',
  
  props: {
    type: {
      type: String as () => NotificationType,
      default: 'info',
      validator: (value: string) => ['success', 'error', 'info', 'warning'].includes(value),
    },
    message: {
      type: String,
      default: '',
    },
    title: {
      type: String,
      default: '',
    },
    position: {
      type: String as () => NotificationPosition,
      default: 'top-right',
      validator: (value: string) => 
        ['top-right', 'top-left', 'bottom-right', 'bottom-left'].includes(value),
    },
    dismissible: {
      type: Boolean,
      default: true,
    },
    timeout: {
      type: Number,
      default: 5000, // 5 seconds
    },
    icon: {
      type: String,
      default: '',
    },
  },
  
  emits: ['dismissed'],
  
  setup(props, { emit }) {
    const isVisible = ref(false);
    let timeoutId: number | null = null;
    
    const show = () => {
      isVisible.value = true;
      
      if (props.timeout > 0) {
        // Clear any existing timeout
        if (timeoutId) {
          window.clearTimeout(timeoutId);
        }
        
        // Set new timeout
        timeoutId = window.setTimeout(() => {
          dismiss();
        }, props.timeout);
      }
    };
    
    const dismiss = () => {
      isVisible.value = false;
      emit('dismissed');
      
      if (timeoutId) {
        window.clearTimeout(timeoutId);
        timeoutId = null;
      }
    };
    
    // Auto-show notification when component is mounted
    onMounted(() => {
      // Small delay to ensure the component is fully rendered
      setTimeout(() => {
        show();
      }, 100);
    });
    
    // Clean up timeouts when component is unmounted
    onUnmounted(() => {
      if (timeoutId) {
        window.clearTimeout(timeoutId);
      }
    });
    
    // Get appropriate background color based on notification type
    const getBackgroundColor = computed(() => {
      const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8',
      };
      return colors[props.type as keyof typeof colors] || colors.info;
    });
    
    // Get appropriate text color based on notification type
    const getTextColor = computed(() => {
      return ['warning'].includes(props.type) ? '#212529' : '#fff';
    });
    
    // Get appropriate icon based on notification type if not provided
    const getIcon = computed(() => {
      if (props.icon) return props.icon;
      
      const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle',
      };
      
      return `fas fa-${icons[props.type as keyof typeof icons] || 'info-circle'}`;
    });
    
    return {
      isVisible,
      dismiss,
      getBackgroundColor,
      getTextColor,
      icon: getIcon,
    };
  },
});
</script>

<style scoped>
.notification {
  position: fixed;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-width: 300px;
  max-width: 400px;
  padding: 1rem;
  margin: 0.5rem;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background-color: var(--notification-bg, #17a2b8);
  color: var(--notification-color, #fff);
  transition: all 0.3s ease;
  overflow: hidden;
}

/* Position classes */
.top-right {
  top: 1rem;
  right: 1rem;
}

.top-left {
  top: 1rem;
  left: 1rem;
}

.bottom-right {
  bottom: 1rem;
  right: 1rem;
}

.bottom-left {
  bottom: 1rem;
  left: 1rem;
}

.notification-content {
  display: flex;
  align-items: flex-start;
  flex-grow: 1;
  margin-right: 1rem;
}

.notification-icon {
  margin-right: 0.75rem;
  font-size: 1.25rem;
  line-height: 1;
  display: flex;
  align-items: center;
}

.notification-message {
  flex: 1;
}

.notification-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.notification-text {
  font-size: 0.9rem;
  line-height: 1.4;
}

.notification-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.25rem;
  font-weight: bold;
  line-height: 1;
  opacity: 0.7;
  cursor: pointer;
  padding: 0.25rem;
  margin: -0.25rem -0.25rem -0.25rem 0.5rem;
  transition: opacity 0.2s ease;
}

.notification-close:hover {
  opacity: 1;
}

/* Animation */
.notification-slide-enter-active,
.notification-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.notification-slide-enter-from,
.notification-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.notification-slide-enter-to,
.notification-slide-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* For bottom positions */
.bottom-right.notification-slide-enter-from,
.bottom-right.notification-slide-leave-to,
.bottom-left.notification-slide-enter-from,
.bottom-left.notification-slide-leave-to {
  transform: translateY(20px);
}
</style>
