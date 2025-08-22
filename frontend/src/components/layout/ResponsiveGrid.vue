<template>
  <v-row :class="gridClass">
    <v-col
      v-for="(item, index) in items"
      :key="index"
      :cols="getColSize('mobile')"
      :sm="getColSize('tablet')"
      :md="getColSize('desktop')"
      :lg="getColSize('large')"
      :xl="getColSize('xlarge')"
    >
      <slot :item="item" :index="index" />
    </v-col>
  </v-row>
</template>

<script setup>
import { computed } from 'vue'
import { useResponsive } from '@/composables/useResponsive'

const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  columns: {
    type: Object,
    default: () => ({
      mobile: 1,
      tablet: 2,
      desktop: 3,
      large: 4,
      xlarge: 4
    })
  },
  spacing: {
    type: String,
    default: '4'
  }
})

const { isMobile, isTablet } = useResponsive()

const gridClass = computed(() => ({
  'responsive-grid': true,
  [`responsive-grid--spacing-${props.spacing}`]: true,
  'responsive-grid--mobile': isMobile.value,
  'responsive-grid--tablet': isTablet.value
}))

const getColSize = (breakpoint) => {
  const columns = props.columns[breakpoint] || 1
  return Math.floor(12 / columns)
}
</script>

<style scoped>
.responsive-grid {
  margin: 0;
}

.responsive-grid--spacing-2 {
  margin: -8px;
}

.responsive-grid--spacing-2 .v-col {
  padding: 8px;
}

.responsive-grid--spacing-4 {
  margin: -16px;
}

.responsive-grid--spacing-4 .v-col {
  padding: 16px;
}

.responsive-grid--spacing-6 {
  margin: -24px;
}

.responsive-grid--spacing-6 .v-col {
  padding: 24px;
}

@media (max-width: 600px) {
  .responsive-grid--mobile .v-col {
    padding: 8px;
  }
}
</style>