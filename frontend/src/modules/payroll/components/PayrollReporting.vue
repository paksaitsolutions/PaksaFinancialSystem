<template>
  <div class="payroll-reporting">
    <v-card>
      <v-card-title>
        <h2>Payroll Reports</h2>
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedReportType"
              :items="reportTypes"
              item-title="name"
              item-value="type"
              label="Report Type"
              @update:modelValue="onReportTypeChange"
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="startDate"
              label="Start Date"
              type="date"
              v-if="selectedReportType !== 'YEAR_END_SUMMARY'"
            ></v-text-field>
            <v-text-field
              v-model="selectedYear"
              label="Year"
              type="number"
              v-else
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="3" v-if="selectedReportType !== 'YEAR_END_SUMMARY'">
            <v-text-field
              v-model="endDate"
              label="End Date"
              type="date"
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="2">
            <v-btn
              color="primary"
              @click="generateReport"
              :loading="loading"
              :disabled="!canGenerateReport"
              block
            >
              Generate Report
            </v-btn>
          </v-col>
        </v-row>

        <!-- Additional Filters -->
        <v-row v-if="selectedReportType === 'PAYROLL_SUMMARY'">
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedDepartment"
              :items="departments"
              label="Department (Optional)"
              clearable
            ></v-select>
          </v-col>
        </v-row>

        <v-row v-if="selectedReportType === 'EMPLOYEE_EARNINGS'">
          <v-col cols="12" md="6">
            <v-select
              v-model="selectedEmployees"
              :items="employees"
              item-title="full_name"
              item-value="id"
              label="Employees (Optional)"
              multiple
              clearable
            ></v-select>
          </v-col>
        </v-row>

        <!-- Report Results -->
        <v-divider class="my-6"></v-divider>

        <!-- Payroll Summary Report -->
        <div v-if="reportData && selectedReportType === 'PAYROLL_SUMMARY'">
          <h3>Payroll Summary Report</h3>
          <p class="text-subtitle-1">{{ formatDate(reportData.period_start) }} - {{ formatDate(reportData.period_end) }}</p>
          
          <v-row class="mt-4">
            <v-col cols="12" md="3">
              <v-card class="text-center pa-4" color="blue lighten-5">
                <h2>{{ reportData.total_employees }}</h2>
                <p>Total Employees</p>
              </v-card>
            </v-col>
            <v-col cols="12" md="3">
              <v-card class="text-center pa-4" color="green lighten-5">
                <h2>{{ formatCurrency(reportData.total_gross_pay) }}</h2>
                <p>Total Gross Pay</p>
              </v-card>
            </v-col>
            <v-col cols="12" md="3">
              <v-card class="text-center pa-4" color="orange lighten-5">
                <h2>{{ formatCurrency(reportData.total_taxes) }}</h2>
                <p>Total Taxes</p>
              </v-card>
            </v-col>
            <v-col cols="12" md="3">
              <v-card class="text-center pa-4" color="purple lighten-5">
                <h2>{{ formatCurrency(reportData.total_net_pay) }}</h2>
                <p>Total Net Pay</p>
              </v-card>
            </v-col>
          </v-row>

          <v-card class="mt-4">
            <v-card-title>Department Breakdown</v-card-title>
            <v-card-text>
              <v-data-table
                :headers="departmentHeaders"
                :items="Object.entries(reportData.by_department).map(([dept, data]) => ({department: dept, ...data}))"
                hide-default-footer
              >
                <template v-slot:item.gross_pay="{ item }">
                  {{ formatCurrency(item.gross_pay) }}
                </template>
                <template v-slot:item.net_pay="{ item }">
                  {{ formatCurrency(item.net_pay) }}
                </template>
                <template v-slot:item.taxes="{ item }">
                  {{ formatCurrency(item.taxes) }}
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </div>

        <!-- Employee Earnings Report -->
        <div v-if="reportData && selectedReportType === 'EMPLOYEE_EARNINGS'">
          <h3>Employee Earnings Report</h3>
          
          <v-data-table
            :headers="earningsHeaders"
            :items="reportData"
            :items-per-page="10"
          >
            <template v-slot:item.total_gross="{ item }">
              {{ formatCurrency(item.total_gross) }}
            </template>
            <template v-slot:item.total_net="{ item }">
              {{ formatCurrency(item.total_net) }}
            </template>
            <template v-slot:item.total_taxes="{ item }">
              {{ formatCurrency(item.total_taxes) }}
            </template>
            <template v-slot:item.total_benefits="{ item }">
              {{ formatCurrency(item.total_benefits) }}
            </template>
          </v-data-table>
        </div>

        <!-- Tax Liability Report -->
        <div v-if="reportData && selectedReportType === 'TAX_LIABILITY'">
          <h3>Tax Liability Report</h3>
          <p class="text-subtitle-1">{{ formatDate(reportData.period_start) }} - {{ formatDate(reportData.period_end) }}</p>
          
          <v-row class="mt-4">
            <v-col cols="12" md="4">
              <v-card class="pa-4">
                <h4>Federal Income Tax</h4>
                <h2 class="text-primary">{{ formatCurrency(reportData.federal_income_tax) }}</h2>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card class="pa-4">
                <h4>State Income Tax</h4>
                <h2 class="text-success">{{ formatCurrency(reportData.state_income_tax) }}</h2>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card class="pa-4">
                <h4>Social Security Tax</h4>
                <h2 class="text-warning">{{ formatCurrency(reportData.social_security_tax) }}</h2>
              </v-card>
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="4">
              <v-card class="pa-4">
                <h4>Medicare Tax</h4>
                <h2 class="text-info">{{ formatCurrency(reportData.medicare_tax) }}</h2>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card class="pa-4">
                <h4>Unemployment Tax</h4>
                <h2 class="text-secondary">{{ formatCurrency(reportData.unemployment_tax) }}</h2>
              </v-card>
            </v-col>
            <v-col cols="12" md="4">
              <v-card class="pa-4" color="red lighten-5">
                <h4>Total Tax Liability</h4>
                <h2 class="text-error">{{ formatCurrency(reportData.total_tax_liability) }}</h2>
              </v-card>
            </v-col>
          </v-row>
        </div>

        <!-- Benefits Report -->
        <div v-if="reportData && selectedReportType === 'BENEFITS_REPORT'">
          <h3>Benefits Report</h3>
          <p class="text-subtitle-1">{{ formatDate(reportData.period_start) }} - {{ formatDate(reportData.period_end) }}</p>
          
          <v-row class="mt-4">
            <v-col cols="12" md="6">
              <v-card class="text-center pa-4" color="blue lighten-5">
                <h2>{{ formatCurrency(reportData.total_employee_contributions) }}</h2>
                <p>Employee Contributions</p>
              </v-card>
            </v-col>
            <v-col cols="12" md="6">
              <v-card class="text-center pa-4" color="green lighten-5">
                <h2>{{ formatCurrency(reportData.total_employer_contributions) }}</h2>
                <p>Employer Contributions</p>
              </v-card>
            </v-col>
          </v-row>

          <v-card class="mt-4">
            <v-card-title>Benefits by Type</v-card-title>
            <v-card-text>
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th>Benefit Type</th>
                      <th class="text-right">Enrollments</th>
                      <th class="text-right">Employee Contributions</th>
                      <th class="text-right">Employer Contributions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(data, type) in reportData.by_benefit_type" :key="type">
                      <td>{{ formatBenefitType(type) }}</td>
                      <td class="text-right">{{ data.enrollment_count }}</td>
                      <td class="text-right">{{ formatCurrency(data.employee_contributions) }}</td>
                      <td class="text-right">{{ formatCurrency(data.employer_contributions) }}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-card-text>
          </v-card>
        </div>

        <!-- Department Costs Report -->
        <div v-if="reportData && selectedReportType === 'DEPARTMENT_COSTS'">
          <h3>Department Costs Report</h3>
          <p class="text-subtitle-1">{{ formatDate(reportData.period_start) }} - {{ formatDate(reportData.period_end) }}</p>
          
          <v-card class="mt-4">
            <v-card-title>
              Department Costs
              <v-spacer></v-spacer>
              <v-chip color="primary" large>
                Total: {{ formatCurrency(reportData.total_cost) }}
              </v-chip>
            </v-card-title>
            <v-card-text>
              <v-data-table
                :headers="departmentCostHeaders"
                :items="reportData.departments"
                hide-default-footer
              >
                <template v-slot:item.gross_pay="{ item }">
                  {{ formatCurrency(item.gross_pay) }}
                </template>
                <template v-slot:item.taxes="{ item }">
                  {{ formatCurrency(item.taxes) }}
                </template>
                <template v-slot:item.benefits="{ item }">
                  {{ formatCurrency(item.benefits) }}
                </template>
                <template v-slot:item.total_cost="{ item }">
                  <strong>{{ formatCurrency(item.total_cost) }}</strong>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </div>

        <!-- Year-End Summary -->
        <div v-if="reportData && selectedReportType === 'YEAR_END_SUMMARY'">
          <h3>Year-End Summary {{ reportData.year }}</h3>
          
          <v-row class="mt-4">
            <v-col cols="12" md="3">
              <v-card class="text-center pa-4" color="blue lighten-5">
                <h2>{{ reportData.total_employees }}</h2>
                <p>Total Employees</p>
              </v-card>
            </v-col>
            <v-col cols="12" md="3">
              <v-card class="text-center pa-4" color="green lighten-5">
                <h2>{{ formatCurrency(reportData.total_gross_pay) }}</h2>
                <p>Total Gross Pay</p>
              </v-card>
            </v-col>
            <v-col cols="12" md="3">
              <v-card class="text-center pa-4" color="orange lighten-5">
                <h2>{{ formatCurrency(reportData.total_taxes) }}</h2>
                <p>Total Taxes</p>
              </v-card>
            </v-col>
            <v-col cols="12" md="3">
              <v-card class="text-center pa-4" color="purple lighten-5">
                <h2>{{ formatCurrency(reportData.total_net_pay) }}</h2>
                <p>Total Net Pay</p>
              </v-card>
            </v-col>
          </v-row>

          <v-card class="mt-4">
            <v-card-title>Quarterly Breakdown</v-card-title>
            <v-card-text>
              <v-data-table
                :headers="quarterlyHeaders"
                :items="reportData.quarterly_breakdown"
                hide-default-footer
              >
                <template v-slot:item.gross_pay="{ item }">
                  {{ formatCurrency(item.gross_pay) }}
                </template>
                <template v-slot:item.net_pay="{ item }">
                  {{ formatCurrency(item.net_pay) }}
                </template>
                <template v-slot:item.taxes="{ item }">
                  {{ formatCurrency(item.taxes) }}
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>

          <v-card class="mt-4">
            <v-card-title>Top Earners</v-card-title>
            <v-card-text>
              <v-data-table
                :headers="topEarnersHeaders"
                :items="reportData.top_earners"
                hide-default-footer
              >
                <template v-slot:item.total_gross="{ item }">
                  {{ formatCurrency(item.total_gross) }}
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'PayrollReporting',
  data: () => ({
    loading: false,
    selectedReportType: 'PAYROLL_SUMMARY',
    startDate: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().substr(0, 10),
    endDate: new Date().toISOString().substr(0, 10),
    selectedYear: new Date().getFullYear(),
    selectedDepartment: null,
    selectedEmployees: [],
    reportData: null,
    employees: [],
    departments: ['HR', 'Finance', 'IT', 'Marketing', 'Operations', 'Sales'],
    reportTypes: [
      { type: 'PAYROLL_SUMMARY', name: 'Payroll Summary', description: 'Overall payroll summary with department breakdown' },
      { type: 'EMPLOYEE_EARNINGS', name: 'Employee Earnings', description: 'Detailed earnings report by employee' },
      { type: 'TAX_LIABILITY', name: 'Tax Liability', description: 'Tax liability breakdown by type' },
      { type: 'BENEFITS_REPORT', name: 'Benefits Report', description: 'Employee benefits contributions and costs' },
      { type: 'DEPARTMENT_COSTS', name: 'Department Costs', description: 'Payroll costs breakdown by department' },
      { type: 'YEAR_END_SUMMARY', name: 'Year-End Summary', description: 'Annual payroll summary with quarterly breakdown' }
    ],
    departmentHeaders: [
      { title: 'Department', key: 'department' },
      { title: 'Employees', key: 'employee_count' },
      { title: 'Gross Pay', key: 'gross_pay' },
      { title: 'Net Pay', key: 'net_pay' },
      { title: 'Taxes', key: 'taxes' }
    ],
    earningsHeaders: [
      { title: 'Employee', key: 'employee_name' },
      { title: 'Code', key: 'employee_code' },
      { title: 'Department', key: 'department' },
      { title: 'Gross Pay', key: 'total_gross' },
      { title: 'Net Pay', key: 'total_net' },
      { title: 'Taxes', key: 'total_taxes' },
      { title: 'Benefits', key: 'total_benefits' }
    ],
    departmentCostHeaders: [
      { title: 'Department', key: 'department' },
      { title: 'Employees', key: 'employee_count' },
      { title: 'Gross Pay', key: 'gross_pay' },
      { title: 'Taxes', key: 'taxes' },
      { title: 'Benefits', key: 'benefits' },
      { title: 'Total Cost', key: 'total_cost' }
    ],
    quarterlyHeaders: [
      { title: 'Quarter', key: 'quarter' },
      { title: 'Gross Pay', key: 'gross_pay' },
      { title: 'Net Pay', key: 'net_pay' },
      { title: 'Taxes', key: 'taxes' }
    ],
    topEarnersHeaders: [
      { title: 'Employee', key: 'employee_name' },
      { title: 'Code', key: 'employee_code' },
      { title: 'Department', key: 'department' },
      { title: 'Total Gross', key: 'total_gross' }
    ]
  }),

  computed: {
    canGenerateReport() {
      if (this.selectedReportType === 'YEAR_END_SUMMARY') {
        return this.selectedYear && this.selectedYear > 2000
      }
      return this.startDate && this.endDate && this.startDate <= this.endDate
    }
  },

  mounted() {
    this.fetchEmployees()
  },

  methods: {
    async fetchEmployees() {
      try {
        const response = await fetch('/api/payroll/employees?is_active=true')
        const data = await response.json()
        this.employees = data.items
      } catch (error) {
        console.error('Error fetching employees:', error)
      }
    },

    onReportTypeChange() {
      this.reportData = null
    },

    async generateReport() {
      if (!this.canGenerateReport) return

      this.loading = true
      try {
        let url = `/api/payroll/payroll-reports/${this.getReportEndpoint()}`
        const params = new URLSearchParams()

        if (this.selectedReportType === 'YEAR_END_SUMMARY') {
          params.append('year', this.selectedYear.toString())
        } else {
          params.append('start_date', this.startDate)
          params.append('end_date', this.endDate)
        }

        if (this.selectedReportType === 'PAYROLL_SUMMARY' && this.selectedDepartment) {
          params.append('department', this.selectedDepartment)
        }

        if (this.selectedReportType === 'EMPLOYEE_EARNINGS' && this.selectedEmployees.length > 0) {
          params.append('employee_ids', this.selectedEmployees.join(','))
        }

        const response = await fetch(`${url}?${params}`)
        if (response.ok) {
          this.reportData = await response.json()
        }
      } catch (error) {
        console.error('Error generating report:', error)
      } finally {
        this.loading = false
      }
    },

    getReportEndpoint() {
      const endpoints = {
        'PAYROLL_SUMMARY': 'payroll-summary',
        'EMPLOYEE_EARNINGS': 'employee-earnings',
        'TAX_LIABILITY': 'tax-liability',
        'BENEFITS_REPORT': 'benefits',
        'DEPARTMENT_COSTS': 'department-costs',
        'YEAR_END_SUMMARY': 'year-end-summary'
      }
      return endpoints[this.selectedReportType]
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      }).format(date)
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    },

    formatBenefitType(type) {
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }
  }
}
</script>

<style scoped>
.payroll-reporting {
  padding: 16px;
}
</style>