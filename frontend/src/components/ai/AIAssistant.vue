<template>
  <div class="ai-assistant" :class="{ 'ai-assistant--expanded': isExpanded }">
    <!-- Minimized State -->
    <div v-if="!isExpanded" class="ai-assistant__minimized" @click="toggleExpand">
      <div class="ai-assistant__avatar">
        <i class="pi pi-robot"></i>
      </div>
      <span class="ai-assistant__badge" v-if="unreadCount > 0">{{ unreadCount }}</span>
    </div>

    <!-- Expanded State -->
    <div v-else class="ai-assistant__expanded">
      <div class="ai-assistant__header">
        <h3>AI Assistant</h3>
        <Button 
          icon="pi pi-times" 
          class="p-button-text p-button-rounded p-button-sm" 
          @click="toggleExpand"
        />
      </div>
      
      <div class="ai-assistant__messages" ref="messagesContainer">
        <div 
          v-for="(message, index) in messages" 
          :key="index"
          class="ai-assistant__message"
          :class="`ai-assistant__message--${message.role}`"
        >
          <div class="ai-assistant__message-avatar">
            <i :class="message.role === 'user' ? 'pi pi-user' : 'pi pi-robot'"></i>
          </div>
          <div class="ai-assistant__message-content">
            <div v-if="message.content" class="ai-assistant__message-text" v-html="formatMessage(message.content)"></div>
            
            <!-- Suggestions -->
            <div v-if="message.suggestions && message.suggestions.length > 0" class="ai-assistant__suggestions">
              <Button 
                v-for="(suggestion, idx) in message.suggestions" 
                :key="idx"
                :label="suggestion.text"
                :class="`p-button-${suggestion.type === 'action' ? 'primary' : 'secondary'}`"
                class="p-button-sm"
                @click="selectSuggestion(suggestion)"
              />
            </div>
            
            <!-- Actions -->
            <div v-if="message.actions && message.actions.length > 0" class="ai-assistant__actions">
              <Button 
                v-for="(action, idx) in message.actions" 
                :key="idx"
                :label="action.label || 'View'"
                class="p-button-sm"
                @click="handleAction(action)"
              />
            </div>
          </div>
        </div>
        
        <div v-if="isLoading" class="ai-assistant__typing">
          <div class="ai-assistant__typing-dot"></div>
          <div class="ai-assistant__typing-dot"></div>
          <div class="ai-assistant__typing-dot"></div>
        </div>
      </div>
      
      <div class="ai-assistant__input">
        <InputText 
          v-model="userInput" 
          placeholder="Ask me anything..." 
          class="w-full"
          @keyup.enter="sendMessage"
          :disabled="isLoading"
        />
        <Button 
          icon="pi pi-send" 
          class="p-button-text" 
          @click="sendMessage"
          :disabled="!userInput.trim() || isLoading"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { useToast } from 'primevue/usetoast';
import axios from 'axios';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  suggestions?: Array<{ text: string; type: string }>;
  actions?: Array<{ type: string; [key: string]: any }>;
}

const props = defineProps({
  initialContext: {
    type: Object,
    default: () => ({})
  }
});

const toast = useToast();
const route = useRoute();
const messagesContainer = ref<HTMLElement | null>(null);

// State
const isExpanded = ref(false);
const isLoading = ref(false);
const userInput = ref('');
const messages = ref<Message[]>([]);
const unreadCount = ref(0);
const currentContext = ref({
  module: '',
  ...props.initialContext
});

// Update context when route changes
watch(() => route.path, (newPath) => {
  // Extract module from path (e.g., /hrm/employees -> hrm)
  const moduleMatch = newPath.split('/')[1];
  if (moduleMatch) {
    currentContext.value.module = moduleMatch;
  }
}, { immediate: true });

// Methods
const toggleExpand = () => {
  isExpanded.value = !isExpanded.value;
  if (isExpanded.value) {
    unreadCount.value = 0;
    scrollToBottom();
  }
};

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;
  
  const userMessage = userInput.value;
  addMessage('user', userMessage);
  userInput.value = '';
  
  try {
    isLoading.value = true;
    
    const response = await axios.post('/api/ai/query', {
      query: userMessage,
      context: currentContext.value
    });
    
    const { response: assistantResponse, suggestions, actions, context_updates } = response.data;
    
    // Update context if needed
    if (context_updates) {
      currentContext.value = { ...currentContext.value, ...context_updates };
    }
    
    addMessage('assistant', assistantResponse, { suggestions, actions });
  } catch (error) {
    console.error('Error sending message to AI:', error);
    addMessage('assistant', 'Sorry, I encountered an error processing your request.');
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to get response from AI assistant',
      life: 3000
    });
  } finally {
    isLoading.value = false;
  }
};

const addMessage = (role: 'user' | 'assistant', content: string, options: {
  suggestions?: Array<{ text: string; type: string }>;
  actions?: Array<{ type: string; [key: string]: any }>;
} = {}) => {
  messages.value.push({
    role,
    content,
    timestamp: new Date(),
    ...options
  });
  
  if (!isExpanded.value && role === 'assistant') {
    unreadCount.value++;
  }
  
  scrollToBottom();
};

const selectSuggestion = (suggestion: { text: string; type: string }) => {
  userInput.value = suggestion.text;
  sendMessage();
};

const handleAction = (action: { type: string; [key: string]: any }) => {
  switch (action.type) {
    case 'navigate':
      // Use Vue Router to navigate
      if (action.path) {
        // In a real implementation, you would use the router
        console.log('Navigating to:', action.path);
        // router.push(action.path);
      }
      break;
    case 'open_modal':
      // Handle modal opening
      console.log('Opening modal:', action.modalId);
      break;
    default:
      console.log('Action triggered:', action);
  }
};

const formatMessage = (text: string) => {
  // Simple markdown-like formatting
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
    .replace(/\*(.*?)\*/g, '<em>$1</em>')                // Italic
    .replace(/`(.*?)`/g, '<code>$1</code>')               // Inline code
    .replace(/\n/g, '<br>');                              // Line breaks
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// Initial welcome message
onMounted(() => {
  addMessage('assistant', 'Hello! I\'m your AI assistant. How can I help you today?', {
    suggestions: [
      { text: 'How do I create a new employee?', type: 'help' },
      { text: 'Show me the leave calendar', type: 'action' },
      { text: 'Generate a report', type: 'action' }
    ]
  });
});
</script>

<style scoped lang="scss">
.ai-assistant {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1000;
  transition: all 0.3s ease;
  
  &__minimized {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background-color: var(--primary-color);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    position: relative;
    
    &:hover {
      transform: scale(1.05);
    }
    
    .pi {
      font-size: 1.5rem;
    }
  }
  
  &__avatar {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  &__badge {
    position: absolute;
    top: -5px;
    right: -5px;
    background-color: var(--red-500);
    color: white;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: bold;
  }
  
  &__expanded {
    width: 400px;
    max-width: 90vw;
    max-height: 80vh;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  &__header {
    padding: 1rem;
    background-color: var(--primary-color);
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      margin: 0;
      font-size: 1.1rem;
      font-weight: 600;
    }
    
    button {
      color: white !important;
    }
  }
  
  &__messages {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  &__message {
    display: flex;
    gap: 0.75rem;
    max-width: 85%;
    
    &--user {
      align-self: flex-end;
      flex-direction: row-reverse;
      
      .ai-assistant__message-content {
        background-color: var(--primary-color);
        color: white;
        border-radius: 1rem 1rem 0 1rem;
      }
    }
    
    &--assistant {
      align-self: flex-start;
      
      .ai-assistant__message-content {
        background-color: var(--surface-100);
        color: var(--text-color);
        border-radius: 1rem 1rem 1rem 0;
      }
    }
  }
  
  &__message-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: var(--surface-200);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    
    .pi {
      font-size: 1rem;
      color: var(--text-color-secondary);
    }
  }
  
  &__message-content {
    padding: 0.75rem 1rem;
    word-break: break-word;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  &__message-text {
    line-height: 1.5;
    
    :deep(code) {
      background-color: var(--surface-300);
      padding: 0.2em 0.4em;
      border-radius: 4px;
      font-family: monospace;
      font-size: 0.9em;
    }
    
    :deep(strong) {
      font-weight: 600;
    }
    
    :deep(em) {
      font-style: italic;
    }
  }
  
  &__suggestions, &__actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.75rem;
    
    button {
      margin: 0 !important;
      white-space: nowrap;
    }
  }
  
  &__typing {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    
    &-dot {
      width: 8px;
      height: 8px;
      background-color: var(--primary-color);
      border-radius: 50%;
      animation: typing 1.4s infinite ease-in-out;
      
      &:nth-child(1) { animation-delay: 0s; }
      &:nth-child(2) { animation-delay: 0.2s; }
      &:nth-child(3) { animation-delay: 0.4s; }
    }
    
    @keyframes typing {
      0%, 60%, 100% { transform: translateY(0); }
      30% { transform: translateY(-5px); }
    }
  }
  
  &__input {
    display: flex;
    padding: 1rem;
    border-top: 1px solid var(--surface-200);
    background-color: var(--surface-0);
    
    .p-inputtext {
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
      border-right: none;
    }
    
    button {
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    }
  }
}

// Responsive adjustments
@media (max-width: 640px) {
  .ai-assistant {
    bottom: 1rem;
    right: 1rem;
    
    &__expanded {
      width: calc(100vw - 2rem);
      height: 80vh;
    }
  }
}
</style>
