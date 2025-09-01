<template>
  <div
    :class="containerClass"
    :style="containerStyle"
  >
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useResponsive } from '@/composables/useResponsive'

const props = defineProps({
  fluid: {
    type: Boolean,
    default: false
  },
  maxWidth: {
    type: String,
    default: '1200px'
  },
  padding: {
    type: Object,
    default: () => ({
      mobile: '16px',
      tablet: '24px',
      desktop: '32px'
    })
  }
})

const { isMobile, isTablet, isDesktop } = useResponsive()

const containerClass = computed(() => ({
  'responsive-container': true,
  'responsive-container--mobile': isMobile.value,
  'responsive-container--tablet': isTablet.value,
  'responsive-container--desktop': isDesktop.value
}))

const containerStyle = computed(() => {
  const padding = isMobile.value 
    ? props.padding.mobile 
    : isTablet.value 
      ? props.padding.tablet 
      : props.padding.desktop

  return {
    maxWidth: props.fluid ? '100%' : props.maxWidth,
    padding
  }
})
</script>

<style scoped>
.responsive-container {
  width: 100%;
  margin: 0 auto;
  transition: padding 0.3s ease;
}

.responsive-container--mobile {
  padding-left: 16px !important;
  padding-right: 16px !important;
}

.responsive-container--tablet {
  padding-left: 24px !important;
  padding-right: 24px !important;
}

.responsive-container--desktop {
  padding-left: 32px !important;
  padding-right: 32px !important;
}
</style>