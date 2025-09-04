<template>
  <div class="approvals-container">
    <div class="page-header">
      <h1>Approval Workflows</h1>
      <p>Manage financial transaction approvals</p>
    </div>

    <div class="approval-tabs">
      <TabView>
        <TabPanel header="Pending Approvals">
          <DataTable :value="pendingApprovals" :loading="loading" responsiveLayout="scroll">
            <Column field="transaction_id" header="Transaction ID" sortable></Column>
            <Column field="transaction_type" header="Type" sortable>
              <template #body="slotProps">
                <Tag :value="slotProps.data.transaction_type" :severity="getTypeSeverity(slotProps.data.transaction_type)" />
              </template>
            </Column>
            <Column field="amount" header="Amount" sortable>
              <template #body="slotProps">
                ${{ slotProps.data.amount.toLocaleString() }}
              </template>
            </Column>
            <Column field="description" header="Description"></Column>
            <Column field="requested_by" header="Requested By"></Column>
            <Column field="priority" header="Priority">
              <template #body="slotProps">
                <Tag :value="slotProps.data.priority" :severity="getPrioritySeverity(slotProps.data.priority)" />
              </template>
            </Column>
            <Column header="Actions">
              <template #body="slotProps">
                <div class="action-buttons">
                  <Button icon="pi pi-check" class="p-button-success p-button-sm" @click="approveTransaction(slotProps.data)" />
                  <Button icon="pi pi-times" class="p-button-danger p-button-sm" @click="rejectTransaction(slotProps.data)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </TabPanel>

        <TabPanel header="Approval History">
          <DataTable :value="approvalHistory" responsiveLayout="scroll">
            <Column field="transaction_id" header="Transaction ID" sortable></Column>
            <Column field="action" header="Action" sortable>
              <template #body="slotProps">
                <Tag :value="slotProps.data.action" :severity="getActionSeverity(slotProps.data.action)" />
              </template>
            </Column>
            <Column field="processed_by" header="Processed By"></Column>
            <Column field="processed_date" header="Date" sortable></Column>
            <Column field="comments" header="Comments"></Column>
          </DataTable>
        </TabPanel>

        <TabPanel header="Settings">
          <div class="approval-settings">
            <Card>
              <template #title>Approval Limits</template>
              <template #content>
                <div class="settings-grid">
                  <div class="setting-item">
                    <label>Journal Entry Limit</label>
                    <InputNumber v-model="settings.approval_limits.journal_entry" mode="currency" currency="USD" />
                  </div>
                  <div class="setting-item">
                    <label>Invoice Limit</label>
                    <InputNumber v-model="settings.approval_limits.invoice" mode="currency" currency="USD" />
                  </div>
                  <div class="setting-item">
                    <label>Payment Limit</label>
                    <InputNumber v-model="settings.approval_limits.payment" mode="currency" currency="USD" />
                  </div>
                  <div class="setting-item">
                    <label>Budget Limit</label>
                    <InputNumber v-model="settings.approval_limits.budget" mode="currency" currency="USD" />
                  </div>
                </div>
                <Button label="Save Settings" icon="pi pi-save" @click="saveSettings" />
              </template>
            </Card>
          </div>
        </TabPanel>
      </TabView>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const loading = ref(false)
const pendingApprovals = ref([])
const approvalHistory = ref([])
const settings = ref({
  approval_limits: {
    journal_entry: 10000,
    invoice: 5000,
    payment: 2500,
    budget: 50000
  }
})

const loadPendingApprovals = async () => {
  loading.value = true
  try {
    pendingApprovals.value = [
      {
        id: 1,
        transaction_id: "JE-001",
        transaction_type: "journal_entry",
        amount: 5000.00,
        description: "Monthly depreciation entry",
        requested_by: "john.doe@company.com",
        priority: "normal"
      }
    ]
  } finally {
    loading.value = false
  }
}

const approveTransaction = (transaction: any) => {
  toast.add({ severity: 'success', summary: 'Approved', detail: `Transaction ${transaction.transaction_id} approved` })
}

const rejectTransaction = (transaction: any) => {
  toast.add({ severity: 'error', summary: 'Rejected', detail: `Transaction ${transaction.transaction_id} rejected` })
}

const getTypeSeverity = (type: string) => {
  const severities: Record<string, string> = {
    journal_entry: 'info',
    invoice: 'warning',
    payment: 'success',
    budget: 'danger'
  }
  return severities[type] || 'info'
}

const getPrioritySeverity = (priority: string) => {
  const severities: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    normal: 'info',
    low: 'success'
  }
  return severities[priority] || 'info'
}

const getActionSeverity = (action: string) => {
  const severities: Record<string, string> = {
    approved: 'success',
    rejected: 'danger',
    pending: 'warning'
  }
  return severities[action] || 'info'
}

const saveSettings = () => {
  toast.add({ severity: 'success', summary: 'Settings Saved', detail: 'Approval settings updated successfully' })
}

onMounted(() => {
  loadPendingApprovals()
})
</script>

<style scoped>
.approvals-container {
  padding: 1rem;
}

.page-header {
  margin-bottom: 2rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.setting-item label {
  font-weight: 600;
  color: var(--text-color);
}
</style>