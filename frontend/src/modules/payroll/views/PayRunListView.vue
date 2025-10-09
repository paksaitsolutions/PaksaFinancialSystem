<template>
  <div class="pay-run-list">
    <div class="grid">
      <div class="col-12">
        <div class="flex justify-content-between align-items-center mb-4">
          <h1>Pay Runs</h1>
          <Button label="Create Pay Run" icon="pi pi-plus" @click="showCreateDialog = true" />
        </div>
        
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3>Pay Runs</h3>
              <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText v-model="search" placeholder="Search pay runs" />
              </span>
            </div>
          </template>
          
          <template #content>
            <DataTable
              :value="payRuns"
              :loading="loading"
              :paginator="true"
              :rows="10"
              :globalFilter="search"
              responsiveLayout="scroll"
            >
              <Column field="run_number" header="Run Number" sortable />
              <Column field="pay_period_start" header="Period Start" sortable>
                <template #body="{ data }">
                  {{ formatDate(data.pay_period_start) }}
                </template>
              </Column>
              <Column field="pay_period_end" header="Period End" sortable>
                <template #body="{ data }">
                  {{ formatDate(data.pay_period_end) }}
                </template>
              </Column>
              <Column field="pay_date" header="Pay Date" sortable>
                <template #body="{ data }">
                  {{ formatDate(data.pay_date) }}
                </template>
              </Column>
              <Column field="status" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.status.toUpperCase()" :severity="getStatusColor(data.status)" />
                </template>
              </Column>
              <Column field="total_net_pay" header="Total Net Pay">
                <template #body="{ data }">
                  {{ formatCurrency(data.total_net_pay) }}
                </template>
              </Column>
              <Column header="Actions">
                <template #body="{ data }">
                  <div class="flex gap-2">
                    <Button icon="pi pi-eye" size="small" @click="viewPayRun(data)" v-tooltip="'View Details'" />
                    <Button 
                      icon="pi pi-play" 
                      size="small" 
                      severity="warning"
                      @click="processPayRun(data)"
                      :disabled="data.status !== 'draft'"
                      v-tooltip="'Process Pay Run'"
                    />
                    <Button 
                      icon="pi pi-check" 
                      size="small" 
                      severity="success"
                      @click="approvePayRun(data)"
                      :disabled="data.status !== 'processing'"
                      v-tooltip="'Approve Pay Run'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>
    
    <!-- Create Pay Run Dialog -->
    <Dialog v-model:visible="showCreateDialog" :style="{width: '600px'}" header="Create New Pay Run" :modal="true">
      <div class="grid p-fluid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="pay_period_start">Pay Period Start *</label>
            <Calendar id="pay_period_start" v-model="newPayRun.pay_period_start" dateFormat="yy-mm-dd" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="pay_period_end">Pay Period End *</label>
            <Calendar id="pay_period_end" v-model="newPayRun.pay_period_end" dateFormat="yy-mm-dd" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="pay_date">Pay Date *</label>
            <Calendar id="pay_date" v-model="newPayRun.pay_date" dateFormat="yy-mm-dd" />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" @click="showCreateDialog = false" class="p-button-text" />
        <Button label="Create" icon="pi pi-check" @click="createPayRun" :loading="creating" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useRouter } from 'vue-router'
import payrollService, { type PayRun } from '@/services/payrollService'

const toast = useToast()
const router = useRouter()

const loading = ref(false)
const creating = ref(false)
const search = ref('')
const showCreateDialog = ref(false)
const payRuns = ref<PayRun[]>([])

const newPayRun = ref({
  pay_period_start: new Date(),
  pay_period_end: new Date(),
  pay_date: new Date()
})

const loadPayRuns = async () => {
  loading.value = true
  try {
    payRuns.value = await payrollService.getPayRuns()
  } catch (error) {
    console.error('Error loading pay runs:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load pay runs' })
  } finally {
    loading.value = false
  }
}

const createPayRun = async () => {
  creating.value = true
  try {
    const data = {
      pay_period_start: newPayRun.value.pay_period_start.toISOString().split('T')[0],
      pay_period_end: newPayRun.value.pay_period_end.toISOString().split('T')[0],
      pay_date: newPayRun.value.pay_date.toISOString().split('T')[0]
    }
    
    await payrollService.createPayRun(data)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Pay run created successfully' })
    showCreateDialog.value = false
    await loadPayRuns()
  } catch (error) {
    console.error('Error creating pay run:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create pay run' })
  } finally {
    creating.value = false
  }
}

const processPayRun = async (payRun: PayRun) => {
  try {
    await payrollService.processPayRun(payRun.id)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Pay run processed successfully' })
    await loadPayRuns()
  } catch (error) {
    console.error('Error processing pay run:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to process pay run' })
  }
}

const approvePayRun = async (payRun: PayRun) => {
  try {
    await payrollService.approvePayRun(payRun.id)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Pay run approved successfully' })
    await loadPayRuns()
  } catch (error) {
    console.error('Error approving pay run:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to approve pay run' })
  }
}

const viewPayRun = (payRun: PayRun) => {
  router.push(`/payroll/pay-runs/${payRun.id}`)
}

const getStatusColor = (status: string): string => {
  return payrollService.getStatusColor(status)
}

const formatCurrency = (amount: number): string => {
  return payrollService.formatCurrency(amount)
}

const formatDate = (dateString: string): string => {
  return payrollService.formatDate(dateString)
}

onMounted(() => {
  loadPayRuns()
})
</script>