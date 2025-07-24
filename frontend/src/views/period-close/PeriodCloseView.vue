<template>
  <div class="period-close">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center">
              <h2>Period Close Management</h2>
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="openCloseDialog">
                <v-icon left>mdi-calendar-check</v-icon>
                Start Period Close
              </v-btn>
            </v-card-title>

            <v-card-text>
              <!-- Current Period Status -->
              <v-row class="mb-6">
                <v-col cols="12" md="4">
                  <v-card color="primary" dark>
                    <v-card-text class="text-center">
                      <v-icon size="40" class="mb-2">mdi-calendar</v-icon>
                      <div class="text-h6">{{ currentPeriod.name }}</div>
                      <div class="text-caption">Current Period</div>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="12" md="4">
                  <v-card :color="getStatusColor(currentPeriod.status)" dark>
                    <v-card-text class="text-center">
                      <v-icon size="40" class="mb-2">mdi-check-circle</v-icon>
                      <div class="text-h6">{{ formatStatus(currentPeriod.status) }}</div>
                      <div class="text-caption">Status</div>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="12" md="4">
                  <v-card color="info" dark>
                    <v-card-text class="text-center">
                      <v-icon size="40" class="mb-2">mdi-clock</v-icon>
                      <div class="text-h6">{{ formatDate(currentPeriod.end_date) }}</div>
                      <div class="text-caption">Period End</div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Period Close Checklist -->
              <v-card class="mb-6">
                <v-card-title>Period Close Checklist</v-card-title>
                <v-card-text>
                  <v-list>
                    <v-list-item
                      v-for="(task, index) in closeTasks"
                      :key="index"
                      :class="task.completed ? 'text-success' : ''"
                    >
                      <template v-slot:prepend>
                        <v-icon :color="task.completed ? 'success' : 'grey'">
                          {{ task.completed ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                        </v-icon>
                      </template>
                      <v-list-item-title>{{ task.name }}</v-list-item-title>
                      <v-list-item-subtitle>{{ task.description }}</v-list-item-subtitle>
                      <template v-slot:append>
                        <v-btn
                          v-if="!task.completed"
                          size="small"
                          color="primary"
                          @click="completeTask(index)"
                        >
                          Complete
                        </v-btn>
                      </template>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>

              <!-- Period History -->
              <v-card>
                <v-card-title>Period Close History</v-card-title>
                <v-card-text>
                  <v-data-table
                    :headers="historyHeaders"
                    :items="periodHistory"
                    :items-per-page="10"
                  >
                    <template v-slot:item.status="{ item }">
                      <v-chip :color="getStatusColor(item.status)" small>
                        {{ formatStatus(item.status) }}
                      </v-chip>
                    </template>
                    <template v-slot:item.start_date="{ item }">
                      {{ formatDate(item.start_date) }}
                    </template>
                    <template v-slot:item.end_date="{ item }">
                      {{ formatDate(item.end_date) }}
                    </template>
                    <template v-slot:item.closed_date="{ item }">
                      {{ item.closed_date ? formatDate(item.closed_date) : 'N/A' }}
                    </template>
                    <template v-slot:item.actions="{ item }">
                      <v-btn icon small @click="viewPeriodDetails(item)">
                        <v-icon small>mdi-eye</v-icon>
                      </v-btn>
                      <v-btn
                        v-if="item.status === 'closed'"
                        icon
                        small
                        @click="reopenPeriod(item)"
                      >
                        <v-icon small>mdi-lock-open</v-icon>
                      </v-btn>
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Period Close Dialog -->
    <v-dialog v-model="closeDialog" max-width="600px">
      <v-card>
        <v-card-title>Start Period Close Process</v-card-title>
        <v-card-text>
          <v-form ref="closeForm" v-model="closeFormValid">
            <v-row>
              <v-col cols="12">
                <v-select
                  v-model="selectedPeriod"
                  :items="availablePeriods"
                  item-title="name"
                  item-value="id"
                  label="Select Period to Close"
                  :rules="[v => !!v || 'Period is required']"
                ></v-select>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="closeNotes"
                  label="Close Notes"
                  rows="3"
                  placeholder="Enter any notes about this period close..."
                ></v-textarea>
              </v-col>
              <v-col cols="12">
                <v-checkbox
                  v-model="confirmClose"
                  label="I confirm that all transactions have been reviewed and the period is ready to close"
                  :rules="[v => !!v || 'Confirmation is required']"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            @click="startPeriodClose"
            :disabled="!closeFormValid"
            :loading="closing"
          >
            Start Close Process
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: 'PeriodCloseView',
  data: () => ({
    closeDialog: false,
    closeFormValid: false,
    closing: false,
    selectedPeriod: null,
    closeNotes: '',
    confirmClose: false,
    currentPeriod: {
      name: 'January 2024',
      status: 'open',
      end_date: '2024-01-31'
    },
    closeTasks: [
      {
        name: 'Review Journal Entries',
        description: 'Ensure all journal entries are posted and reviewed',
        completed: true
      },
      {
        name: 'Bank Reconciliation',
        description: 'Complete bank reconciliation for all accounts',
        completed: true
      },
      {
        name: 'Accounts Receivable Review',
        description: 'Review and age accounts receivable',
        completed: false
      },
      {
        name: 'Accounts Payable Review',
        description: 'Review outstanding payables and accruals',
        completed: false
      },
      {
        name: 'Fixed Asset Depreciation',
        description: 'Calculate and record depreciation',
        completed: false
      },
      {
        name: 'Inventory Valuation',
        description: 'Review and adjust inventory values',
        completed: false
      },
      {
        name: 'Accruals and Prepayments',
        description: 'Record necessary accruals and prepayments',
        completed: false
      },
      {
        name: 'Trial Balance Review',
        description: 'Review trial balance for accuracy',
        completed: false
      }
    ],
    availablePeriods: [
      { id: 1, name: 'January 2024' },
      { id: 2, name: 'December 2023' },
      { id: 3, name: 'November 2023' }
    ],
    historyHeaders: [
      { title: 'Period', key: 'name' },
      { title: 'Start Date', key: 'start_date' },
      { title: 'End Date', key: 'end_date' },
      { title: 'Status', key: 'status' },
      { title: 'Closed Date', key: 'closed_date' },
      { title: 'Actions', key: 'actions', sortable: false }
    ],
    periodHistory: [
      {
        id: 1,
        name: 'December 2023',
        start_date: '2023-12-01',
        end_date: '2023-12-31',
        status: 'closed',
        closed_date: '2024-01-05'
      },
      {
        id: 2,
        name: 'November 2023',
        start_date: '2023-11-01',
        end_date: '2023-11-30',
        status: 'closed',
        closed_date: '2023-12-03'
      },
      {
        id: 3,
        name: 'October 2023',
        start_date: '2023-10-01',
        end_date: '2023-10-31',
        status: 'closed',
        closed_date: '2023-11-02'
      }
    ]
  }),

  methods: {
    openCloseDialog() {
      this.closeDialog = true
    },

    async startPeriodClose() {
      if (!this.$refs.closeForm.validate()) return

      this.closing = true
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        this.closeDialog = false
        this.currentPeriod.status = 'closing'
        
        // Show success message
        this.$emit('show-snackbar', 'Period close process started successfully', 'success')
      } catch (error) {
        console.error('Error starting period close:', error)
        this.$emit('show-snackbar', 'Error starting period close', 'error')
      } finally {
        this.closing = false
      }
    },

    completeTask(index) {
      this.closeTasks[index].completed = true
    },

    viewPeriodDetails(period) {
      console.log('View period details:', period)
    },

    async reopenPeriod(period) {
      if (confirm(`Are you sure you want to reopen ${period.name}?`)) {
        try {
          // Simulate API call
          await new Promise(resolve => setTimeout(resolve, 1000))
          period.status = 'open'
          this.$emit('show-snackbar', 'Period reopened successfully', 'success')
        } catch (error) {
          console.error('Error reopening period:', error)
          this.$emit('show-snackbar', 'Error reopening period', 'error')
        }
      }
    },

    getStatusColor(status) {
      const colors = {
        open: 'success',
        closing: 'warning',
        closed: 'error',
        locked: 'grey'
      }
      return colors[status] || 'grey'
    },

    formatStatus(status) {
      return status.charAt(0).toUpperCase() + status.slice(1)
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.period-close {
  padding: 16px;
}
</style>