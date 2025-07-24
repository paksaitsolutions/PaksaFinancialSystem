<template>
  <div class="payroll-processing">
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Payroll Processing</h2>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="openCreateRunDialog">
          <v-icon left>mdi-plus</v-icon>
          New Payroll Run
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="payrollRuns"
          :loading="loading"
          :items-per-page="10"
        >
          <template v-slot:item.status="{ item }">
            <v-chip
              :color="getStatusColor(item.status)"
              small
            >
              {{ item.status }}
            </v-chip>
          </template>
          
          <template v-slot:item.total_gross_pay="{ item }">
            {{ formatCurrency(item.total_gross_pay) }}
          </template>
          
          <template v-slot:item.total_net_pay="{ item }">
            {{ formatCurrency(item.total_net_pay) }}
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn icon small @click="viewPayrollRun(item)" v-if="item.status === 'DRAFT'">
              <v-icon small>mdi-calculator</v-icon>
            </v-btn>
            <v-btn icon small @click="processPayroll(item)" v-if="item.status === 'DRAFT'">
              <v-icon small>mdi-play</v-icon>
            </v-btn>
            <v-btn icon small @click="approvePayroll(item)" v-if="item.status === 'PROCESSING'">
              <v-icon small>mdi-check</v-icon>
            </v-btn>
            <v-btn icon small @click="viewPayslips(item)">
              <v-icon small>mdi-file-document</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Create Payroll Run Dialog -->
    <v-dialog v-model="createRunDialog" max-width="600px">
      <v-card>
        <v-card-title>Create New Payroll Run</v-card-title>
        <v-card-text>
          <v-form ref="createForm" v-model="createFormValid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="newRun.pay_period_start"
                  label="Pay Period Start"
                  type="date"
                  :rules="[v => !!v || 'Start date is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="newRun.pay_period_end"
                  label="Pay Period End"
                  type="date"
                  :rules="[v => !!v || 'End date is required']"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="newRun.pay_date"
                  label="Pay Date"
                  type="date"
                  :rules="[v => !!v || 'Pay date is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="newRun.department"
                  :items="departments"
                  label="Department (Optional)"
                  clearable
                ></v-select>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="newRun.description"
                  label="Description (Optional)"
                  rows="3"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="createRunDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="createPayrollRun" :disabled="!createFormValid">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Payroll Calculation Dialog -->
    <v-dialog v-model="calculationDialog" max-width="800px">
      <v-card>
        <v-card-title>Calculate Payroll</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <h3>Select Employees</h3>
              <v-data-table
                v-model="selectedEmployees"
                :headers="employeeHeaders"
                :items="employees"
                :loading="employeesLoading"
                show-select
                item-key="id"
              >
                <template v-slot:item.base_salary="{ item }">
                  {{ formatCurrency(item.base_salary) }}
                </template>
              </v-data-table>
            </v-col>
          </v-row>
          
          <v-row class="mt-4">
            <v-col cols="12" md="6">
              <v-checkbox
                v-model="calculationOptions.include_overtime"
                label="Include Overtime"
              ></v-checkbox>
            </v-col>
            <v-col cols="12" md="6">
              <v-checkbox
                v-model="calculationOptions.include_bonus"
                label="Include Bonus"
              ></v-checkbox>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="calculationDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="calculatePayroll" :disabled="selectedEmployees.length === 0">Calculate</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Calculation Results Dialog -->
    <v-dialog v-model="resultsDialog" max-width="1000px">
      <v-card>
        <v-card-title>Payroll Calculation Results</v-card-title>
        <v-card-text>
          <v-data-table
            :headers="resultsHeaders"
            :items="calculationResults"
            :loading="calculationLoading"
          >
            <template v-slot:item.basic_salary="{ item }">
              {{ formatCurrency(item.basic_salary) }}
            </template>
            <template v-slot:item.gross_pay="{ item }">
              {{ formatCurrency(item.gross_pay) }}
            </template>
            <template v-slot:item.net_pay="{ item }">
              {{ formatCurrency(item.net_pay) }}
            </template>
          </v-data-table>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="resultsDialog = false">Cancel</v-btn>
          <v-btn color="success" @click="processCalculatedPayroll">Process Payroll</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: 'PayrollProcessing',
  data: () => ({
    loading: false,
    employeesLoading: false,
    calculationLoading: false,
    createRunDialog: false,
    calculationDialog: false,
    resultsDialog: false,
    createFormValid: false,
    payrollRuns: [],
    employees: [],
    selectedEmployees: [],
    calculationResults: [],
    currentPayrollRun: null,
    departments: ['HR', 'Finance', 'IT', 'Marketing', 'Operations', 'Sales'],
    newRun: {
      pay_period_start: '',
      pay_period_end: '',
      pay_date: '',
      department: null,
      description: ''
    },
    calculationOptions: {
      include_overtime: true,
      include_bonus: true
    },
    headers: [
      { title: 'Period', key: 'pay_period_start' },
      { title: 'Pay Date', key: 'pay_date' },
      { title: 'Status', key: 'status' },
      { title: 'Employees', key: 'employee_count' },
      { title: 'Gross Pay', key: 'total_gross_pay' },
      { title: 'Net Pay', key: 'total_net_pay' },
      { title: 'Actions', key: 'actions', sortable: false }
    ],
    employeeHeaders: [
      { title: 'ID', key: 'employee_id' },
      { title: 'Name', key: 'full_name' },
      { title: 'Department', key: 'department' },
      { title: 'Base Salary', key: 'base_salary' }
    ],
    resultsHeaders: [
      { title: 'Employee', key: 'employee_name' },
      { title: 'Basic Salary', key: 'basic_salary' },
      { title: 'Gross Pay', key: 'gross_pay' },
      { title: 'Deductions', key: 'total_deductions' },
      { title: 'Net Pay', key: 'net_pay' }
    ]
  }),

  mounted() {
    this.fetchPayrollRuns()
    this.fetchEmployees()
  },

  methods: {
    async fetchPayrollRuns() {
      this.loading = true
      try {
        const response = await fetch('/api/payroll/payroll-processing/runs')
        const data = await response.json()
        this.payrollRuns = data.items
      } catch (error) {
        console.error('Error fetching payroll runs:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchEmployees() {
      this.employeesLoading = true
      try {
        const response = await fetch('/api/payroll/employees?is_active=true')
        const data = await response.json()
        this.employees = data.items
      } catch (error) {
        console.error('Error fetching employees:', error)
      } finally {
        this.employeesLoading = false
      }
    },

    openCreateRunDialog() {
      this.newRun = {
        pay_period_start: '',
        pay_period_end: '',
        pay_date: '',
        department: null,
        description: ''
      }
      this.createRunDialog = true
    },

    async createPayrollRun() {
      if (this.$refs.createForm.validate()) {
        try {
          const response = await fetch('/api/payroll/payroll-processing/runs', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(this.newRun)
          })
          
          if (response.ok) {
            this.createRunDialog = false
            this.fetchPayrollRuns()
          }
        } catch (error) {
          console.error('Error creating payroll run:', error)
        }
      }
    },

    viewPayrollRun(payrollRun) {
      this.currentPayrollRun = payrollRun
      this.selectedEmployees = []
      this.calculationDialog = true
    },

    async calculatePayroll() {
      if (this.selectedEmployees.length === 0) return
      
      this.calculationLoading = true
      try {
        const response = await fetch(`/api/payroll/payroll-processing/runs/${this.currentPayrollRun.id}/calculate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            employee_ids: this.selectedEmployees.map(emp => emp.id),
            pay_period_start: this.currentPayrollRun.pay_period_start,
            pay_period_end: this.currentPayrollRun.pay_period_end,
            include_overtime: this.calculationOptions.include_overtime,
            include_bonus: this.calculationOptions.include_bonus
          })
        })
        
        if (response.ok) {
          this.calculationResults = await response.json()
          this.calculationDialog = false
          this.resultsDialog = true
        }
      } catch (error) {
        console.error('Error calculating payroll:', error)
      } finally {
        this.calculationLoading = false
      }
    },

    async processCalculatedPayroll() {
      try {
        const payslipsData = this.calculationResults.map(result => ({
          employee_id: result.employee_id,
          payroll_run_id: this.currentPayrollRun.id,
          gross_pay: result.gross_pay,
          basic_salary: result.basic_salary,
          overtime_pay: result.overtime_pay,
          bonus: result.bonus,
          allowances: result.allowances,
          deductions: result.deductions,
          tax_deductions: result.tax_deductions,
          net_pay: result.net_pay
        }))

        const response = await fetch(`/api/payroll/payroll-processing/runs/${this.currentPayrollRun.id}/process`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payslipsData)
        })
        
        if (response.ok) {
          this.resultsDialog = false
          this.fetchPayrollRuns()
        }
      } catch (error) {
        console.error('Error processing payroll:', error)
      }
    },

    async approvePayroll(payrollRun) {
      try {
        const response = await fetch(`/api/payroll/payroll-processing/runs/${payrollRun.id}/approve`, {
          method: 'POST'
        })
        
        if (response.ok) {
          this.fetchPayrollRuns()
        }
      } catch (error) {
        console.error('Error approving payroll:', error)
      }
    },

    viewPayslips(payrollRun) {
      this.$router.push(`/payroll/payslips?run=${payrollRun.id}`)
    },

    getStatusColor(status) {
      const colors = {
        'DRAFT': 'grey',
        'PROCESSING': 'orange',
        'COMPLETED': 'blue',
        'APPROVED': 'green',
        'PAID': 'success',
        'CANCELLED': 'error'
      }
      return colors[status] || 'grey'
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }
  }
}
</script>

<style scoped>
.payroll-processing {
  padding: 16px;
}
</style>