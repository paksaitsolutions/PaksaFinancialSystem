<template>
  <div class="bills-view">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div class="header-text">
            <h1>
              <i class="pi pi-file-text mr-2"></i>
              AP Bills
            </h1>
            <p class="text-600">Manage vendor bills and invoices</p>
          </div>
          <div class="header-actions">
            <Button 
              label="New Bill" 
              icon="pi pi-plus" 
              @click="handleNewBill"
              class="mr-2"
            />
            <Button 
              label="Import Bills" 
              icon="pi pi-upload" 
              @click="handleImportBills"
              severity="secondary"
              outlined
            />
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Summary Cards -->
      <div class="grid mb-4">
        <div class="col-12 md:col-6 lg:col-3">
          <Card class="h-full shadow-2">
            <template #title>Total Bills</template>
            <template #content>
              <div class="flex align-items-center justify-content-between">
                <div>
                  <div class="text-3xl font-bold mb-1">{{ totalBills }}</div>
                  <div class="text-sm text-500">All bills</div>
                </div>
                <div class="flex align-items-center justify-content-center border-circle w-3rem h-3rem bg-blue-500">
                  <i class="pi pi-file-text text-white text-xl"></i>
                </div>
              </div>
            </template>
          </Card>
        </div>
        <div class="col-12 md:col-6 lg:col-3">
          <Card class="h-full shadow-2">
            <template #title>Pending Approval</template>
            <template #content>
              <div class="flex align-items-center justify-content-between">
                <div>
                  <div class="text-3xl font-bold mb-1">{{ pendingBills }}</div>
                  <div class="text-sm text-500">Awaiting approval</div>
                </div>
                <div class="flex align-items-center justify-content-center border-circle w-3rem h-3rem bg-amber-500">
                  <i class="pi pi-clock text-white text-xl"></i>
                </div>
              </div>
            </template>
          </Card>
        </div>
        <div class="col-12 md:col-6 lg:col-3">
          <Card class="h-full shadow-2">
            <template #title>Approved</template>
            <template #content>
              <div class="flex align-items-center justify-content-between">
                <div>
                  <div class="text-3xl font-bold mb-1">{{ approvedBills }}</div>
                  <div class="text-sm text-500">Ready for payment</div>
                </div>
                <div class="flex align-items-center justify-content-center border-circle w-3rem h-3rem bg-green-500">
                  <i class="pi pi-check text-white text-xl"></i>
                </div>
              </div>
            </template>
          </Card>
        </div>
        <div class="col-12 md:col-6 lg:col-3">
          <Card class="h-full shadow-2">
            <template #title>Overdue</template>
            <template #content>
              <div class="flex align-items-center justify-content-between">
                <div>
                  <div class="text-3xl font-bold mb-1">{{ overdueBills }}</div>
                  <div class="text-sm text-500">Past due date</div>
                </div>
                <div class="flex align-items-center justify-content-center border-circle w-3rem h-3rem bg-red-500">
                  <i class="pi pi-exclamation-triangle text-white text-xl"></i>
                </div>
              </div>
            </template>
          </Card>
        </div>
      </div>

      <!-- Bills Table -->
      <Card>
        <template #title>Bills</template>
        <template #content>
          <DataTable 
            :value="bills" 
            :loading="loading"
            :paginator="true"
            :rows="10"
            :rowsPerPageOptions="[10, 25, 50]"
            paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
            currentPageReportTemplate="Showing {first} to {last} of {totalRecords} bills"
            responsiveLayout="scroll"
          >
            <template #empty>No bills found.</template>
            <template #loading>Loading bills data. Please wait.</template>
            
            <Column field="billNumber" header="Bill #" :sortable="true" style="width: 10rem" />
            
            <Column field="vendor.name" header="Vendor" :sortable="true" style="width: 15rem" />
            
            <Column field="billDate" header="Bill Date" :sortable="true" style="width: 10rem">
              <template #body="{ data }">
                {{ formatDate(data.billDate) }}
              </template>
            </Column>
            
            <Column field="dueDate" header="Due Date" :sortable="true" style="width: 10rem">
              <template #body="{ data }">
                {{ formatDate(data.dueDate) }}
              </template>
            </Column>
            
            <Column field="amount" header="Amount" :sortable="true" style="width: 10rem">
              <template #body="{ data }">
                {{ formatCurrency(data.amount) }}
              </template>
            </Column>
            
            <Column field="status" header="Status" :sortable="true" style="width: 10rem">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            
            <Column header="Actions" style="width: 8rem">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button 
                    icon="pi pi-eye" 
                    class="p-button-rounded p-button-text" 
                    @click="viewBill(data.id)"
                    v-tooltip.top="'View Details'"
                  />
                  <Button 
                    icon="pi pi-pencil" 
                    class="p-button-rounded p-button-text p-button-success" 
                    @click="editBill(data.id)"
                    v-tooltip.top="'Edit'"
                  />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';

type BillStatus = 'draft' | 'pending' | 'approved' | 'paid' | 'overdue';

type Bill = {
  id: string;
  billNumber: string;
  vendor: { name: string };
  billDate: string;
  dueDate: string;
  amount: number;
  status: BillStatus;
};

const router = useRouter();
const toast = useToast();

const loading = ref<boolean>(true);
const bills = ref<Bill[]>([]);

const totalBills = computed(() => bills.value.length);
const pendingBills = computed(() => bills.value.filter(b => b.status === 'pending').length);
const approvedBills = computed(() => bills.value.filter(b => b.status === 'approved').length);
const overdueBills = computed(() => bills.value.filter(b => b.status === 'overdue').length);

const loadBills = async () => {
  loading.value = true;
  try {
    const { billService } = await import('@/api/apService');
    const response = await billService.getBills();
    bills.value = response.bills || response.data || [];
  } catch (error) {
    console.error('Error loading bills:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load bills',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

const handleNewBill = () => {
  router.push({ name: 'CreateBill' });
};

const handleImportBills = () => {
  router.push({ name: 'ImportBills' });
};

const viewBill = (id: string) => {
  // Navigate to bill details view
  console.log('View bill:', id);
};

const editBill = (id: string) => {
  // Navigate to edit bill view
  console.log('Edit bill:', id);
};

const formatDate = (dateString: string): string => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount || 0);
};

const getStatusSeverity = (status: BillStatus): string => {
  switch (status) {
    case 'draft':
      return 'info';
    case 'pending':
      return 'warning';
    case 'approved':
      return 'success';
    case 'paid':
      return 'success';
    case 'overdue':
      return 'danger';
    default:
      return 'info';
  }
};

onMounted(async () => {
  await loadBills();
});
</script>

<style scoped>
.bills-view {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  background-color: var(--surface-card);
  border-bottom: 1px solid var(--surface-border);
  padding: 1.5rem 0;
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-text h1 {
  margin: 0;
  display: flex;
  align-items: center;
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-color);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

@media screen and (max-width: 960px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>