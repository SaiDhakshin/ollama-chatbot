import { defineStore } from 'pinia';
import axios from 'axios';

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [] as any
  }),
  actions: {
    async sendMessage(userMessage: any) {
      this.messages.push({ role: 'user', content: userMessage });
      
      try {
        const response = await axios.post('http://localhost:5001/chat', { message: userMessage });
        this.messages.push({ role: 'bot', content: response.data.reply });
      } catch (error) {
        console.error('Error fetching chatbot response:', error);
      }
    }
  }
});
