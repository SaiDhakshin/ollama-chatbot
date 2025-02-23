<script setup>
import { ref, onMounted } from 'vue';
import { useChatStore } from '../stores/chat';
import axios from 'axios';

const chatStore = useChatStore();
const userMessage = ref('');
const toggleChat = ref(false);
const showCorrectionForm = ref(false);
const correction = ref('');

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

const sendFeedback = async (isSend) => {
  if (!chatStore.messages.length) return;
  const lastBotMessage = chatStore.messages.find(msg => msg.role === 'bot');
  if (!lastBotMessage) return; // Ensure there's a bot response to give feedback on
  let payload = {
    question: chatStore.messages[chatStore.messages.length - 2]?.content || '', // User's last question
    bot_answer: lastBotMessage.content, // Bot's response
    correct_answer: isSend ? null : correction.value, // If not helpful, send user's correction
  };
  try {
    await axios.post("http://127.0.0.1:5002/feedback", payload);
    alert("Feedback sent successfully! Thank you.");

    // Reset correction form after submitting
    showCorrectionForm.value = false;
    correction.value = '';
  } catch (error) {
    console.error("Error sending feedback:", error);
    alert("Failed to send feedback. Please try again.");
  }
}
</script>

<template>
  <div class="chat-window-container">
    <div v-if="toggleChat" class="chat-window">
      <div class="chat-container">
        <div v-for="(msg, index) in chatStore.messages" :key="index" :class="msg.role">
          <p>{{ msg.content }}</p>
        </div>
      </div>
      <div v-if="chatStore.messages?.[chatStore.messages?.length - 1]?.role == 'bot'" class="feedback-buttons">
        <button @click="sendFeedback(true)">👍 Helpful</button>
        <button @click="showCorrectionForm = true">👎 Not Helpful</button>
      </div>
      <div class="input-container">
        <template v-if="showCorrectionForm">
          <input v-model="correction" placeholder="What should the answer be?" />
          <button @click="sendFeedback(false)">Submit</button>
        </template>
        <template v-else >          
          <input v-model="userMessage" @keyup.enter="sendMessage" placeholder="Type a message..." />
          <button @click="sendMessage">Send</button>
        </template>
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

.feedback-buttons {
  padding: 5px;
}
</style>
