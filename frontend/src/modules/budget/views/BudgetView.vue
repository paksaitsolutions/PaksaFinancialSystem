<template>
  <div class="p-4">
    <Card>
      <template #header>
        <div class="flex justify-content-between align-items-center p-4">
          <h2 class="m-0">Budget Management</h2>
          <Button 
            label="New Budget" 
            icon="pi pi-plus" 
            @click="openCreateDialog"
          />
        </div>
      </template>
      <template #content>
        <!-- Filters -->
        <div class="grid mb-4">
          <div class="col-12 md:col-3">
            <InputText
              v-model="filters.search"
              placeholder="Search budgets..."
              class="w-full"
            />
          </div>
          <div class="col-12 md:col-3">
            <Dropdown
              v-model="filters.status"
              :options="budgetStatuses"
              placeholder="Select Status"
              class="w-full"
              showClear
            />
          </div>
          <div class="col-12 md:col-3">
            <Dropdown
              v-model="filters.type"
              :options="budgetTypes"
              placeholder="Select Type"
              class="w-full"
              showClear
            />
          </div>
          <div class="col-12 md:col-3">
            <Button 
              label="Clear Filters" 
              severity="secondary" 
              outlined 
              @click="clearFilters" 
              class="w-full"
            />
          </div>
        </div>

        <!-- Budget Table -->
        <DataTable
          :value="filteredBudgets"
          :loading="loading"
          :paginator="true"
          :rows="10"
          responsiveLayout="scroll"
        >
          <Column field="name" header="Name">
            <template #body="{ data }">
              <a href="#" @click.prevent="openEditDialog(data)" class="text-primary cursor-pointer">
                {{ data.name }}
              </a>
            </template>
          </Column>
          
          <Column field="amount" header="Amount">
            <template #body="{ data }">
              {{ formatCurrency(data.amount) }}
            </template>
          </Column>
          
          <Column field="status" header="Status">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          
          <Column field="type" header="Type">
            <template #body="{ data }">
              <Tag :value="data.type" severity="info" />
            </template>
          </Column>
          
          <Column field="startDate" header="Start Date">
            <template #body="{ data }">
              {{ formatDate(data.startDate) }}
            </template>
          </Column>
          
          <Column field="endDate" header="End Date">
            <template #body="{ data }">
              {{ formatDate(data.endDate) }}
            </template>
          </Column>
          
          <Column header="Actions">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button 
                  icon="pi pi-pencil" 
                  size="small" 
                  severity="info" 
                  @click="openEditDialog(data)"
                />
                <Button 
                  v-if="data.status === 'PENDING_APPROVAL'" 
                  icon="pi pi-check" 
                  size="small" 
                  severity="success" 
                  @click="openApprovalDialog(data)"
                />
                <Button 
                  v-if="data.status === 'PENDING_APPROVAL'" 
                  icon="pi pi-times" 
                  size="small" 
                  severity="warning" 
                  @click="openRejectDialog(data)"
                />
                <Button 
                  icon="pi pi-trash" 
                  size="small" 
                  severity="danger" 
                  @click="confirmDelete(data.id)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Budget Form Dialog -->
    <Dialog 
      v-model:visible="dialog.visible" 
      modal 
      :header="dialog.mode === 'create' ? 'New Budget' : 'Edit Budget'"
      :style="{ width: '50rem' }"
    >
      <BudgetForm 
        v-if="dialog.visible"
        :budget="dialog.budget"
        :loading="dialog.loading"
        @submit="handleSave"
        @cancel="dialog.visible = false"
      />
    </Dialog>

    <!-- Approval Dialog -->
    <Dialog 
      v-model:visible="approvalDialog.visible" 
      modal 
      header="Approve Budget"
      :style="{ width: '30rem' }"
    >
      <p class="mb-3">Are you sure you want to approve this budget?</p>
      <Textarea
        v-model="approvalNotes"
        placeholder="Approval Notes (Optional)"
        rows="3"
        class="w-full"
      />
      <template #footer>
        <Button 
          label="Cancel" 
          severity="secondary" 
          @click="approvalDialog.visible = false" 
          :disabled="approvalDialog.loading"
        />
        <Button 
          label="Approve" 
          severity="success" 
          @click="handleApproval" 
          :loading="approvalDialog.loading"
        />
      </template>
    </Dialog>

    <!-- Reject Dialog -->
    <Dialog 
      v-model:visible="rejectDialog.visible" 
      modal 
      header="Reject Budget"
      :style="{ width: '30rem' }"
    >
      <Textarea
        v-model="rejectNotes"
        placeholder="Reason for rejection"
        rows="3"
        class="w-full"
      />
      <template #footer>
        <Button 
          label="Cancel" 
          severity="secondary" 
          @click="rejectDialog.visible = false" 
          :disabled="rejectDialog.loading"
        />
        <Button 
          label="Reject" 
          severity="danger" 
          @click="handleReject" 
          :loading="rejectDialog.loading"
        />
      </template>
    </Dialog>
  </div>
</template>

<script>
import BudgetForm from '../components/BudgetForm.vue'
import { useBudgetStore } from '../store/budget'

export default {
  name: 'BudgetView',
  components: {
    BudgetForm
  },
  
  data: () => ({
    loading: false,
    dialog: {
      visible: false,
      loading: false,
      mode: 'create',
      budget: null
    },
    approvalDialog: {
      visible: false,
      loading: false
    },
    rejectDialog: {
      visible: false,
      loading: false
    },
    selectedBudget: null,
    approvalNotes: '',
    rejectNotes: '',
    filters: {
      search: '',
      status: null,
      type: null
    },
    budgetStatuses: [
      'DRAFT',
      'PENDING_APPROVAL', 
      'APPROVED',
      'REJECTED',
      'ARCHIVED'
    ],
    budgetTypes: [
      'OPERATIONAL',
      'CAPITAL',
      'PROJECT',
      'DEPARTMENT'
    ],
    headers: [
      { title: 'Name', key: 'name' },
      { title: 'Amount', key: 'amount' },
      { title: 'Type', key: 'type' },
      { title: 'Status', key: 'status' },
      { title: 'Start Date', key: 'startDate' },
      { title: 'End Date', key: 'endDate' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
  }),
  
  computed: {
    budgets() {
      return this.budgetStore.budgets
    },
    
    filteredBudgets() {
      let filtered = this.budgets
      
      if (this.filters.search) {
        filtered = filtered.filter(budget => 
          budget.name.toLowerCase().includes(this.filters.search.toLowerCase())
        )
      }
      
      if (this.filters.status) {
        filtered = filtered.filter(budget => budget.status === this.filters.status)
      }
      
      if (this.filters.type) {
        filtered = filtered.filter(budget => budget.type === this.filters.type)
      }
      
      return filtered
    }
  },
  
  async mounted() {
    this.budgetStore = useBudgetStore()
    await this.loadBudgets()
  },
  
  methods: {
    async loadBudgets() {
      try {
        this.loading = true
        await this.budgetStore.fetchBudgets()
      } catch (error) {
        console.error('Error loading budgets:', error)
      } finally {
        this.loading = false
      }
    },
    
    openCreateDialog() {
      this.dialog = {
        visible: true,
        loading: false,
        mode: 'create',
        budget: {
          name: '',
          amount: 0,
          type: 'OPERATIONAL',
          status: 'DRAFT',
          startDate: new Date().toISOString().substr(0, 10),
          endDate: '',
          description: ''
        }
      }
    },
    
    openEditDialog(budget) {
      this.dialog = {
        visible: true,
        loading: false,
        mode: 'edit',
        budget: { ...budget }
      }
    },
    
    openApprovalDialog(budget) {
      this.selectedBudget = budget
      this.approvalNotes = ''
      this.approvalDialog.visible = true
    },
    
    openRejectDialog(budget) {
      this.selectedBudget = budget
      this.rejectNotes = ''
      this.rejectDialog.visible = true
    },
    
    async handleSave(budgetData) {
      try {
        this.dialog.loading = true
        
        if (this.dialog.mode === 'create') {
          await this.budgetStore.createBudget(budgetData)
        } else {
          await this.budgetStore.updateBudget(budgetData.id, budgetData)
        }
        
        this.dialog.visible = false
        await this.loadBudgets()
      } catch (error) {
        console.error('Error saving budget:', error)
      } finally {
        this.dialog.loading = false
      }
    },
    
    async handleApproval() {
      try {
        this.approvalDialog.loading = true
        await this.budgetStore.approveBudget(this.selectedBudget.id, this.approvalNotes)
        this.approvalDialog.visible = false
        await this.loadBudgets()
      } catch (error) {
        console.error('Error approving budget:', error)
      } finally {
        this.approvalDialog.loading = false
      }
    },
    
    async handleReject() {
      if (!this.rejectNotes.trim()) return
      
      try {
        this.rejectDialog.loading = true
        await this.budgetStore.rejectBudget(this.selectedBudget.id, this.rejectNotes)
        this.rejectDialog.visible = false
        await this.loadBudgets()
      } catch (error) {
        console.error('Error rejecting budget:', error)
      } finally {
        this.rejectDialog.loading = false
      }
    },
    
    async confirmDelete(budgetId) {
      if (confirm('Are you sure you want to delete this budget?')) {
        try {
          await this.budgetStore.deleteBudget(budgetId)
          await this.loadBudgets()
        } catch (error) {
          console.error('Error deleting budget:', error)
        }
      }
    },
    
    clearFilters() {
      this.filters = {
        search: '',
        status: null,
        type: null
      }
    },
    
    getStatusSeverity(status) {
      const severities = {
        DRAFT: 'info',
        PENDING_APPROVAL: 'warning',
        APPROVED: 'success',
        REJECTED: 'danger',
        ARCHIVED: 'secondary'
      }
      return severities[status] || 'info'
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>