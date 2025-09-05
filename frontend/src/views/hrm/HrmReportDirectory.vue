<template>
  <div class="directory-report-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Employee Directory</h1>
        <p class="text-color-secondary">Complete employee directory and contact information</p>
      </div>
      <div class="flex gap-2">
        <Button label="Export PDF" icon="pi pi-file-pdf" @click="exportPDF" />
        <Button label="Export Excel" icon="pi pi-file-excel" @click="exportExcel" />
      </div>
    </div>

    <Card>
      <template #content>
        <div class="flex justify-content-between align-items-center mb-4">
          <div class="p-inputgroup" style="width: 300px;">
            <span class="p-inputgroup-addon">
              <i class="pi pi-search"></i>
            </span>
            <InputText v-model="searchTerm" placeholder="Search employees..." />
          </div>
          <Dropdown v-model="selectedDepartment" :options="departments" optionLabel="name" optionValue="code" placeholder="All Departments" class="w-12rem" />
        </div>

        <DataTable :value="filteredEmployees" :loading="loading" paginator :rows="15">
          <Column field="photo" header="Photo" style="width: 80px">
            <template #body="{ data }">
              <Avatar :image="data.photo" :label="data.name.charAt(0)" shape="circle" />
            </template>
          </Column>
          <Column field="employeeId" header="ID" sortable />
          <Column field="name" header="Name" sortable />
          <Column field="position" header="Position" sortable />
          <Column field="department" header="Department" sortable />
          <Column field="email" header="Email" sortable />
          <Column field="phone" header="Phone" sortable />
          <Column field="extension" header="Ext." sortable />
          <Column field="location" header="Location" sortable />
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface Employee {
  id: number;
  employeeId: string;
  name: string;
  position: string;
  department: string;
  email: string;
  phone: string;
  extension: string;
  location: string;
  photo?: string;
}

const toast = useToast();
const loading = ref(false);
const searchTerm = ref('');
const selectedDepartment = ref('');

const employees = ref<Employee[]>([]);
const departments = ref([
  { name: 'All Departments', code: '' },
  { name: 'IT', code: 'IT' },
  { name: 'HR', code: 'HR' },
  { name: 'Finance', code: 'Finance' },
  { name: 'Sales', code: 'Sales' },
  { name: 'Marketing', code: 'Marketing' }
]);

const filteredEmployees = computed(() => {
  let filtered = employees.value;
  
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase();
    filtered = filtered.filter(emp => 
      emp.name.toLowerCase().includes(search) ||
      emp.employeeId.toLowerCase().includes(search) ||
      emp.email.toLowerCase().includes(search)
    );
  }
  
  if (selectedDepartment.value) {
    filtered = filtered.filter(emp => emp.department === selectedDepartment.value);
  }
  
  return filtered;
});

const exportPDF = () => {
  toast.add({
    severity: 'success',
    summary: 'Export Started',
    detail: 'Employee directory PDF is being generated',
    life: 3000
  });
};

const exportExcel = () => {
  toast.add({
    severity: 'success',
    summary: 'Export Started',
    detail: 'Employee directory Excel file is being generated',
    life: 3000
  });
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    employees.value = [
      { id: 1, employeeId: 'EMP001', name: 'John Doe', position: 'Software Engineer', department: 'IT', email: 'john.doe@company.com', phone: '(555) 123-4567', extension: '1001', location: 'Building A, Floor 2' },
      { id: 2, employeeId: 'EMP002', name: 'Jane Smith', position: 'HR Manager', department: 'HR', email: 'jane.smith@company.com', phone: '(555) 123-4568', extension: '1002', location: 'Building B, Floor 1' },
      { id: 3, employeeId: 'EMP003', name: 'Mike Johnson', position: 'Financial Analyst', department: 'Finance', email: 'mike.johnson@company.com', phone: '(555) 123-4569', extension: '1003', location: 'Building A, Floor 3' },
      { id: 4, employeeId: 'EMP004', name: 'Sarah Wilson', position: 'Sales Representative', department: 'Sales', email: 'sarah.wilson@company.com', phone: '(555) 123-4570', extension: '1004', location: 'Building C, Floor 1' },
      { id: 5, employeeId: 'EMP005', name: 'David Brown', position: 'Marketing Specialist', department: 'Marketing', email: 'david.brown@company.com', phone: '(555) 123-4571', extension: '1005', location: 'Building B, Floor 2' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.directory-report-view {
  padding: 0;
}
</style>