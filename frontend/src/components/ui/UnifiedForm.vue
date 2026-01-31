<template>
  <Card>
    <template #header v-if="title">
      <div class="form-header">
        <h3 class="form-title">{{ title }}</h3>
        <div v-if="$slots.actions" class="form-actions">
          <slot name="actions"></slot>
        </div>
      </div>
    </template>
    <template #content>
      <form @submit.prevent="$emit('submit')" class="unified-form">
        <slot></slot>
        <div v-if="showActions" class="form-footer">
          <Button 
            type="button" 
            label="Cancel" 
            class="btn-secondary" 
            @click="$emit('cancel')"
          />
          <Button 
            type="submit" 
            :label="submitLabel" 
            :loading="loading"
            class="btn-primary"
          />
        </div>
      </form>
    </template>
  </Card>
</template>

<script setup lang="ts">

interface Props {
  title?: string
  submitLabel?: string
  loading?: boolean
  showActions?: boolean
}

withDefaults(defineProps<Props>(), {
  submitLabel: 'Save',
  showActions: true
})

defineEmits(['submit', 'cancel'])
</script>

<style scoped>
.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-lg);
}

.form-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  margin: 0;
}

.form-actions {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.unified-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--surface-200);
  margin-top: var(--spacing-lg);
}

:deep(.form-group) {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

:deep(.form-label) {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-color);
}

:deep(.form-input) {
  width: 100%;
}

:deep(.form-row) {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

@media (max-width: 768px) {
  .form-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .form-actions {
    justify-content: flex-start;
  }
  
  .form-footer {
    flex-direction: column;
  }
  
  :deep(.form-row) {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
}
</style>