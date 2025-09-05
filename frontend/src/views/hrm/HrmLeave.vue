<template>
  <div class="leave-management">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Leave Management</h1>
        <p class="text-color-secondary">Manage employee leave requests and policies</p>
      </div>
      <Button label="New Leave Request" icon="pi pi-plus" @click="openNewRequest" />
    </div>

    <div class="grid">
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="text-center">
              <i class="pi pi-calendar text-4xl text-blue-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.totalRequests }}</div>
              <div class="text-color-secondary">Total Requests</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="text-center">
              <i class="pi pi-clock text-4xl text-orange-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.pendingRequests }}</div>
              <div class="text-color-secondary">Pending</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="text-center">
              <i class="pi pi-check text-4xl text-green-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.approvedRequests }}</div>
              <div class="text-color-secondary">Approved</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="text-center">
              <i class="pi pi-times text-4xl text-red-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.rejectedRequests }}</div>
              <div class="text-color-secondary">Rejected</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Card class="mt-4">
      <template #title>Recent Leave Requests</template>
      <template #content>
        <DataTable :value="leaveRequests" :loading="loading" paginator :rows="10">
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
              <Button icon="pi pi-eye" class="p-button-text" @click="viewRequest(data)" />
              <Button v-if="data.status === 'pending'" icon="pi pi-check" class="p-button-text p-button-success" @click="approveRequest(data)" />
              <Button v-if="data.status === 'pending'" icon="pi pi-times" class="p-button-text p-button-danger" @click="rejectRequest(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="requestDialog" header="Leave Request Details" :modal="true" :style="{width: '600px'}">
      <div class="field">
        <label>Employee</label>
        <Dropdown v-model="request.employeeId" :options="employees" optionLabel="name" optionValue="id" placeholder="Select Employee" class="w-full" />
      </div>
      <div class="field">
        <label>Leave Type</label>
        <Dropdown v-model="request.leaveType" :options="leaveTypes" placeholder="Select Leave Type" class="w-full" />
      </div>
      <div class="grid">
        <div class="col-6">
          <div class="field">
            <label>Start Date</label>
            <Calendar v-model="request.startDate" class="w-full" @update:modelValue="calculateDays" />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label>End Date</label>
            <Calendar v-model="request.endDate" class="w-full" @update:modelValue="calculateDays" />
          </div>
        </div>
      </div>
      <div class="field">
        <label>Days Requested</label>
        <InputNumber v-model="request.days" class="w-full" :min="1" />
      </div>
      <div class="field">
        <label>Reason</label>
        <Textarea v-model="request.reason" rows="3" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="requestDialog = false" />
        <Button label="Submit" @click="submitRequest" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface LeaveRequest {
  id?: number;
  employeeId: number;
  employeeName: string;
  leaveType: string;
  startDate: Date;
  endDate: Date;
  days: number;
  reason: string;
  status: string;
}

const toast = useToast();
const loading = ref(false);
const requestDialog = ref(false);

const stats = ref({
  totalRequests: 45,
  pendingRequests: 8,
  approvedRequests: 32,
  rejectedRequests: 5
});

const leaveRequests = ref<LeaveRequest[]>([]);
const request = ref<LeaveRequest>({
  employeeId: 0,
  employeeName: '',
  leaveType: '',
  startDate: new Date(),
  endDate: new Date(),
  days: 0,
  reason: '',
  status: 'pending'
});

const employees = ref([
  { id: 1, name: 'John Doe' },
  { id: 2, name: 'Jane Smith' },
  { id: 3, name: 'Mike Johnson' }
]);

const leaveTypes = ref(['Annual Leave', 'Sick Leave', 'Personal Leave', 'Maternity Leave', 'Emergency Leave']);

const openNewRequest = () => {
  request.value = {
    employeeId: 0,
    employeeName: '',
    leaveType: '',
    startDate: new Date(),
    endDate: new Date(),
    days: 0,
    reason: '',
    status: 'pending'
  };
  requestDialog.value = true;
};

const calculateDays = () => {
  if (request.value.startDate && request.value.endDate) {
    const diffTime = Math.abs(request.value.endDate.getTime() - request.value.startDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    request.value.days = diffDays;
  }
};

const submitRequest = () => {
  const employee = employees.value.find(e => e.id === request.value.employeeId);
  if (employee) {
    request.value.employeeName = employee.name;
    request.value.days = Math.ceil((request.value.endDate.getTime() - request.value.startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    leaveRequests.value.unshift({ ...request.value, id: Date.now() });
    requestDialog.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Leave request submitted', life: 3000 });
  }
};

const viewRequest = (req: LeaveRequest) => {
  request.value = { ...req };
  requestDialog.value = true;
};

const approveRequest = (req: LeaveRequest) => {
  const index = leaveRequests.value.findIndex(r => r.id === req.id);
  if (index !== -1) {
    leaveRequests.value[index].status = 'approved';
    stats.value.approvedRequests++;
    stats.value.pendingRequests--;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Leave request approved', life: 3000 });
  }
};

const rejectRequest = (req: LeaveRequest) => {
  const index = leaveRequests.value.findIndex(r => r.id === req.id);
  if (index !== -1) {
    leaveRequests.value[index].status = 'rejected';
    stats.value.rejectedRequests++;
    stats.value.pendingRequests--;
    toast.add({ severity: 'info', summary: 'Info', detail: 'Leave request rejected', life: 3000 });
  }
};

const getStatusSeverity = (status: string) => {
  switch (status) {
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
      { id: 1, employeeId: 1, employeeName: 'John Doe', leaveType: 'Annual Leave', startDate: new Date('2024-02-15'), endDate: new Date('2024-02-20'), days: 6, reason: 'Family vacation', status: 'pending' },
      { id: 2, employeeId: 2, employeeName: 'Jane Smith', leaveType: 'Sick Leave', startDate: new Date('2024-02-10'), endDate: new Date('2024-02-12'), days: 3, reason: 'Medical appointment', status: 'approved' },
      { id: 3, employeeId: 3, employeeName: 'Mike Johnson', leaveType: 'Personal Leave', startDate: new Date('2024-02-08'), endDate: new Date('2024-02-09'), days: 2, reason: 'Personal matters', status: 'rejected' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.leave-management {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>