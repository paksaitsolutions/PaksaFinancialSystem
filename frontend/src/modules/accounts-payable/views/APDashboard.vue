<template>
  <div class="ap-dashboard">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Accounts Payable</h1>
        <p class="text-color-secondary">Manage vendor bills and payments</p>
      </div>
      <Button label="Create Bill" icon="pi pi-plus" @click="$router.push('/ap/create-bill')" />
    </div>

    <div class="grid">
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-credit-card text-4xl text-red-500 mb-3"></i>
              <div class="text-2xl font-bold">${{ stats.totalPayable }}</div>
              <div class="text-color-secondary">Total Payable</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-clock text-4xl text-orange-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.overdueBills }}</div>
              <div class="text-color-secondary">Overdue Bills</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-users text-4xl text-blue-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.activeVendors }}</div>
              <div class="text-color-secondary">Active Vendors</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-money-bill text-4xl text-green-500 mb-3"></i>
              <div class="text-2xl font-bold">${{ stats.monthlyPayments }}</div>
              <div class="text-color-secondary">Monthly Payments</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- AP Module Navigation -->
    <div class="grid mb-4">
      <div class="col-12">
        <Card>
          <template #title>Accounts Payable Modules</template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6 lg:col-3">
                <div class="module-card" @click="$router.push('/ap/vendors')">
                  <i class="pi pi-users text-3xl text-blue-500 mb-2"></i>
                  <h4>Vendors</h4>
                  <p class="text-sm text-color-secondary">Manage vendor information</p>
                </div>
              </div>
              <div class="col-12 md:col-6 lg:col-3">
                <div class="module-card" @click="$router.push('/ap/invoices')">
                  <i class="pi pi-file-edit text-3xl text-orange-500 mb-2"></i>
                  <h4>Invoices</h4>
                  <p class="text-sm text-color-secondary">Process vendor invoices</p>
                </div>
              </div>
              <div class="col-12 md:col-6 lg:col-3">
                <div class="module-card" @click="$router.push('/ap/payments')">
                  <i class="pi pi-money-bill text-3xl text-green-500 mb-2"></i>
                  <h4>Payments</h4>
                  <p class="text-sm text-color-secondary">Manage vendor payments</p>
                </div>
              </div>
              <div class="col-12 md:col-6 lg:col-3">
                <div class="module-card" @click="$router.push('/ap/reports')">
                  <i class="pi pi-chart-bar text-3xl text-purple-500 mb-2"></i>
                  <h4>Reports</h4>
                  <p class="text-sm text-color-secondary">AP reports and analytics</p>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <div class="grid">
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>Recent Bills</template>
          <template #content>
            <DataTable :value="recentBills" :rows="5">
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
      </div>
      <div class="col-12 lg:col-4">
        <Card>
          <template #title>Quick Actions</template>
          <template #content>
            <div class="quick-actions">
              <Button label="Add Vendor" icon="pi pi-user-plus" class="w-full mb-2" @click="$router.push('/ap/add-vendor')" />
              <Button label="Record Payment" icon="pi pi-money-bill" class="w-full mb-2 p-button-secondary" @click="$router.push('/ap/record-payment')" />
              <Button label="Import Bills" icon="pi pi-upload" class="w-full mb-2 p-button-success" @click="$router.push('/ap/import-bills')" />
              <Button label="View All Vendors" icon="pi pi-users" class="w-full mb-2 p-button-help" @click="$router.push('/ap/vendors')" />
              <Button label="View Reports" icon="pi pi-chart-bar" class="w-full p-button-info" @click="$router.push('/ap/reports')" />
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const stats = ref({
  totalPayable: '125,430',
  overdueBills: 8,
  activeVendors: 45,
  monthlyPayments: '89,240'
})

const recentBills = ref([
  { vendor: 'Office Supplies Co.', billNumber: 'INV-001', dueDate: '2024-01-20', amount: '$1,250.00', status: 'pending' },
  { vendor: 'Tech Solutions Ltd.', billNumber: 'INV-002', dueDate: '2024-01-18', amount: '$3,500.00', status: 'overdue' },
  { vendor: 'Utility Company', billNumber: 'INV-003', dueDate: '2024-01-25', amount: '$450.00', status: 'pending' },
  { vendor: 'Marketing Agency', billNumber: 'INV-004', dueDate: '2024-01-15', amount: '$2,800.00', status: 'paid' },
  { vendor: 'Equipment Rental', billNumber: 'INV-005', dueDate: '2024-01-22', amount: '$850.00', status: 'pending' }
])

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
.ap-dashboard {
  padding: 0;
}

.metric-card {
  text-align: center;
}

.quick-actions {
  display: flex;
  flex-direction: column;
}

.module-card {
  text-align: center;
  padding: 1.5rem;
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.module-card:hover {
  background-color: var(--surface-hover);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.module-card h4 {
  margin: 0.5rem 0;
  color: var(--text-color);
}

.module-card p {
  margin: 0;
}
</style>