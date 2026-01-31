<template>
  <UnifiedDashboard 
    title="Accounts Payable" 
    subtitle="Manage vendor bills and payments"
  >
    <template #actions>
      <Button label="Create Bill" icon="pi pi-plus" class="btn-primary" @click="$router.push('/ap/create-bill')" />
    </template>
    
    <template #metrics>
      <UnifiedMetrics :metrics="dashboardMetrics" />
    </template>
    
    <template #content>

      <Card class="mb-4">
        <template #header>
          <h3 class="card-title">Accounts Payable Modules</h3>
        </template>
        <template #content>
          <div class="modules-grid">
            <div class="module-card" @click="$router.push('/ap/vendors')">
              <i class="pi pi-users" style="color: var(--primary-500)"></i>
              <h4>Vendors</h4>
              <p>Manage vendor information</p>
            </div>
            <div class="module-card" @click="$router.push('/ap/invoices')">
              <i class="pi pi-file-edit" style="color: var(--warning-500)"></i>
              <h4>Invoices</h4>
              <p>Process vendor invoices</p>
            </div>
            <div class="module-card" @click="$router.push('/ap/payments')">
              <i class="pi pi-money-bill" style="color: var(--success-500)"></i>
              <h4>Payments</h4>
              <p>Manage vendor payments</p>
            </div>
            <div class="module-card" @click="$router.push('/ap/reports')">
              <i class="pi pi-chart-bar" style="color: var(--info-500)"></i>
              <h4>Reports</h4>
              <p>AP reports and analytics</p>
            </div>
          </div>
        </template>
      </Card>

      <div class="content-grid">
        <Card>
          <template #header>
            <h3 class="card-title">Recent Bills</h3>
          </template>
          <template #content>
            <DataTable :value="recentBills" :rows="5" class="compact-table">
              <Column field="vendor" header="Vendor" />
              <Column field="billNumber" header="Bill #" />
              <Column field="dueDate" header="Due Date" />
              <Column field="amount" header="Amount" />
              <Column field="status" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
        <Card>
          <template #header>
            <h3 class="card-title">Quick Actions</h3>
          </template>
          <template #content>
            <div class="actions-list">
              <Button label="Add Vendor" icon="pi pi-user-plus" class="action-btn" @click="$router.push('/ap/add-vendor')" />
              <Button label="Record Payment" icon="pi pi-money-bill" class="action-btn btn-secondary" @click="$router.push('/ap/record-payment')" />
              <Button label="Import Bills" icon="pi pi-upload" class="action-btn" @click="$router.push('/ap/import-bills')" />
              <Button label="View Reports" icon="pi pi-chart-bar" class="action-btn" @click="$router.push('/ap/reports')" />
            </div>
          </template>
        </Card>
      </div>
    </template>
  </UnifiedDashboard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apService, type APStats, type RecentBill } from '@/services/apService'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const stats = ref<APStats>({
  totalPayable: '0',
  overdueBills: 0,
  activeVendors: 0,
  monthlyPayments: '0'
})

const dashboardMetrics = computed(() => [
  {
    id: 'payable',
    icon: 'pi pi-credit-card',
    value: `$${stats.value.totalPayable}`,
    label: 'Total Payable',
    color: 'var(--error-500)'
  },
  {
    id: 'overdue',
    icon: 'pi pi-clock',
    value: stats.value.overdueBills,
    label: 'Overdue Bills',
    color: 'var(--warning-500)'
  },
  {
    id: 'vendors',
    icon: 'pi pi-users',
    value: stats.value.activeVendors,
    label: 'Active Vendors',
    color: 'var(--primary-500)'
  },
  {
    id: 'payments',
    icon: 'pi pi-money-bill',
    value: `$${stats.value.monthlyPayments}`,
    label: 'Monthly Payments',
    color: 'var(--success-500)'
  }
])

const recentBills = ref<RecentBill[]>([])
const loading = ref(false)

const loadDashboardData = async () => {
  loading.value = true
  try {
    const [statsData, billsData] = await Promise.all([
      apService.getDashboardStats(),
      apService.getRecentBills()
    ])
    
    stats.value = statsData
    recentBills.value = billsData
  } catch (error) {
    console.error('Error loading AP dashboard data:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load dashboard data',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboardData()
})

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'paid': return 'success'
    case 'overdue': return 'danger'
    case 'pending': return 'warning'
    default: return 'info'
  }
}
</script>

<style scoped>
.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.module-card {
  text-align: center;
  padding: var(--spacing-lg);
  border: 1px solid var(--surface-200);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--surface-0);
}

.module-card:hover {
  background: var(--surface-50);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.module-card i {
  font-size: 2.5rem;
  margin-bottom: var(--spacing-md);
  display: block;
}

.module-card h4 {
  margin: var(--spacing-sm) 0;
  color: var(--text-color);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
}

.module-card p {
  margin: 0;
  color: var(--text-color-secondary);
  font-size: var(--font-size-sm);
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-lg);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  margin: 0;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.action-btn {
  width: 100%;
  justify-content: flex-start;
}

:deep(.compact-table .p-datatable-tbody td) {
  padding: var(--spacing-sm) var(--spacing-md);
}

:deep(.compact-table .p-datatable-thead th) {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

@media (max-width: 768px) {
  .modules-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }
  
  .content-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
}

@media (max-width: 480px) {
  .modules-grid {
    grid-template-columns: 1fr;
  }
}
</style>