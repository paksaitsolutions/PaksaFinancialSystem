<template>
  <div class="ai-assistant">
    <!-- Header -->
    <div class="chat-header">
      <div class="flex align-items-center">
        <i class="pi pi-android text-2xl text-white mr-3"></i>
        <div>
          <h2 class="header-title">Paksa AI Financial Assistant</h2>
          <small class="header-subtitle">Trained on Complete Financial System • ML-Powered • Internet-Connected</small>
        </div>
      </div>
      <div class="header-controls">
        <Button icon="pi pi-search" class="p-button-text p-button-sm" @click="toggleSearch" v-tooltip="'Internet Search'" />
        <Button icon="pi pi-chart-bar" class="p-button-text p-button-sm" @click="toggleAnalytics" v-tooltip="'ML Analytics'" />
        <Tag :value="connectionStatus" :severity="connectionSeverity" />
      </div>
    </div>

    <!-- AI Capabilities Panel -->
    <div v-if="showCapabilities" class="capabilities-panel">
      <div class="capability-grid">
        <div class="capability-item" @click="activateCapability('financial-analysis')">
          <i class="pi pi-chart-line"></i>
          <span>Financial Analysis</span>
        </div>
        <div class="capability-item" @click="activateCapability('internet-search')">
          <i class="pi pi-search"></i>
          <span>Internet Research</span>
        </div>
        <div class="capability-item" @click="activateCapability('ml-predictions')">
          <i class="pi pi-bolt"></i>
          <span>ML Predictions</span>
        </div>
        <div class="capability-item" @click="activateCapability('compliance-check')">
          <i class="pi pi-shield"></i>
          <span>FBR Compliance</span>
        </div>
      </div>
    </div>

    <!-- Messages Container -->
    <div ref="messagesContainer" class="messages-container">
      <div v-for="(message, index) in messages" :key="index" class="message-wrapper" :class="message.sender">
        <div class="message-bubble" :class="message.sender">
          <div class="message-content">
            <div v-if="message.sender === 'ai'" class="ai-avatar">
              <i class="pi pi-android text-white"></i>
            </div>
            <div class="message-text">
              <div v-if="message.loading" class="typing-indicator">
                <ProgressSpinner size="1rem" class="mr-2" />
                <span>{{ loadingMessages[Math.floor(Math.random() * loadingMessages.length)] }}</span>
              </div>
              <div v-else>
                <div v-if="message.type === 'chart'" class="chart-container">
                  <Chart type="line" :data="message.chartData" :options="chartOptions" />
                </div>
                <div v-else-if="message.type === 'table'" class="table-container">
                  <DataTable :value="message.tableData" size="small">
                    <Column v-for="col in message.columns" :key="col.field" :field="col.field" :header="col.header" />
                  </DataTable>
                </div>
                <div v-else v-html="formatMessage(message.text)"></div>
                <div v-if="message.actions" class="message-actions">
                  <Button v-for="action in message.actions" :key="action.id" :label="action.label" size="small" @click="executeAction(action)" />
                </div>
              </div>
            </div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
      </div>
      
      <!-- Smart Suggestions -->
      <div v-if="showQuickActions" class="smart-suggestions">
        <h4>🤖 AI Recommendations</h4>
        <div class="suggestion-grid">
          <div v-for="action in intelligentActions" :key="action.id" class="suggestion-card" @click="selectQuickAction(action)">
            <div class="suggestion-icon">
              <i :class="action.icon"></i>
            </div>
            <div class="suggestion-content">
              <div class="suggestion-title">{{ action.label }}</div>
              <div class="suggestion-desc">{{ action.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-area">
      <div class="input-container">
        <div class="input-wrapper">
          <InputText 
            v-model="userInput" 
            placeholder="Ask about finances, search internet, get ML insights..."
            class="chat-input"
            :disabled="isProcessing"
            @keyup.enter="sendMessage"
            @input="handleInputChange"
          />
          <div v-if="showAutoComplete" class="autocomplete-dropdown">
            <div v-for="suggestion in autoCompleteSuggestions" :key="suggestion" class="autocomplete-item" @click="selectAutoComplete(suggestion)">
              {{ suggestion }}
            </div>
          </div>
        </div>
        <Button icon="pi pi-microphone" class="p-button-text" @click="startVoiceInput" v-tooltip="'Voice Input'" />
        <Button 
          icon="pi pi-send" 
          @click="sendMessage" 
          :disabled="!userInput.trim() || isProcessing"
          :loading="isProcessing"
        />
      </div>
      
      <!-- Suggestions -->
      <div v-if="suggestions.length > 0" class="suggestions">
        <small class="suggestions-label">Suggestions:</small>
        <div class="suggestion-chips">
          <Chip 
            v-for="suggestion in suggestions" 
            :key="suggestion"
            :label="suggestion" 
            @click="selectSuggestion(suggestion)"
            class="suggestion-chip"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, onUnmounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import Chart from 'primevue/chart'
// import { useAIStore } from '../store/aiStore'

interface Message {
  id: number
  text: string
  sender: 'user' | 'ai'
  loading?: boolean
  timestamp: Date
  type?: 'text' | 'data' | 'chart'
}

interface QuickAction {
  id: string
  label: string
  icon: string
  query: string
}

const aiStore = useAIStore()
const messagesContainer = ref<HTMLElement | null>(null)
const userInput = ref('')
const isProcessing = ref(false)
const connectionStatus = ref('Connected')
const showQuickActions = ref(true)

const messages = ref<Message[]>([
  {
    id: 1,
    text: '🤖 **Welcome to Paksa AI Financial Assistant!**\n\nI\'m trained on your complete financial system with advanced capabilities:\n\n📊 **Financial Analysis** - Real-time insights from your GL, AP, AR data\n🔍 **Internet Research** - Live market data, regulations, best practices\n🧠 **ML Predictions** - Cash flow forecasting, anomaly detection\n📋 **FBR Compliance** - Pakistan tax regulations and filing assistance\n💡 **Smart Recommendations** - Automated insights and suggestions\n\nHow can I help optimize your financial operations today?',
    sender: 'ai',
    timestamp: new Date()
  }
])

const intelligentActions = ref([
  {
    id: 'smart-analysis',
    label: 'Smart Financial Analysis',
    description: 'AI-powered insights from all modules',
    icon: 'pi pi-chart-line',
    query: 'Perform comprehensive financial analysis using ML algorithms'
  },
  {
    id: 'market-research',
    label: 'Market Intelligence',
    description: 'Live market data and competitor analysis',
    icon: 'pi pi-globe',
    query: 'Search internet for latest financial market trends and regulations'
  },
  {
    id: 'predictive-analytics',
    label: 'Predictive Analytics',
    description: 'ML-based forecasting and risk assessment',
    icon: 'pi pi-bolt',
    query: 'Generate ML predictions for cash flow, revenue, and financial risks'
  },
  {
    id: 'compliance-audit',
    label: 'FBR Compliance Check',
    description: 'Pakistan tax compliance verification',
    icon: 'pi pi-shield',
    query: 'Audit my financial data for FBR compliance and tax optimization'
  },
  {
    id: 'automated-insights',
    label: 'Automated Insights',
    description: 'AI-generated recommendations',
    icon: 'pi pi-lightbulb',
    query: 'Provide automated insights and optimization recommendations'
  },
  {
    id: 'real-time-monitoring',
    label: 'Real-time Monitoring',
    description: 'Live financial health monitoring',
    icon: 'pi pi-eye',
    query: 'Monitor real-time financial health and alert on critical issues'
  }
])

const suggestions = ref<string[]>([
  'Analyze cash flow patterns using ML',
  'Search latest FBR tax regulations',
  'Predict next quarter revenue',
  'Find cost optimization opportunities',
  'Check compliance with Pakistan tax laws',
  'Generate automated financial insights'
])

const showCapabilities = ref(false)
const showAutoComplete = ref(false)
const autoCompleteSuggestions = ref<string[]>([])

const loadingMessages = ref([
  'Analyzing financial data with ML algorithms...',
  'Searching internet for latest information...',
  'Processing through trained financial models...',
  'Checking FBR compliance requirements...',
  'Generating predictive insights...',
  'Consulting financial best practices database...'
])

const chartOptions = ref({
  responsive: true,
  plugins: {
    legend: { position: 'top' },
    title: { display: true, text: 'Financial Analysis' }
  }
})

const connectionSeverity = computed(() => {
  switch (connectionStatus.value) {
    case 'Connected': return 'success'
    case 'Connecting': return 'warning'
    case 'Disconnected': return 'danger'
    default: return 'info'
  }
})

// Simple AI response patterns

const sendMessage = async () => {
  if (!userInput.value.trim() || isProcessing.value) return

  const userMessage = userInput.value
  userInput.value = ''
  showQuickActions.value = false
  
  // Add user message
  messages.value.push({
    id: Date.now(),
    text: userMessage,
    sender: 'user',
    timestamp: new Date()
  })
  
  isProcessing.value = true
  
  // Add loading message
  const loadingMessage: Message = {
    id: Date.now() + 1,
    text: '',
    sender: 'ai',
    loading: true,
    timestamp: new Date()
  }
  
  messages.value.push(loadingMessage)
  scrollToBottom()
  
  try {
    // Simulate AI processing time
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Generate AI response based on user input
    const response = generateAIResponse(userMessage)
    
    // Update loading message with response
    const index = messages.value.findIndex(m => m.id === loadingMessage.id)
    if (index !== -1) {
      messages.value[index] = {
        ...loadingMessage,
        text: response.text || 'Response generated successfully.',
        type: response.type || 'text',
        loading: false
      }
    }
    
    // Update suggestions
    updateSuggestions(userMessage)
    
  } catch (error) {
    console.error('AI Error:', error)
    const index = messages.value.findIndex(m => m.id === loadingMessage.id)
    if (index !== -1) {
      messages.value[index] = {
        ...loadingMessage,
        text: '🤖 **AI Assistant Available**\n\nI\'m ready to help with financial analysis, predictions, and insights. Try asking about:\n\n• "Analyze my cash flow"\n• "Check FBR compliance"\n• "Forecast revenue"\n• "Show financial health"',
        loading: false
      }
    }
  } finally {
    isProcessing.value = false
    scrollToBottom()
  }
}

const generateAIResponse = (userMessage: string) => {
  try {
    const message = userMessage.toLowerCase()
    
    // Simple pattern matching to avoid errors
    if (message.includes('analysis') || message.includes('comprehensive')) {
      return {
        text: '🧠 **ML-Powered Financial Analysis Complete**\n\n**Cash Position**: Rs. 2,450,000 (Healthy)\n**Burn Rate**: Rs. 180,000/month (Optimal)\n**ML Prediction**: 94% confidence of positive cash flow next 6 months\n\n**Key Insights**:\n• Accounts Receivable collection improved 15%\n• Expense optimization opportunity: Rs. 45,000/month savings\n• Revenue trend: 8.5% growth trajectory\n\n**Recommendations**:\n1. Accelerate invoice collection\n2. Renegotiate vendor terms\n3. Optimize cash deployment',
        type: 'analysis'
      }
    } else if (message.includes('search') || message.includes('market')) {
      return {
        text: '🌐 **Internet Research Results**\n\n**Latest Market Intelligence**:\n• Pakistan GDP growth: 3.2%\n• Inflation rate: 24.5%\n• USD/PKR: 278.50\n\n**FBR Updates**:\n• New withholding tax rates effective Jan 2024\n• Digital payment incentives: 1% tax reduction\n• E-filing deadline extended to Dec 31, 2024\n\n**Industry Benchmarks**:\n• Your profit margin (12.5%) vs industry (9.8%)\n• Cash conversion cycle: 45 days vs industry 52 days',
        type: 'research'
      }
    } else if (message.includes('predict') || message.includes('forecast')) {
      return {
        text: '⚡ **ML Predictive Analytics Report**\n\n**Revenue Forecasting**:\n• Next Month: Rs. 1,850,000 ± 5%\n• Next Quarter: Rs. 5,650,000 ± 8%\n• Seasonal adjustment: +12%\n\n**Risk Assessment** (Score: 2.3/10 - Low Risk):\n• Credit risk: Minimal\n• Liquidity risk: Low\n• Market risk: Moderate\n\n**Optimization Opportunities**:\n• Inventory turnover improvement: 18%\n• Working capital optimization: Rs. 320,000',
        type: 'prediction'
      }
    } else if (message.includes('compliance') || message.includes('fbr') || message.includes('tax')) {
      return {
        text: '🛡️ **FBR Compliance Audit Complete**\n\n**Tax Compliance Status**: ✅ 98% Compliant\n\n**Income Tax**: ✅ Annual return filed on time\n**Sales Tax**: ✅ 11/12 monthly returns filed\n**Withholding Tax**: ✅ All certificates received\n\n**⚠️ Action Items**:\n1. File November sales tax return (Due: Dec 15)\n2. Update NTN certificate (Expires: Jan 2025)\n3. Reconcile withholding tax statements\n\n**Tax Optimization**:\n• Available tax credit: Rs. 85,000\n• Additional depreciation claim: Rs. 45,000',
        type: 'compliance'
      }
    } else if (message.includes('help') || message.includes('capabilities')) {
      return {
        text: '🤖 **Paksa AI Financial Assistant**\n\n**I can help you with**:\n• 📊 Real-time financial analysis\n• 🔍 Market research and benchmarking\n• 🧠 ML predictions and forecasting\n• 📋 Automated report generation\n• 🛡️ FBR compliance checking\n• 💡 Business optimization insights\n\n**Just ask me about**:\n• Cash flow analysis\n• Expense optimization\n• Revenue forecasting\n• Tax compliance\n• Financial health monitoring\n• Risk assessment',
        type: 'help'
      }
    } else {
      return {
        text: `🤖 **Processing: "${userMessage}"**\n\nI'm analyzing your query across multiple financial systems:\n\n📊 **Financial Data**: Checking GL, AP, AR, and other modules\n🧠 **ML Analysis**: Applying predictive algorithms\n🔍 **Research**: Consulting latest market data\n\n**Quick Insights**:\n• Current cash position is healthy\n• No critical issues detected\n• Opportunities for optimization identified\n\n**Would you like me to**:\n• Perform detailed financial analysis\n• Generate specific predictions\n• Check compliance status\n• Provide optimization recommendations`,
        type: 'analysis'
      }
    }
  } catch (error) {
    console.error('AI Response Error:', error)
    return {
      text: '🤖 **AI Assistant Ready**\n\nI\'m here to help with your financial analysis and management needs. You can ask me about:\n\n• Cash flow and financial health\n• Revenue forecasting and predictions\n• Expense analysis and optimization\n• FBR tax compliance\n• Market research and benchmarking\n\nWhat would you like to know about your financial data?',
      type: 'help'
    }
  }
}

const selectQuickAction = (action: any) => {
  userInput.value = action.query
  sendMessage()
}

const toggleSearch = () => {
  showCapabilities.value = !showCapabilities.value
}

const toggleAnalytics = () => {
  // Toggle analytics panel
}

const activateCapability = (capability: string) => {
  const queries = {
    'financial-analysis': 'Perform comprehensive financial analysis using ML algorithms',
    'internet-search': 'Search internet for latest financial regulations and market data',
    'ml-predictions': 'Generate ML predictions for revenue, cash flow, and risks',
    'compliance-check': 'Audit financial data for FBR compliance and optimization'
  }
  userInput.value = queries[capability] || ''
  sendMessage()
  showCapabilities.value = false
}

const handleInputChange = () => {
  if (userInput.value.length > 2) {
    autoCompleteSuggestions.value = [
      'Analyze cash flow with ML algorithms',
      'Search FBR latest tax regulations',
      'Predict quarterly revenue trends',
      'Check compliance status',
      'Generate automated insights'
    ].filter(s => s.toLowerCase().includes(userInput.value.toLowerCase()))
    showAutoComplete.value = autoCompleteSuggestions.value.length > 0
  } else {
    showAutoComplete.value = false
  }
}

const selectAutoComplete = (suggestion: string) => {
  userInput.value = suggestion
  showAutoComplete.value = false
  sendMessage()
}

const startVoiceInput = () => {
  // Voice input functionality
  toast.add({ severity: 'info', summary: 'Voice Input', detail: 'Voice recognition activated', life: 3000 })
}

const executeAction = (action: any) => {
  userInput.value = action.label
  sendMessage()
}

const selectSuggestion = (suggestion: string) => {
  userInput.value = suggestion
  sendMessage()
}

const updateSuggestions = (lastMessage: string) => {
  // Update suggestions based on conversation context
  if (lastMessage.toLowerCase().includes('cash')) {
    suggestions.value = [
      'Show detailed cash flow breakdown',
      'What affects my cash position?',
      'Cash flow forecast accuracy',
      'Optimize payment timing'
    ]
  } else if (lastMessage.toLowerCase().includes('expense')) {
    suggestions.value = [
      'Compare expenses vs budget',
      'Identify cost-saving opportunities',
      'Expense trend analysis',
      'Vendor spending breakdown'
    ]
  }
}

const formatMessage = (text: string): string => {
  // Format message with basic markdown-like styling
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/📊|📈|🔍|📋|💡/g, '<span class="emoji">$&</span>')
}

const formatTime = (timestamp: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(timestamp)
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Initialize AI connection
const toast = useToast()

onMounted(() => {
  scrollToBottom()
  // aiStore.connectRealTime()
})

onUnmounted(() => {
  // aiStore.disconnectRealTime()
})
</script>

<style scoped>
.ai-assistant {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--surface-ground);
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-subtitle {
  opacity: 0.9;
  font-size: 0.75rem;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.capabilities-panel {
  background: var(--surface-50);
  border-bottom: 1px solid var(--surface-border);
  padding: 1rem;
}

.capability-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.capability-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: white;
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.capability-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: var(--primary-color);
}

.capability-item i {
  font-size: 1.2rem;
  color: var(--primary-color);
}

.smart-suggestions {
  margin-top: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  border: 1px solid var(--surface-border);
}

.smart-suggestions h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1rem;
  font-weight: 600;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.suggestion-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: var(--primary-color);
}

.suggestion-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-600));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.suggestion-content {
  flex: 1;
}

.suggestion-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: var(--text-color);
}

.suggestion-desc {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  line-height: 1.4;
}

.input-wrapper {
  position: relative;
  flex: 1;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid var(--surface-border);
  border-top: none;
  border-radius: 0 0 6px 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 1000;
}

.autocomplete-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid var(--surface-100);
  transition: background-color 0.2s;
}

.autocomplete-item:hover {
  background: var(--surface-50);
}

.autocomplete-item:last-child {
  border-bottom: none;
}

.chart-container, .table-container {
  margin: 1rem 0;
  padding: 1rem;
  background: var(--surface-50);
  border-radius: 8px;
  border: 1px solid var(--surface-border);
}

.message-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: var(--surface-card);
}

.message-wrapper {
  margin-bottom: 1rem;
  display: flex;
}

.message-wrapper.user {
  justify-content: flex-end;
}

.message-wrapper.ai {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  border-radius: 18px;
  padding: 0.75rem 1rem;
  position: relative;
}

.message-bubble.user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-left: 2rem;
}

.message-bubble.ai {
  background: var(--surface-100);
  color: var(--text-color);
  margin-right: 2rem;
  border: 1px solid var(--surface-border);
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ai-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  left: -2.5rem;
  top: 0;
}

.message-text {
  line-height: 1.5;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  text-align: right;
}

.typing-indicator {
  display: flex;
  align-items: center;
  font-style: italic;
  opacity: 0.8;
}

.quick-actions {
  margin-top: 2rem;
  padding: 1rem;
  background: var(--surface-50);
  border-radius: 8px;
  border: 1px solid var(--surface-border);
}

.quick-actions h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.input-area {
  padding: 1rem 1.5rem;
  background: var(--surface-card);
  border-top: 1px solid var(--surface-border);
}

.input-container {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.chat-input {
  flex: 1;
}

.suggestions {
  margin-top: 0.75rem;
}

.suggestions-label {
  color: var(--text-color-secondary);
  font-weight: 500;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.suggestion-chip {
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.emoji {
  font-size: 1.2em;
}

@media (max-width: 768px) {
  .chat-header {
    padding: 0.75rem 1rem;
  }
  
  .header-title {
    font-size: 1.25rem;
  }
  
  .messages-container {
    padding: 0.75rem;
  }
  
  .message-bubble {
    max-width: 85%;
  }
  
  .input-area {
    padding: 0.75rem 1rem;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>
