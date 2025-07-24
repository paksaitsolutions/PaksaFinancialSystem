<template>
  <div class="employee-management">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-4">Employee Management</h1>
          
          <v-tabs v-model="activeTab" background-color="primary" dark>
            <v-tab value="list">Employee List</v-tab>
            <v-tab value="stats">Department Statistics</v-tab>
          </v-tabs>
          
          <v-card class="mt-4">
            <v-window v-model="activeTab">
              <v-window-item value="list">
                <employee-list />
              </v-window-item>
              
              <v-window-item value="stats">
                <v-card-text>
                  <h2 class="text-h5 mb-4">Department Statistics</h2>
                  
                  <v-row v-if="loading">
                    <v-col cols="12" class="text-center">
                      <v-progress-circular indeterminate color="primary"></v-progress-circular>
                    </v-col>
                  </v-row>
                  
                  <v-row v-else>
                    <v-col cols="12" md="6">
                      <v-card outlined>
                        <v-card-title>Employee Count by Department</v-card-title>
                        <v-card-text>
                          <v-simple-table>
                            <template v-slot:default>
                              <thead>
                                <tr>
                                  <th>Department</th>
                                  <th class="text-right">Employee Count</th>
                                </tr>
                              </thead>
                              <tbody>
                                <tr v-for="(count, dept) in departmentStats" :key="dept">
                                  <td>{{ dept }}</td>
                                  <td class="text-right">{{ count }}</td>
                                </tr>
                              </tbody>
                            </template>
                          </v-simple-table>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    
                    <v-col cols="12" md="6">
                      <v-card outlined height="100%">
                        <v-card-title>Department Distribution</v-card-title>
                        <v-card-text class="d-flex justify-center align-center">
                          <!-- Placeholder for chart -->
                          <div class="text-center">
                            <p>Department distribution chart will be displayed here</p>
                          </div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-window-item>
            </v-window>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import EmployeeList from '../components/employee/EmployeeList.vue'

export default {
  name: 'EmployeeManagementView',
  components: {
    EmployeeList
  },
  data: () => ({
    activeTab: 'list',
    loading: false,
    departmentStats: {}
  }),
  
  watch: {
    activeTab(val) {
      if (val === 'stats') {
        this.fetchDepartmentStats()
      }
    }
  },
  
  methods: {
    async fetchDepartmentStats() {
      this.loading = true
      try {
        // Replace with actual API call
        const response = await fetch('/api/payroll/employees/stats/department-counts')
        this.departmentStats = await response.json()
      } catch (error) {
        console.error('Error fetching department statistics:', error)
        // Show error notification
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.employee-management {
  padding: 16px;
}
</style>