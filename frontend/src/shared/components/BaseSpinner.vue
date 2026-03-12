<template>
  <span class="spinner" :class="{ 'spinner-small': small }"></span>
</template>

<script setup lang="ts">
defineProps<{
  small?: boolean
}>()
</script>

<style scoped>
.spinner { 
  width: 18px; 
  height: 18px; 
  border: 3px solid rgba(255, 255, 255, 0.3); 
  border-top-color: #fff; 
  border-radius: 50%; 
  animation: spin 0.8s linear infinite; 
}
.spinner-small { 
  width: 14px; 
  height: 14px; 
  border-width: 2px;
  border-style: solid;
  border-color: rgba(245, 158, 11, 0.2);
  border-top-color: #f59e0b; 
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
