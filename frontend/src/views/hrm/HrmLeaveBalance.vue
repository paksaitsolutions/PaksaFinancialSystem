<template>
  <div class="leave-balance-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Leave Balance</h1>
        <p class="text-color-secondary">View employee leave balances and entitlements</p>
      </div>
      <Button label="Export Report" icon="pi pi-download" @click="exportReport" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="leaveBalances" :loading="loading" paginator :rows="10">
          <Column field="employeeId" header="Employee ID" sortable />
          <Column field="employeeName" header="Employee" sortable />
          <Column field="department" header="Department" sortable />
          <Column field="annualLeave" header="Annual Leave" sortable>
            <template #body="{ data }">
              {{ data.annualLeave.used }}/{{ data.annualLeave.total }} days
            </template>
          </Column>
          <Column field="sickLeave" header="Sick Leave" sortable>
            <template #body="{ data }">
              {{ data.sickLeave.used }}/{{ data.sickLeave.total }} days
            </template>
          </Column>
          <Column field="personalLeave" header="Personal Leave" sortable>
            <template #body="{ data }">
              {{ data.personalLeave.used }}/{{ data.personalLeave.total }} days
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text" @click="viewDetails(data)" />
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

interface LeaveBalance {
  id: number;
  employeeId: string;
  employeeName: string;
  department: string;
  annualLeave: { used: number; total: number };
  sickLeave: { used: number; total: number };
  personalLeave: { used: number; total: number };
}

const toast = useToast();
const loading = ref(false);
const leaveBalances = ref<LeaveBalance[]>([]);

const exportReport = () => {
  toast.add({ severity: 'success', summary: 'Export Started', detail: 'Leave balance report is being generated', life: 3000 });
};

const viewDetails = (balance: LeaveBalance) => {
  toast.add({ severity: 'info', summary: 'View Details', detail: `Viewing details for ${balance.employeeName}`, life: 3000 });
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    leaveBalances.value = [
      { id: 1, employeeId: 'EMP001', employeeName: 'John Doe', department: 'IT', annualLeave: { used: 5, total: 21 }, sickLeave: { used: 2, total: 10 }, personalLeave: { used: 1, total: 5 } },
      { id: 2, employeeId: 'EMP002', employeeName: 'Jane Smith', department: 'HR', annualLeave: { used: 8, total: 21 }, sickLeave: { used: 0, total: 10 }, personalLeave: { used: 2, total: 5 } },
      { id: 3, employeeId: 'EMP003', employeeName: 'Mike Johnson', department: 'Finance', annualLeave: { used: 12, total: 21 }, sickLeave: { used: 3, total: 10 }, personalLeave: { used: 0, total: 5 } }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.leave-balance-view {
  padding: 0;
}
</style>