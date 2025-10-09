<template>
  <div class="cash-flow">
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <h2 class="m-0">Cash Flow Statement</h2>
          <div class="flex gap-2">
            <Button icon="pi pi-download" label="Export" severity="secondary" />
            <Button icon="pi pi-print" label="Print" severity="secondary" />
          </div>
        </div>
      </template>
      
      <template #content>
        <div class="statement-content">
          <div class="statement-section">
            <h3>Cash Flows from Operating Activities</h3>
            <div class="line-item">
              <span>Net Income</span>
              <span>$510,000</span>
            </div>
            <div class="subsection">
              <h4>Adjustments to reconcile net income:</h4>
              <div class="line-item">
                <span>Depreciation</span>
                <span>$45,000</span>
              </div>
              <div class="line-item">
                <span>Accounts Receivable (increase)</span>
                <span>($25,000)</span>
              </div>
              <div class="line-item">
                <span>Inventory (increase)</span>
                <span>($15,000)</span>
              </div>
              <div class="line-item">
                <span>Accounts Payable increase</span>
                <span>$20,000</span>
              </div>
            </div>
            <div class="line-item total">
              <span>Net Cash from Operating Activities</span>
              <span>$535,000</span>
            </div>
          </div>

          <div class="statement-section">
            <h3>Cash Flows from Investing Activities</h3>
            <div class="line-item">
              <span>Purchase of Equipment</span>
              <span>($75,000)</span>
            </div>
            <div class="line-item">
              <span>Sale of Investments</span>
              <span>$30,000</span>
            </div>
            <div class="line-item total">
              <span>Net Cash from Investing Activities</span>
              <span>($45,000)</span>
            </div>
          </div>

          <div class="statement-section">
            <h3>Cash Flows from Financing Activities</h3>
            <div class="line-item">
              <span>Loan Proceeds</span>
              <span>$100,000</span>
            </div>
            <div class="line-item">
              <span>Loan Repayments</span>
              <span>($50,000)</span>
            </div>
            <div class="line-item">
              <span>Dividends Paid</span>
              <span>($80,000)</span>
            </div>
            <div class="line-item total">
              <span>Net Cash from Financing Activities</span>
              <span>($30,000)</span>
            </div>
          </div>

          <div class="cash-summary">
            <div class="line-item">
              <span>Net Increase in Cash</span>
              <span>$460,000</span>
            </div>
            <div class="line-item">
              <span>Cash at Beginning of Period</span>
              <span>$125,000</span>
            </div>
            <div class="line-item final-cash">
              <span>Cash at End of Period</span>
              <span>$585,000</span>
            </div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
// Cash Flow Statement component
</script>

<style scoped>
.cash-flow {
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

.subsection {
  margin: 1rem 0;
  padding-left: 1rem;
}

.subsection h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: var(--text-color-secondary);
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
  background: var(--surface-50);
}

.cash-summary {
  margin-top: 2rem;
  padding: 1rem;
  background: var(--surface-50);
  border-radius: 6px;
  border: 2px solid var(--primary-color);
}

.line-item.final-cash {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--green-700);
  border-top: 2px solid var(--green-500);
  margin-top: 0.5rem;
  padding-top: 0.75rem;
}
</style>