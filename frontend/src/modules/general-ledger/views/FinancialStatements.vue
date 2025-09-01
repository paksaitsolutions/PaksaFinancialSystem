<template>
  <div class="financial-statements">
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <Button icon="pi pi-arrow-left" class="p-button-text" @click="$router.go(-1)" />
          <div>
            <h1>Financial Statements</h1>
            <p class="subtitle">Generate Balance Sheet, Income Statement, and Cash Flow reports</p>
          </div>
        </div>
      </div>
    </div>

    <div class="content-container">
      <Card>
        <template #content>
          <div class="text-center p-6">
            <i class="pi pi-chart-bar text-6xl text-primary mb-4"></i>
            <h3 class="mb-3">Financial Statements</h3>
            <p class="text-600 mb-4">Generate comprehensive financial reports including Balance Sheet, Income Statement, and Cash Flow Statement.</p>
            <Button label="Back to Dashboard" @click="$router.push('/gl')" />
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
// Placeholder component
</script>

<style scoped>
.financial-statements {
  padding: 0;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-left h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: #1f2937;
}

.subtitle {
  margin: 0.25rem 0 0 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem 2rem;
}
</style>