<template>
  <div class="actions">
    <button class="btn-generate" :disabled="disabled || loading" @click="$emit('generate')">
      <BaseSpinner v-if="loading" />
      <span v-else>Analyse All</span>
    </button>
    <button v-if="hasFiles" class="btn-clear" @click="$emit('clear')">
      Clear
    </button>
  </div>
</template>

<script setup lang="ts">
import BaseSpinner from '../../../shared/components/BaseSpinner.vue'

defineProps<{
  loading: boolean
  hasFiles: boolean
  disabled: boolean
}>()

defineEmits(['generate', 'clear'])
</script>

<style scoped>
.actions { display: flex; gap: 12px; margin-bottom: 20px; }
.btn-generate {
  flex: 2; padding: 16px; background: linear-gradient(135deg, var(--accent), var(--accent2)); color: #fff;
  border: none; border-radius: var(--radius); font-size: 1rem; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 10px; transition: all 0.3s;
}
.btn-generate:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(236, 72, 153, 0.4); }
.btn-generate:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-clear { 
  flex: 1; 
  padding: 16px; 
  background: transparent; 
  color: var(--muted); 
  border: 1px solid var(--border); 
  border-radius: var(--radius); 
  cursor: pointer; 
  font-weight: 600; 
}
</style>
