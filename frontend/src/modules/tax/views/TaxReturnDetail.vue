<template>
  <div class="tax-return-detail">
    <div class="grid">
      <div class="col-12">
        <Breadcrumb :home="breadcrumbHome" :model="breadcrumbItems" />
      </div>
      
      <div class="col-12">
        <Card>
          <template #title>
            <div class="flex align-items-center justify-content-between">
              <span>Tax Return #{{ taxReturn?.return_reference || 'Loading...' }}</span>
              <div class="flex gap-2">
                <Button 
                  label="Back to List" 
                  icon="pi pi-arrow-left" 
                  class="p-button-text"
                  @click="goBack"
                />
                <Button 
                  label="Edit" 
                  icon="pi pi-pencil" 
                  class="p-button-outlined"
                  @click="editReturn"
                />
                <Button 
                  label="File Return" 
                  icon="pi pi-send" 
                  class="p-button-success"
                  :loading="isFiling"
                  @click="fileReturn"
                />
              </div>
            </div>
          </template>
          
          <template #content>
            <div v-if="isLoading" class="flex justify-content-center p-5">
              <ProgressSpinner />
            </div>
            
            <div v-else-if="error" class="p-4">
              <Message severity="error" :closable="false">
                {{ error }}
              </Message>
              <Button 
                label="Retry" 
                icon="pi pi-refresh" 
                class="mt-3"
                @click="loadTaxReturn"
              />
            </div>
            
            <div v-else>
              <!-- Return Summary -->
              <div class="grid">
                <div class="col-12 md:col-6 lg:col-4">
                  <div class="p-3 border-round border-1 surface-border">
                    <div class="text-500 font-medium mb-2">Filing Period</div>
                    <div class="text-900 font-medium">
                      {{ formatDate(taxReturn.start_date) }} - {{ formatDate(taxReturn.end_date) }}
                    </div>
                  </div>
                </div>
                
                <div class="col-12 md:col-6 lg:col-4">
                  <div class="p-3 border-round border-1 surface-border">
                    <div class="text-500 font-medium mb-2">Status</div>
                    <Tag :value="taxReturn.status" :severity="getStatusSeverity(taxReturn.status)" />
                  </div>
                </div>
                
                <div class="col-12 md:col-6 lg:col-4">
                  <div class="p-3 border-round border-1 surface-border">
                    <div class="text-500 font-medium mb-2">Total Tax Due</div>
                    <div class="text-900 font-bold text-xl">
                      {{ formatCurrency(taxReturn.total_tax_due) }}
                    </div>
                  </div>
                </div>
                
                <div class="col-12 md:col-6">
                  <div class="p-3 border-round border-1 surface-border">
                    <div class="text-500 font-medium mb-2">Tax Type</div>
                    <div class="text-900 font-medium">
                      {{ taxReturn.tax_type }} - {{ taxReturn.jurisdiction_code }}
                    </div>
                  </div>
                </div>
                
                <div class="col-12 md:col-6">
                  <div class="p-3 border-round border-1 surface-border">
                    <div class="text-500 font-medium mb-2">Filing Date</div>
                    <div class="text-900 font-medium">
                      {{ taxReturn.filing_date ? formatDate(taxReturn.filing_date) : 'Not filed yet' }}
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Tabs -->
              <TabView class="mt-5">
                <TabPanel header="Overview">
                  <div class="grid">
                    <div class="col-12 md:col-8">
                      <h4>Tax Calculation Summary</h4>
                      <DataTable 
                        :value="taxReturn.tax_calculations || []"
                        :scrollable="true"
                        scrollHeight="400px"
                        class="p-datatable-sm"
                      >
                        <Column field="tax_type" header="Tax Type" :sortable="true" />
                        <Column field="taxable_amount" header="Taxable Amount" :sortable="true">
                          <template #body="{ data }">
                            {{ formatCurrency(data.taxable_amount) }}
                          </template>
                        </Column>
                        <Column field="tax_rate" header="Rate" :sortable="true">
                          <template #body="{ data }">
                            {{ (data.tax_rate * 100).toFixed(2) }}%
                          </template>
                        </Column>
                        <Column field="tax_amount" header="Tax Amount" :sortable="true">
                          <template #body="{ data }">
                            <strong>{{ formatCurrency(data.tax_amount) }}</strong>
                          </template>
                        </Column>
                      </DataTable>
                    </div>
                    
                    <div class="col-12 md:col-4">
                      <h4>Payment Information</h4>
                      <div class="p-4 border-round border-1 surface-border">
                        <div class="mb-3">
                          <div class="text-500">Payment Status</div>
                          <div class="font-medium">
                            <Tag 
                              :value="taxReturn.payment_status || 'Unpaid'" 
                              :severity="getPaymentStatusSeverity(taxReturn.payment_status)" 
                            />
                          </div>
                        </div>
                        
                        <div class="mb-3">
                          <div class="text-500">Amount Due</div>
                          <div class="text-900 font-bold text-xl">
                            {{ formatCurrency(taxReturn.total_tax_due) }}
                          </div>
                        </div>
                        
                        <div class="mb-3">
                          <div class="text-500">Due Date</div>
                          <div class="font-medium">
                            {{ formatDate(taxReturn.due_date) }}
                            <Tag 
                              v-if="isDueSoon"
                              value="Due Soon" 
                              severity="warning" 
                              class="ml-2"
                            />
                            <Tag 
                              v-else-if="isOverdue"
                              value="Overdue" 
                              severity="danger" 
                              class="ml-2"
                            />
                          </div>
                        </div>
                        
                        <Button 
                          label="Make Payment" 
                          icon="pi pi-credit-card" 
                          class="w-full mt-3"
                          :disabled="taxReturn.status === 'paid'"
                          @click="initiatePayment"
                        />
                      </div>
                      
                      <h4 class="mt-5">Filing History</h4>
                      <Timeline :value="filingHistory" align="alternate" class="mt-3">
                        <template #content="slotProps">
                          <div class="text-sm">
                            <div class="font-bold">{{ slotProps.item.status }}</div>
                            <div>{{ formatDateTime(slotProps.item.timestamp) }}</div>
                            <div v-if="slotProps.item.notes" class="text-500">
                              {{ slotProps.item.notes }}
                            </div>
                          </div>
                        </template>
                      </Timeline>
                    </div>
                  </div>
                </TabPanel>
                
                <TabPanel header="Attachments">
                  <TaxAttachmentList :tax-return-id="taxReturnId" />
                </TabPanel>
                
                <TabPanel header="Audit Log">
                  <DataTable 
                    :value="auditLogs"
                    :loading="isLoadingAuditLogs"
                    :paginator="true"
                    :rows="10"
                    :rowsPerPageOptions="[10, 25, 50]"
                    class="p-datatable-sm"
                  >
                    <Column field="timestamp" header="Date" :sortable="true">
                      <template #body="{ data }">
                        {{ formatDateTime(data.timestamp) }}
                      </template>
                    </Column>
                    <Column field="action" header="Action" :sortable="true" />
                    <Column field="user" header="User" :sortable="true" />
                    <Column field="details" header="Details" />
                  </DataTable>
                </TabPanel>
              </TabView>
            </div>
          </template>
        </Card>
      </div>
    </div>
    
    <!-- Payment Dialog -->
    <Dialog 
      v-model:visible="showPaymentDialog" 
      header="Make Payment" 
      :modal="true"
      :style="{ width: '500px' }"
      :closable="!isProcessingPayment"
      :closeOnEscape="!isProcessingPayment"
    >
      <PaymentForm 
        v-if="showPaymentDialog"
        :amount="taxReturn.total_tax_due"
        :due-date="taxReturn.due_date"
        :tax-return-id="taxReturn.id"
        @payment-submitted="onPaymentSubmitted"
        @cancel="showPaymentDialog = false"
      />
    </Dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';
import { format } from 'date-fns';
import TaxAttachmentList from '@/modules/tax/components/TaxAttachmentList.vue';
import PaymentForm from '@/components/payments/PaymentForm.vue';
import { useTaxReturnStore } from '../store/tax-return';

export default defineComponent({
  name: 'TaxReturnDetail',
  components: {
    TaxAttachmentList,
    PaymentForm
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const toast = useToast();
    const { t } = useI18n();
    const taxReturnStore = useTaxReturnStore();
    
    const taxReturnId = ref(route.params.id as string);
    const taxReturn = ref<any>({});
    const isLoading = ref(false);
    const error = ref<string | null>(null);
    const isFiling = ref(false);
    const showPaymentDialog = ref(false);
    const isProcessingPayment = ref(false);
    const isLoadingAuditLogs = ref(false);
    const auditLogs = ref<any[]>([]);
    
    // Mock data - replace with actual API calls
    const filingHistory = ref([
      { status: 'Draft Created', timestamp: new Date(), notes: 'Initial draft' },
      { status: 'Calculated', timestamp: new Date(Date.now() - 86400000), notes: 'Tax calculation completed' },
      { status: 'Submitted', timestamp: new Date(Date.now() - 172800000), notes: 'Submitted to tax authority' },
    ]);
    
    const breadcrumbHome = {
      icon: 'pi pi-home',
      to: '/dashboard'
    };
    
    const breadcrumbItems = computed(() => [
      { label: 'Tax', to: '/tax' },
      { label: 'Returns', to: '/tax/returns' },
      { label: `Return #${taxReturnId.value}`, to: `/tax/returns/${taxReturnId.value}` }
    ]);
    
    // Computed properties
    const isDueSoon = computed(() => {
      if (!taxReturn.value.due_date) return false;
      const dueDate = new Date(taxReturn.value.due_date);
      const today = new Date();
      const diffTime = dueDate.getTime() - today.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays > 0 && diffDays <= 7; // Due within 7 days
    });
    
    const isOverdue = computed(() => {
      if (!taxReturn.value.due_date) return false;
      const dueDate = new Date(taxReturn.value.due_date);
      const today = new Date();
      return dueDate < today && taxReturn.value.status !== 'paid';
    });
    
    // Methods
    const loadTaxReturn = async () => {
      try {
        isLoading.value = true;
        error.value = null;
        
        // Fetch tax return details
        taxReturn.value = await taxReturnStore.getTaxReturnById(taxReturnId.value);
        
        // Load audit logs
        await loadAuditLogs();
      } catch (err: any) {
        console.error('Failed to load tax return:', err);
        error.value = err.response?.data?.message || 'Failed to load tax return details';
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: error.value,
          life: 5000
        });
      } finally {
        isLoading.value = false;
      }
    };
    
    const loadAuditLogs = async () => {
      try {
        isLoadingAuditLogs.value = true;
        // TODO: Replace with actual API call
        // auditLogs.value = await taxReturnStore.getAuditLogs(taxReturnId.value);
        
        // Mock data for now
        auditLogs.value = [
          { 
            id: '1', 
            timestamp: new Date(), 
            action: 'VIEWED', 
            user: 'John Doe', 
            details: 'Viewed tax return details' 
          },
          { 
            id: '2', 
            timestamp: new Date(Date.now() - 3600000), 
            action: 'UPDATED', 
            user: 'Jane Smith', 
            details: 'Updated tax calculation' 
          },
          { 
            id: '3', 
            timestamp: new Date(Date.now() - 86400000), 
            action: 'CREATED', 
            user: 'System', 
            details: 'Created tax return' 
          },
        ];
      } catch (err) {
        console.error('Failed to load audit logs:', err);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load audit logs',
          life: 5000
        });
      } finally {
        isLoadingAuditLogs.value = false;
      }
    };
    
    const editReturn = () => {
      router.push(`/tax/returns/${taxReturnId.value}/edit`);
    };
    
    const fileReturn = async () => {
      try {
        isFiling.value = true;
        
        // TODO: Implement actual filing logic
        // await taxReturnStore.fileTaxReturn(taxReturnId.value);
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Tax return filed successfully',
          life: 5000
        });
        
        // Refresh the tax return data
        await loadTaxReturn();
      } catch (err: any) {
        console.error('Failed to file tax return:', err);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: err.response?.data?.message || 'Failed to file tax return',
          life: 5000
        });
      } finally {
        isFiling.value = false;
      }
    };
    
    const initiatePayment = () => {
      showPaymentDialog.value = true;
    };
    
    const onPaymentSubmitted = async (paymentData: any) => {
      try {
        isProcessingPayment.value = true;
        
        // TODO: Implement actual payment submission
        // await taxReturnStore.submitPayment(taxReturnId.value, paymentData);
        
        toast.add({
          severity: 'success',
          summary: 'Payment Submitted',
          detail: 'Your payment has been submitted successfully',
          life: 5000
        });
        
        // Close the dialog and refresh data
        showPaymentDialog.value = false;
        await loadTaxReturn();
      } catch (err: any) {
        console.error('Payment submission failed:', err);
        toast.add({
          severity: 'error',
          summary: 'Payment Failed',
          detail: err.response?.data?.message || 'Failed to process payment',
          life: 5000
        });
      } finally {
        isProcessingPayment.value = false;
      }
    };
    
    const goBack = () => {
      router.push('/tax/returns');
    };
    
    const formatDate = (dateString: string) => {
      if (!dateString) return 'N/A';
      return format(new Date(dateString), 'MMM d, yyyy');
    };
    
    const formatDateTime = (date: Date) => {
      return format(date, 'MMM d, yyyy h:mm a');
    };
    
    const formatCurrency = (amount: number) => {
      if (amount === undefined || amount === null) return '$0.00';
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount);
    };
    
    const getStatusSeverity = (status: string) => {
      switch (status?.toLowerCase()) {
        case 'draft':
          return 'warning';
        case 'filed':
          return 'info';
        case 'paid':
          return 'success';
        case 'overdue':
          return 'danger';
        case 'processing':
          return 'info';
        default:
          return 'secondary';
      }
    };
    
    const getPaymentStatusSeverity = (status: string) => {
      switch (status?.toLowerCase()) {
        case 'paid':
          return 'success';
        case 'pending':
          return 'warning';
        case 'failed':
          return 'danger';
        case 'refunded':
          return 'info';
        default:
          return 'secondary';
      }
    };
    
    // Lifecycle hooks
    onMounted(() => {
      loadTaxReturn();
    });
    
    return {
      // Refs
      taxReturnId,
      taxReturn,
      isLoading,
      error,
      isFiling,
      showPaymentDialog,
      isProcessingPayment,
      filingHistory,
      auditLogs,
      isLoadingAuditLogs,
      breadcrumbHome,
      breadcrumbItems,
      
      // Computed
      isDueSoon,
      isOverdue,
      
      // Methods
      loadTaxReturn,
      editReturn,
      fileReturn,
      initiatePayment,
      onPaymentSubmitted,
      goBack,
      formatDate,
      formatDateTime,
      formatCurrency,
      getStatusSeverity,
      getPaymentStatusSeverity
    };
  }
});
</script>

<style scoped>
.tax-return-detail {
  padding: 1rem;
}

:deep(.p-timeline-event-opposite) {
  display: none;
}

:deep(.p-timeline-event-content) {
  padding: 0.5rem 0;
}

:deep(.p-timeline-event-connector) {
  background-color: var(--surface-d);
}
</style>
