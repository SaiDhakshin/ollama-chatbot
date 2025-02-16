<template>
    <div>
      <!-- Chat Button -->
      <button
        class="fixed bottom-4 right-4 inline-flex items-center justify-center text-sm font-medium border rounded-full w-16 h-16 bg-black hover:bg-gray-700 text-white cursor-pointer"
        @click="toggleChat"
      >
        <svg width="30" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
        </svg>
      </button>
  
      <!-- Chat Window -->
      <div v-if="isChatOpen" class="fixed bottom-[calc(4rem+1.5rem)] right-0 mr-4 bg-white p-6 rounded-lg border w-[440px] h-[634px] shadow-lg">
        <div class="flex flex-col space-y-1.5 pb-6">
          <h2 class="font-semibold text-lg tracking-tight">Chatbot</h2>
          <p class="text-sm text-gray-500">Powered by Llama</p>
        </div>
  
        <!-- Chat Messages -->
        <div class="overflow-y-auto h-[474px] pr-4">
          <div v-for="(message, index) in messages" :key="index" class="flex gap-3 my-4 text-gray-600 text-sm">
            <span class="relative flex shrink-0 overflow-hidden rounded-full w-8 h-8 bg-gray-100 border p-1">
              <svg v-if="message.sender === 'AI'" width="20" height="20" viewBox="0 0 24 24" fill="black" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z"></path>
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 16 16" fill="black" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0Zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4Z"></path>
              </svg>
            </span>
            <p class="leading-relaxed">
              <span class="block font-bold text-gray-700">{{ message.sender }}</span>
              {{ message.text }}
            </p>
          </div>
        </div>
  
        <!-- Input Box -->
        <div class="flex items-center pt-0">
          <form @submit.prevent="sendMessage" class="flex items-center justify-center w-full space-x-2">
            <input
              v-model="inputMessage"
              class="flex h-10 w-full rounded-md border px-3 py-2 text-sm placeholder-gray-400 focus:ring-gray-400"
              placeholder="Type your message"
            />
            <button class="bg-black text-white px-4 py-2 rounded-md hover:bg-gray-800">Send</button>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { defineComponent, ref } from 'vue';
  import { useChatStore } from '../stores/chat';
  
  export default defineComponent({
    setup() {
      const chatStore = useChatStore();
      const isChatOpen = ref(false);
      const inputMessage = ref('');
  
      const toggleChat = () => {
        isChatOpen.value = !isChatOpen.value;
      };
  
      const sendMessage = () => {
        if (!inputMessage.value.trim()) return;
        chatStore.addMessage({ sender: 'You', text: inputMessage.value });
        inputMessage.value = '';
        
        // Simulate AI response
        setTimeout(() => {
          chatStore.addMessage({ sender: 'AI', text: 'I am here to help!' });
        }, 1000);
      };
  
      return {
        isChatOpen,
        toggleChat,
        inputMessage,
        sendMessage,
        messages: chatStore.messages,
      };
    }
  });
  </script>
  
  <style>
  ::-webkit-scrollbar {
    width: 6px;
  }
  ::-webkit-scrollbar-thumb {
    background: #b0b0b0;
    border-radius: 3px;
  }
  </style>
  