<template>
  <div class="leave-types-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Leave Types</h1>
        <p class="text-color-secondary">Configure different types of leave available to employees</p>
      </div>
      <Button label="Add Leave Type" icon="pi pi-plus" @click="showDialog" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="leaveTypes" :loading="loading" paginator :rows="10">
          <Column field="name" header="Leave Type" sortable />
          <Column field="code" header="Code" sortable />
          <Column field="maxDays" header="Max Days/Year" sortable />
          <Column field="carryForward" header="Carry Forward" sortable>
            <template #body="{ data }">
              <Tag :value="data.carryForward ? 'Yes' : 'No'" :severity="data.carryForward ? 'success' : 'danger'" />
            </template>
          </Column>
          <Column field="requiresApproval" header="Requires Approval" sortable>
            <template #body="{ data }">
              <Tag :value="data.requiresApproval ? 'Yes' : 'No'" :severity="data.requiresApproval ? 'warning' : 'info'" />
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editLeaveType(data)" />
              <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="deleteLeaveType(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="Leave Type" :modal="true" :style="{width: '500px'}">
      <div class="field">
        <label>Leave Type Name</label>
        <InputText v-model="newLeaveType.name" class="w-full" />
      </div>
      <div class="field">
        <label>Code</label>
        <InputText v-model="newLeaveType.code" class="w-full" />
      </div>
      <div class="field">
        <label>Maximum Days per Year</label>
        <InputNumber v-model="newLeaveType.maxDays" class="w-full" />
      </div>
      <div class="field">
        <label>Description</label>
        <Textarea v-model="newLeaveType.description" rows="3" class="w-full" />
      </div>
      <div class="field">
        <div class="flex align-items-center">
          <Checkbox v-model="newLeaveType.carryForward" inputId="carryForward" />
          <label for="carryForward" class="ml-2">Allow Carry Forward</label>
        </div>
      </div>
      <div class="field">
        <div class="flex align-items-center">
          <Checkbox v-model="newLeaveType.requiresApproval" inputId="requiresApproval" />
          <label for="requiresApproval" class="ml-2">Requires Approval</label>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Save" @click="saveLeaveType" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface LeaveType {
  id: number;
  name: string;
  code: string;
  maxDays: number;
  description: string;
  carryForward: boolean;
  requiresApproval: boolean;
  status: string;
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);
const editing = ref(false);

const leaveTypes = ref<LeaveType[]>([]);

const newLeaveType = ref({
  name: '',
  code: '',
  maxDays: 0,
  description: '',
  carryForward: false,
  requiresApproval: true
});

const showDialog = () => {
  newLeaveType.value = {
    name: '',
    code: '',
    maxDays: 0,
    description: '',
    carryForward: false,
    requiresApproval: true
  };
  editing.value = false;
  dialogVisible.value = true;
};

const saveLeaveType = () => {
  if (newLeaveType.value.name && newLeaveType.value.code) {
    const leaveType: LeaveType = {
      id: Date.now(),
      name: newLeaveType.value.name,
      code: newLeaveType.value.code,
      maxDays: newLeaveType.value.maxDays,
      description: newLeaveType.value.description,
      carryForward: newLeaveType.value.carryForward,
      requiresApproval: newLeaveType.value.requiresApproval,
      status: 'Active'
    };
    
    leaveTypes.value.push(leaveType);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Leave type created', life: 3000 });
  }
};

const editLeaveType = (leaveType: LeaveType) => {
  newLeaveType.value = { ...leaveType };
  editing.value = true;
  dialogVisible.value = true;
};

const deleteLeaveType = (leaveType: LeaveType) => {
  leaveTypes.value = leaveTypes.value.filter(lt => lt.id !== leaveType.id);
  toast.add({ severity: 'success', summary: 'Success', detail: 'Leave type deleted', life: 3000 });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'active': return 'success';
    case 'inactive': return 'danger';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    leaveTypes.value = [
      { id: 1, name: 'Annual Leave', code: 'AL', maxDays: 21, description: 'Yearly vacation leave', carryForward: true, requiresApproval: true, status: 'Active' },
      { id: 2, name: 'Sick Leave', code: 'SL', maxDays: 10, description: 'Medical leave', carryForward: false, requiresApproval: false, status: 'Active' },
      { id: 3, name: 'Personal Leave', code: 'PL', maxDays: 5, description: 'Personal time off', carryForward: false, requiresApproval: true, status: 'Active' },
      { id: 4, name: 'Maternity Leave', code: 'ML', maxDays: 90, description: 'Maternity leave', carryForward: false, requiresApproval: true, status: 'Active' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.leave-types-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>