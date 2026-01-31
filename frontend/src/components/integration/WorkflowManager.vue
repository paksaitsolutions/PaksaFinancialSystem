<template>
  <div class="workflow-manager">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-4">Integrated Workflows</h1>
        </v-col>
      </v-row>
      
      <!-- Workflow Cards -->
      <v-row>
        <v-col cols="12" md="4" v-for="workflow in workflows" :key="workflow.id">
          <v-card @click="openWorkflow(workflow)" class="workflow-card" hover>
            <v-card-text>
              <div class="d-flex align-center mb-3">
                <v-icon :color="workflow.color" size="32" class="mr-3">{{ workflow.icon }}</v-icon>
                <div>
                  <div class="text-h6">{{ workflow.title }}</div>
                  <div class="text-caption text--secondary">{{ workflow.description }}</div>
                </div>
              </div>
              <v-chip :color="workflow.status === 'active' ? 'success' : 'warning'" small>
                {{ workflow.status }}
              </v-chip>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <!-- Workflow Dialog -->
      <v-dialog v-model="workflowDialog" max-width="800px">
        <v-card v-if="selectedWorkflow">
          <v-card-title>{{ selectedWorkflow.title }}</v-card-title>
          <v-card-text>
            <v-form ref="workflowForm" v-model="formValid">
              <div v-if="selectedWorkflow.id === 'purchase-to-payment'">
                <v-text-field
                  v-model="workflowData.bill_number"
                  label="Bill Number"
                  required
                ></v-text-field>
                <v-text-field
                  v-model="workflowData.total_amount"
                  label="Total Amount"
                  type="number"
                  required
                ></v-text-field>
                <v-text-field
                  v-model="workflowData.bill_date"
                  label="Bill Date"
                  type="date"
                  required
                ></v-text-field>
                <v-text-field
                  v-model="workflowData.due_date"
                  label="Due Date"
                  type="date"
                  required
                ></v-text-field>
              </div>
              
              <div v-if="selectedWorkflow.id === 'invoice-to-cash'">
                <v-select
                  v-model="workflowData.customer_id"
                  :items="customers"
                  item-title="name"
                  item-value="id"
                  label="Customer"
                  required
                ></v-select>
                <v-text-field
                  v-model="workflowData.total_amount"
                  label="Total Amount"
                  type="number"
                  required
                ></v-text-field>
                <v-text-field
                  v-model="workflowData.invoice_date"
                  label="Invoice Date"
                  type="date"
                  required
                ></v-text-field>
              </div>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="workflowDialog = false">Cancel</v-btn>
            <v-btn color="primary" @click="processWorkflow" :loading="processing">
              Process Workflow
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      
      <!-- Results Dialog -->
      <v-dialog v-model="resultsDialog" max-width="600px">
        <v-card>
          <v-card-title>Workflow Results</v-card-title>
          <v-card-text>
            <div v-if="workflowResults">
              <v-alert type="success" class="mb-3">
                Workflow {{ workflowResults.workflow_id }} completed successfully!
              </v-alert>
              <v-list>
                <v-list-item v-for="(step, index) in workflowResults.workflow_results" :key="index">
                  <v-list-item-content>
                    <v-list-item-title>Step {{ index + 1 }}: {{ step.step }}</v-list-item-title>
                    <v-list-item-subtitle v-if="step.result">
                      {{ JSON.stringify(step.result, null, 2) }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                  <v-list-item-action>
                    <v-icon color="success">mdi-check</v-icon>
                  </v-list-item-action>
                </v-list-item>
              </v-list>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="resultsDialog = false">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useIntegrationStore } from '@/stores/integration'


/**
 * WorkflowManager Component
 * 
 * @component
 */

export default {
  name: 'WorkflowManager',
  setup() {
    const integrationStore = useIntegrationStore()
    const workflowDialog = ref(false)
    const resultsDialog = ref(false)
    const selectedWorkflow = ref(null)
    const workflowData = ref({})
    const workflowResults = ref(null)
    const formValid = ref(false)
    const processing = ref(false)
    const customers = ref([])
    
    const workflows = ref([
      {
        id: 'purchase-to-payment',
        title: 'Purchase to Payment',
        description: 'Complete P2P workflow from vendor to cash',
        icon: 'mdi-cart-arrow-down',
        color: 'primary',
        status: 'active'
      },
      {
        id: 'invoice-to-cash',
        title: 'Invoice to Cash',
        description: 'Complete I2C workflow from customer to cash',
        icon: 'mdi-receipt-text',
        color: 'success',
        status: 'active'
      },
      {
        id: 'budget-to-actual',
        title: 'Budget to Actual',
        description: 'Budget tracking and variance analysis',
        icon: 'mdi-chart-timeline-variant',
        color: 'warning',
        status: 'active'
      }
    ])
    
    const openWorkflow = (workflow) => {
      selectedWorkflow.value = workflow
      workflowData.value = {}
      workflowDialog.value = true
    }
    
    const processWorkflow = async () => {
      processing.value = true
      try {
        let result
        
        if (selectedWorkflow.value.id === 'purchase-to-payment') {
          result = await integrationStore.processPurchaseToPayment({
            ...workflowData.value,
            bank_account_id: 1,
            vendor_data: {
              name: 'Sample Vendor',
              email: 'vendor@example.com'
            }
          })
        } else if (selectedWorkflow.value.id === 'invoice-to-cash') {
          result = await integrationStore.processInvoiceToCash(workflowData.value)
        }
        
        workflowResults.value = result
        workflowDialog.value = false
        resultsDialog.value = true
      } catch (error) {
        console.error('Workflow processing error:', error)
      } finally {
        processing.value = false
      }
    }
    
    const loadCustomers = async () => {
      // Mock customer data - in real app would load from API
      customers.value = [
        { id: 1, name: 'Customer A' },
        { id: 2, name: 'Customer B' },
        { id: 3, name: 'Customer C' }
      ]
    }
    
    onMounted(() => {
      loadCustomers()
    })
    
    return {
      workflows,
      workflowDialog,
      resultsDialog,
      selectedWorkflow,
      workflowData,
      workflowResults,
      formValid,
      processing,
      customers,
      openWorkflow,
      processWorkflow
    }
  }
}
</script>

<style scoped>
.workflow-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.workflow-card:hover {
  transform: translateY(-2px);
}
</style>