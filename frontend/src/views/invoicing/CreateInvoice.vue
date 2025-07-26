<template>
  <v-container>
    <v-row>
      <v-col>
        <h1 class="text-h4 mb-4">Create New Invoice</h1>
        <v-card>
          <v-card-title>Invoice Details</v-card-title>
          <v-card-text>
            <v-form>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field label="Customer" variant="outlined" required />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field label="Invoice Number" variant="outlined" required />
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field label="Date" type="date" variant="outlined" required />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field label="Due Date" type="date" variant="outlined" required />
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12">
                  <v-textarea label="Description" variant="outlined" rows="3" />
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field label="Amount" type="number" variant="outlined" prefix="$" required />
                </v-col>
                <v-col cols="12" md="6">
                  <v-select label="Status" :items="['Draft', 'Sent', 'Paid', 'Overdue']" variant="outlined" required />
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="primary">Create Invoice</v-btn>
            <v-btn variant="outlined" @click="$router.go(-1)">Cancel</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
// Create invoice functionality
</script>