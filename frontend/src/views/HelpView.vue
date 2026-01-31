<template>
  <div class="help-page">
    <div class="grid">
      <div class="col-12 md:col-4">
        <Card>
          <template #header>
            <div class="help-header">
              <h2>Documentation</h2>
            </div>
          </template>
          <template #content>
            <div class="help-menu" v-if="!loading">
              <div 
                v-for="section in helpContent.sections" 
                :key="section.title"
                class="help-section-item mb-3"
                @click="selectSection(section)"
                :class="{ 'active': selectedSection?.title === section.title }"
              >
                <i :class="`pi ${section.icon} mr-2`"></i>
                {{ section.title }}
              </div>
            </div>
            <div v-else class="text-center p-4">
              <ProgressSpinner />
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-8">
        <Card v-if="selectedSection">
          <template #header>
            <div class="help-content-header">
              <i :class="`pi ${selectedSection.icon} mr-2`"></i>
              {{ selectedSection.title }}
            </div>
          </template>
          <template #content>
            <div class="help-content-body">
              <div v-if="selectedSection.title === 'Quick Start Guide'" v-html="quickStartContent"></div>
              <div v-else-if="selectedSection.title === 'Module Documentation'" v-html="moduleDocContent"></div>
              <div v-else>
                <ul class="help-list">
                  <li v-for="item in selectedSection.items" :key="item.text" class="mb-2">
                    <i :class="`pi ${item.icon} mr-2`"></i>
                    {{ item.text }}
                  </li>
                </ul>
              </div>
            </div>
          </template>
        </Card>
        
        <Card v-else>
          <template #content>
            <div class="text-center p-6">
              <i class="pi pi-info-circle text-4xl text-primary mb-3"></i>
              <h3>Select a topic from the left menu</h3>
              <p class="text-muted">Choose a documentation section to view detailed information</p>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const loading = ref(true)
const helpContent = ref({ sections: [] })
const selectedSection = ref(null)

const quickStartContent = ref(`
<h3>🚀 Getting Started</h3>
<h4>First-Time Login</h4>
<ol>
  <li><strong>Access the System</strong> - Navigate to the application URL</li>
  <li><strong>Login</strong> - Use your credentials (admin@paksa.com / admin123 for demo)</li>
  <li><strong>Dashboard Overview</strong> - Familiarize yourself with the interface</li>
</ol>

<h4>✨ Quick Actions</h4>
<ul>
  <li><strong>Create Records</strong> - Use the + button for quick creation</li>
  <li><strong>Navigate</strong> - Use the sidebar menu to access modules</li>
  <li><strong>Search</strong> - Use Ctrl+K for quick search</li>
</ul>

<h4>📋 Step-by-Step Guides</h4>
<p><strong>Creating an Invoice:</strong></p>
<ol>
  <li>Go to Accounts Receivable → Invoices</li>
  <li>Click "New Invoice"</li>
  <li>Fill in customer details and line items</li>
  <li>Save and send</li>
</ol>
`)

const moduleDocContent = ref(`
<h3>📚 Module Documentation</h3>

<h4>General Ledger</h4>
<ul>
  <li>Chart of Accounts management</li>
  <li>Journal entries and adjustments</li>
  <li>Financial statement generation</li>
  <li>Trial balance and reconciliation</li>
</ul>

<h4>Accounts Payable</h4>
<ul>
  <li>Vendor management</li>
  <li>Invoice processing</li>
  <li>Payment processing</li>
  <li>1099 reporting</li>
</ul>

<h4>Accounts Receivable</h4>
<ul>
  <li>Customer management</li>
  <li>Invoice creation</li>
  <li>Payment processing</li>
  <li>Collections management</li>
</ul>

<h4>Budget Management</h4>
<ul>
  <li>Budget creation and planning</li>
  <li>Forecast modeling</li>
  <li>Variance analysis</li>
  <li>Departmental budgeting</li>
</ul>
`)

const selectSection = (section) => {
  selectedSection.value = section
}

const fetchHelpContent = async () => {
  try {
    const response = await axios.get('/api/v1/help/content')
    helpContent.value = response.data
    // Auto-select first section
    if (response.data.sections.length > 0) {
      selectedSection.value = response.data.sections[0]
    }
  } catch (error) {
    console.error('Failed to load help content:', error)
    // Fallback content
    helpContent.value = {
      sections: [
        {
          title: 'Quick Start Guide',
          icon: 'pi-play',
          items: [
            { text: 'Navigate to Dashboard to view financial overview', icon: 'pi-home' },
            { text: 'Use General Ledger for accounting entries', icon: 'pi-book' }
          ]
        }
      ]
    }
    selectedSection.value = helpContent.value.sections[0]
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchHelpContent()
})
</script>

<style scoped>
.help-page {
  padding: 1rem;
}

.help-header {
  text-align: center;
  padding: 1rem;
}

.help-header h2 {
  color: var(--primary-color);
  margin: 0;
}

.help-section-item {
  padding: 1rem;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.help-section-item:hover {
  background-color: var(--surface-hover);
  border-color: var(--primary-color);
}

.help-section-item.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.help-content-header {
  padding: 1rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--primary-color);
}

.help-content-body {
  padding: 0 1rem;
}

.help-list {
  list-style: none;
  padding: 0;
}

.help-list li {
  padding: 0.5rem 0;
  display: flex;
  align-items: center;
}

:deep(h3) {
  color: var(--primary-color);
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

:deep(h4) {
  color: var(--text-color);
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

:deep(ul), :deep(ol) {
  margin-left: 1.5rem;
}

:deep(li) {
  margin-bottom: 0.5rem;
}
</style>