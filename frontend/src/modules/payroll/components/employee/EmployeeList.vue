<template>
  <div class="employee-list">
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Employee Management</h2>
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
          class="mr-4"
          density="compact"
        ></v-text-field>
        <v-btn color="primary" @click="openCreateDialog">
          <v-icon left>mdi-plus</v-icon>
          Add Employee
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="employees"
          :search="search"
          :loading="loading"
          :items-per-page="10"
          :footer-props="{
            'items-per-page-options': [10, 25, 50, 100],
          }"
        >
          <template v-slot:item.status="{ item }">
            <v-chip
              :color="item.is_active ? 'success' : 'error'"
              small
            >
              {{ item.is_active ? 'Active' : 'Inactive' }}
            </v-chip>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn icon small @click="openEditDialog(item)">
              <v-icon small>mdi-pencil</v-icon>
            </v-btn>
            <v-btn icon small @click="confirmDelete(item)">
              <v-icon small>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Employee Form Dialog -->
    <v-dialog v-model="dialog" max-width="800px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ formTitle }}</span>
        </v-card-title>

        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-container>
              <v-row>
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="editedItem.employee_id"
                    label="Employee ID*"
                    :disabled="editedIndex !== -1"
                    :rules="[v => !!v || 'Employee ID is required']"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="editedItem.first_name"
                    label="First Name*"
                    :rules="[v => !!v || 'First name is required']"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="editedItem.last_name"
                    label="Last Name*"
                    :rules="[v => !!v || 'Last name is required']"
                  ></v-text-field>
                </v-col>
              </v-row>
              
              <v-row>
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="editedItem.email"
                    label="Email*"
                    :rules="[
                      v => !!v || 'Email is required',
                      v => /.+@.+\..+/.test(v) || 'Email must be valid'
                    ]"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="editedItem.phone_number"
                    label="Phone Number*"
                    :rules="[v => !!v || 'Phone number is required']"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="4">
                  <v-select
                    v-model="editedItem.department"
                    :items="departments"
                    label="Department*"
                    :rules="[v => !!v || 'Department is required']"
                  ></v-select>
                </v-col>
              </v-row>
              
              <v-row>
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="editedItem.job_title"
                    label="Job Title*"
                    :rules="[v => !!v || 'Job title is required']"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="4">
                  <v-select
                    v-model="editedItem.employment_type"
                    :items="employmentTypes"
                    label="Employment Type*"
                    :rules="[v => !!v || 'Employment type is required']"
                  ></v-select>
                </v-col>
                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="editedItem.base_salary"
                    label="Base Salary*"
                    type="number"
                    :rules="[
                      v => !!v || 'Base salary is required',
                      v => v > 0 || 'Base salary must be greater than 0'
                    ]"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-container>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue-darken-1" text @click="close">Cancel</v-btn>
          <v-btn color="blue-darken-1" text @click="save" :disabled="!valid">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="text-h5">Delete Employee</v-card-title>
        <v-card-text>
          Are you sure you want to delete this employee? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue-darken-1" text @click="deleteDialog = false">Cancel</v-btn>
          <v-btn color="error" text @click="deleteItemConfirm">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: 'EmployeeList',
  data: () => ({
    search: '',
    loading: false,
    dialog: false,
    deleteDialog: false,
    valid: true,
    employees: [],
    departments: ['HR', 'Finance', 'IT', 'Marketing', 'Operations', 'Sales'],
    employmentTypes: ['FULL_TIME', 'PART_TIME', 'CONTRACT', 'TEMPORARY', 'INTERN'],
    headers: [
      { title: 'ID', key: 'employee_id' },
      { title: 'Name', key: 'full_name' },
      { title: 'Department', key: 'department' },
      { title: 'Job Title', key: 'job_title' },
      { title: 'Email', key: 'email' },
      { title: 'Status', key: 'status' },
      { title: 'Actions', key: 'actions', sortable: false }
    ],
    editedIndex: -1,
    editedItem: {
      id: '',
      employee_id: '',
      first_name: '',
      last_name: '',
      email: '',
      phone_number: '',
      department: '',
      job_title: '',
      employment_type: 'FULL_TIME',
      base_salary: 0,
      is_active: true
    },
    defaultItem: {
      id: '',
      employee_id: '',
      first_name: '',
      last_name: '',
      email: '',
      phone_number: '',
      department: '',
      job_title: '',
      employment_type: 'FULL_TIME',
      base_salary: 0,
      is_active: true
    }
  }),

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? 'New Employee' : 'Edit Employee'
    }
  },

  mounted() {
    this.fetchEmployees()
    this.fetchDepartments()
  },

  methods: {
    async fetchEmployees() {
      this.loading = true
      try {
        // Replace with actual API call
        const response = await fetch('/api/payroll/employees')
        const data = await response.json()
        this.employees = data.items
      } catch (error) {
        console.error('Error fetching employees:', error)
        // Show error notification
      } finally {
        this.loading = false
      }
    },

    async fetchDepartments() {
      try {
        // Replace with actual API call
        const response = await fetch('/api/payroll/employees/departments/list')
        const data = await response.json()
        if (data && data.length) {
          this.departments = data
        }
      } catch (error) {
        console.error('Error fetching departments:', error)
      }
    },

    openCreateDialog() {
      this.editedIndex = -1
      this.editedItem = Object.assign({}, this.defaultItem)
      this.dialog = true
    },

    openEditDialog(item) {
      this.editedIndex = this.employees.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },

    close() {
      this.dialog = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })
    },

    async save() {
      if (this.$refs.form.validate()) {
        try {
          if (this.editedIndex > -1) {
            // Update existing employee
            await this.updateEmployee(this.editedItem)
          } else {
            // Create new employee
            await this.createEmployee(this.editedItem)
          }
          this.close()
          this.fetchEmployees()
        } catch (error) {
          console.error('Error saving employee:', error)
          // Show error notification
        }
      }
    },

    async createEmployee(employee) {
      // Replace with actual API call
      await fetch('/api/payroll/employees', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(employee)
      })
    },

    async updateEmployee(employee) {
      // Replace with actual API call
      await fetch(`/api/payroll/employees/${employee.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(employee)
      })
    },

    confirmDelete(item) {
      this.editedItem = Object.assign({}, item)
      this.deleteDialog = true
    },

    async deleteItemConfirm() {
      try {
        // Replace with actual API call
        await fetch(`/api/payroll/employees/${this.editedItem.id}`, {
          method: 'DELETE'
        })
        this.deleteDialog = false
        this.fetchEmployees()
      } catch (error) {
        console.error('Error deleting employee:', error)
        // Show error notification
      }
    }
  }
}
</script>

<style scoped>
.employee-list {
  padding: 16px;
}
</style>