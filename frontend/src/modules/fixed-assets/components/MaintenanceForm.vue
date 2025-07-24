<template>
  <v-form ref="form" v-model="valid">
    <v-row>
      <v-col cols="12">
        <v-select
          v-model="maintenanceData.asset_id"
          :items="assets"
          item-title="name"
          item-value="id"
          label="Asset"
          :rules="[v => !!v || 'Asset is required']"
          required
        ></v-select>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" md="6">
        <v-select
          v-model="maintenanceData.maintenance_type"
          :items="maintenanceTypes"
          label="Maintenance Type"
          :rules="[v => !!v || 'Type is required']"
          required
        ></v-select>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-text-field
          v-model="maintenanceData.scheduled_date"
          label="Scheduled Date"
          type="date"
          :rules="[v => !!v || 'Date is required']"
          required
        ></v-text-field>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12">
        <v-textarea
          v-model="maintenanceData.description"
          label="Description"
          :rules="[v => !!v || 'Description is required']"
          required
        ></v-textarea>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" md="6">
        <v-text-field
          v-model="maintenanceData.estimated_cost"
          label="Estimated Cost"
          type="number"
          prefix="$"
        ></v-text-field>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-text-field
          v-model="maintenanceData.vendor_name"
          label="Vendor Name"
        ></v-text-field>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12">
        <v-textarea
          v-model="maintenanceData.notes"
          label="Notes"
          rows="3"
        ></v-textarea>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" class="d-flex justify-end">
        <v-btn @click="$emit('cancel')" class="mr-2">Cancel</v-btn>
        <v-btn 
          color="primary" 
          @click="submit" 
          :disabled="!valid || loading"
          :loading="loading"
        >
          Save Maintenance
        </v-btn>
      </v-col>
    </v-row>
  </v-form>
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
  
  data: () => ({
    valid: false,
    maintenanceData: {
      asset_id: null,
      maintenance_type: 'Preventive',
      description: '',
      scheduled_date: '',
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
  }),
  
  watch: {
    maintenance: {
      handler(newMaintenance) {
        if (newMaintenance) {
          this.maintenanceData = { ...newMaintenance }
        }
      },
      immediate: true,
      deep: true
    }
  },
  
  methods: {
    async submit() {
      const { valid } = await this.$refs.form.validate()
      if (valid) {
        this.$emit('submit', { ...this.maintenanceData })
      }
    }
  }
}
</script>