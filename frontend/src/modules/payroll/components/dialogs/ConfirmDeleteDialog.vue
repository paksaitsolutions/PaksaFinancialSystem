<template>
  <Dialog
    v-model:visible="visible"
    :style="{ width: '450px' }"
    header="Confirm Deletion"
    :modal="true"
  >
    <div class="confirmation-content">
      <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
      <span v-if="item">
        Are you sure you want to delete <b>{{ itemName }}</b>?
      </span>
    </div>
    <template #footer>
      <Button
        label="No"
        icon="pi pi-times"
        class="p-button-text"
        @click="onCancel"
      />
      <Button
        label="Yes"
        icon="pi pi-check"
        class="p-button-danger"
        @click="onConfirm"
      />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';

export default defineComponent({
  name: 'ConfirmDeleteDialog',
  components: {
    Dialog,
    Button,
  },
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    item: {
      type: [Object, null],
      default: null,
    },
    itemName: {
      type: String,
      default: 'this item',
    },
  },
  emits: ['confirm', 'cancel', 'update:show'],
  setup(props, { emit }) {
    const visible = ref(props.show);

    watch(
      () => props.show,
      (newVal) => {
        visible.value = newVal;
      }
    );

    const onConfirm = () => {
      emit('confirm', props.item);
      emit('update:show', false);
    };

    const onCancel = () => {
      emit('cancel');
      emit('update:show', false);
    };

    return {
      visible,
      onConfirm,
      onCancel,
    };
  },
});
</script>

<style scoped>
.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
