<template>
  <div class="chat-interface">
    <v-card class="chat-card" height="600">
      <!-- Chat Header -->
      <v-card-title class="chat-header">
        <v-icon class="mr-2">mdi-robot</v-icon>
        Financial Assistant
        <v-spacer></v-spacer>
        <v-btn icon size="small" @click="clearChat">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-card-title>
      
      <!-- Chat Messages -->
      <v-card-text class="chat-messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="welcome-message">
          <v-icon size="48" color="primary">mdi-robot-happy</v-icon>
          <h3 class="mt-2">Hello! I'm your Financial Assistant</h3>
          <p class="text-grey">I can help you with revenue analysis, expense tracking, invoicing, budgets, and more!</p>
          
          <div class="suggestion-chips mt-4">
            <v-chip
              v-for="suggestion in welcomeSuggestions"
              :key="suggestion"
              class="ma-1"
              @click="sendMessage(suggestion)"
            >
              {{ suggestion }}
            </v-chip>
          </div>
        </div>
        
        <div v-else>
          <div
            v-for="message in messages"
            :key="message.id"
            class="message-container"
            :class="message.message_type"
          >
            <div class="message-bubble">
              <div class="message-content">{{ message.content }}</div>
              <div class="message-time">
                {{ formatTime(message.created_at) }}
                <span v-if="message.confidence_score" class="confidence">
                  ({{ Math.round(parseFloat(message.confidence_score) * 100) }}%)
                </span>
              </div>
            </div>
          </div>
          
          <!-- Suggestions -->
          <div v-if="currentSuggestions.length" class="suggestions mt-3">
            <v-chip
              v-for="suggestion in currentSuggestions"
              :key="suggestion"
              size="small"
              class="ma-1"
              @click="sendMessage(suggestion)"
            >
              {{ suggestion }}
            </v-chip>
          </div>
          
          <!-- Action Buttons -->
          <div v-if="currentActions.length" class="actions mt-3">
            <v-btn
              v-for="action in currentActions"
              :key="action.label"
              size="small"
              color="primary"
              variant="outlined"
              class="ma-1"
              @click="executeAction(action)"
            >
              {{ action.label }}
            </v-btn>
          </div>
        </div>
        
        <!-- Typing Indicator -->
        <div v-if="isTyping" class="typing-indicator">
          <div class="message-container assistant">
            <div class="message-bubble">
              <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      </v-card-text>
      
      <!-- Chat Input -->
      <v-card-actions class="chat-input">
        <v-text-field
          v-model="currentMessage"
          placeholder="Ask me anything about your finances..."
          variant="outlined"
          density="compact"
          hide-details
          @keyup.enter="sendMessage()"
          :disabled="isTyping"
        >
          <template v-slot:append-inner>
            <v-btn
              icon
              size="small"
              color="primary"
              :disabled="!currentMessage.trim() || isTyping"
              @click="sendMessage()"
            >
              <v-icon>mdi-send</v-icon>
            </v-btn>
          </template>
        </v-text-field>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

const { showSnackbar } = useSnackbar();

// Data
const messages = ref([]);
const currentMessage = ref('');
const isTyping = ref(false);
const currentSuggestions = ref([]);
const currentActions = ref([]);
const sessionId = ref(null);
const messagesContainer = ref(null);

const welcomeSuggestions = [
  "Show me revenue report",
  "Create new invoice",
  "Expense analysis",
  "Budget status",
  "Help with payroll"
];

// Methods
const sendMessage = async (message = null) => {
  const messageText = message || currentMessage.value.trim();
  if (!messageText) return;
  
  // Add user message to chat
  const userMessage = {
    id: Date.now(),
    message_type: 'user',
    content: messageText,
    created_at: new Date().toISOString()
  };
  messages.value.push(userMessage);
  
  // Clear input and show typing
  currentMessage.value = '';
  isTyping.value = true;
  currentSuggestions.value = [];
  currentActions.value = [];
  
  await scrollToBottom();
  
  try {
    const response = await apiClient.post('/api/v1/ai-assistant/chat', {
      message: messageText,
      session_id: sessionId.value
    });
    
    const chatResponse = response.data;
    sessionId.value = chatResponse.session_id;
    
    // Add AI response to chat
    const aiMessage = {
      id: Date.now() + 1,
      message_type: 'assistant',
      content: chatResponse.response,
      confidence_score: chatResponse.confidence.toString(),
      created_at: new Date().toISOString()
    };
    messages.value.push(aiMessage);
    
    // Update suggestions and actions
    currentSuggestions.value = chatResponse.suggestions || [];
    currentActions.value = chatResponse.actions || [];
    
  } catch (error) {
    showSnackbar('Failed to get response from assistant', 'error');
    console.error('Chat error:', error);
    
    // Add error message
    const errorMessage = {
      id: Date.now() + 1,
      message_type: 'assistant',
      content: "I'm sorry, I'm having trouble responding right now. Please try again.",
      created_at: new Date().toISOString()
    };
    messages.value.push(errorMessage);
  } finally {
    isTyping.value = false;
    await scrollToBottom();
  }
};

const executeAction = (action) => {
  switch (action.type) {
    case 'generate_report':
      showSnackbar('Generating report...', 'info');
      // Implement report generation
      break;
    case 'open_dashboard':
      showSnackbar('Opening dashboard...', 'info');
      // Navigate to dashboard
      break;
    case 'open_module':
      showSnackbar('Opening module...', 'info');
      // Navigate to module
      break;
    case 'open_form':
      showSnackbar('Opening form...', 'info');
      // Navigate to form
      break;
    default:
      console.log('Unknown action:', action);
  }
};

const clearChat = () => {
  messages.value = [];
  sessionId.value = null;
  currentSuggestions.value = [];
  currentActions.value = [];
  currentMessage.value = '';
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

// Lifecycle
onMounted(() => {
  // Auto-focus on input
  // Could load chat history here if needed
});
</script>

<style scoped>
.chat-interface {
  max-width: 800px;
  margin: 0 auto;
}

.chat-card {
  display: flex;
  flex-direction: column;
}

.chat-header {
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.message-container {
  margin-bottom: 16px;
  display: flex;
}

.message-container.user {
  justify-content: flex-end;
}

.message-container.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
}

.user .message-bubble {
  background-color: #1976d2;
  color: white;
}

.assistant .message-bubble {
  background-color: #f5f5f5;
  color: #333;
}

.message-content {
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 4px;
}

.confidence {
  font-weight: bold;
}

.suggestions, .actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  margin-left: 8px;
}

.typing-indicator {
  margin-bottom: 16px;
}

.typing-dots {
  display: flex;
  align-items: center;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #999;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input {
  border-top: 1px solid #e0e0e0;
  padding: 16px;
}
</style>