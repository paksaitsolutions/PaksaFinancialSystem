<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Tax Exemption Form</v-card-title>
          <v-card-text>
            <v-form ref="form" v-model="valid">
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model="exemption.certificateNumber"
                    label="Certificate Number"
                    :rules="[rules.required]"
                    required
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model="exemption.expiryDate"
                    label="Expiry Date"
                    type="date"
                    :rules="[rules.required]"
                    required
                  />
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12">
                  <v-select
                    v-model="exemption.taxType"
                    :items="taxTypes"
                    label="Tax Type"
                    :rules="[rules.required]"
                    required
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="primary" :disabled="!valid" @click="saveExemption">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';

const valid = ref(false);

const exemption = reactive({
  certificateNumber: '',
  expiryDate: '',
  taxType: ''
});

const taxTypes = [
  'Sales Tax',
  'VAT',
  'GST',
  'Use Tax'
];

const rules = {
  required: (value: string) => !!value || 'Required'
};

const saveExemption = () => {
  console.log('Saving exemption:', exemption);
};
</script>