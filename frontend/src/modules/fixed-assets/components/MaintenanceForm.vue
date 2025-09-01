<template>
  <div class="maintenance-form">
    <div class="grid">
      <div class="col-12 md:col-6">
        <label for="asset_id" class="block text-900 font-medium mb-2">Asset</label>
        <Dropdown
          id="asset_id"
          v-model="formData.asset_id"
          :options="assets"
          optionLabel="name"
          optionValue="id"
          placeholder="Select Asset"
          class="w-full"
        />
      </div>
      
      <div class="col-12 md:col-6">
        <label for="maintenance_type" class="block text-900 font-medium mb-2">Maintenance Type</label>
        <Dropdown
          id="maintenance_type"
          v-model="formData.maintenance_type"
          :options="maintenanceTypes"
          placeholder="Select Type"
          class="w-full"
        />
      </div>
      
      <div class="col-12">
        <label for="description" class="block text-900 font-medium mb-2">Description</label>
        <Textarea
          id="description"
          v-model="formData.description"
          rows="3"
          class="w-full"
          placeholder="Enter maintenance description"
        />
      </div>
      
      <div class="col-12 md:col-6">
        <label for="scheduled_date" class="block text-900 font-medium mb-2">Scheduled Date</label>
        <Calendar
          id="scheduled_date"
          v-model="formData.scheduled_date"
          dateFormat="yy-mm-dd"
          class="w-full"
        />
      </div>
      
      <div class="col-12 md:col-6">
        <label for="estimated_cost" class="block text-900 font-medium mb-2">Estimated Cost</label>
        <InputNumber
          id="estimated_cost"
          v-model="formData.estimated_cost"
          mode="currency"
          currency="USD"
          locale="en-US"
          class="w-full"
        />
      </div>
      
      <div class="col-12 md:col-6">
        <label for="vendor_name" class="block text-900 font-medium mb-2">Vendor Name</label>
        <InputText
          id="vendor_name"
          v-model="formData.vendor_name"
          class="w-full"
          placeholder="Enter vendor name"
        />
      </div>
      
      <div class="col-12">
        <label for="notes" class="block text-900 font-medium mb-2">Notes</label>
        <Textarea
          id="notes"
          v-model="formData.notes"
          rows="2"
          class="w-full"
          placeholder="Additional notes"
        />
      </div>
    </div>
    
    <div class="flex justify-content-end gap-2 mt-4">
      <Button
        label="Cancel"
        icon="pi pi-times"
        outlined
        @click="$emit('cancel')"
      />
      <Button
        label="Save"
        icon="pi pi-check"
        :loading="loading"
        @click="handleSubmit"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'MaintenanceForm',
  
  props: {
    maintenance: {
      type: Object,
      default: () => ({})
    },
    assets: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['submit', 'cancel'],
  
  data() {
    return {
      formData: {
        asset_id: null,
        maintenance_type: 'Preventive',
        description: '',
        scheduled_date: new Date(),
        estimated_cost: 0,
        vendor_name: '',
        notes: ''
      },
      maintenanceTypes: [
        'Preventive',
        'Corrective',
        'Emergency',
        'Routine'
      ]
    }
  },
  
  watch: {
    maintenance: {
      handler(newVal) {
        if (newVal) {
          this.formData = { ...newVal }
        }
      },
      immediate: true
    }
  },
  
  methods: {
    handleSubmit() {
      this.$emit('submit', this.formData)
    }
  }
}
</script>