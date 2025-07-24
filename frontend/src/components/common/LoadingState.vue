<template>
  <div class="loading-state">
    <v-progress-circular
      v-if="loading"
      :size="size"
      :width="width"
      color="primary"
      indeterminate
    ></v-progress-circular>
    
    <div v-else-if="error" class="error-state text-center">
      <v-icon :size="iconSize" color="error" class="mb-2">mdi-alert-circle</v-icon>
      <p class="text-h6 mb-2">{{ errorTitle }}</p>
      <p class="text-body-2 mb-4">{{ errorMessage }}</p>
      <v-btn color="primary" @click="$emit('retry')" v-if="showRetry">
        <v-icon start>mdi-refresh</v-icon>
        Try Again
      </v-btn>
    </div>
    
    <div v-else-if="empty" class="empty-state text-center">
      <v-icon :size="iconSize" color="grey-lighten-1" class="mb-2">{{ emptyIcon }}</v-icon>
      <p class="text-h6 mb-2">{{ emptyTitle }}</p>
      <p class="text-body-2 mb-4">{{ emptyMessage }}</p>
      <slot name="empty-action"></slot>
    </div>
    
    <slot v-else></slot>
  </div>
</template>

<script setup lang="ts">
interface Props {
  loading?: boolean
  error?: Error | null
  empty?: boolean
  size?: number
  width?: number
  iconSize?: number
  errorTitle?: string
  errorMessage?: string
  emptyTitle?: string
  emptyMessage?: string
  emptyIcon?: string
  showRetry?: boolean
}

withDefaults(defineProps<Props>(), {
  loading: false,
  error: null,
  empty: false,
  size: 40,
  width: 4,
  iconSize: 64,
  errorTitle: 'Something went wrong',
  errorMessage: 'Please try again later',
  emptyTitle: 'No data found',
  emptyMessage: 'There are no items to display',
  emptyIcon: 'mdi-inbox',
  showRetry: true
})

defineEmits<{
  retry: []
}>()
</script>

<style scoped>
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.error-state,
.empty-state {
  padding: 2rem;
}
</style>