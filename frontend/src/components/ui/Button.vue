<template>
  <button
    :class="[
      'btn',
      `btn-${variant}`,
      `btn-${size}`,
      { 'btn-block': block },
      { 'btn-rounded': rounded },
      { 'btn-loading': loading },
      { 'btn-icon': icon && !$slots.default },
    ]"
    :type="type"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="btn-spinner">
      <svg class="spinner" viewBox="0 0 50 50">
        <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
      </svg>
    </span>
    
    <span v-else-if="icon" class="btn-icon-content">
      <i :class="icon"></i>
    </span>
    
    <span v-if="$slots.default" class="btn-content">
      <slot></slot>
    </span>
    
    <span v-if="badge" class="btn-badge">{{ badge }}</span>
  </button>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Button',
  
  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: (value: string) => 
        ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark', 'link'].includes(value),
    },
    size: {
      type: String,
      default: 'md',
      validator: (value: string) => ['sm', 'md', 'lg'].includes(value),
    },
    type: {
      type: String,
      default: 'button',
      validator: (value: string) => ['button', 'submit', 'reset'].includes(value),
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    block: {
      type: Boolean,
      default: false,
    },
    rounded: {
      type: Boolean,
      default: false,
    },
    icon: {
      type: String,
      default: '',
    },
    badge: {
      type: [String, Number],
      default: null,
    },
  },
  
  emits: ['click'],
  
  setup(_, { emit }) {
    const handleClick = (event: Event) => {
      if (!_.loading && !_.disabled) {
        emit('click', event);
      }
    };
    
    return {
      handleClick,
    };
  },
});
</script>

<style scoped>
.btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  user-select: none;
  border: 1px solid transparent;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  line-height: 1.5;
  border-radius: 0.25rem;
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out,
    border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  cursor: pointer;
  text-decoration: none;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* Button Sizes */
.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  line-height: 1.5;
  border-radius: 0.2rem;
}

.btn-lg {
  padding: 0.5rem 1.5rem;
  font-size: 1.25rem;
  line-height: 1.5;
  border-radius: 0.3rem;
}

/* Button Variants */
.btn-primary {
  color: #fff;
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.btn-primary:hover {
  background-color: #0b5ed7;
  border-color: #0a58ca;
}

.btn-secondary {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}

.btn-secondary:hover {
  background-color: #5c636a;
  border-color: #565e64;
}

.btn-success {
  color: #fff;
  background-color: #198754;
  border-color: #198754;
}

.btn-success:hover {
  background-color: #157347;
  border-color: #146c43;
}

.btn-danger {
  color: #fff;
  background-color: #dc3545;
  border-color: #dc3545;
}

.btn-danger:hover {
  background-color: #bb2d3b;
  border-color: #b02a37;
}

.btn-warning {
  color: #000;
  background-color: #ffc107;
  border-color: #ffc107;
}

.btn-warning:hover {
  background-color: #ffca2c;
  border-color: #ffc720;
}

.btn-info {
  color: #000;
  background-color: #0dcaf0;
  border-color: #0dcaf0;
}

.btn-info:hover {
  background-color: #31d2f2;
  border-color: #25cff2;
}

.btn-light {
  color: #000;
  background-color: #f8f9fa;
  border-color: #f8f9fa;
}

.btn-light:hover {
  background-color: #f9fafb;
  border-color: #f9fafb;
}

.btn-dark {
  color: #fff;
  background-color: #212529;
  border-color: #212529;
}

.btn-dark:hover {
  background-color: #1c1f23;
  border-color: #1a1e21;
}

.btn-link {
  font-weight: 400;
  color: #0d6efd;
  text-decoration: underline;
  background-color: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
}

.btn-link:hover {
  color: #0a58ca;
  text-decoration: underline;
}

/* Button States */
.btn:disabled,
.btn.disabled,
.btn[disabled] {
  opacity: 0.65;
  pointer-events: none;
  cursor: not-allowed;
}

.btn-block {
  display: block;
  width: 100%;
}

.btn-rounded {
  border-radius: 50px;
}

/* Button with Icon */
.btn-icon {
  width: 2.5rem;
  height: 2.5rem;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-icon.btn-sm {
  width: 2rem;
  height: 2rem;
}

.btn-icon.btn-lg {
  width: 3rem;
  height: 3rem;
}

/* Loading State */
.btn-loading {
  position: relative;
  color: transparent !important;
  pointer-events: none;
}

.btn-loading .btn-spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 1.5rem;
  height: 1.5rem;
}

.spinner {
  animation: rotate 2s linear infinite;
  width: 100%;
  height: 100%;
}

.spinner .path {
  stroke: currentColor;
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

/* Badge */
.btn-badge {
  position: absolute;
  top: -0.5rem;
  right: -0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1;
  color: #fff;
  background-color: #dc3545;
  border-radius: 50%;
  padding: 0.25rem 0.5rem;
  min-width: 1.25rem;
  height: 1.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Focus and Active States */
.btn:focus {
  outline: 0;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

.btn:active {
  transform: translateY(1px);
}
</style>
