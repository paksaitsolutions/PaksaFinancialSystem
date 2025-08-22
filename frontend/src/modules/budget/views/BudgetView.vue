<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Budget Management</h2>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="openCreateDialog">
          <v-icon left>mdi-plus</v-icon>
          New Budget
        </v-btn>
      </v-card-title>

      <v-card-text>
        <!-- Filters -->
        <v-row class="mb-4">
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filters.search"
              label="Search"
              prepend-inner-icon="mdi-magnify"
              clearable
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.status"
              :items="budgetStatuses"
              label="Status"
              clearable
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.type"
              :items="budgetTypes"
              label="Type"
              clearable
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-btn variant="outlined" @click="clearFilters" block>
              Clear Filters
            </v-btn>
          </v-col>
        </v-row>

        <!-- Budget Table -->
        <v-data-table
          :headers="headers"
          :items="filteredBudgets"
          :loading="loading"
          :items-per-page="10"
        >
          <template v-slot:item.name="{ item }">
            <a href="#" @click.prevent="openEditDialog(item)" class="text-primary">
              {{ item.name }}
            </a>
          </template>
          
          <template v-slot:item.amount="{ item }">
            {{ formatCurrency(item.amount) }}
          </template>
          
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" small>
              {{ item.status }}
            </v-chip>
          </template>
          
          <template v-slot:item.type="{ item }">
            <v-chip variant="outlined" small>
              {{ item.type }}
            </v-chip>
          </template>
          
          <template v-slot:item.startDate="{ item }">
            {{ formatDate(item.startDate) }}
          </template>
          
          <template v-slot:item.endDate="{ item }">
            {{ formatDate(item.endDate) }}
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn icon small @click="openEditDialog(item)">
              <v-icon small>mdi-pencil</v-icon>
            </v-btn>
            <v-btn 
              v-if="item.status === 'PENDING_APPROVAL'" 
              icon 
              small 
              color="success"
              @click="openApprovalDialog(item)"
            >
              <v-icon small>mdi-check</v-icon>
            </v-btn>
            <v-btn 
              v-if="item.status === 'PENDING_APPROVAL'" 
              icon 
              small 
              color="warning"
              @click="openRejectDialog(item)"
            >
              <v-icon small>mdi-close</v-icon>
            </v-btn>
            <v-btn icon small color="error" @click="confirmDelete(item.id)">
              <v-icon small>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Budget Form Dialog -->
    <v-dialog v-model="dialog.visible" max-width="800px">
      <v-card>
        <v-card-title>{{ dialog.mode === 'create' ? 'New Budget' : 'Edit Budget' }}</v-card-title>
        <v-card-text>
          <BudgetForm 
            v-if="dialog.visible"
            :budget="dialog.budget"
            :loading="dialog.loading"
            @submit="handleSave"
            @cancel="dialog.visible = false"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Approval Dialog -->
    <v-dialog v-model="approvalDialog.visible" max-width="500px">
      <v-card>
        <v-card-title>Approve Budget</v-card-title>
        <v-card-text>
          <p>Are you sure you want to approve this budget?</p>
          <v-textarea
            v-model="approvalNotes"
            label="Approval Notes (Optional)"
            rows="3"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="approvalDialog.visible = false" :disabled="approvalDialog.loading">
            Cancel
          </v-btn>
          <v-btn color="success" @click="handleApproval" :loading="approvalDialog.loading">
            Approve
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Reject Dialog -->
    <v-dialog v-model="rejectDialog.visible" max-width="500px">
      <v-card>
        <v-card-title>Reject Budget</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="rejectNotes"
            label="Reason for rejection"
            rows="3"
            :rules="[v => !!v || 'Reason is required']"
            required
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="rejectDialog.visible = false" :disabled="rejectDialog.loading">
            Cancel
          </v-btn>
          <v-btn color="error" @click="handleReject" :loading="rejectDialog.loading">
            Reject
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import BudgetForm from '../components/BudgetForm.vue'
import { useBudgetStore } from '../store/budget'

export default {
  name: 'BudgetView',
  components: {
    ResponsiveContainer,
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
    
    getStatusColor(status) {
      const colors = {
        DRAFT: 'grey',
        PENDING_APPROVAL: 'orange',
        APPROVED: 'success',
        REJECTED: 'error',
        ARCHIVED: 'secondary'
      }
      return colors[status] || 'grey'
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