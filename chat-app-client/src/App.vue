<script setup lang="ts">
import Chat from './views/Chat.vue'
</script>

<template>
  <div class="chat-widget">
   <Chat/>
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
.chat-widget {
  position: fixed;
  bottom: 10px;
  right: 10px;
}
</style>
