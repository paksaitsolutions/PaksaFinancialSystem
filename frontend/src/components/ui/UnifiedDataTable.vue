<template>
  <Card>
    <template #header v-if="title">
      <div class="table-header">
        <h3 class="table-title">{{ title }}</h3>
        <div v-if="$slots.actions" class="table-actions">
          <slot name="actions"></slot>
        </div>
      </div>
    </template>
    <template #content>
      <DataTable 
        :value="data" 
        :loading="loading"
        :paginator="paginator"
        :rows="rows"
        :totalRecords="totalRecords"
        :lazy="lazy"
        @page="$emit('page', $event)"
        @sort="$emit('sort', $event)"
        @filter="$emit('filter', $event)"
        class="unified-table"
        :class="{ 'compact': compact }"
      >
        <slot></slot>
      </DataTable>
    </template>
  </Card>
</template>

<script setup lang="ts">
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'

interface Props {
  title?: string
  data: any[]
  loading?: boolean
  paginator?: boolean
  rows?: number
  totalRecords?: number
  lazy?: boolean
  compact?: boolean
}

defineProps<Props>()
defineEmits(['page', 'sort', 'filter'])
</script>

<style scoped>
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-lg);
}

.table-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  margin: 0;
}

.table-actions {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

:deep(.unified-table .p-datatable-tbody td) {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--surface-200);
}

:deep(.unified-table .p-datatable-thead th) {
  padding: var(--spacing-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  background: var(--surface-50);
  border-bottom: 1px solid var(--surface-200);
}

:deep(.unified-table.compact .p-datatable-tbody td) {
  padding: var(--spacing-sm) var(--spacing-md);
}

:deep(.unified-table.compact .p-datatable-thead th) {
  padding: var(--spacing-sm) var(--spacing-md);
}

@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .table-actions {
    justify-content: flex-start;
  }
}
</style>