<template>
  <div class="employee-management">
    <div class="grid">
      <div class="col-12">
        <h1 class="mb-4">Employee Management</h1>
        
        <TabView v-model:activeIndex="activeTab">
          <TabPanel header="Employee List">
            <employee-list />
          </TabPanel>
          
          <TabPanel header="Department Statistics">
            <div class="mt-4">
              <h2 class="mb-4">Department Statistics</h2>
              
              <div v-if="loading" class="text-center">
                <ProgressSpinner />
              </div>
              
              <div v-else class="grid">
                <div class="col-12 md:col-6">
                  <Card>
                    <template #title>Employee Count by Department</template>
                    <template #content>
                      <DataTable :value="departmentStatsArray" responsiveLayout="scroll">
                        <Column field="department" header="Department" />
                        <Column field="count" header="Employee Count" class="text-right" />
                      </DataTable>
                    </template>
                  </Card>
                </div>
                
                <div class="col-12 md:col-6">
                  <Card>
                    <template #title>Department Distribution</template>
                    <template #content>
                      <div class="text-center">
                        <p>Department distribution chart will be displayed here</p>
                      </div>
                    </template>
                  </Card>
                </div>
              </div>
            </div>
          </TabPanel>
        </TabView>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { payrollService } from '@/services/payrollService'

const activeTab = ref(0)
const loading = ref(false)
const departmentStats = ref<Record<string, number>>({})

const departmentStatsArray = computed(() => {
  return Object.entries(departmentStats.value).map(([department, count]) => ({
    department,
    count
  }))
})

watch(activeTab, (val) => {
  if (val === 1) {
    fetchDepartmentStats()
  }
})

const fetchDepartmentStats = async () => {
  loading.value = true
  try {
    departmentStats.value = await payrollService.getDepartmentStats()
  } catch (error) {
    console.error('Error fetching department statistics:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.employee-management {
  padding: 16px;
}
</style>