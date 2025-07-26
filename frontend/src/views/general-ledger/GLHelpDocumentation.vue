<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Help Topics</v-card-title>
          <v-list>
            <v-list-item 
              v-for="topic in helpTopics" 
              :key="topic.id"
              @click="selectedTopic = topic"
              :class="{ 'v-list-item--active': selectedTopic.id === topic.id }"
            >
              <template v-slot:prepend>
                <v-icon>{{ topic.icon }}</v-icon>
              </template>
              <v-list-item-title>{{ topic.title }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="9">
        <v-card>
          <v-card-title>
            <v-icon left>{{ selectedTopic.icon }}</v-icon>
            {{ selectedTopic.title }}
          </v-card-title>
          
          <v-card-text>
            <div v-html="selectedTopic.content"></div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'GLHelpDocumentation',
  
  data: () => ({
    selectedTopic: null,
    
    helpTopics: [
      {
        id: 1,
        title: 'Getting Started',
        icon: 'mdi-play-circle',
        content: `
          <h3>Welcome to General Ledger</h3>
          <p>The General Ledger is the core of your accounting system. It contains all financial transactions and provides the foundation for financial reporting.</p>
          
          <h4>Key Features:</h4>
          <ul>
            <li>Chart of Accounts management</li>
            <li>Journal Entry processing</li>
            <li>Trial Balance generation</li>
            <li>Financial Statement preparation</li>
            <li>Period-end closing procedures</li>
          </ul>
          
          <h4>Quick Start:</h4>
          <ol>
            <li>Set up your Chart of Accounts</li>
            <li>Configure GL settings</li>
            <li>Start recording journal entries</li>
            <li>Generate reports as needed</li>
          </ol>
        `
      },
      {
        id: 2,
        title: 'Chart of Accounts',
        icon: 'mdi-file-tree',
        content: `
          <h3>Chart of Accounts Management</h3>
          <p>The Chart of Accounts is a listing of all accounts used in your general ledger.</p>
          
          <h4>Account Types:</h4>
          <ul>
            <li><strong>Assets:</strong> Resources owned by the company</li>
            <li><strong>Liabilities:</strong> Debts owed by the company</li>
            <li><strong>Equity:</strong> Owner's interest in the company</li>
            <li><strong>Revenue:</strong> Income earned by the company</li>
            <li><strong>Expenses:</strong> Costs incurred by the company</li>
          </ul>
          
          <h4>Best Practices:</h4>
          <ul>
            <li>Use consistent numbering scheme</li>
            <li>Group similar accounts together</li>
            <li>Keep account names clear and descriptive</li>
            <li>Review and update regularly</li>
          </ul>
          
          <h4>How to Add an Account:</h4>
          <ol>
            <li>Go to Chart of Accounts</li>
            <li>Click "Add Account"</li>
            <li>Enter account code and name</li>
            <li>Select account type</li>
            <li>Save the account</li>
          </ol>
        `
      },
      {
        id: 3,
        title: 'Journal Entries',
        icon: 'mdi-notebook',
        content: `
          <h3>Journal Entry Processing</h3>
          <p>Journal entries record financial transactions using double-entry bookkeeping principles.</p>
          
          <h4>Double-Entry Bookkeeping:</h4>
          <p>Every transaction affects at least two accounts, with total debits equaling total credits.</p>
          
          <h4>Creating Journal Entries:</h4>
          <ol>
            <li>Navigate to Journal Entries</li>
            <li>Click "New Entry"</li>
            <li>Enter entry date and description</li>
            <li>Add debit and credit lines</li>
            <li>Ensure debits equal credits</li>
            <li>Save and post the entry</li>
          </ol>
          
          <h4>Common Entry Types:</h4>
          <ul>
            <li>Sales transactions</li>
            <li>Purchase transactions</li>
            <li>Adjusting entries</li>
            <li>Closing entries</li>
            <li>Correcting entries</li>
          </ul>
          
          <h4>Tips:</h4>
          <ul>
            <li>Use clear, descriptive references</li>
            <li>Review entries before posting</li>
            <li>Keep supporting documentation</li>
            <li>Follow company policies</li>
          </ul>
        `
      },
      {
        id: 4,
        title: 'Trial Balance',
        icon: 'mdi-scale-balance',
        content: `
          <h3>Trial Balance Reports</h3>
          <p>The Trial Balance lists all accounts with their debit and credit balances to verify that debits equal credits.</p>
          
          <h4>Purpose:</h4>
          <ul>
            <li>Verify accounting equation balance</li>
            <li>Detect posting errors</li>
            <li>Prepare for financial statements</li>
            <li>Review account balances</li>
          </ul>
          
          <h4>Types of Trial Balance:</h4>
          <ul>
            <li><strong>Unadjusted:</strong> Before adjusting entries</li>
            <li><strong>Adjusted:</strong> After adjusting entries</li>
            <li><strong>Post-Closing:</strong> After closing entries</li>
          </ul>
          
          <h4>Generating Trial Balance:</h4>
          <ol>
            <li>Go to Reports > Trial Balance</li>
            <li>Select date range</li>
            <li>Choose account filters if needed</li>
            <li>Generate report</li>
            <li>Review for accuracy</li>
          </ol>
          
          <h4>Troubleshooting:</h4>
          <p>If trial balance doesn't balance:</p>
          <ul>
            <li>Check for transposition errors</li>
            <li>Verify all entries are posted</li>
            <li>Review journal entry calculations</li>
            <li>Check for missing entries</li>
          </ul>
        `
      },
      {
        id: 5,
        title: 'Financial Statements',
        icon: 'mdi-file-document-multiple',
        content: `
          <h3>Financial Statement Generation</h3>
          <p>Generate key financial statements from your general ledger data.</p>
          
          <h4>Primary Statements:</h4>
          <ul>
            <li><strong>Balance Sheet:</strong> Financial position at a point in time</li>
            <li><strong>Income Statement:</strong> Revenues and expenses for a period</li>
            <li><strong>Cash Flow Statement:</strong> Cash receipts and payments</li>
            <li><strong>Statement of Equity:</strong> Changes in owner's equity</li>
          </ul>
          
          <h4>Generating Statements:</h4>
          <ol>
            <li>Ensure all transactions are recorded</li>
            <li>Complete adjusting entries</li>
            <li>Generate trial balance</li>
            <li>Run financial statement reports</li>
            <li>Review for accuracy</li>
          </ol>
          
          <h4>Customization Options:</h4>
          <ul>
            <li>Date ranges and periods</li>
            <li>Comparative periods</li>
            <li>Account groupings</li>
            <li>Format preferences</li>
            <li>Export options</li>
          </ul>
        `
      },
      {
        id: 6,
        title: 'Period-End Closing',
        icon: 'mdi-calendar-check',
        content: `
          <h3>Period-End Closing Process</h3>
          <p>The period-end closing process prepares your books for the next accounting period.</p>
          
          <h4>Closing Steps:</h4>
          <ol>
            <li><strong>Pre-closing checklist:</strong>
              <ul>
                <li>Complete bank reconciliations</li>
                <li>Review accounts receivable</li>
                <li>Review accounts payable</li>
                <li>Record depreciation</li>
                <li>Make adjusting entries</li>
              </ul>
            </li>
            <li><strong>Generate reports:</strong>
              <ul>
                <li>Trial balance</li>
                <li>Financial statements</li>
                <li>Account analysis</li>
              </ul>
            </li>
            <li><strong>Closing entries:</strong>
              <ul>
                <li>Close revenue accounts</li>
                <li>Close expense accounts</li>
                <li>Close income summary</li>
              </ul>
            </li>
            <li><strong>Final review:</strong>
              <ul>
                <li>Verify all entries posted</li>
                <li>Review financial statements</li>
                <li>Lock the period</li>
              </ul>
            </li>
          </ol>
          
          <h4>Best Practices:</h4>
          <ul>
            <li>Follow a consistent schedule</li>
            <li>Use closing checklists</li>
            <li>Document procedures</li>
            <li>Review before finalizing</li>
          </ul>
        `
      },
      {
        id: 7,
        title: 'Settings & Configuration',
        icon: 'mdi-cog',
        content: `
          <h3>General Ledger Settings</h3>
          <p>Configure your GL settings to match your company's accounting practices.</p>
          
          <h4>Account Settings:</h4>
          <ul>
            <li>Default currency</li>
            <li>Account code format</li>
            <li>Account code length</li>
            <li>Description requirements</li>
          </ul>
          
          <h4>Period Settings:</h4>
          <ul>
            <li>Fiscal year start month</li>
            <li>Period type (monthly/quarterly)</li>
            <li>Auto-create periods</li>
            <li>Future period posting rules</li>
          </ul>
          
          <h4>Posting Rules:</h4>
          <ul>
            <li>Require balanced entries</li>
            <li>Allow negative balances</li>
            <li>Approval requirements</li>
            <li>Approval thresholds</li>
          </ul>
          
          <h4>Numbering:</h4>
          <ul>
            <li>Journal entry prefix</li>
            <li>Next journal number</li>
            <li>Yearly reset options</li>
          </ul>
          
          <h4>Accessing Settings:</h4>
          <ol>
            <li>Go to General Ledger</li>
            <li>Click Settings</li>
            <li>Modify configurations</li>
            <li>Save changes</li>
          </ol>
        `
      }
    ]
  }),
  
  mounted() {
    this.selectedTopic = this.helpTopics[0]
  }
}
</script>

<style scoped>
.v-list-item--active {
  background-color: rgba(25, 118, 210, 0.12);
}

h3 {
  color: #1976d2;
  margin-bottom: 16px;
}

h4 {
  color: #424242;
  margin: 16px 0 8px 0;
}

ul, ol {
  margin-left: 20px;
}

li {
  margin-bottom: 4px;
}

p {
  margin-bottom: 12px;
}
</style>