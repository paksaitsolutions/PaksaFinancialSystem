<template>
  <div class="employee-detail">
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Employee Details</h2>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="$router.push('/payroll/employees')">
          <v-icon left>mdi-arrow-left</v-icon>
          Back to List
        </v-btn>
        <v-btn color="warning" class="ml-2" @click="editEmployee">
          <v-icon left>mdi-pencil</v-icon>
          Edit
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-row v-if="loading">
          <v-col cols="12" class="text-center">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
          </v-col>
        </v-row>

        <template v-else>
          <v-row>
            <v-col cols="12" md="6">
              <v-card outlined>
                <v-card-title>Personal Information</v-card-title>
                <v-card-text>
                  <v-list dense>
                    <v-list-item>
                      <v-list-item-title>Employee ID:</v-list-item-title>
                      <v-list-item-subtitle>{{ employee.employee_id }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Full Name:</v-list-item-title>
                      <v-list-item-subtitle>{{ employee.full_name }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Date of Birth:</v-list-item-title>
                      <v-list-item-subtitle>{{ formatDate(employee.date_of_birth) }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Gender:</v-list-item-title>
                      <v-list-item-subtitle>{{ formatGender(employee.gender) }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Marital Status:</v-list-item-title>
                      <v-list-item-subtitle>{{ formatMaritalStatus(employee.marital_status) }}</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" md="6">
              <v-card outlined>
                <v-card-title>Contact Information</v-card-title>
                <v-card-text>
                  <v-list dense>
                    <v-list-item>
                      <v-list-item-title>Email:</v-list-item-title>
                      <v-list-item-subtitle>{{ employee.email }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Phone:</v-list-item-title>
                      <v-list-item-subtitle>{{ employee.phone_number }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Address:</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ employee.address_line1 }}
                        <span v-if="employee.address_line2">, {{ employee.address_line2 }}</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>City, State, Postal:</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ employee.city }}, {{ employee.state }} {{ employee.postal_code }}
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Country:</v-list-item-title>
                      <v-list-item-subtitle>{{ employee.country }}</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <v-row class="mt-4">
            <v-col cols="12" md="6">
              <v-card outlined>
                <v-card-title>Employment Details</v-card-title>
                <v-card-text>
                  <v-list dense>
                    <v-list-item>
                      <v-list-item-title>Department:</v-list-item-title>
                      <v-list-item-subtitle>{{ employee.department }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Job Title:</v-list-item-title>
                      <v-list-item-subtitle>{{ employee.job_title }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Employment Type:</v-list-item-title>
                      <v-list-item-subtitle>{{ formatEmploymentType(employee.employment_type) }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Hire Date:</v-list-item-title>
                      <v-list-item-subtitle>{{ formatDate(employee.hire_date) }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item v-if="employee.termination_date">
                      <v-list-item-title>Termination Date:</v-list-item-title>
                      <v-list-item-subtitle>{{ formatDate(employee.termination_date) }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Status:</v-list-item-title>
                      <v-list-item-subtitle>
                        <v-chip
                          :color="employee.is_active ? 'success' : 'error'"
                          small
                        >
                          {{ employee.is_active ? 'Active' : 'Inactive' }}
                        </v-chip>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" md="6">
              <v-card outlined>
                <v-card-title>Compensation & Payment</v-card-title>
                <v-card-text>
                  <v-list dense>
                    <v-list-item>
                      <v-list-item-title>Base Salary:</v-list-item-title>
                      <v-list-item-subtitle>{{ formatCurrency(employee.base_salary, employee.currency) }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Payment Method:</v-list-item-title>
                      <v-list-item-subtitle>{{ formatPaymentMethod(employee.payment_method) }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Payment Frequency:</v-list-item-title>
                      <v-list-item-subtitle>{{ formatPaymentFrequency(employee.payment_frequency) }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item v-if="employee.bank_name">
                      <v-list-item-title>Bank Details:</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ employee.bank_name }}, {{ employee.bank_branch }}
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item v-if="employee.account_number">
                      <v-list-item-title>Account:</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ maskAccountNumber(employee.account_number) }} ({{ employee.account_type }})
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'EmployeeDetail',
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data: () => ({
    loading: false,
    employee: {
      id: '',
      employee_id: '',
      first_name: '',
      last_name: '',
      middle_name: '',
      full_name: '',
      date_of_birth: '',
      gender: '',
      marital_status: '',
      email: '',
      phone_number: '',
      address_line1: '',
      address_line2: '',
      city: '',
      state: '',
      postal_code: '',
      country: '',
      department: '',
      job_title: '',
      employment_type: '',
      hire_date: '',
      termination_date: null,
      is_active: true,
      base_salary: 0,
      currency: 'USD',
      payment_method: '',
      payment_frequency: '',
      bank_name: '',
      bank_branch: '',
      account_number: '',
      account_type: ''
    }
  }),

  mounted() {
    this.fetchEmployeeDetails()
  },

  methods: {
    async fetchEmployeeDetails() {
      this.loading = true
      try {
        // Replace with actual API call
        const response = await fetch(`/api/payroll/employees/${this.id}`)
        this.employee = await response.json()
      } catch (error) {
        console.error('Error fetching employee details:', error)
        // Show error notification
      } finally {
        this.loading = false
      }
    },

    editEmployee() {
      this.$router.push(`/payroll/employees/${this.id}/edit`)
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

    formatGender(gender) {
      const genderMap = {
        'M': 'Male',
        'F': 'Female',
        'O': 'Other'
      }
      return genderMap[gender] || gender
    },

    formatMaritalStatus(status) {
      return status ? status.charAt(0) + status.slice(1).toLowerCase() : 'N/A'
    },

    formatEmploymentType(type) {
      if (!type) return 'N/A'
      return type.split('_').map(word => 
        word.charAt(0) + word.slice(1).toLowerCase()
      ).join(' ')
    },

    formatCurrency(amount, currency = 'USD') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
      }).format(amount)
    },

    formatPaymentMethod(method) {
      if (!method) return 'N/A'
      return method.split('_').map(word => 
        word.charAt(0) + word.slice(1).toLowerCase()
      ).join(' ')
    },

    formatPaymentFrequency(frequency) {
      if (!frequency) return 'N/A'
      return frequency.split('_').map(word => 
        word.charAt(0) + word.slice(1).toLowerCase()
      ).join(' ')
    },

    maskAccountNumber(accountNumber) {
      if (!accountNumber) return 'N/A'
      const visible = 4
      const masked = accountNumber.length - visible
      return '*'.repeat(masked) + accountNumber.slice(-visible)
    }
  }
}
</script>

<style scoped>
.employee-detail {
  padding: 16px;
}
</style>