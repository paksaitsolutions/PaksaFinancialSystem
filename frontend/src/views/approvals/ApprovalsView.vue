<template>
  <div class="approvals-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Approval Workflows</h1>
        <p class="text-color-secondary">Manage pending approvals and workflow processes</p>
      </div>
      <Button label="Create Workflow" icon="pi pi-plus" @click="createWorkflow" />
    </div>

    <div class="grid">
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-clock text-4xl text-orange-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.pendingApprovals }}</div>
              <div class="text-color-secondary">Pending Approvals</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-check text-4xl text-green-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.approvedToday }}</div>
              <div class="text-color-secondary">Approved Today</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-times text-4xl text-red-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.rejectedToday }}</div>
              <div class="text-color-secondary">Rejected Today</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-cog text-4xl text-blue-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.activeWorkflows }}</div>
              <div class="text-color-secondary">Active Workflows</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Card>
      <template #title>Pending Approvals</template>
      <template #content>
        <DataTable :value="pendingApprovals" :loading="loading" paginator :rows="10">
          <Column field="type" header="Type" sortable />
          <Column field="requestor" header="Requestor" sortable />
          <Column field="amount" header="Amount" sortable />
          <Column field="description" header="Description" sortable />
          <Column field="submittedDate" header="Submitted" sortable />
          <Column field="priority" header="Priority" sortable>
            <template #body="{ data }">
              <Tag :value="data.priority" :severity="getPrioritySeverity(data.priority)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-check" class="p-button-text p-button-success mr-2" @click="approveRequest(data)" v-tooltip="'Approve'" />
              <Button icon="pi pi-times" class="p-button-text p-button-danger mr-2" @click="rejectRequest(data)" v-tooltip="'Reject'" />
              <Button icon="pi pi-eye" class="p-button-text" @click="viewDetails(data)" v-tooltip="'View Details'" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const loading = ref(false)

const stats = ref({
  pendingApprovals: 15,
  approvedToday: 8,
  rejectedToday: 2,
  activeWorkflows: 12
})

const pendingApprovals = ref([
  { id: 1, type: 'Purchase Order', requestor: 'John Doe', amount: '$5,500.00', description: 'Office Equipment Purchase', submittedDate: '2024-01-15', priority: 'high' },
  { id: 2, type: 'Expense Report', requestor: 'Jane Smith', amount: '$1,200.00', description: 'Business Travel Expenses', submittedDate: '2024-01-14', priority: 'medium' },
  { id: 3, type: 'Budget Approval', requestor: 'Mike Johnson', amount: '$25,000.00', description: 'Q1 Marketing Budget', submittedDate: '2024-01-13', priority: 'high' },
  { id: 4, type: 'Vendor Payment', requestor: 'Sarah Wilson', amount: '$3,800.00', description: 'Monthly Service Payment', submittedDate: '2024-01-12', priority: 'low' },
  { id: 5, type: 'Capital Expenditure', requestor: 'David Brown', amount: '$15,000.00', description: 'New Server Equipment', submittedDate: '2024-01-11', priority: 'medium' }
])

const createWorkflow = () => {
  toast.add({ severity: 'info', summary: 'Info', detail: 'Workflow creation feature coming soon', life: 3000 })
}

const approveRequest = (request: any) => {
  const index = pendingApprovals.value.findIndex(r => r.id === request.id)
  if (index !== -1) {
    pendingApprovals.value.splice(index, 1)
    stats.value.pendingApprovals--
    stats.value.approvedToday++
    toast.add({ severity: 'success', summary: 'Success', detail: `${request.type} approved`, life: 3000 })
  }
}

const rejectRequest = (request: any) => {
  const index = pendingApprovals.value.findIndex(r => r.id === request.id)
  if (index !== -1) {
    pendingApprovals.value.splice(index, 1)
    stats.value.pendingApprovals--
    stats.value.rejectedToday++
    toast.add({ severity: 'info', summary: 'Info', detail: `${request.type} rejected`, life: 3000 })
  }
}

const viewDetails = (request: any) => {
  toast.add({ severity: 'info', summary: 'Info', detail: `Viewing details for ${request.type}`, life: 3000 })
}

const getPrioritySeverity = (priority: string) => {
  switch (priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'success'
    default: return 'info'
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.approvals-view {
  padding: 0;
}

.metric-card {
  text-align: center;
}
</style>