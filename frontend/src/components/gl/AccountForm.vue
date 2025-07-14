<template>
  <v-card>
    <v-card-title>
      {{ isEdit ? 'Edit Account' : 'Create Account' }}
    </v-card-title>
    
    <v-card-text>
      <v-form ref="form" v-model="valid" @submit.prevent="handleSubmit">
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formData.account_code"
              label="Account Code"
              :rules="[rules.required]"
              :disabled="isEdit"
              required
            />
          </v-col>
          
          <v-col cols="12" md="6">
            <v-select
              v-model="formData.account_type"
              :items="accountTypes"
              label="Account Type"
              :rules="[rules.required]"
              required
            />
          </v-col>
        </v-row>
        
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="formData.account_name"
              label="Account Name"
              :rules="[rules.required]"
              required
            />
          </v-col>
        </v-row>
        
        <v-row>
          <v-col cols="12">
            <v-textarea
              v-model="formData.description"
              label="Description"
              rows="3"
            />
          </v-col>
        </v-row>
        
        <v-row>
          <v-col cols="12">
            <v-switch
              v-model="formData.is_active"
              label="Active"
            />
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
    
    <v-card-actions>
      <v-spacer />
      <v-btn @click="$emit('cancel')">Cancel</v-btn>
      <v-btn 
        color="primary" 
        :loading="loading"
        :disabled="!valid"
        @click="handleSubmit"
      >
        {{ isEdit ? 'Update' : 'Create' }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useGLStore } from '@/store/glAccounts'

interface Props {
  account?: any
  isEdit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isEdit: false
})

const emit = defineEmits<{
  cancel: []
  success: [account: any]
}>()

const glStore = useGLStore()
const form = ref()
const valid = ref(false)
const loading = ref(false)

const accountTypes = [
  { title: 'Asset', value: 'asset' },
  { title: 'Liability', value: 'liability' },
  { title: 'Equity', value: 'equity' },
  { title: 'Revenue', value: 'revenue' },
  { title: 'Expense', value: 'expense' }
]

const formData = reactive({
  account_code: '',
  account_name: '',
  account_type: '',
  description: '',
  is_active: true
})

const rules = {
  required: (value: any) => !!value || 'This field is required'
}

const isEdit = computed(() => props.isEdit)

onMounted(() => {
  if (props.account) {
    Object.assign(formData, props.account)
  }
})

const handleSubmit = async () => {
  if (!valid.value) return
  
  loading.value = true
  try {
    let result
    if (isEdit.value) {
      result = await glStore.updateAccount(props.account.id, formData)
    } else {
      result = await glStore.createAccount(formData)
    }
    emit('success', result)
  } catch (error) {
    console.error('Error saving account:', error)
  } finally {
    loading.value = false
  }
}
</script>