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
          v-model="assetData.asset_name"
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
          v-model="assetData.asset_category"
          :options="categories"
          optionLabel="name"
          optionValue="value"
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
        <InputText
          v-model="assetData.purchase_date"
          type="date"
          placeholder="Purchase Date"
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
        @click="submit"
        :disabled="loading"
        :loading="loading"
      />
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { fixedAssetsService, type FixedAsset } from '@/services/fixedAssetsService'

interface Props {
  asset?: FixedAsset
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  asset: () => ({} as FixedAsset),
  loading: false
})

const emit = defineEmits<{
  submit: [asset: FixedAsset]
  cancel: []
}>()

const errors = ref<Record<string, string>>({})
const categories = ref<{name: string, value: string}[]>([])

const assetData = reactive<Partial<FixedAsset>>({
  asset_number: '',
  asset_name: '',
  asset_category: '',
  location: '',
  purchase_date: '',
  purchase_cost: 0,
  salvage_value: 0,
  useful_life_years: 5,
  depreciation_method: 'straight_line'
})

const depreciationMethods = [
  { title: 'Straight Line', value: 'straight_line' },
  { title: 'Declining Balance', value: 'declining_balance' },
  { title: 'Units of Production', value: 'units_of_production' }
]

const loadCategories = async () => {
  try {
    categories.value = await fixedAssetsService.getCategories()
  } catch (error) {
    console.error('Error loading categories:', error)
    // Fallback categories
    categories.value = [
      { name: 'IT Equipment', value: 'IT Equipment' },
      { name: 'Office Furniture', value: 'Office Furniture' },
      { name: 'Vehicles', value: 'Vehicles' },
      { name: 'Machinery', value: 'Machinery' },
      { name: 'Buildings', value: 'Buildings' },
      { name: 'Other', value: 'Other' }
    ]
  }
}

watch(() => props.asset, (newAsset) => {
  if (newAsset && Object.keys(newAsset).length > 0) {
    Object.assign(assetData, newAsset)
  }
}, { immediate: true, deep: true })

const validateForm = () => {
  errors.value = {}
  
  if (!assetData.asset_number) {
    errors.value.asset_number = 'Asset number is required'
  }
  
  if (!assetData.asset_name) {
    errors.value.name = 'Name is required'
  }
  
  if (!assetData.asset_category) {
    errors.value.category = 'Category is required'
  }
  
  if (!assetData.purchase_date) {
    errors.value.purchase_date = 'Purchase date is required'
  }
  
  if (!assetData.purchase_cost || assetData.purchase_cost <= 0) {
    errors.value.purchase_cost = 'Cost is required and must be positive'
  }
  
  if (!assetData.useful_life_years || assetData.useful_life_years <= 0) {
    errors.value.useful_life_years = 'Useful life is required and must be positive'
  }
  
  return Object.keys(errors.value).length === 0
}

const submit = () => {
  if (validateForm()) {
    emit('submit', { ...assetData } as FixedAsset)
  }
}

onMounted(() => {
  loadCategories()
})
</script>