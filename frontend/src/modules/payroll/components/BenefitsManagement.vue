<template>
  <v-card>
    <v-card-title>
      <span class="text-h5">Benefits Management</span>
      <v-spacer></v-spacer>
      <v-btn color="primary" @click="addBenefitPlan">
        Add Benefit Plan
      </v-btn>
    </v-card-title>
    
    <v-card-text>
      <v-tabs v-model="activeTab">
        <v-tab value="plans">Benefit Plans</v-tab>
        <v-tab value="enrollments">Employee Enrollments</v-tab>
        <v-tab value="costs">Cost Analysis</v-tab>
        <v-tab value="reports">Reports</v-tab>
      </v-tabs>
      
      <v-tabs-window v-model="activeTab">
        <!-- Benefit Plans -->
        <v-tabs-window-item value="plans">
          <v-data-table
            :headers="planHeaders"
            :items="benefitPlans"
            class="mt-4"
          >
            <template v-slot:item.benefit_type="{ item }">
              <v-chip :color="getBenefitTypeColor(item.benefit_type)" size="small">
                {{ formatBenefitType(item.benefit_type) }}
              </v-chip>
            </template>
            
            <template v-slot:item.employee_cost="{ item }">
              ${{ item.employee_cost?.toLocaleString() || 0 }}
            </template>
            
            <template v-slot:item.employer_contribution="{ item }">
              <span v-if="item.employer_contribution_type === 'percentage'">
                {{ (item.employer_contribution_amount * 100).toFixed(1) }}%
              </span>
              <span v-else>
                ${{ item.employer_contribution_amount?.toLocaleString() || 0 }}
              </span>
            </template>
            
            <template v-slot:item.actions="{ item }">
              <v-btn icon size="small" @click="editBenefitPlan(item)">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn icon size="small" @click="deleteBenefitPlan(item)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-tabs-window-item>
        
        <!-- Employee Enrollments -->
        <v-tabs-window-item value="enrollments">
          <v-row class="mt-4">
            <v-col cols="12" md="4">
              <v-select
                v-model="selectedEmployee"
                :items="employees"
                item-title="full_name"
                item-value="id"
                label="Select Employee"
                @update:modelValue="loadEmployeeBenefits"
              ></v-select>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-select
                v-model="filterBenefitType"
                :items="benefitTypes"
                label="Filter by Benefit Type"
                clearable
              ></v-select>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-btn color="primary" @click="enrollEmployee" :disabled="!selectedEmployee">
                Enroll in Benefits
              </v-btn>
            </v-col>
          </v-row>
          
          <v-data-table
            :headers="enrollmentHeaders"
            :items="filteredEnrollments"
            class="mt-4"
          >
            <template v-slot:item.benefit_type="{ item }">
              <v-chip :color="getBenefitTypeColor(item.benefit_type)" size="small">
                {{ formatBenefitType(item.benefit_type) }}
              </v-chip>
            </template>
            
            <template v-slot:item.employee_deduction="{ item }">
              ${{ item.employee_deduction?.toLocaleString() || 0 }}
            </template>
            
            <template v-slot:item.employer_contribution="{ item }">
              ${{ item.employer_contribution?.toLocaleString() || 0 }}
            </template>
            
            <template v-slot:item.is_active="{ item }">
              <v-chip :color="item.is_active ? 'success' : 'error'" size="small">
                {{ item.is_active ? 'Active' : 'Inactive' }}
              </v-chip>
            </template>
            
            <template v-slot:item.actions="{ item }">
              <v-btn icon size="small" @click="editEnrollment(item)">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn icon size="small" @click="terminateEnrollment(item)">
                <v-icon>mdi-stop</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-tabs-window-item>
        
        <!-- Cost Analysis -->
        <v-tabs-window-item value="costs">
          <v-row class="mt-4">
            <v-col cols="12" md="3">
              <v-card>
                <v-card-text>
                  <div class="text-h4 text-primary">
                    ${{ totalEmployeeCosts.toLocaleString() }}
                  </div>
                  <div class="text-subtitle-1">Total Employee Costs</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="3">
              <v-card>
                <v-card-text>
                  <div class="text-h4 text-success">
                    ${{ totalEmployerCosts.toLocaleString() }}
                  </div>
                  <div class="text-subtitle-1">Total Employer Costs</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="3">
              <v-card>
                <v-card-text>
                  <div class="text-h4 text-info">
                    {{ enrollmentRate.toFixed(1) }}%
                  </div>
                  <div class="text-subtitle-1">Overall Enrollment Rate</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="3">
              <v-card>
                <v-card-text>
                  <div class="text-h4 text-warning">
                    ${{ averageCostPerEmployee.toLocaleString() }}
                  </div>
                  <div class="text-subtitle-1">Avg Cost Per Employee</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          
          <v-row class="mt-4">
            <v-col cols="12" md="6">
              <v-card>
                <v-card-title>Cost by Benefit Type</v-card-title>
                <v-card-text>
                  <!-- Chart would go here -->
                  <div class="text-center pa-4">
                    <v-icon size="64" color="grey">mdi-chart-pie</v-icon>
                    <div class="text-subtitle-1 mt-2">Cost Distribution Chart</div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-card>
                <v-card-title>Enrollment Trends</v-card-title>
                <v-card-text>
                  <!-- Chart would go here -->
                  <div class="text-center pa-4">
                    <v-icon size="64" color="grey">mdi-chart-line</v-icon>
                    <div class="text-subtitle-1 mt-2">Enrollment Trend Chart</div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-tabs-window-item>
        
        <!-- Reports -->
        <v-tabs-window-item value="reports">
          <v-row class="mt-4">
            <v-col cols="12" md="4">
              <v-card>
                <v-card-title>Enrollment Summary</v-card-title>
                <v-card-text>
                  <v-btn block color="primary" @click="generateEnrollmentReport">
                    Generate Report
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-card>
                <v-card-title>Cost Analysis</v-card-title>
                <v-card-text>
                  <v-btn block color="primary" @click="generateCostReport">
                    Generate Report
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-card>
                <v-card-title>Compliance Report</v-card-title>
                <v-card-text>
                  <v-btn block color="primary" @click="generateComplianceReport">
                    Generate Report
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-tabs-window-item>
      </v-tabs-window>
    </v-card-text>
    
    <!-- Benefit Plan Dialog -->
    <v-dialog v-model="planDialog" max-width="800px">
      <v-card>
        <v-card-title>
          {{ editingPlan.id ? 'Edit' : 'Add' }} Benefit Plan
        </v-card-title>
        
        <v-card-text>
          <v-form ref="planForm">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editingPlan.name"
                  label="Plan Name"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editingPlan.benefit_type"
                  :items="benefitTypes"
                  label="Benefit Type"
                  required
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="editingPlan.description"
                  label="Description"
                  rows="3"
                ></v-textarea>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editingPlan.employee_cost"
                  label="Employee Cost"
                  type="number"
                  step="0.01"
                  prefix="$"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editingPlan.employer_contribution_type"
                  :items="contributionTypes"
                  label="Employer Contribution Type"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editingPlan.employer_contribution_amount"
                  :label="editingPlan.employer_contribution_type === 'percentage' ? 'Contribution Percentage' : 'Contribution Amount'"
                  type="number"
                  step="0.01"
                  :prefix="editingPlan.employer_contribution_type === 'percentage' ? '' : '$'"
                  :suffix="editingPlan.employer_contribution_type === 'percentage' ? '%' : ''"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-switch
                  v-model="editingPlan.is_active"
                  label="Active"
                ></v-switch>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="planDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveBenefitPlan">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'BenefitsManagement',
  setup() {
    const activeTab = ref('plans')
    const planDialog = ref(false)
    const selectedEmployee = ref(null)
    const filterBenefitType = ref(null)
    
    const benefitPlans = ref([
      {
        id: 1,
        name: 'Health Insurance Premium',
        benefit_type: 'health_insurance',
        description: 'Comprehensive health coverage',
        employee_cost: 200,
        employer_contribution_type: 'percentage',
        employer_contribution_amount: 0.8,
        is_active: true
      },
      {
        id: 2,
        name: '401(k) Plan',
        benefit_type: '401k',
        description: 'Retirement savings plan',
        employee_cost: 0,
        employer_contribution_type: 'percentage',
        employer_contribution_amount: 0.03,
        is_active: true
      }
    ])
    
    const employees = ref([
      { id: 1, full_name: 'John Doe', department: 'Engineering' },
      { id: 2, full_name: 'Jane Smith', department: 'Marketing' }
    ])
    
    const enrollments = ref([
      {
        id: 1,
        employee_id: 1,
        employee_name: 'John Doe',
        benefit_name: 'Health Insurance Premium',
        benefit_type: 'health_insurance',
        coverage_level: 'family',
        employee_deduction: 120,
        employer_contribution: 480,
        is_active: true,
        effective_date: '2024-01-01'
      }
    ])
    
    const editingPlan = ref({
      id: null,
      name: '',
      benefit_type: '',
      description: '',
      employee_cost: 0,
      employer_contribution_type: 'percentage',
      employer_contribution_amount: 0,
      is_active: true
    })
    
    const benefitTypes = [
      { title: 'Health Insurance', value: 'health_insurance' },
      { title: 'Dental Insurance', value: 'dental_insurance' },
      { title: 'Vision Insurance', value: 'vision_insurance' },
      { title: '401(k)', value: '401k' },
      { title: 'Life Insurance', value: 'life_insurance' },
      { title: 'Disability Insurance', value: 'disability_insurance' },
      { title: 'HSA', value: 'hsa' },
      { title: 'FSA', value: 'fsa' }
    ]
    
    const contributionTypes = [
      { title: 'Percentage', value: 'percentage' },
      { title: 'Fixed Amount', value: 'fixed' }
    ]
    
    const planHeaders = [
      { title: 'Plan Name', key: 'name' },
      { title: 'Benefit Type', key: 'benefit_type' },
      { title: 'Employee Cost', key: 'employee_cost' },
      { title: 'Employer Contribution', key: 'employer_contribution' },
      { title: 'Active', key: 'is_active' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
    
    const enrollmentHeaders = [
      { title: 'Employee', key: 'employee_name' },
      { title: 'Benefit', key: 'benefit_name' },
      { title: 'Type', key: 'benefit_type' },
      { title: 'Coverage', key: 'coverage_level' },
      { title: 'Employee Cost', key: 'employee_deduction' },
      { title: 'Employer Cost', key: 'employer_contribution' },
      { title: 'Status', key: 'is_active' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
    
    const filteredEnrollments = computed(() => {
      let filtered = enrollments.value
      
      if (selectedEmployee.value) {
        filtered = filtered.filter(e => e.employee_id === selectedEmployee.value)
      }
      
      if (filterBenefitType.value) {
        filtered = filtered.filter(e => e.benefit_type === filterBenefitType.value)
      }
      
      return filtered
    })
    
    const totalEmployeeCosts = computed(() => {
      return enrollments.value.reduce((sum, e) => sum + (e.employee_deduction || 0), 0)
    })
    
    const totalEmployerCosts = computed(() => {
      return enrollments.value.reduce((sum, e) => sum + (e.employer_contribution || 0), 0)
    })
    
    const enrollmentRate = computed(() => {
      if (employees.value.length === 0) return 0
      const enrolledEmployees = new Set(enrollments.value.map(e => e.employee_id)).size
      return (enrolledEmployees / employees.value.length) * 100
    })
    
    const averageCostPerEmployee = computed(() => {
      if (employees.value.length === 0) return 0
      return (totalEmployeeCosts.value + totalEmployerCosts.value) / employees.value.length
    })
    
    const getBenefitTypeColor = (type) => {
      const colors = {
        'health_insurance': 'blue',
        'dental_insurance': 'green',
        'vision_insurance': 'purple',
        '401k': 'orange',
        'life_insurance': 'red',
        'disability_insurance': 'teal',
        'hsa': 'indigo',
        'fsa': 'pink'
      }
      return colors[type] || 'grey'
    }
    
    const formatBenefitType = (type) => {
      return benefitTypes.find(bt => bt.value === type)?.title || type
    }
    
    const addBenefitPlan = () => {
      editingPlan.value = {
        id: null,
        name: '',
        benefit_type: '',
        description: '',
        employee_cost: 0,
        employer_contribution_type: 'percentage',
        employer_contribution_amount: 0,
        is_active: true
      }
      planDialog.value = true
    }
    
    const editBenefitPlan = (plan) => {
      editingPlan.value = { ...plan }
      planDialog.value = true
    }
    
    const saveBenefitPlan = () => {
      if (editingPlan.value.id) {
        // Update existing plan
        const index = benefitPlans.value.findIndex(p => p.id === editingPlan.value.id)
        if (index >= 0) {
          benefitPlans.value[index] = { ...editingPlan.value }
        }
      } else {
        // Add new plan
        editingPlan.value.id = Date.now()
        benefitPlans.value.push({ ...editingPlan.value })
      }
      planDialog.value = false
    }
    
    const deleteBenefitPlan = (plan) => {
      const index = benefitPlans.value.findIndex(p => p.id === plan.id)
      if (index >= 0) {
        benefitPlans.value.splice(index, 1)
      }
    }
    
    const loadEmployeeBenefits = () => {
      // Load benefits for selected employee
    }
    
    const enrollEmployee = () => {
      // Open enrollment dialog
    }
    
    const editEnrollment = (enrollment) => {
      // Edit enrollment
    }
    
    const terminateEnrollment = (enrollment) => {
      // Terminate enrollment
    }
    
    const generateEnrollmentReport = () => {
      // Generate enrollment report
    }
    
    const generateCostReport = () => {
      // Generate cost report
    }
    
    const generateComplianceReport = () => {
      // Generate compliance report
    }
    
    return {
      activeTab,
      planDialog,
      selectedEmployee,
      filterBenefitType,
      benefitPlans,
      employees,
      enrollments,
      editingPlan,
      benefitTypes,
      contributionTypes,
      planHeaders,
      enrollmentHeaders,
      filteredEnrollments,
      totalEmployeeCosts,
      totalEmployerCosts,
      enrollmentRate,
      averageCostPerEmployee,
      getBenefitTypeColor,
      formatBenefitType,
      addBenefitPlan,
      editBenefitPlan,
      saveBenefitPlan,
      deleteBenefitPlan,
      loadEmployeeBenefits,
      enrollEmployee,
      editEnrollment,
      terminateEnrollment,
      generateEnrollmentReport,
      generateCostReport,
      generateComplianceReport
    }
  }
}
</script>