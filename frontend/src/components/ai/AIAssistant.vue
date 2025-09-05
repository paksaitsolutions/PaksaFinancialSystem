<template>
  <div class="ai-assistant" :class="{ 'ai-assistant-open': isOpen }">
    <Button 
      v-if="!isOpen"
      icon="pi pi-comments" 
      class="ai-toggle-btn p-button-rounded p-button-help"
      @click="toggleAssistant"
      v-tooltip.left="'AI Assistant'"
    />
    
    <Card v-if="isOpen" class="ai-chat-card">
      <template #header>
        <div class="ai-header">
          <div class="ai-title">
            <i class="pi pi-comments"></i>
            <span>AI Assistant</span>
          </div>
          <Button 
            icon="pi pi-times" 
            class="p-button-text p-button-sm"
            @click="toggleAssistant"
          />
        </div>
      </template>
      
      <template #content>
        <div class="ai-messages" ref="messagesContainer">
          <div v-for="message in messages" :key="message.id" class="message" :class="message.type">
            <div class="message-content">{{ message.content }}</div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
        
        <div class="ai-input">
          <InputText 
            v-model="currentMessage"
            placeholder="Ask me anything about your finances..."
            @keyup.enter="sendMessage"
            class="w-full"
          />
          <Button 
            icon="pi pi-send" 
            class="p-button-sm"
            @click="sendMessage"
            :disabled="!currentMessage.trim()"
          />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

interface Message {
  id: number
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const isOpen = ref(false)
const currentMessage = ref('')
const messagesContainer = ref<HTMLElement>()
const messages = ref<Message[]>([
  {
    id: 1,
    type: 'assistant',
    content: 'Hello! I\'m your AI financial assistant. How can I help you today?',
    timestamp: new Date()
  }
])

const toggleAssistant = () => {
  isOpen.value = !isOpen.value
}

const sendMessage = async () => {
  if (!currentMessage.value.trim()) return

  const userMessage: Message = {
    id: Date.now(),
    type: 'user',
    content: currentMessage.value,
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  const messageText = currentMessage.value
  currentMessage.value = ''

  await nextTick()
  scrollToBottom()

  // Simulate AI response
  setTimeout(() => {
    const aiResponse: Message = {
      id: Date.now() + 1,
      type: 'assistant',
      content: getAIResponse(messageText),
      timestamp: new Date()
    }
    messages.value.push(aiResponse)
    nextTick(() => scrollToBottom())
  }, 1000)
}

const getAIResponse = (message: string): string => {
  const responses = [
    'I can help you with that financial query. Let me analyze your data...',
    'Based on your financial records, here\'s what I found...',
    'That\'s a great question about your finances. Here\'s my analysis...',
    'I\'ve reviewed your accounts and here\'s my recommendation...'
  ]
  return responses[Math.floor(Math.random() * responses.length)]
}

const formatTime = (date: Date): string => {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>

<style scoped>
.ai-assistant {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1000;
}

.ai-toggle-btn {
  width: 60px;
  height: 60px;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.ai-chat-card {
  width: 350px;
  height: 500px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--surface-border);
}

.ai-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--primary-color);
}

.ai-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  max-height: 350px;
}

.message {
  margin-bottom: 1rem;
}

.message.user {
  text-align: right;
}

.message.user .message-content {
  background: var(--primary-color);
  color: white;
  margin-left: 2rem;
}

.message.assistant .message-content {
  background: var(--surface-100);
  margin-right: 2rem;
}

.message-content {
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  display: inline-block;
  max-width: 80%;
  word-wrap: break-word;
}

.message-time {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  margin-top: 0.25rem;
}

.ai-input {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid var(--surface-border);
}

@media (max-width: 768px) {
  .ai-assistant {
    bottom: 1rem;
    right: 1rem;
  }
  
  .ai-chat-card {
    width: 300px;
    height: 400px;
  }
}
</style>