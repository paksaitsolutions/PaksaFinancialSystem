<template>
  <div class="payslips-view">
    <div class="grid">
      <div class="col-12">
        <div class="flex justify-content-between align-items-center mb-4">
          <h1>Payslips</h1>
          <div class="flex gap-2">
            <Button icon="pi pi-refresh" @click="loadPayslips" :loading="loading" />
            <Button label="Export" icon="pi pi-download" severity="secondary" />
          </div>
        </div>
        
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3>Employee Payslips</h3>
              <div class="flex gap-2">
                <span class="p-input-icon-left">
                  <i class="pi pi-search" />
                  <InputText v-model="search" placeholder="Search payslips" />
                </span>
                <Dropdown 
                  v-model="selectedEmployee" 
                  :options="employees" 
                  optionLabel="full_name" 
                  optionValue="id"
                  placeholder="Filter by Employee"
                  showClear
                  @change="filterByEmployee"
                />
              </div>
            </div>
          </template>
          
          <template #content>
            <DataTable
              :value="payslips"
              :loading="loading"
              :paginator="true"
              :rows="10"
              :globalFilter="search"
              responsiveLayout="scroll"
            >
              <Column field="payslip_number" header="Payslip Number" sortable />
              <Column field="employee.full_name" header="Employee" sortable>
                <template #body="{ data }">
                  {{ getEmployeeName(data.employee_id) }}
                </template>
              </Column>
              <Column field="pay_period_start" header="Pay Period" sortable>
                <template #body="{ data }">
                  {{ formatDate(data.pay_period_start) }} - {{ formatDate(data.pay_period_end) }}
                </template>
              </Column>
              <Column field="pay_date" header="Pay Date" sortable>
                <template #body="{ data }">
                  {{ formatDate(data.pay_date) }}
                </template>
              </Column>
              <Column field="gross_pay" header="Gross Pay" sortable>
                <template #body="{ data }">
                  {{ formatCurrency(data.gross_pay) }}
                </template>
              </Column>
              <Column field="total_deductions" header="Deductions" sortable>
                <template #body="{ data }">
                  {{ formatCurrency(data.total_deductions) }}
                </template>
              </Column>
              <Column field="net_pay" header="Net Pay" sortable>
                <template #body="{ data }">
                  <strong>{{ formatCurrency(data.net_pay) }}</strong>
                </template>
              </Column>
              <Column field="is_paid" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.is_paid ? 'Paid' : 'Pending'" :severity="data.is_paid ? 'success' : 'warning'" />
                </template>
              </Column>
              <Column header="Actions">
                <template #body="{ data }">
                  <div class="flex gap-2">
                    <Button icon="pi pi-eye" size="small" @click="viewPayslip(data)" v-tooltip="'View Details'" />
                    <Button icon="pi pi-download" size="small" severity="secondary" @click="downloadPayslip(data)" v-tooltip="'Download PDF'" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- Payslip Detail Dialog -->
    <Dialog v-model:visible="showDetailDialog" :style="{width: '800px'}" header="Payslip Details" :modal="true">
      <div v-if="selectedPayslip" class="payslip-detail">
        <div class="grid">
          <div class="col-12 md:col-6">
            <h4>Employee Information</h4>
            <p><strong>Name:</strong> {{ getEmployeeName(selectedPayslip.employee_id) }}</p>
            <p><strong>Payslip Number:</strong> {{ selectedPayslip.payslip_number }}</p>
            <p><strong>Pay Period:</strong> {{ formatDate(selectedPayslip.pay_period_start) }} - {{ formatDate(selectedPayslip.pay_period_end) }}</p>
            <p><strong>Pay Date:</strong> {{ formatDate(selectedPayslip.pay_date) }}</p>
          </div>
          
          <div class="col-12 md:col-6">
            <h4>Hours</h4>
            <p><strong>Regular Hours:</strong> {{ selectedPayslip.regular_hours }}</p>
            <p><strong>Overtime Hours:</strong> {{ selectedPayslip.overtime_hours }}</p>
          </div>
        </div>

        <Divider />

        <div class="grid">
          <div class="col-12 md:col-6">
            <h4>Earnings</h4>
            <div class="earning-item">
              <span>Base Salary:</span>
              <span>{{ formatCurrency(selectedPayslip.gross_pay) }}</span>
            </div>
            <div class="earning-item total">
              <span><strong>Gross Pay:</strong></span>
              <span><strong>{{ formatCurrency(selectedPayslip.gross_pay) }}</strong></span>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <h4>Deductions</h4>
            <div class="deduction-item">
              <span>Federal Tax:</span>
              <span>{{ formatCurrency(selectedPayslip.federal_tax) }}</span>
            </div>
            <div class="deduction-item">
              <span>State Tax:</span>
              <span>{{ formatCurrency(selectedPayslip.state_tax) }}</span>
            </div>
            <div class="deduction-item">
              <span>Health Insurance:</span>
              <span>{{ formatCurrency(selectedPayslip.health_insurance) }}</span>
            </div>
            <div class="deduction-item total">
              <span><strong>Total Deductions:</strong></span>
              <span><strong>{{ formatCurrency(selectedPayslip.total_deductions) }}</strong></span>
            </div>
          </div>
        </div>

        <Divider />

        <div class="net-pay-section">
          <div class="flex justify-content-between align-items-center">
            <h3>Net Pay:</h3>
            <h3 class="text-primary">{{ formatCurrency(selectedPayslip.net_pay) }}</h3>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Close" icon="pi pi-times" @click="showDetailDialog = false" class="p-button-text" />
        <Button label="Download PDF" icon="pi pi-download" @click="downloadPayslip(selectedPayslip)" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import payrollService, { type Payslip, type Employee } from '@/services/payrollService'

const toast = useToast()

const loading = ref(false)
const search = ref('')
const selectedEmployee = ref('')
const showDetailDialog = ref(false)
const payslips = ref<Payslip[]>([])
const employees = ref<Employee[]>([])
const selectedPayslip = ref<Payslip | null>(null)

const loadPayslips = async () => {
  loading.value = true
  try {
    const params = selectedEmployee.value ? { employee_id: selectedEmployee.value } : {}
    payslips.value = await payrollService.getPayslips(params)
  } catch (error) {
    console.error('Error loading payslips:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load payslips' })
  } finally {
    loading.value = false
  }
}

const loadEmployees = async () => {
  try {
    employees.value = await payrollService.getEmployees()
  } catch (error) {
    console.error('Error loading employees:', error)
  }
}

const filterByEmployee = () => {
  loadPayslips()
}

const viewPayslip = (payslip: Payslip) => {
  selectedPayslip.value = payslip
  showDetailDialog.value = true
}

const downloadPayslip = (payslip: Payslip) => {
  // Mock PDF download
  toast.add({ 
    severity: 'info', 
    summary: 'Download', 
    detail: `Downloading payslip ${payslip.payslip_number}` 
  })
}

const getEmployeeName = (employeeId: string): string => {
  const employee = employees.value.find(emp => emp.id === employeeId)
  return employee ? employee.full_name : 'Unknown Employee'
}

const formatCurrency = (amount: number): string => {
  return payrollService.formatCurrency(amount)
}

const formatDate = (dateString: string): string => {
  return payrollService.formatDate(dateString)
}

onMounted(() => {
  loadEmployees()
  loadPayslips()
})
</script>

<style scoped>
.payslips-view {
  padding: 1rem;
}

.payslip-detail {
  padding: 1rem 0;
}

.earning-item,
.deduction-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e9ecef;
}

.earning-item.total,
.deduction-item.total {
  border-top: 2px solid #dee2e6;
  border-bottom: 2px solid #dee2e6;
  margin-top: 0.5rem;
}

.net-pay-section {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}
</style>