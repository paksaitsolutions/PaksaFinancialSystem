<template>
  <div class="grid">
    <div class="col-12 md:col-6 lg:3">
      <Card class="h-full">
        <template #title>Total Taxable Amount</template>
        <template #content>
          <div class="flex flex-column h-full">
            <div class="text-3xl font-bold text-primary">
              {{ formatCurrency(reportData?.total_taxable_amount || 0, reportData?.currency) }}
            </div>
            <div class="text-500 mt-2">Accumulated taxable base</div>
            <div class="mt-auto pt-2 text-sm text-500">
              <i class="pi pi-info-circle mr-1"></i>
              <span>Total amount subject to tax</span>
            </div>
          </div>
        </template>
      </Card>
    </div>
    
    <div class="col-12 md:col-6 lg:3">
      <Card class="h-full">
        <template #title>Total Tax Amount</template>
        <template #content>
          <div class="flex flex-column h-full">
            <div class="text-3xl font-bold text-primary">
              {{ formatCurrency(reportData?.total_tax_amount || 0, reportData?.currency) }}
            </div>
            <div class="text-500 mt-2">Accumulated tax liability</div>
            <div class="mt-auto pt-2 text-sm text-500">
              <i class="pi pi-info-circle mr-1"></i>
              <span>Total tax calculated</span>
            </div>
          </div>
        </template>
      </Card>
    </div>
    
    <div class="col-12 md:col-6 lg:3">
      <Card class="h-full">
        <template #title>Total Collected</template>
        <template #content>
          <div class="flex flex-column h-full">
            <div class="text-3xl font-bold text-green-500">
              {{ formatCurrency(reportData?.total_collected || 0, reportData?.currency) }}
            </div>
            <div class="text-500 mt-2">Taxes collected from customers</div>
            <div class="mt-auto pt-2 text-sm text-500">
              <i class="pi pi-info-circle mr-1"></i>
              <span>Amount already received</span>
            </div>
          </div>
        </template>
      </Card>
    </div>
    
    <div class="col-12 md:col-6 lg:3">
      <Card class="h-full">
        <template #title>Total Owed</template>
        <template #content>
          <div class="flex flex-column h-full">
            <div class="text-3xl font-bold" :class="getAmountClass(reportData?.total_owed || 0)">
              {{ formatCurrency(reportData?.total_owed || 0, reportData?.currency) }}
            </div>
            <div class="text-500 mt-2">Net tax liability</div>
            <div class="mt-auto pt-2 text-sm" :class="getTextClass(reportData?.total_owed || 0)">
              <i class="pi" :class="getIconClass(reportData?.total_owed || 0)"></i>
              <span class="ml-1">{{ getOwedStatus(reportData?.total_owed || 0) }}</span>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import { formatCurrency } from '@/utils/formatters';

const props = defineProps({
  reportData: {
    type: Object,
    default: () => ({
      total_taxable_amount: 0,
      total_tax_amount: 0,
      total_collected: 0,
      total_owed: 0,
      currency: 'USD'
    })
  }
});

// Helper methods
const getAmountClass = (amount: number) => {
  if (amount === 0) return 'text-500';
  return amount > 0 ? 'text-red-500' : 'text-green-500';
};

const getTextClass = (amount: number) => {
  if (amount === 0) return 'text-500';
  return amount > 0 ? 'text-red-500' : 'text-green-500';
};

const getIconClass = (amount: number) => {
  if (amount === 0) return 'pi-info-circle text-500';
  return amount > 0 ? 'pi-arrow-up-right text-red-500' : 'pi-arrow-down-left text-green-500';
};

const getOwedStatus = (amount: number) => {
  if (amount === 0) return 'No amount owed';
  return amount > 0 
    ? `Owed to tax authorities` 
    : `Overpaid (refund due)`;
};
</script>

<style scoped>
.p-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.p-card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.text-3xl {
  font-size: 1.75rem;
  line-height: 2.25rem;
}

.text-green-500 {
  color: var(--green-500);
}

.text-red-500 {
  color: var(--red-500);
}

.text-500 {
  color: var(--text-color-secondary);
}

.mt-auto {
  margin-top: auto;
}
</style>
