<template>
  <div class="leave-calendar-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Leave Calendar</h1>
        <p class="text-color-secondary">View team leave schedule and availability</p>
      </div>
      <div class="flex gap-2">
        <Button label="Today" @click="goToToday" />
        <Button label="Month View" @click="changeView('month')" />
      </div>
    </div>

    <Card>
      <template #content>
        <div class="calendar-container">
          <FullCalendar :options="calendarOptions" />
        </div>
      </template>
    </Card>

    <div class="grid mt-4">
      <div class="col-12 md:col-4">
        <Card>
          <template #title>Leave Summary</template>
          <template #content>
            <div class="flex flex-column gap-3">
              <div class="flex justify-content-between">
                <span>On Leave Today:</span>
                <span class="font-bold">{{ summary.onLeaveToday }}</span>
              </div>
              <div class="flex justify-content-between">
                <span>Upcoming Leaves:</span>
                <span class="font-bold">{{ summary.upcomingLeaves }}</span>
              </div>
              <div class="flex justify-content-between">
                <span>Available Staff:</span>
                <span class="font-bold text-green-600">{{ summary.availableStaff }}</span>
              </div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-8">
        <Card>
          <template #title>Recent Leave Requests</template>
          <template #content>
            <div class="flex flex-column gap-3">
              <div v-for="request in recentRequests" :key="request.id" class="flex justify-content-between align-items-center p-2 border-round surface-border border-1">
                <div>
                  <div class="font-medium">{{ request.employeeName }}</div>
                  <div class="text-sm text-color-secondary">{{ request.dates }}</div>
                </div>
                <Tag :value="request.status" :severity="getStatusSeverity(request.status)" />
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';

interface LeaveRequest {
  id: number;
  employeeName: string;
  dates: string;
  status: string;
}

const summary = ref({
  onLeaveToday: 3,
  upcomingLeaves: 8,
  availableStaff: 42
});

const recentRequests = ref<LeaveRequest[]>([
  { id: 1, employeeName: 'John Doe', dates: 'Jan 15-19, 2024', status: 'Approved' },
  { id: 2, employeeName: 'Jane Smith', dates: 'Jan 22-24, 2024', status: 'Pending' },
  { id: 3, employeeName: 'Mike Johnson', dates: 'Feb 1-3, 2024', status: 'Approved' }
]);

const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,dayGridWeek'
  },
  events: [
    {
      title: 'John Doe - Annual Leave',
      start: '2024-01-15',
      end: '2024-01-20',
      color: '#3b82f6'
    },
    {
      title: 'Jane Smith - Sick Leave',
      start: '2024-01-22',
      end: '2024-01-25',
      color: '#ef4444'
    },
    {
      title: 'Mike Johnson - Personal Leave',
      start: '2024-02-01',
      end: '2024-02-04',
      color: '#f59e0b'
    }
  ],
  height: 'auto'
});

const goToToday = () => {
  // Calendar API to go to today
  console.log('Go to today');
};

const changeView = (view: string) => {
  calendarOptions.value.initialView = view === 'month' ? 'dayGridMonth' : 'dayGridWeek';
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'approved': return 'success';
    case 'rejected': return 'danger';
    case 'pending': return 'warning';
    default: return 'info';
  }
};

onMounted(() => {
  // Initialize calendar
});
</script>

<style scoped>
.leave-calendar-view {
  padding: 0;
}

.calendar-container {
  min-height: 500px;
}

:deep(.fc) {
  font-family: inherit;
}

:deep(.fc-toolbar-title) {
  font-size: 1.5rem;
  font-weight: 600;
}

:deep(.fc-button) {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

:deep(.fc-button:hover) {
  background: var(--primary-color-dark);
  border-color: var(--primary-color-dark);
}
</style>