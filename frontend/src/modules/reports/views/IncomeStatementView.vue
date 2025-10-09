<template>
  <div class="income-statement">
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <h2 class="m-0">Income Statement</h2>
          <div class="flex gap-2">
            <Button icon="pi pi-download" label="Export" severity="secondary" />
            <Button icon="pi pi-print" label="Print" severity="secondary" />
          </div>
        </div>
      </template>
      
      <template #content>
        <div class="statement-content">
          <div class="statement-section">
            <h3>Revenue</h3>
            <div class="line-item">
              <span>Sales Revenue</span>
              <span>$1,250,000</span>
            </div>
            <div class="line-item">
              <span>Service Revenue</span>
              <span>$350,000</span>
            </div>
            <div class="line-item total">
              <span>Total Revenue</span>
              <span>$1,600,000</span>
            </div>
          </div>

          <div class="statement-section">
            <h3>Cost of Goods Sold</h3>
            <div class="line-item">
              <span>Materials</span>
              <span>$400,000</span>
            </div>
            <div class="line-item">
              <span>Labor</span>
              <span>$300,000</span>
            </div>
            <div class="line-item total">
              <span>Total COGS</span>
              <span>$700,000</span>
            </div>
          </div>

          <div class="line-item gross-profit">
            <span>Gross Profit</span>
            <span>$900,000</span>
          </div>

          <div class="statement-section">
            <h3>Operating Expenses</h3>
            <div class="line-item">
              <span>Salaries & Benefits</span>
              <span>$250,000</span>
            </div>
            <div class="line-item">
              <span>Rent</span>
              <span>$60,000</span>
            </div>
            <div class="line-item">
              <span>Utilities</span>
              <span>$25,000</span>
            </div>
            <div class="line-item">
              <span>Marketing</span>
              <span>$45,000</span>
            </div>
            <div class="line-item total">
              <span>Total Operating Expenses</span>
              <span>$380,000</span>
            </div>
          </div>

          <div class="line-item operating-income">
            <span>Operating Income</span>
            <span>$520,000</span>
          </div>

          <div class="statement-section">
            <h3>Other Income/Expenses</h3>
            <div class="line-item">
              <span>Interest Income</span>
              <span>$5,000</span>
            </div>
            <div class="line-item">
              <span>Interest Expense</span>
              <span>($15,000)</span>
            </div>
          </div>

          <div class="line-item net-income">
            <span>Net Income</span>
            <span>$510,000</span>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
// Income Statement component
</script>

<style scoped>
.income-statement {
  padding: 1.5rem;
}

.statement-content {
  max-width: 800px;
  margin: 0 auto;
}

.statement-section {
  margin-bottom: 2rem;
  padding: 1rem;
  border: 1px solid var(--surface-border);
  border-radius: 6px;
}

.statement-section h3 {
  margin: 0 0 1rem 0;
  color: var(--primary-color);
  font-weight: 600;
}

.line-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--surface-200);
}

.line-item:last-child {
  border-bottom: none;
}

.line-item.total {
  font-weight: 600;
  border-top: 2px solid var(--surface-300);
  margin-top: 0.5rem;
  padding-top: 0.75rem;
}

.line-item.gross-profit,
.line-item.operating-income,
.line-item.net-income {
  font-weight: 700;
  font-size: 1.1rem;
  background: var(--surface-50);
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 6px;
  border: 2px solid var(--primary-color);
}

.line-item.net-income {
  background: var(--green-50);
  border-color: var(--green-500);
  color: var(--green-700);
}
</style>