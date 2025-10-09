<template>
  <div class="hrm-attendance">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Attendance Management</h1>
        <p class="text-color-secondary">Track and manage employee attendance</p>
      </div>
      <Button 
        label="Mark Attendance" 
        icon="pi pi-clock" 
        @click="markAttendance" 
        :loading="markingAttendance"
        :disabled="markingAttendance"
      />
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
          <Column field="employee_id" header="Employee ID" sortable />
          <Column header="Name" sortable>
            <template #body="{ data }">
              {{ data.employee ? `${data.employee.first_name} ${data.employee.last_name}` : 'N/A' }}
            </template>
          </Column>
          <Column header="Check In" sortable>
            <template #body="{ data }">
              {{ formatTime(data.check_in_time) }}
            </template>
          </Column>
          <Column header="Check Out" sortable>
            <template #body="{ data }">
              {{ formatTime(data.check_out_time) }}
            </template>
          </Column>
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
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { hrmService, type AttendanceRecord } from '@/services/hrmService';

const toast = useToast();
const loading = ref(false);
const markingAttendance = ref(false);

const attendanceRecords = ref<AttendanceRecord[]>([]);

const stats = computed(() => {
  const present = attendanceRecords.value.filter(r => r.status === 'PRESENT').length;
  const absent = attendanceRecords.value.filter(r => r.status === 'ABSENT').length;
  const late = attendanceRecords.value.filter(r => r.status === 'LATE').length;
  const total = attendanceRecords.value.length;
  const rate = total > 0 ? Math.round((present / total) * 100) : 0;
  
  return { present, absent, late, rate };
});

const markAttendance = async () => {
  markingAttendance.value = true;
  try {
    const today = new Date().toISOString().split('T')[0];
    const now = new Date().toLocaleTimeString('en-US', { hour12: false });
    
    // For demo purposes, using a default employee ID
    // In a real app, this would come from the authenticated user
    const employeeId = 'EMP001';
    
    await hrmService.recordAttendance(employeeId, {
      date: today,
      check_in_time: now,
      status: 'PRESENT'
    });
    
    toast.add({
      severity: 'success',
      summary: 'Attendance Marked',
      detail: 'Your attendance has been recorded successfully',
      life: 3000
    });
    
    // Reload attendance records
    await loadAttendanceRecords();
  } catch (error) {
    console.error('Error marking attendance:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to mark attendance. Please try again.',
      life: 3000
    });
  } finally {
    markingAttendance.value = false;
  }
};

const loadAttendanceRecords = async () => {
  try {
    const today = new Date().toISOString().split('T')[0];
    const response = await hrmService.getAttendanceRecords({
      start_date: today,
      end_date: today
    });
    attendanceRecords.value = response.data;
  } catch (error) {
    console.error('Error loading attendance records:', error);
    // Fallback to mock data if API fails
    attendanceRecords.value = [
      {
        id: '1',
        employee_id: 'EMP001',
        employee: { employee_id: 'EMP001', first_name: 'John', last_name: 'Doe' } as any,
        date: new Date().toISOString().split('T')[0],
        check_in_time: '09:00:00',
        check_out_time: '17:30:00',
        status: 'PRESENT'
      },
      {
        id: '2',
        employee_id: 'EMP002',
        employee: { employee_id: 'EMP002', first_name: 'Jane', last_name: 'Smith' } as any,
        date: new Date().toISOString().split('T')[0],
        check_in_time: '09:15:00',
        check_out_time: '17:45:00',
        status: 'LATE'
      },
      {
        id: '3',
        employee_id: 'EMP003',
        employee: { employee_id: 'EMP003', first_name: 'Mike', last_name: 'Johnson' } as any,
        date: new Date().toISOString().split('T')[0],
        status: 'ABSENT'
      }
    ];
  }
};

const getStatusSeverity = (status: string) => {
  switch (status.toUpperCase()) {
    case 'PRESENT': return 'success';
    case 'ABSENT': return 'danger';
    case 'LATE': return 'warning';
    default: return 'info';
  }
};

const formatTime = (time?: string) => {
  if (!time) return '-';
  return new Date(`2000-01-01T${time}`).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
};

onMounted(async () => {
  loading.value = true;
  try {
    await loadAttendanceRecords();
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