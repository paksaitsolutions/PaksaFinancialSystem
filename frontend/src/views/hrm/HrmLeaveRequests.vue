<template>
  <div class="leave-requests-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Leave Requests</h1>
        <p class="text-color-secondary">Manage employee leave requests</p>
      </div>
      <Button label="New Leave Request" icon="pi pi-plus" @click="showDialog" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="leaveRequests" :loading="loading" paginator :rows="10">
          <Column field="employeeId" header="Employee ID" sortable />
          <Column field="employeeName" header="Employee" sortable />
          <Column field="leaveType" header="Leave Type" sortable />
          <Column field="startDate" header="Start Date" sortable />
          <Column field="endDate" header="End Date" sortable />
          <Column field="days" header="Days" sortable />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-check" class="p-button-text p-button-success" @click="approveRequest(data)" v-if="data.status === 'Pending'" />
              <Button icon="pi pi-times" class="p-button-text p-button-danger" @click="rejectRequest(data)" v-if="data.status === 'Pending'" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="New Leave Request" :modal="true" :style="{width: '500px'}">
      <div class="field">
        <label>Employee</label>
        <Dropdown v-model="newRequest.employeeId" :options="employees" optionLabel="name" optionValue="id" placeholder="Select Employee" class="w-full" />
      </div>
      <div class="field">
        <label>Leave Type</label>
        <Dropdown v-model="newRequest.leaveType" :options="leaveTypes" placeholder="Select Leave Type" class="w-full" />
      </div>
      <div class="field">
        <label>Start Date</label>
        <Calendar v-model="newRequest.startDate" class="w-full" />
      </div>
      <div class="field">
        <label>End Date</label>
        <Calendar v-model="newRequest.endDate" class="w-full" />
      </div>
      <div class="field">
        <label>Reason</label>
        <Textarea v-model="newRequest.reason" rows="3" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Submit" @click="submitRequest" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface LeaveRequest {
  id: number;
  employeeId: string;
  employeeName: string;
  leaveType: string;
  startDate: string;
  endDate: string;
  days: number;
  status: string;
  reason: string;
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);

const leaveRequests = ref<LeaveRequest[]>([]);
const employees = ref([
  { id: 'EMP001', name: 'John Doe' },
  { id: 'EMP002', name: 'Jane Smith' },
  { id: 'EMP003', name: 'Mike Johnson' }
]);

const leaveTypes = ref(['Annual Leave', 'Sick Leave', 'Personal Leave', 'Maternity Leave', 'Emergency Leave']);

const newRequest = ref({
  employeeId: '',
  leaveType: '',
  startDate: null,
  endDate: null,
  reason: ''
});

const showDialog = () => {
  newRequest.value = {
    employeeId: '',
    leaveType: '',
    startDate: null,
    endDate: null,
    reason: ''
  };
  dialogVisible.value = true;
};

const submitRequest = () => {
  const employee = employees.value.find(e => e.id === newRequest.value.employeeId);
  if (employee && newRequest.value.startDate && newRequest.value.endDate) {
    const request: LeaveRequest = {
      id: Date.now(),
      employeeId: newRequest.value.employeeId,
      employeeName: employee.name,
      leaveType: newRequest.value.leaveType,
      startDate: new Date(newRequest.value.startDate).toLocaleDateString(),
      endDate: new Date(newRequest.value.endDate).toLocaleDateString(),
      days: Math.ceil((new Date(newRequest.value.endDate).getTime() - new Date(newRequest.value.startDate).getTime()) / (1000 * 3600 * 24)) + 1,
      status: 'Pending',
      reason: newRequest.value.reason
    };
    
    leaveRequests.value.push(request);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Leave request submitted', life: 3000 });
  }
};

const approveRequest = (request: LeaveRequest) => {
  request.status = 'Approved';
  toast.add({ severity: 'success', summary: 'Approved', detail: 'Leave request approved', life: 3000 });
};

const rejectRequest = (request: LeaveRequest) => {
  request.status = 'Rejected';
  toast.add({ severity: 'info', summary: 'Rejected', detail: 'Leave request rejected', life: 3000 });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'approved': return 'success';
    case 'rejected': return 'danger';
    case 'pending': return 'warning';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    leaveRequests.value = [
      { id: 1, employeeId: 'EMP001', employeeName: 'John Doe', leaveType: 'Annual Leave', startDate: '2024-01-15', endDate: '2024-01-19', days: 5, status: 'Pending', reason: 'Family vacation' },
      { id: 2, employeeId: 'EMP002', employeeName: 'Jane Smith', leaveType: 'Sick Leave', startDate: '2024-01-10', endDate: '2024-01-12', days: 3, status: 'Approved', reason: 'Medical appointment' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.leave-requests-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>