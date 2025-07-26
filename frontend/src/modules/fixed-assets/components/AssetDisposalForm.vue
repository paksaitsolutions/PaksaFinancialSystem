<template>
  <v-dialog v-model="dialog" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Dispose Asset</span>
      </v-card-title>
      
      <v-card-text>
        <v-form ref="form" v-model="valid">
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="disposalData.disposal_date"
                label="Disposal Date"
                type="date"
                :rules="[rules.required]"
                required
              ></v-text-field>
            </v-col>
            
            <v-col cols="12">
              <v-text-field
                v-model="disposalData.disposal_amount"
                label="Disposal Amount"
                type="number"
                step="0.01"
                :rules="[rules.required, rules.positive]"
                required
              ></v-text-field>
            </v-col>
            
            <v-col cols="12">
              <v-textarea
                v-model="disposalData.disposal_reason"
                label="Disposal Reason"
                :rules="[rules.required]"
                required
              ></v-textarea>
            </v-col>
            
            <v-col cols="12" v-if="gainLoss !== null">
              <v-alert
                :type="gainLoss >= 0 ? 'success' : 'warning'"
                variant="tonal"
              >
                <strong>{{ gainLoss >= 0 ? 'Gain' : 'Loss' }} on Disposal:</strong>
                ${{ Math.abs(gainLoss).toLocaleString() }}
              </v-alert>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text @click="close">Cancel</v-btn>
        <v-btn 
          color="primary" 
          @click="dispose"
          :loading="loading"
          :disabled="!valid"
        >
          Dispose Asset
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'AssetDisposalForm',
  props: {
    modelValue: Boolean,
    asset: Object
  },
  emits: ['update:modelValue', 'disposed'],
  setup(props, { emit }) {
    const form = ref(null)
    const valid = ref(false)
    const loading = ref(false)
    
    const disposalData = ref({
      disposal_date: new Date().toISOString().split('T')[0],
      disposal_amount: 0,
      disposal_reason: ''
    })
    
    const rules = {
      required: value => !!value || 'Required',
      positive: value => value >= 0 || 'Must be positive'
    }
    
    const dialog = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })
    
    const gainLoss = computed(() => {
      if (!props.asset || !disposalData.value.disposal_amount) return null
      const bookValue = props.asset.purchase_cost - props.asset.accumulated_depreciation
      return parseFloat(disposalData.value.disposal_amount) - bookValue
    })
    
    const dispose = async () => {
      if (!form.value.validate()) return
      
      loading.value = true
      try {
        // API call would go here
        emit('disposed', {
          asset_id: props.asset.id,
          ...disposalData.value
        })
        close()
      } catch (error) {
        console.error('Disposal failed:', error)
      } finally {
        loading.value = false
      }
    }
    
    const close = () => {
      dialog.value = false
      disposalData.value = {
        disposal_date: new Date().toISOString().split('T')[0],
        disposal_amount: 0,
        disposal_reason: ''
      }
    }
    
    return {
      form,
      valid,
      loading,
      disposalData,
      rules,
      dialog,
      gainLoss,
      dispose,
      close
    }
  }
}
</script>