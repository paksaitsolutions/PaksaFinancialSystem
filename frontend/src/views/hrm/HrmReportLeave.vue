<template>
  <div class="leave-report-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Leave Reports</h1>
        <p class="text-color-secondary">Analyze leave patterns and usage statistics</p>
      </div>
      <Button label="Generate Report" icon="pi pi-chart-bar" @click="generateReport" />
    </div>

    <div class="grid">
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">156</div>
              <div class="text-color-secondary">Total Leave Days</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">89</div>
              <div class="text-color-secondary">Approved Requests</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="text-center">
              <div class="text-2xl font-bold text-orange-600">12</div>
              <div class="text-color-secondary">Pending Requests</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="text-center">
              <div class="text-2xl font-bold text-red-600">5</div>
              <div class="text-color-secondary">Rejected Requests</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Card>
      <template #title>Leave Usage by Employee</template>
      <template #content>
        <DataTable :value="leaveData" :loading="loading" paginator :rows="10">
          <Column field="employeeId" header="Employee ID" sortable />
          <Column field="employeeName" header="Employee Name" sortable />
          <Column field="department" header="Department" sortable />
          <Column field="annualLeaveUsed" header="Annual Leave Used" sortable />
          <Column field="sickLeaveUsed" header="Sick Leave Used" sortable />
          <Column field="personalLeaveUsed" header="Personal Leave Used" sortable />
          <Column field="totalLeaveUsed" header="Total Used" sortable />
          <Column field="remainingLeave" header="Remaining" sortable>
            <template #body="{ data }">
              <span :class="data.remainingLeave < 5 ? 'text-red-600 font-bold' : 'text-green-600'">
                {{ data.remainingLeave }} days
              </span>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface LeaveData {
  id: number;
  employeeId: string;
  employeeName: string;
  department: string;
  annualLeaveUsed: number;
  sickLeaveUsed: number;
  personalLeaveUsed: number;
  totalLeaveUsed: number;
  remainingLeave: number;
}

const toast = useToast();
const loading = ref(false);
const leaveData = ref<LeaveData[]>([]);

const generateReport = () => {
  toast.add({
    severity: 'success',
    summary: 'Report Generated',
    detail: 'Leave usage report has been generated successfully',
    life: 3000
  });
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    leaveData.value = [
      { id: 1, employeeId: 'EMP001', employeeName: 'John Doe', department: 'IT', annualLeaveUsed: 8, sickLeaveUsed: 2, personalLeaveUsed: 1, totalLeaveUsed: 11, remainingLeave: 15 },
      { id: 2, employeeId: 'EMP002', employeeName: 'Jane Smith', department: 'HR', annualLeaveUsed: 12, sickLeaveUsed: 1, personalLeaveUsed: 2, totalLeaveUsed: 15, remainingLeave: 11 },
      { id: 3, employeeId: 'EMP003', employeeName: 'Mike Johnson', department: 'Finance', annualLeaveUsed: 18, sickLeaveUsed: 3, personalLeaveUsed: 1, totalLeaveUsed: 22, remainingLeave: 4 },
      { id: 4, employeeId: 'EMP004', employeeName: 'Sarah Wilson', department: 'Sales', annualLeaveUsed: 5, sickLeaveUsed: 0, personalLeaveUsed: 0, totalLeaveUsed: 5, remainingLeave: 21 }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.leave-report-view {
  padding: 0;
}
</style>