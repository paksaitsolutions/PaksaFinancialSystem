<template>
  <v-form ref="form" v-model="valid">
    <v-row>
      <v-col cols="12" md="6">
        <v-text-field
          v-model="assetData.asset_number"
          label="Asset Number"
          :rules="[v => !!v || 'Asset number is required']"
          required
        ></v-text-field>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-text-field
          v-model="assetData.name"
          label="Asset Name"
          :rules="[v => !!v || 'Name is required']"
          required
        ></v-text-field>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" md="6">
        <v-select
          v-model="assetData.category"
          :items="categories"
          label="Category"
          :rules="[v => !!v || 'Category is required']"
          required
        ></v-select>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-text-field
          v-model="assetData.location"
          label="Location"
        ></v-text-field>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" md="6">
        <v-text-field
          v-model="assetData.purchase_date"
          label="Purchase Date"
          type="date"
          :rules="[v => !!v || 'Purchase date is required']"
          required
        ></v-text-field>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-text-field
          v-model="assetData.purchase_cost"
          label="Purchase Cost"
          type="number"
          prefix="$"
          :rules="[v => !!v || 'Cost is required', v => v > 0 || 'Cost must be positive']"
          required
        ></v-text-field>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" md="6">
        <v-text-field
          v-model="assetData.useful_life_years"
          label="Useful Life (Years)"
          type="number"
          :rules="[v => !!v || 'Useful life is required', v => v > 0 || 'Must be positive']"
          required
        ></v-text-field>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-text-field
          v-model="assetData.salvage_value"
          label="Salvage Value"
          type="number"
          prefix="$"
        ></v-text-field>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12" md="6">
        <v-select
          v-model="assetData.depreciation_method"
          :items="depreciationMethods"
          label="Depreciation Method"
          required
        ></v-select>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-text-field
          v-model="assetData.vendor_name"
          label="Vendor Name"
        ></v-text-field>
      </v-col>
    </v-row>
    
    <v-row>
      <v-col cols="12">
        <v-textarea
          v-model="assetData.description"
          label="Description"
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
          Save Asset
        </v-btn>
      </v-col>
    </v-row>
  </v-form>
</template>

<script>
export default {
  name: 'AssetForm',
  
  props: {
    asset: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['submit', 'cancel'],
  
  data: () => ({
    valid: false,
    assetData: {
      asset_number: '',
      name: '',
      description: '',
      category: '',
      location: '',
      purchase_date: '',
      purchase_cost: 0,
      salvage_value: 0,
      useful_life_years: 5,
      depreciation_method: 'straight_line',
      vendor_name: ''
    },
    categories: [
      'IT Equipment',
      'Office Furniture',
      'Vehicles',
      'Machinery',
      'Buildings',
      'Other'
    ],
    depreciationMethods: [
      { title: 'Straight Line', value: 'straight_line' },
      { title: 'Declining Balance', value: 'declining_balance' },
      { title: 'Units of Production', value: 'units_of_production' }
    ]
  }),
  
  watch: {
    asset: {
      handler(newAsset) {
        if (newAsset) {
          this.assetData = { ...newAsset }
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
        this.$emit('submit', { ...this.assetData })
      }
    }
  }
}
</script>