<template>
  <div class="attendance-report-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Attendance Reports</h1>
        <p class="text-color-secondary">Generate detailed attendance reports and analytics</p>
      </div>
      <Button label="Generate Report" icon="pi pi-file-pdf" @click="generateReport" />
    </div>

    <Card>
      <template #title>Attendance Summary</template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-3">
            <div class="text-center p-3 border-round surface-border border-1">
              <div class="text-2xl font-bold text-blue-600">95%</div>
              <div class="text-color-secondary">Overall Attendance</div>
            </div>
          </div>
          <div class="col-12 md:col-3">
            <div class="text-center p-3 border-round surface-border border-1">
              <div class="text-2xl font-bold text-green-600">42</div>
              <div class="text-color-secondary">Present Today</div>
            </div>
          </div>
          <div class="col-12 md:col-3">
            <div class="text-center p-3 border-round surface-border border-1">
              <div class="text-2xl font-bold text-red-600">3</div>
              <div class="text-color-secondary">Absent Today</div>
            </div>
          </div>
          <div class="col-12 md:col-3">
            <div class="text-center p-3 border-round surface-border border-1">
              <div class="text-2xl font-bold text-orange-600">2</div>
              <div class="text-color-secondary">Late Arrivals</div>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <Card class="mt-4">
      <template #title>Detailed Attendance Report</template>
      <template #content>
        <DataTable :value="attendanceData" :loading="loading" paginator :rows="10">
          <Column field="employeeId" header="Employee ID" sortable />
          <Column field="employeeName" header="Employee Name" sortable />
          <Column field="department" header="Department" sortable />
          <Column field="daysPresent" header="Days Present" sortable />
          <Column field="daysAbsent" header="Days Absent" sortable />
          <Column field="lateArrivals" header="Late Arrivals" sortable />
          <Column field="attendanceRate" header="Attendance %" sortable>
            <template #body="{ data }">
              <Tag :value="`${data.attendanceRate}%`" :severity="getAttendanceSeverity(data.attendanceRate)" />
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

interface AttendanceData {
  id: number;
  employeeId: string;
  employeeName: string;
  department: string;
  daysPresent: number;
  daysAbsent: number;
  lateArrivals: number;
  attendanceRate: number;
}

const toast = useToast();
const loading = ref(false);
const attendanceData = ref<AttendanceData[]>([]);

const generateReport = () => {
  toast.add({
    severity: 'success',
    summary: 'Report Generated',
    detail: 'Attendance report has been generated successfully',
    life: 3000
  });
};

const getAttendanceSeverity = (rate: number) => {
  if (rate >= 95) return 'success';
  if (rate >= 85) return 'warning';
  return 'danger';
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    attendanceData.value = [
      { id: 1, employeeId: 'EMP001', employeeName: 'John Doe', department: 'IT', daysPresent: 20, daysAbsent: 1, lateArrivals: 2, attendanceRate: 95 },
      { id: 2, employeeId: 'EMP002', employeeName: 'Jane Smith', department: 'HR', daysPresent: 21, daysAbsent: 0, lateArrivals: 0, attendanceRate: 100 },
      { id: 3, employeeId: 'EMP003', employeeName: 'Mike Johnson', department: 'Finance', daysPresent: 18, daysAbsent: 3, lateArrivals: 1, attendanceRate: 86 }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.attendance-report-view {
  padding: 0;
}
</style>