<template>
  <Card class="mb-4">
    <template #title>
      <div class="flex align-items-center">
        <i class="pi pi-filter mr-2" style="font-size: 1.25rem"></i>
        <span>Filters</span>
      </div>
    </template>
    <template #content>
      <div class="grid">
        <div class="col-12 md:col-6 lg:col-3">
          <div class="field">
            <label for="dateRange">Date Range</label>
            <Calendar 
              id="dateRange"
              v-model="localDateRange" 
              selectionMode="range" 
              :manualInput="false"
              :showIcon="true"
              dateFormat="yy-mm-dd"
              :maxDate="new Date()"
              class="w-full"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6 lg:col-3">
          <div class="field">
            <label for="taxType">Tax Type</label>
            <MultiSelect
              id="taxType"
              v-model="localSelectedTaxTypes"
              :options="availableTaxTypes"
              optionLabel="name"
              optionValue="code"
              placeholder="All Tax Types"
              display="chip"
              class="w-full"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6 lg:col-3">
          <div class="field">
            <label for="jurisdiction">Jurisdiction</label>
            <MultiSelect
              id="jurisdiction"
              v-model="localSelectedJurisdictions"
              :options="availableJurisdictions"
              optionLabel="name"
              optionValue="code"
              placeholder="All Jurisdictions"
              display="chip"
              class="w-full"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6 lg:3">
          <div class="field">
            <label for="groupBy">Group By</label>
            <Dropdown
              id="groupBy"
              v-model="localGroupBy"
              :options="groupByOptions"
              optionLabel="name"
              optionValue="value"
              placeholder="Group By"
              class="w-full"
            />
          </div>
        </div>
        
        <div class="col-12 flex justify-content-end gap-2 mt-3">
          <Button 
            label="Reset" 
            icon="pi pi-refresh" 
            @click="handleReset" 
            class="p-button-text"
            :disabled="isLoading"
          />
          <Button 
            label="Apply Filters" 
            icon="pi pi-check" 
            @click="handleApply" 
            :loading="isLoading"
          />
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps({
  dateRange: {
    type: Array,
    default: () => []
  },
  selectedTaxTypes: {
    type: Array,
    default: () => []
  },
  selectedJurisdictions: {
    type: Array,
    default: () => []
  },
  groupBy: {
    type: String,
    default: 'month'
  },
  availableTaxTypes: {
    type: Array,
    default: () => []
  },
  availableJurisdictions: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits([
  'update:dateRange',
  'update:selectedTaxTypes',
  'update:selectedJurisdictions',
  'update:groupBy',
  'apply-filters',
  'reset-filters'
]);

// Local state
const localDateRange = ref([...props.dateRange]);
const localSelectedTaxTypes = ref([...props.selectedTaxTypes]);
const localSelectedJurisdictions = ref([...props.selectedJurisdictions]);
const localGroupBy = ref(props.groupBy);

// Group by options
const groupByOptions = [
  { name: 'Daily', value: 'day' },
  { name: 'Weekly', value: 'week' },
  { name: 'Monthly', value: 'month' },
  { name: 'Quarterly', value: 'quarter' },
  { name: 'Yearly', value: 'year' }
];

// Watch for prop changes and update local state
watch(() => props.dateRange, (newVal) => {
  localDateRange.value = [...newVal];
}, { deep: true });

watch(() => props.selectedTaxTypes, (newVal) => {
  localSelectedTaxTypes.value = [...newVal];
}, { deep: true });

watch(() => props.selectedJurisdictions, (newVal) => {
  localSelectedJurisdictions.value = [...newVal];
}, { deep: true });

watch(() => props.groupBy, (newVal) => {
  localGroupBy.value = newVal;
});

// Emit update events when local state changes
watch(localDateRange, (newVal) => {
  emit('update:dateRange', [...newVal]);
}, { deep: true });

watch(localSelectedTaxTypes, (newVal) => {
  emit('update:selectedTaxTypes', [...newVal]);
}, { deep: true });

watch(localSelectedJurisdictions, (newVal) => {
  emit('update:selectedJurisdictions', [...newVal]);
}, { deep: true });

watch(localGroupBy, (newVal) => {
  emit('update:groupBy', newVal);
});

// Handle apply button click
const handleApply = () => {
  emit('apply-filters');
};

// Handle reset button click
const handleReset = () => {
  // Reset local state to default values
  const today = new Date();
  const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
  
  localDateRange.value = [firstDayOfMonth, today];
  localSelectedTaxTypes.value = [];
  localSelectedJurisdictions.value = [];
  localGroupBy.value = 'month';
  
  // Emit reset event
  emit('reset-filters');
};
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .grid > div {
    margin-bottom: 1rem;
  }
}
</style>
