<template>
  <div class="gl-reporting-dashboard">
    <h1>General Ledger Reports</h1>
    
    <div class="grid">
      <div class="col-12 md:col-6 lg:col-4">
        <Card>
          <template #title>Trial Balance</template>
          <template #content>
            <p>View trial balance report</p>
            <Button label="View Report" @click="$router.push('/gl/trial-balance')" />
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:col-4">
        <Card>
          <template #title>Financial Statements</template>
          <template #content>
            <p>Generate financial statements</p>
            <Button label="View Statements" @click="$router.push('/gl/financial-statements')" />
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:col-4">
        <Card>
          <template #title>Journal Entries</template>
          <template #content>
            <p>View journal entries</p>
            <Button label="View Entries" @click="$router.push('/gl/journal-entries')" />
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// GL Reporting Dashboard
</script>

<style scoped>
.gl-reporting-dashboard {
  padding: 1rem;
}
</style>