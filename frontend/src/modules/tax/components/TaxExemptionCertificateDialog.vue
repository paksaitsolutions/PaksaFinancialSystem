<template>
  <v-dialog
    v-model="dialog"
    :max-width="800"
    persistent
    @keydown.esc="close"
  >
    <v-card>
      <v-card-title class="text-h5">
        {{ isEdit ? 'Edit' : 'Add New' }} Tax Exemption Certificate
      </v-card-title>
      
      <v-card-text>
        <TaxExemptionCertificateForm
          ref="form"
          :certificate="certificate"
          :loading="loading"
          @submit="save"
          @cancel="close"
        />
      </v-card-text>
      
      <v-card-actions>
        <v-spacer />
        <v-btn
          text
          color="grey"
          :disabled="loading"
          @click="close"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          :loading="loading"
          @click="submitForm"
        >
          {{ isEdit ? 'Update' : 'Save' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from '@vue/composition-api';
import TaxExemptionCertificateForm from './TaxExemptionCertificateForm.vue';

export default defineComponent({
  name: 'TaxExemptionCertificateDialog',
  
  components: {
    TaxExemptionCertificateForm,
  },
  
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    certificate: {
      type: Object,
      default: null,
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  
  setup(props, { emit }) {
    const dialog = ref(props.value);
    const form = ref<any>(null);
    const isEdit = ref(!!props.certificate?.id);
    
    watch(() => props.value, (val) => {
      dialog.value = val;
    });
    
    watch(() => props.certificate, (val) => {
      isEdit.value = !!(val && val.id);
    }, { immediate: true });
    
    const close = () => {
      dialog.value = false;
      emit('input', false);
      emit('close');
    };
    
    const save = async (data: any) => {
      emit('save', data);
    };
    
    const submitForm = () => {
      if (form.value) {
        form.value.submit();
      }
    };
    
    return {
      dialog,
      form,
      isEdit,
      close,
      save,
      submitForm,
    };
  },
});
</script>
