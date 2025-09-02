<template>
  <div class="ai-assistant">
    <!-- Header -->
    <div class="chat-header">
      <div class="flex align-items-center">
        <i class="pi pi-comments text-2xl text-white mr-3"></i>
        <h2 class="header-title">AI Finance Assistant</h2>
      </div>
      <div class="header-status">
        <Tag :value="connectionStatus" :severity="connectionSeverity" />
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
                <span>AI is thinking...</span>
              </div>
              <div v-else v-html="formatMessage(message.text)"></div>
            </div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
      </div>
      
      <!-- Quick Actions -->
      <div v-if="showQuickActions" class="quick-actions">
        <h4>Quick Actions</h4>
        <div class="action-buttons">
          <Button 
            v-for="action in quickActions" 
            :key="action.id"
            :label="action.label" 
            :icon="action.icon" 
            size="small" 
            severity="secondary" 
            @click="selectQuickAction(action)"
          />
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-area">
      <div class="input-container">
        <InputText 
          v-model="userInput" 
          placeholder="Ask me anything about your financial data..."
          class="chat-input"
          :disabled="isProcessing"
          @keyup.enter="sendMessage"
        />
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
import { useAIStore } from '../store/aiStore'

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
    text: 'Hello! I\'m your AI Finance Assistant. I can help you analyze financial data, generate reports, and provide insights. How can I assist you today?',
    sender: 'ai',
    timestamp: new Date()
  }
])

const quickActions = ref<QuickAction[]>([
  {
    id: 'cash-flow',
    label: 'Cash Flow Analysis',
    icon: 'pi pi-chart-line',
    query: 'Show me the current cash flow analysis'
  },
  {
    id: 'expenses',
    label: 'Expense Breakdown',
    icon: 'pi pi-chart-pie',
    query: 'Analyze my expense categories for this month'
  },
  {
    id: 'anomalies',
    label: 'Detect Anomalies',
    icon: 'pi pi-exclamation-triangle',
    query: 'Check for any financial anomalies'
  },
  {
    id: 'forecast',
    label: 'Revenue Forecast',
    icon: 'pi pi-trending-up',
    query: 'Generate revenue forecast for next quarter'
  }
])

const suggestions = ref<string[]>([
  'What\'s my current cash position?',
  'Show top 5 expenses this month',
  'Any unusual transactions?',
  'Generate P&L summary'
])

const connectionSeverity = computed(() => {
  switch (connectionStatus.value) {
    case 'Connected': return 'success'
    case 'Connecting': return 'warning'
    case 'Disconnected': return 'danger'
    default: return 'info'
  }
})

// Real-time AI responses
const aiResponses = {
  'cash flow': 'Based on your current data, your cash flow is positive with $45,230 in available funds. Your 30-day forecast shows steady growth.',
  'expenses': 'Your top expense categories this month are: Office Supplies (32%), Marketing (28%), Utilities (15%), and Travel (12%).',
  'anomalies': 'I detected 2 potential anomalies: Unusual spike in office supplies spending (+45% vs last month) and irregular payment timing from Client ABC.',
  'forecast': 'Revenue forecast for Q1 2024: $125,000 (Conservative), $145,000 (Realistic), $165,000 (Optimistic). Based on current trends and seasonal patterns.'
}

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
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Generate AI response based on user input
    const response = generateAIResponse(userMessage)
    
    // Update loading message with response
    const index = messages.value.findIndex(m => m.id === loadingMessage.id)
    if (index !== -1) {
      messages.value[index] = {
        ...loadingMessage,
        text: response,
        loading: false
      }
    }
    
    // Update suggestions based on context
    updateSuggestions(userMessage)
    
  } catch (error) {
    console.error('Error getting AI response:', error)
    const index = messages.value.findIndex(m => m.id === loadingMessage.id)
    if (index !== -1) {
      messages.value[index] = {
        ...loadingMessage,
        text: 'I apologize, but I encountered an error processing your request. Please try again or contact support if the issue persists.',
        loading: false
      }
    }
  } finally {
    isProcessing.value = false
    scrollToBottom()
  }
}

const generateAIResponse = (userMessage: string): string => {
  const message = userMessage.toLowerCase()
  
  // Pattern matching for different types of queries
  if (message.includes('cash') || message.includes('flow')) {
    return aiResponses['cash flow']
  } else if (message.includes('expense') || message.includes('spending')) {
    return aiResponses['expenses']
  } else if (message.includes('anomal') || message.includes('unusual') || message.includes('irregular')) {
    return aiResponses['anomalies']
  } else if (message.includes('forecast') || message.includes('predict') || message.includes('revenue')) {
    return aiResponses['forecast']
  } else if (message.includes('help') || message.includes('what can you do')) {
    return 'I can help you with: 📊 Financial analysis, 📈 Cash flow forecasting, 🔍 Anomaly detection, 📋 Report generation, 💡 Business insights, and much more. Just ask me anything about your financial data!'
  } else {
    return `I understand you're asking about "${userMessage}". Let me analyze your financial data... Based on current patterns, I recommend reviewing your cash flow trends and expense categories. Would you like me to generate a detailed report?`
  }
}

const selectQuickAction = (action: QuickAction) => {
  userInput.value = action.query
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
onMounted(() => {
  scrollToBottom()
  aiStore.connectRealTime()
})

onUnmounted(() => {
  aiStore.disconnectRealTime()
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
