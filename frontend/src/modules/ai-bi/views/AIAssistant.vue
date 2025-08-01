<template>
  <div class="ai-assistant">
    <v-container fluid class="h-100 pa-0 d-flex flex-column">
      <v-toolbar color="primary" dark>
        <v-toolbar-title>AI Finance Assistant</v-toolbar-title>
      </v-toolbar>

      <div ref="messagesContainer" class="flex-grow-1 overflow-y-auto pa-4">
        <v-row v-for="(message, index) in messages" :key="index" class="mb-4">
          <v-col :cols="message.sender === 'ai' ? 10 : 12" :offset="message.sender === 'ai' ? 0 : 2"
                 :class="{ 'text-right': message.sender === 'user' }">
            <v-card
              :color="message.sender === 'ai' ? 'grey-lighten-4' : 'primary'"
              :class="{ 'ml-auto': message.sender === 'user' }"
              max-width="80%"
              elevation="2"
              rounded
            >
              <v-card-text :class="{ 'text-white': message.sender === 'user' }">
                {{ message.text }}
                <div v-if="message.loading" class="d-flex align-center mt-2">
                  <v-progress-circular indeterminate size="16" class="mr-2"></v-progress-circular>
                  <span class="text-caption">AI is thinking...</span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>

      <v-divider></v-divider>

      <div class="pa-4">
        <v-form @submit.prevent="sendMessage">
          <v-text-field
            v-model="userInput"
            variant="outlined"
            :loading="isProcessing"
            :disabled="isProcessing"
            append-inner-icon="mdi-send"
            hide-details
            placeholder="Ask me anything about your financial data..."
            @click:append-inner="sendMessage"
          ></v-text-field>
        </v-form>
      </div>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';

const messagesContainer = ref<HTMLElement | null>(null);
const userInput = ref('');
const isProcessing = ref(false);

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  loading?: boolean;
}

const messages = ref<Message[]>([
  {
    id: 1,
    text: 'Hello! I\'m your AI Finance Assistant. How can I help you today?',
    sender: 'ai'
  }
]);

const sendMessage = async () => {
  if (!userInput.value.trim() || isProcessing.value) return;

  const userMessage = userInput.value;
  userInput.value = '';
  
  messages.value.push({
    id: Date.now(),
    text: userMessage,
    sender: 'user'
  });
  
  isProcessing.value = true;
  
  const loadingMessage = {
    id: Date.now() + 1,
    text: '',
    sender: 'ai' as const,
    loading: true
  };
  
  messages.value.push(loadingMessage);
  scrollToBottom();
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Simple response simulation
    const response = `I received your message: "${userMessage}". In a real implementation, this would be an AI response.`;
    
    // Update the loading message with actual response
    const index = messages.value.findIndex(m => m.id === loadingMessage.id);
    if (index !== -1) {
      messages.value[index] = {
        ...loadingMessage,
        text: response,
        loading: false
      };
    }
  } catch (error) {
    console.error('Error getting AI response:', error);
    const index = messages.value.findIndex(m => m.id === loadingMessage.id);
    if (index !== -1) {
      messages.value[index] = {
        ...loadingMessage,
        text: 'Sorry, I encountered an error. Please try again.',
        loading: false
      };
    }
  } finally {
    isProcessing.value = false;
    scrollToBottom();
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped>
.ai-assistant {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.v-container {
  height: 100%;
  padding: 0;
}

.flex-grow-1 {
  flex-grow: 1;
  overflow-y: auto;
}
</style>
