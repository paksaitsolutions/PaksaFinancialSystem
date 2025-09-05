<template>
  <div class="hrm-attendance">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Attendance Management</h1>
        <p class="text-color-secondary">Track and manage employee attendance</p>
      </div>
      <Button label="Mark Attendance" icon="pi pi-clock" @click="markAttendance" />
    </div>

    <div class="grid">
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-blue-100 text-blue-600 mr-3">
                <i class="pi pi-users text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Present Today</div>
                <div class="text-2xl font-bold">{{ stats.present }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-red-100 text-red-600 mr-3">
                <i class="pi pi-user-minus text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Absent Today</div>
                <div class="text-2xl font-bold">{{ stats.absent }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-orange-100 text-orange-600 mr-3">
                <i class="pi pi-clock text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Late Arrivals</div>
                <div class="text-2xl font-bold">{{ stats.late }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-green-100 text-green-600 mr-3">
                <i class="pi pi-percentage text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Attendance Rate</div>
                <div class="text-2xl font-bold">{{ stats.rate }}%</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Card>
      <template #title>Today's Attendance</template>
      <template #content>
        <DataTable :value="attendanceRecords" :loading="loading" paginator :rows="10">
          <Column field="employeeId" header="Employee ID" sortable />
          <Column field="name" header="Name" sortable />
          <Column field="checkIn" header="Check In" sortable />
          <Column field="checkOut" header="Check Out" sortable />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
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

interface AttendanceRecord {
  id: number;
  employeeId: string;
  name: string;
  checkIn: string;
  checkOut: string;
  status: string;
}

const toast = useToast();
const loading = ref(false);

const stats = ref({
  present: 45,
  absent: 5,
  late: 3,
  rate: 90
});

const attendanceRecords = ref<AttendanceRecord[]>([]);

const markAttendance = () => {
  toast.add({
    severity: 'success',
    summary: 'Attendance Marked',
    detail: 'Your attendance has been recorded',
    life: 3000
  });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'present': return 'success';
    case 'absent': return 'danger';
    case 'late': return 'warning';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    attendanceRecords.value = [
      { id: 1, employeeId: 'EMP001', name: 'John Doe', checkIn: '09:00 AM', checkOut: '05:30 PM', status: 'Present' },
      { id: 2, employeeId: 'EMP002', name: 'Jane Smith', checkIn: '09:15 AM', checkOut: '05:45 PM', status: 'Late' },
      { id: 3, employeeId: 'EMP003', name: 'Mike Johnson', checkIn: '-', checkOut: '-', status: 'Absent' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.hrm-attendance {
  padding: 0;
}
</style>