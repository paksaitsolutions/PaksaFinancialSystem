<template>
  <div class="turnover-report-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Turnover Analysis</h1>
        <p class="text-color-secondary">Employee turnover metrics and retention analysis</p>
      </div>
      <Button label="Generate Report" icon="pi pi-chart-line" @click="generateReport" />
    </div>

    <div class="grid">
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="text-center">
              <div class="text-2xl font-bold text-red-600">8.5%</div>
              <div class="text-color-secondary">Annual Turnover Rate</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">91.5%</div>
              <div class="text-color-secondary">Retention Rate</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">12</div>
              <div class="text-color-secondary">Employees Left</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">15</div>
              <div class="text-color-secondary">New Hires</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <div class="grid">
      <div class="col-12 md:col-6">
        <Card>
          <template #title>Turnover by Department</template>
          <template #content>
            <DataTable :value="departmentTurnover" :loading="loading">
              <Column field="department" header="Department" sortable />
              <Column field="employees" header="Total Employees" sortable />
              <Column field="left" header="Employees Left" sortable />
              <Column field="turnoverRate" header="Turnover Rate" sortable>
                <template #body="{ data }">
                  <Tag :value="`${data.turnoverRate}%`" :severity="getTurnoverSeverity(data.turnoverRate)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6">
        <Card>
          <template #title>Exit Reasons</template>
          <template #content>
            <DataTable :value="exitReasons" :loading="loading">
              <Column field="reason" header="Reason" sortable />
              <Column field="count" header="Count" sortable />
              <Column field="percentage" header="Percentage" sortable>
                <template #body="{ data }">
                  {{ data.percentage }}%
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <Card class="mt-4">
      <template #title>Recent Departures</template>
      <template #content>
        <DataTable :value="recentDepartures" :loading="loading">
          <Column field="employeeId" header="Employee ID" sortable />
          <Column field="employeeName" header="Employee Name" sortable />
          <Column field="department" header="Department" sortable />
          <Column field="position" header="Position" sortable />
          <Column field="tenure" header="Tenure" sortable />
          <Column field="exitDate" header="Exit Date" sortable />
          <Column field="exitReason" header="Exit Reason" sortable />
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface DepartmentTurnover {
  department: string;
  employees: number;
  left: number;
  turnoverRate: number;
}

interface ExitReason {
  reason: string;
  count: number;
  percentage: number;
}

interface RecentDeparture {
  employeeId: string;
  employeeName: string;
  department: string;
  position: string;
  tenure: string;
  exitDate: string;
  exitReason: string;
}

const toast = useToast();
const loading = ref(false);

const departmentTurnover = ref<DepartmentTurnover[]>([]);
const exitReasons = ref<ExitReason[]>([]);
const recentDepartures = ref<RecentDeparture[]>([]);

const generateReport = () => {
  toast.add({
    severity: 'success',
    summary: 'Report Generated',
    detail: 'Turnover analysis report has been generated successfully',
    life: 3000
  });
};

const getTurnoverSeverity = (rate: number) => {
  if (rate <= 5) return 'success';
  if (rate <= 10) return 'warning';
  return 'danger';
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    departmentTurnover.value = [
      { department: 'IT', employees: 25, left: 2, turnoverRate: 8.0 },
      { department: 'Sales', employees: 30, left: 4, turnoverRate: 13.3 },
      { department: 'HR', employees: 8, left: 0, turnoverRate: 0.0 },
      { department: 'Finance', employees: 15, left: 1, turnoverRate: 6.7 },
      { department: 'Marketing', employees: 12, left: 2, turnoverRate: 16.7 }
    ];

    exitReasons.value = [
      { reason: 'Better Opportunity', count: 5, percentage: 41.7 },
      { reason: 'Relocation', count: 3, percentage: 25.0 },
      { reason: 'Career Change', count: 2, percentage: 16.7 },
      { reason: 'Personal Reasons', count: 1, percentage: 8.3 },
      { reason: 'Retirement', count: 1, percentage: 8.3 }
    ];

    recentDepartures.value = [
      { employeeId: 'EMP045', employeeName: 'Alice Johnson', department: 'Marketing', position: 'Marketing Specialist', tenure: '2 years 3 months', exitDate: '2024-01-15', exitReason: 'Better Opportunity' },
      { employeeId: 'EMP032', employeeName: 'Bob Smith', department: 'Sales', position: 'Sales Representative', tenure: '1 year 8 months', exitDate: '2024-01-10', exitReason: 'Relocation' },
      { employeeId: 'EMP028', employeeName: 'Carol Davis', department: 'IT', position: 'Software Developer', tenure: '3 years 1 month', exitDate: '2024-01-05', exitReason: 'Career Change' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.turnover-report-view {
  padding: 0;
}
</style>