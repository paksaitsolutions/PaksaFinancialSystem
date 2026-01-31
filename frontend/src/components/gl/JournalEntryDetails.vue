<template>
  <Dialog
    v-model:visible="visible"
    :style="{ width: '800px' }"
    :header="`Journal Entry #${entry?.id || ''}`"
    :modal="true"
    class="p-fluid"
  >
    <div v-if="loading" class="flex justify-content-center p-5">
      <ProgressSpinner />
    </div>

    <div v-else>
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Date</label>
            <div class="p-text-secondary">
              {{ formatDate(entry?.entryDate) }}
            </div>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Reference</label>
            <div class="p-text-secondary">
              {{ entry?.reference || 'N/A' }}
            </div>
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Description</label>
            <div class="p-text-secondary">
              {{ entry?.description || 'No description' }}
            </div>
          </div>
        </div>
      </div>

      <div class="mt-4">
        <h4>Journal Lines</h4>
        <DataTable
          :value="entry?.journalLines || []"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[5, 10, 25]"
          class="p-datatable-sm"
        >
          <Column field="accountNumber" header="Account" :sortable="true">
            <template #body="{ data }">
              {{ data.accountNumber }} - {{ data.accountName }}
            </template>
          </Column>
          <Column field="description" header="Description" :sortable="true" />
          <Column field="debit" header="Debit" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.debit) }}
            </template>
          </Column>
          <Column field="credit" header="Credit" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.credit) }}
            </template>
          </Column>
        </DataTable>
      </div>

      <div class="grid mt-4">
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Created By</label>
            <div class="p-text-secondary">
              {{ entry?.createdBy || 'System' }}
            </div>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Created At</label>
            <div class="p-text-secondary">
              {{ formatDateTime(entry?.createdAt) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <Button
        label="Close"
        icon="pi pi-times"
        class="p-button-text"
        @click="close"
      />
      <Button
        v-if="entry"
        label="Print"
        icon="pi pi-print"
        @click="print"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useFormatting } from '@/composables/useFormatting';

const props = defineProps({
  entryId: {
    type: [String, Number],
    default: null,
  },
});

const emit = defineEmits(['close']);

const { formatDate, formatDateTime, formatCurrency } = useFormatting();

const visible = ref(false);
const loading = ref(false);
const entry = ref(null);

const fetchEntryDetails = async () => {
  if (!props.entryId) return;
  
  loading.value = true;
  try {
    // TODO: Replace with actual API call
    // const response = await journalEntryService.getById(props.entryId);
    // entry.value = response.data;
    
    // Mock data for now
    entry.value = {
      id: props.entryId,
      entryDate: new Date().toISOString(),
      reference: `JE-${props.entryId}`,
      description: 'Sample journal entry',
      status: 'Posted',
      createdBy: 'Admin User',
      createdAt: new Date().toISOString(),
      journalLines: [
        {
          id: 1,
          accountNumber: '1000',
          accountName: 'Cash',
          description: 'To record cash payment',
          debit: 1000,
          credit: 0,
        },
        {
          id: 2,
          accountNumber: '4000',
          accountName: 'Revenue',
          description: 'Service revenue',
          debit: 0,
          credit: 1000,
        },
      ],
    };
  } catch (error) {
    console.error('Error fetching journal entry details:', error);
    // TODO: Show error toast/message
  } finally {
    loading.value = false;
  }
};

const open = () => {
  visible.value = true;
  if (props.entryId) {
    fetchEntryDetails();
  }
};

const close = () => {
  visible.value = false;
  emit('close');
};

const print = () => {
  window.print();
};

defineExpose({
  open,
  close,
});
</script>

<style scoped>
:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-dialog-content) {
  max-height: 70vh;
  overflow-y: auto;
}

@media print {
  :deep(.p-dialog-header),
  :deep(.p-dialog-footer) {
    display: none !important;
  }
  
  :deep(.p-dialog-content) {
    overflow: visible !important;
    padding: 0 !important;
  }
}
</style>
