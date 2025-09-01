<template>
  <form @submit.prevent="submit">
    <div class="grid">
      <div class="col-12 md:col-6">
        <InputText
          v-model="assetData.asset_number"
          placeholder="Asset Number"
          :class="{ 'p-invalid': errors.asset_number }"
          class="w-full"
        />
        <small v-if="errors.asset_number" class="p-error">{{ errors.asset_number }}</small>
      </div>
      
      <div class="col-12 md:col-6">
        <InputText
          v-model="assetData.name"
          placeholder="Asset Name"
          :class="{ 'p-invalid': errors.name }"
          class="w-full"
        />
        <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
      </div>
    </div>
    
    <div class="grid">
      <div class="col-12 md:col-6">
        <Dropdown
          v-model="assetData.category"
          :options="categories"
          placeholder="Category"
          :class="{ 'p-invalid': errors.category }"
          class="w-full"
        />
        <small v-if="errors.category" class="p-error">{{ errors.category }}</small>
      </div>
      
      <div class="col-12 md:col-6">
        <InputText
          v-model="assetData.location"
          placeholder="Location"
          class="w-full"
        />
      </div>
    </div>
    
    <div class="grid">
      <div class="col-12 md:col-6">
        <Calendar
          v-model="assetData.purchase_date"
          placeholder="Purchase Date"
          dateFormat="yy-mm-dd"
          :class="{ 'p-invalid': errors.purchase_date }"
          class="w-full"
        />
        <small v-if="errors.purchase_date" class="p-error">{{ errors.purchase_date }}</small>
      </div>
      
      <div class="col-12 md:col-6">
        <InputNumber
          v-model="assetData.purchase_cost"
          placeholder="Purchase Cost"
          mode="currency"
          currency="USD"
          :class="{ 'p-invalid': errors.purchase_cost }"
          class="w-full"
        />
        <small v-if="errors.purchase_cost" class="p-error">{{ errors.purchase_cost }}</small>
      </div>
    </div>
    
    <div class="grid">
      <div class="col-12 md:col-6">
        <InputNumber
          v-model="assetData.useful_life_years"
          placeholder="Useful Life (Years)"
          :class="{ 'p-invalid': errors.useful_life_years }"
          class="w-full"
        />
        <small v-if="errors.useful_life_years" class="p-error">{{ errors.useful_life_years }}</small>
      </div>
      
      <div class="col-12 md:col-6">
        <InputNumber
          v-model="assetData.salvage_value"
          placeholder="Salvage Value"
          mode="currency"
          currency="USD"
          class="w-full"
        />
      </div>
    </div>
    
    <div class="grid">
      <div class="col-12 md:col-6">
        <Dropdown
          v-model="assetData.depreciation_method"
          :options="depreciationMethods"
          optionLabel="title"
          optionValue="value"
          placeholder="Depreciation Method"
          class="w-full"
        />
      </div>
      
      <div class="col-12 md:col-6">
        <InputText
          v-model="assetData.vendor_name"
          placeholder="Vendor Name"
          class="w-full"
        />
      </div>
    </div>
    
    <div class="grid">
      <div class="col-12">
        <Textarea
          v-model="assetData.description"
          placeholder="Description"
          rows="3"
          class="w-full"
        />
      </div>
    </div>
    
    <div class="flex justify-content-end mt-4">
      <Button 
        label="Cancel" 
        @click="$emit('cancel')" 
        class="mr-2" 
        outlined
      />
      <Button 
        label="Save Asset"
        type="submit"
        :disabled="loading"
        :loading="loading"
      />
    </div>
  </form>
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
    errors: {},
    assetData: {
      asset_number: '',
      name: '',
      description: '',
      category: '',
      location: '',
      purchase_date: null,
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
    validateForm() {
      this.errors = {}
      
      if (!this.assetData.asset_number) {
        this.errors.asset_number = 'Asset number is required'
      }
      
      if (!this.assetData.name) {
        this.errors.name = 'Name is required'
      }
      
      if (!this.assetData.category) {
        this.errors.category = 'Category is required'
      }
      
      if (!this.assetData.purchase_date) {
        this.errors.purchase_date = 'Purchase date is required'
      }
      
      if (!this.assetData.purchase_cost || this.assetData.purchase_cost <= 0) {
        this.errors.purchase_cost = 'Cost is required and must be positive'
      }
      
      if (!this.assetData.useful_life_years || this.assetData.useful_life_years <= 0) {
        this.errors.useful_life_years = 'Useful life is required and must be positive'
      }
      
      return Object.keys(this.errors).length === 0
    },
    
    submit() {
      if (this.validateForm()) {
        this.$emit('submit', { ...this.assetData })
      }
    }
  }
}
</script>