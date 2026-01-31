<template>
  <div class="pagination-wrapper">
    <!-- Items info -->
    <div class="pagination-info">
      <span v-if="totalItems > 0">
        Showing {{ startItem }} to {{ endItem }} of {{ totalItems }} entries
      </span>
      <span v-else>No entries found</span>
    </div>

    <!-- Page size selector -->
    <div class="page-size-selector">
      <label for="pageSize">Show:</label>
      <Dropdown
        id="pageSize"
        v-model="selectedPageSize"
        :options="pageSizeOptions"
        option-label="label"
        option-value="value"
        @change="onPageSizeChange"
        class="w-20"
      />
    </div>

    <!-- Pagination controls -->
    <div class="pagination-controls" v-if="totalPages > 1">
      <Button
        icon="pi pi-angle-double-left"
        :disabled="!hasPrevPage"
        @click="$emit('first-page')"
        text
        rounded
        severity="secondary"
        size="small"
      />
      <Button
        icon="pi pi-angle-left"
        :disabled="!hasPrevPage"
        @click="$emit('prev-page')"
        text
        rounded
        severity="secondary"
        size="small"
      />
      
      <!-- Page numbers -->
      <div class="page-numbers">
        <Button
          v-for="page in visiblePages"
          :key="page"
          :label="page.toString()"
          :outlined="page !== currentPage"
          :severity="page === currentPage ? 'primary' : 'secondary'"
          @click="$emit('go-to-page', page)"
          size="small"
          rounded
        />
      </div>
      
      <Button
        icon="pi pi-angle-right"
        :disabled="!hasNextPage"
        @click="$emit('next-page')"
        text
        rounded
        severity="secondary"
        size="small"
      />
      <Button
        icon="pi pi-angle-double-right"
        :disabled="!hasNextPage"
        @click="$emit('last-page')"
        text
        rounded
        severity="secondary"
        size="small"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

interface Props {
  currentPage: number
  totalPages: number
  totalItems: number
  pageSize: number
  startItem: number
  endItem: number
  hasNextPage: boolean
  hasPrevPage: boolean
  loading?: boolean
}

interface Emits {
  (e: 'go-to-page', page: number): void
  (e: 'next-page'): void
  (e: 'prev-page'): void
  (e: 'first-page'): void
  (e: 'last-page'): void
  (e: 'page-size-change', size: number): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<Emits>()

// Page size options
const pageSizeOptions = [
  { label: '10', value: 10 },
  { label: '20', value: 20 },
  { label: '50', value: 50 },
  { label: '100', value: 100 }
]

const selectedPageSize = ref(props.pageSize)

// Watch for external page size changes
watch(() => props.pageSize, (newSize) => {
  selectedPageSize.value = newSize
})

// Calculate visible page numbers
const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 5
  const half = Math.floor(maxVisible / 2)
  
  let start = Math.max(1, props.currentPage - half)
  let end = Math.min(props.totalPages, start + maxVisible - 1)
  
  // Adjust start if we're near the end
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const onPageSizeChange = () => {
  emit('page-size-change', selectedPageSize.value)
}
</script>

<style scoped>
.pagination-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 0;
  flex-wrap: wrap;
}

.pagination-info {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
  margin: 0 0.5rem;
}

@media (max-width: 768px) {
  .pagination-wrapper {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .pagination-controls {
    justify-content: center;
  }
  
  .page-size-selector {
    justify-content: center;
  }
}
</style>