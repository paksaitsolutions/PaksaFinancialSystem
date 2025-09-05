<template>
  <div class="hrm-payroll">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Payroll Management</h1>
        <p class="text-color-secondary">Manage employee payroll and compensation</p>
      </div>
      <Button label="Run Payroll" icon="pi pi-play" @click="runPayroll" />
    </div>

    <div class="grid">
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-blue-100 text-blue-600 mr-3">
                <i class="pi pi-dollar text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Total Payroll</div>
                <div class="text-2xl font-bold">${{ stats.totalPayroll.toLocaleString() }}</div>
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
                <i class="pi pi-users text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Employees Paid</div>
                <div class="text-2xl font-bold">{{ stats.employeesPaid }}</div>
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
                <i class="pi pi-calculator text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Avg Salary</div>
                <div class="text-2xl font-bold">${{ stats.avgSalary.toLocaleString() }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-purple-100 text-purple-600 mr-3">
                <i class="pi pi-calendar text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Pay Period</div>
                <div class="text-xl font-bold">{{ stats.payPeriod }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Card>
      <template #title>Payroll Records</template>
      <template #content>
        <DataTable :value="payrollRecords" :loading="loading" paginator :rows="10">
          <Column field="employeeId" header="Employee ID" sortable />
          <Column field="employeeName" header="Employee" sortable />
          <Column field="department" header="Department" sortable />
          <Column field="baseSalary" header="Base Salary" sortable>
            <template #body="{ data }">
              ${{ data.baseSalary.toLocaleString() }}
            </template>
          </Column>
          <Column field="overtime" header="Overtime" sortable>
            <template #body="{ data }">
              ${{ data.overtime.toLocaleString() }}
            </template>
          </Column>
          <Column field="deductions" header="Deductions" sortable>
            <template #body="{ data }">
              ${{ data.deductions.toLocaleString() }}
            </template>
          </Column>
          <Column field="netPay" header="Net Pay" sortable>
            <template #body="{ data }">
              <span class="font-bold">${{ data.netPay.toLocaleString() }}</span>
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text" @click="viewPayslip(data)" />
              <Button icon="pi pi-download" class="p-button-text p-button-success" @click="downloadPayslip(data)" />
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

interface PayrollRecord {
  id: number;
  employeeId: string;
  employeeName: string;
  department: string;
  baseSalary: number;
  overtime: number;
  deductions: number;
  netPay: number;
  status: string;
}

const toast = useToast();
const loading = ref(false);

const stats = ref({
  totalPayroll: 285000,
  employeesPaid: 45,
  avgSalary: 6333,
  payPeriod: 'Jan 2024'
});

const payrollRecords = ref<PayrollRecord[]>([]);

const runPayroll = () => {
  toast.add({
    severity: 'success',
    summary: 'Payroll Processing',
    detail: 'Payroll run initiated successfully',
    life: 3000
  });
};

const viewPayslip = (record: PayrollRecord) => {
  toast.add({
    severity: 'info',
    summary: 'View Payslip',
    detail: `Viewing payslip for ${record.employeeName}`,
    life: 3000
  });
};

const downloadPayslip = (record: PayrollRecord) => {
  toast.add({
    severity: 'success',
    summary: 'Download Started',
    detail: `Downloading payslip for ${record.employeeName}`,
    life: 3000
  });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'paid': return 'success';
    case 'pending': return 'warning';
    case 'processing': return 'info';
    case 'failed': return 'danger';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    payrollRecords.value = [
      { id: 1, employeeId: 'EMP001', employeeName: 'John Doe', department: 'IT', baseSalary: 8000, overtime: 500, deductions: 1200, netPay: 7300, status: 'Paid' },
      { id: 2, employeeId: 'EMP002', employeeName: 'Jane Smith', department: 'HR', baseSalary: 7500, overtime: 0, deductions: 1100, netPay: 6400, status: 'Paid' },
      { id: 3, employeeId: 'EMP003', employeeName: 'Mike Johnson', department: 'Finance', baseSalary: 9000, overtime: 300, deductions: 1400, netPay: 7900, status: 'Processing' },
      { id: 4, employeeId: 'EMP004', employeeName: 'Sarah Wilson', department: 'Sales', baseSalary: 6500, overtime: 800, deductions: 950, netPay: 6350, status: 'Pending' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.hrm-payroll {
  padding: 0;
}
</style>