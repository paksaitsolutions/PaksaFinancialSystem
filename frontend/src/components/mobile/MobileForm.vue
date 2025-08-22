<template>
  <v-form ref="form" v-model="valid" class="mobile-form">
    <v-container :class="{ 'mobile-container': isMobile }">
      <slot :isMobile="isMobile" :isTablet="isTablet" />
      
      <v-row v-if="showActions" class="mt-4">
        <v-col :cols="isMobile ? 12 : 6">
          <v-btn
            v-if="showCancel"
            :block="isMobile"
            variant="outlined"
            @click="$emit('cancel')"
          >
            Cancel
          </v-btn>
        </v-col>
        <v-col :cols="isMobile ? 12 : 6">
          <v-btn
            :block="isMobile"
            color="primary"
            :loading="loading"
            :disabled="!valid"
            @click="$emit('submit')"
          >
            {{ submitText }}
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script setup>
import { ref } from 'vue'
import { useMobile } from '@/composables/useMobile'

const props = defineProps({
  loading: Boolean,
  showActions: {
    type: Boolean,
    default: true
  },
  showCancel: {
    type: Boolean,
    default: true
  },
  submitText: {
    type: String,
    default: 'Submit'
  }
})

defineEmits(['submit', 'cancel'])

const { isMobile, isTablet } = useMobile()
const form = ref(null)
const valid = ref(false)

const validate = () => {
  return form.value?.validate()
}

const reset = () => {
  form.value?.reset()
}

defineExpose({
  validate,
  reset,
  valid
})
</script>

<style scoped>
.mobile-form .v-text-field,
.mobile-form .v-select,
.mobile-form .v-textarea {
  margin-bottom: 8px;
}

@media (max-width: 600px) {
  .mobile-container {
    padding: 8px !important;
  }
  
  .mobile-form .v-btn {
    margin-bottom: 8px;
  }
}
</style>