<template>
  <Dialog
    v-model:visible="visible"
    :style="{ width: '450px' }"
    header="Confirm"
    :modal="true"
  >
    <div class="confirmation-content">
      <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
      <span v-if="item">
        Are you sure you want to delete <b>{{ item.name || item.title || 'this item' }}</b>?
      </span>
      <span v-else>
        Are you sure you want to delete the selected items?
      </span>
    </div>
    <template #footer>
      <Button
        label="No"
        icon="pi pi-times"
        class="p-button-text"
        @click="close"
      />
      <Button
        label="Yes"
        icon="pi pi-check"
        class="p-button-danger"
        @click="confirmDelete"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';

const emit = defineEmits(['confirm', 'cancel']);

const visible = ref(false);
const item = ref(null);

const open = (itemToDelete = null) => {
  item.value = itemToDelete;
  visible.value = true;
};

const close = () => {
  visible.value = false;
  emit('cancel');
};

const confirmDelete = () => {
  emit('confirm', item.value);
  close();
};

defineExpose({
  open,
  close,
});
</script>

<style scoped>
.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
