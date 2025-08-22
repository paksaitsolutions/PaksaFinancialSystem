<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>GL Account Details</v-card-title>
          <v-card-text>
            <v-form ref="form" v-model="valid">
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model="account.code"
                    label="Account Code"
                    :rules="[rules.required]"
                    required
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model="account.name"
                    label="Account Name"
                    :rules="[rules.required]"
                    required
                  />
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="6">
                  <v-select
                    v-model="account.type"
                    :items="accountTypes"
                    label="Account Type"
                    :rules="[rules.required]"
                    required
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model="account.balance"
                    label="Balance"
                    type="number"
                    readonly
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="primary" :disabled="!valid" @click="saveAccount">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';

const valid = ref(false);

const account = reactive({
  code: '',
  name: '',
  type: '',
  balance: 0
});

const accountTypes = [
  'Asset',
  'Liability',
  'Equity',
  'Revenue',
  'Expense'
];

const rules = {
  required: (value: string) => !!value || 'Required'
};

const saveAccount = () => {
  console.log('Saving account:', account);
};
</script>