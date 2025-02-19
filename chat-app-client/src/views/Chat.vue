<script setup>
import { ref, onMounted } from 'vue';
import { useChatStore } from '../stores/chat';

const chatStore = useChatStore();
const userMessage = ref('');
const toggleChat = ref(false);

const sendMessage = async () => {
  if (userMessage.value.trim() !== '') {
    const chatContainer = document.querySelector('.chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
    await chatStore.sendMessage(userMessage.value);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    userMessage.value = '';
  }
};

onMounted(() => {
  // Scroll to bottom when messages update
  const chatContainer = document.querySelector('.chat-container');
  if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
});
</script>

<template>
  <div class="chat-window-container">
    <div v-if="toggleChat" class="chat-window">
      <div class="chat-container">
        <div v-for="(msg, index) in chatStore.messages" :key="index" :class="msg.role">
          <p>{{ msg.content }}</p>
        </div>
      </div>
      <div class="input-container">
        <input v-model="userMessage" @keyup.enter="sendMessage" placeholder="Type a message..." />
        <button @click="sendMessage">Send</button>
      </div>
    </div>
    <div class="chat-icon" @click="toggleChat = !toggleChat"><img src="../assets/chat-icon.png" alt=""></div>
  </div>
</template>

<style scoped>
.chat-window {
  width: 100%;
  max-width: 400px;
  height: 500px;
  display: flex;
  flex-direction: column;
  border: 1px solid #ccc;
  border-radius: 10px;
  overflow: hidden;
}

.chat-container {
  flex: 1;
  padding: 10px;
  display: flex;
  flex-direction: column;
  overflow-x: scroll;
}

.user {
  align-self: flex-end;
  background: #007bff;
  color: white;
  padding: 8px;
  border-radius: 10px;
  margin: 5px 0;
  justify-self: start;
}

.bot {
  align-self: flex-start;
  background: #f1f1f1;
  padding: 8px;
  border-radius: 10px;
  margin: 5px 0;
  justify-self: end;
}

.input-container {
  display: flex;
  border-top: 1px solid #ccc;
  padding: 10px;
}

input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

button {
  padding: 8px 15px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  margin-left: 10px;
  cursor: pointer;
}

.chat-icon img {
  width: 24px;
  height: 24px;
}

.chat-icon {
  border-radius: 15px;
  height: 28px;
  border: 2px solid black;
  padding: 10px;
  cursor: pointer;
  top: 90%;
}

.chat-window-container {
  display: flex;
  flex-direction: row;
  gap: 15px;
  align-items: flex-end;
}
</style>
