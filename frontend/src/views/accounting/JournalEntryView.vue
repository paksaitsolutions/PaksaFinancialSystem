<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Journal Entry</v-card-title>
          <v-card-text>
            <v-form ref="form" v-model="valid">
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model="journalEntry.reference"
                    label="Reference"
                    :rules="[rules.required]"
                    required
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model="journalEntry.date"
                    label="Date"
                    type="date"
                    :rules="[rules.required]"
                    required
                  />
                </v-col>
              </v-row>
              <v-textarea
                v-model="journalEntry.description"
                label="Description"
                rows="3"
              />
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="primary" :disabled="!valid" @click="saveEntry">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';

const valid = ref(false);

const journalEntry = reactive({
  reference: '',
  date: '',
  description: ''
});

const rules = {
  required: (value: string) => !!value || 'Required'
};

const saveEntry = () => {
  // Implementation
  console.log('Saving journal entry:', journalEntry);
};
</script>