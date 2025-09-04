import { App } from 'vue';
import AIAssistant from '@/components/ai/AIAssistant.vue';

export default {
  install(app: App) {
    // Register AI Assistant component globally
    app.component('AIAssistant', AIAssistant);
    
    // Add global properties
    app.config.globalProperties.$ai = {
      // Method to show the assistant
      show: () => {
        // This would be implemented to control the assistant visibility
        console.log('Show AI Assistant');
      },
      // Method to send a message programmatically
      sendMessage: (message: string) => {
        // This would be implemented to send messages programmatically
        console.log('Sending message to AI:', message);
      }
    };
  }
};
