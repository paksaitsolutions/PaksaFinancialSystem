<template>
  <div class="benefits-management">
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Benefits Management</h2>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="openCreatePlanDialog">
          <v-icon left>mdi-plus</v-icon>
          New Benefit Plan
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-tabs v-model="activeTab" background-color="primary" dark>
          <v-tab value="plans">Benefit Plans</v-tab>
          <v-tab value="enrollments">Employee Enrollments</v-tab>
          <v-tab value="summary">Summary</v-tab>
        </v-tabs>

        <v-window v-model="activeTab" class="mt-4">
          <!-- Benefit Plans Tab -->
          <v-window-item value="plans">
            <v-data-table
              :headers="planHeaders"
              :items="benefitPlans"
              :loading="loading"
              :items-per-page="10"
            >
              <template v-slot:item.benefit_type="{ item }">
                <v-chip small>{{ formatBenefitType(item.benefit_type) }}</v-chip>
              </template>
              
              <template v-slot:item.employee_cost="{ item }">
                {{ formatCurrency(item.employee_cost) }}
              </template>
              
              <template v-slot:item.employer_cost="{ item }">
                {{ formatCurrency(item.employer_cost) }}
              </template>
              
              <template v-slot:item.deduction_type="{ item }">
                <v-chip :color="getDeductionTypeColor(item.deduction_type)" small>
                  {{ formatDeductionType(item.deduction_type) }}
                </v-chip>
              </template>
              
              <template v-slot:item.is_active="{ item }">
                <v-chip :color="item.is_active ? 'success' : 'error'" small>
                  {{ item.is_active ? 'Active' : 'Inactive' }}
                </v-chip>
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn icon small @click="editPlan(item)">
                  <v-icon small>mdi-pencil</v-icon>
                </v-btn>
                <v-btn icon small @click="viewEnrollments(item)">
                  <v-icon small>mdi-account-group</v-icon>
                </v-btn>
                <v-btn icon small @click="deletePlan(item)" :disabled="item.enrolled_count > 0">
                  <v-icon small>mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-window-item>

          <!-- Employee Enrollments Tab -->
          <v-window-item value="enrollments">
            <v-row class="mb-4">
              <v-col cols="12" md="4">
                <v-select
                  v-model="selectedEmployee"
                  :items="employees"
                  item-title="full_name"
                  item-value="id"
                  label="Select Employee"
                  clearable
                  @update:modelValue="loadEmployeeBenefits"
                ></v-select>
              </v-col>
              <v-col cols="12" md="4">
                <v-btn color="primary" @click="openEnrollmentDialog" :disabled="!selectedEmployee">
                  <v-icon left>mdi-plus</v-icon>
                  Enroll in Benefit
                </v-btn>
              </v-col>
            </v-row>

            <v-data-table
              :headers="enrollmentHeaders"
              :items="employeeBenefits"
              :loading="enrollmentsLoading"
              :items-per-page="10"
            >
              <template v-slot:item.benefit_type="{ item }">
                <v-chip small>{{ formatBenefitType(item.benefit_type) }}</v-chip>
              </template>
              
              <template v-slot:item.employee_contribution="{ item }">
                {{ formatCurrency(item.employee_contribution) }}
              </template>
              
              <template v-slot:item.employer_contribution="{ item }">
                {{ formatCurrency(item.employer_contribution) }}
              </template>
              
              <template v-slot:item.is_active="{ item }">
                <v-chip :color="item.is_active ? 'success' : 'error'" small>
                  {{ item.is_active ? 'Active' : 'Terminated' }}
                </v-chip>
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn icon small @click="terminateEnrollment(item)" v-if="item.is_active">
                  <v-icon small>mdi-stop</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-window-item>

          <!-- Summary Tab -->
          <v-window-item value="summary">
            <v-row v-if="summary">
              <v-col cols="12" md="3">
                <v-card class="text-center pa-4" color="blue lighten-5">
                  <h2>{{ summary.total_plans }}</h2>
                  <p>Total Plans</p>
                </v-card>
              </v-col>
              <v-col cols="12" md="3">
                <v-card class="text-center pa-4" color="green lighten-5">
                  <h2>{{ summary.active_plans }}</h2>
                  <p>Active Plans</p>
                </v-card>
              </v-col>
              <v-col cols="12" md="3">
                <v-card class="text-center pa-4" color="orange lighten-5">
                  <h2>{{ summary.total_enrollments }}</h2>
                  <p>Total Enrollments</p>
                </v-card>
              </v-col>
              <v-col cols="12" md="3">
                <v-card class="text-center pa-4" color="purple lighten-5">
                  <h2>{{ formatCurrency(summary.total_employee_cost) }}</h2>
                  <p>Employee Costs</p>
                </v-card>
              </v-col>
            </v-row>

            <v-row class="mt-4" v-if="summary">
              <v-col cols="12">
                <v-card>
                  <v-card-title>Enrollments by Benefit Type</v-card-title>
                  <v-card-text>
                    <v-simple-table>
                      <template v-slot:default>
                        <thead>
                          <tr>
                            <th>Benefit Type</th>
                            <th class="text-right">Enrollments</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="(count, type) in summary.by_type" :key="type">
                            <td>{{ formatBenefitType(type) }}</td>
                            <td class="text-right">{{ count }}</td>
                          </tr>
                        </tbody>
                      </template>
                    </v-simple-table>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-window-item>
        </v-window>
      </v-card-text>
    </v-card>

    <!-- Create/Edit Benefit Plan Dialog -->
    <v-dialog v-model="planDialog" max-width="600px">
      <v-card>
        <v-card-title>{{ planFormTitle }}</v-card-title>
        <v-card-text>
          <v-form ref="planForm" v-model="planFormValid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedPlan.name"
                  label="Plan Name*"
                  :rules="[v => !!v || 'Plan name is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedPlan.benefit_type"
                  :items="benefitTypes"
                  label="Benefit Type*"
                  :rules="[v => !!v || 'Benefit type is required']"
                ></v-select>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="editedPlan.description"
                  label="Description"
                  rows="3"
                ></v-textarea>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedPlan.provider"
                  label="Provider"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedPlan.deduction_type"
                  :items="deductionTypes"
                  label="Deduction Type*"
                  :rules="[v => !!v || 'Deduction type is required']"
                ></v-select>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedPlan.employee_cost"
                  label="Employee Cost"
                  type="number"
                  step="0.01"
                  prefix="$"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedPlan.employer_cost"
                  label="Employer Cost"
                  type="number"
                  step="0.01"
                  prefix="$"
                ></v-text-field>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12">
                <v-checkbox
                  v-model="editedPlan.is_active"
                  label="Active"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="planDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="savePlan" :disabled="!planFormValid">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Employee Enrollment Dialog -->
    <v-dialog v-model="enrollmentDialog" max-width="600px">
      <v-card>
        <v-card-title>Enroll Employee in Benefit</v-card-title>
        <v-card-text>
          <v-form ref="enrollmentForm" v-model="enrollmentFormValid">
            <v-row>
              <v-col cols="12">
                <v-select
                  v-model="newEnrollment.benefit_plan_id"
                  :items="availablePlans"
                  item-title="name"
                  item-value="id"
                  label="Benefit Plan*"
                  :rules="[v => !!v || 'Benefit plan is required']"
                ></v-select>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="newEnrollment.enrollment_date"
                  label="Enrollment Date*"
                  type="date"
                  :rules="[v => !!v || 'Enrollment date is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="newEnrollment.effective_date"
                  label="Effective Date*"
                  type="date"
                  :rules="[v => !!v || 'Effective date is required']"
                ></v-text-field>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="newEnrollment.employee_contribution"
                  label="Employee Contribution"
                  type="number"
                  step="0.01"
                  prefix="$"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="newEnrollment.employer_contribution"
                  label="Employer Contribution"
                  type="number"
                  step="0.01"
                  prefix="$"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="enrollmentDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveEnrollment" :disabled="!enrollmentFormValid">Enroll</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: 'BenefitsManagement',
  data: () => ({
    activeTab: 'plans',
    loading: false,
    enrollmentsLoading: false,
    planDialog: false,
    enrollmentDialog: false,
    planFormValid: false,
    enrollmentFormValid: false,
    benefitPlans: [],
    employees: [],
    employeeBenefits: [],
    summary: null,
    selectedEmployee: null,
    benefitTypes: [],
    deductionTypes: [],
    availablePlans: [],
    editedIndex: -1,
    editedPlan: {
      name: '',
      benefit_type: '',
      description: '',
      provider: '',
      employee_cost: 0,
      employer_cost: 0,
      deduction_type: '',
      is_active: true
    },
    defaultPlan: {
      name: '',
      benefit_type: '',
      description: '',
      provider: '',
      employee_cost: 0,
      employer_cost: 0,
      deduction_type: '',
      is_active: true
    },
    newEnrollment: {
      employee_id: null,
      benefit_plan_id: null,
      enrollment_date: new Date().toISOString().substr(0, 10),
      effective_date: new Date().toISOString().substr(0, 10),
      employee_contribution: 0,
      employer_contribution: 0,
      is_active: true
    },
    planHeaders: [
      { title: 'Name', key: 'name' },
      { title: 'Type', key: 'benefit_type' },
      { title: 'Provider', key: 'provider' },
      { title: 'Employee Cost', key: 'employee_cost' },
      { title: 'Employer Cost', key: 'employer_cost' },
      { title: 'Deduction Type', key: 'deduction_type' },
      { title: 'Enrolled', key: 'enrolled_count' },
      { title: 'Status', key: 'is_active' },
      { title: 'Actions', key: 'actions', sortable: false }
    ],
    enrollmentHeaders: [
      { title: 'Employee', key: 'employee_name' },
      { title: 'Plan', key: 'benefit_plan_name' },
      { title: 'Type', key: 'benefit_type' },
      { title: 'Effective Date', key: 'effective_date' },
      { title: 'Employee Cost', key: 'employee_contribution' },
      { title: 'Employer Cost', key: 'employer_contribution' },
      { title: 'Status', key: 'is_active' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
  }),

  computed: {
    planFormTitle() {
      return this.editedIndex === -1 ? 'New Benefit Plan' : 'Edit Benefit Plan'
    }
  },

  mounted() {
    this.fetchBenefitPlans()
    this.fetchEmployees()
    this.fetchBenefitTypes()
    this.fetchDeductionTypes()
    this.fetchSummary()
  },

  methods: {
    async fetchBenefitPlans() {
      this.loading = true
      try {
        const response = await fetch('/api/payroll/benefits/plans')
        const data = await response.json()
        this.benefitPlans = data.items
      } catch (error) {
        console.error('Error fetching benefit plans:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchEmployees() {
      try {
        const response = await fetch('/api/payroll/employees?is_active=true')
        const data = await response.json()
        this.employees = data.items
      } catch (error) {
        console.error('Error fetching employees:', error)
      }
    },

    async fetchBenefitTypes() {
      try {
        const response = await fetch('/api/payroll/benefits/types')
        this.benefitTypes = await response.json()
      } catch (error) {
        console.error('Error fetching benefit types:', error)
      }
    },

    async fetchDeductionTypes() {
      try {
        const response = await fetch('/api/payroll/benefits/deduction-types')
        this.deductionTypes = await response.json()
      } catch (error) {
        console.error('Error fetching deduction types:', error)
      }
    },

    async fetchSummary() {
      try {
        const response = await fetch('/api/payroll/benefits/summary')
        this.summary = await response.json()
      } catch (error) {
        console.error('Error fetching summary:', error)
      }
    },

    async loadEmployeeBenefits() {
      if (!this.selectedEmployee) {
        this.employeeBenefits = []
        return
      }

      this.enrollmentsLoading = true
      try {
        const response = await fetch(`/api/payroll/benefits/employees/${this.selectedEmployee}/benefits`)
        this.employeeBenefits = await response.json()
      } catch (error) {
        console.error('Error loading employee benefits:', error)
      } finally {
        this.enrollmentsLoading = false
      }
    },

    openCreatePlanDialog() {
      this.editedIndex = -1
      this.editedPlan = Object.assign({}, this.defaultPlan)
      this.planDialog = true
    },

    editPlan(plan) {
      this.editedIndex = this.benefitPlans.indexOf(plan)
      this.editedPlan = Object.assign({}, plan)
      this.planDialog = true
    },

    async savePlan() {
      if (this.$refs.planForm.validate()) {
        try {
          const url = this.editedIndex === -1 
            ? '/api/payroll/benefits/plans'
            : `/api/payroll/benefits/plans/${this.editedPlan.id}`
          
          const method = this.editedIndex === -1 ? 'POST' : 'PUT'
          
          const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.editedPlan)
          })
          
          if (response.ok) {
            this.planDialog = false
            this.fetchBenefitPlans()
            this.fetchSummary()
          }
        } catch (error) {
          console.error('Error saving benefit plan:', error)
        }
      }
    },

    async deletePlan(plan) {
      if (confirm('Are you sure you want to delete this benefit plan?')) {
        try {
          const response = await fetch(`/api/payroll/benefits/plans/${plan.id}`, {
            method: 'DELETE'
          })
          
          if (response.ok) {
            this.fetchBenefitPlans()
            this.fetchSummary()
          }
        } catch (error) {
          console.error('Error deleting benefit plan:', error)
        }
      }
    },

    openEnrollmentDialog() {
      this.newEnrollment.employee_id = this.selectedEmployee
      this.availablePlans = this.benefitPlans.filter(plan => plan.is_active)
      this.enrollmentDialog = true
    },

    async saveEnrollment() {
      if (this.$refs.enrollmentForm.validate()) {
        try {
          const response = await fetch('/api/payroll/benefits/enrollments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.newEnrollment)
          })
          
          if (response.ok) {
            this.enrollmentDialog = false
            this.loadEmployeeBenefits()
            this.fetchSummary()
          }
        } catch (error) {
          console.error('Error saving enrollment:', error)
        }
      }
    },

    async terminateEnrollment(enrollment) {
      const endDate = prompt('Enter termination date (YYYY-MM-DD):')
      if (endDate) {
        try {
          const response = await fetch(`/api/payroll/benefits/enrollments/${enrollment.id}/terminate`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ end_date: endDate })
          })
          
          if (response.ok) {
            this.loadEmployeeBenefits()
            this.fetchSummary()
          }
        } catch (error) {
          console.error('Error terminating enrollment:', error)
        }
      }
    },

    formatBenefitType(type) {
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },

    formatDeductionType(type) {
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },

    getDeductionTypeColor(type) {
      const colors = {
        'PRE_TAX': 'green',
        'POST_TAX': 'orange',
        'EMPLOYER_PAID': 'blue'
      }
      return colors[type] || 'grey'
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
.benefits-management {
  padding: 16px;
}
</style>