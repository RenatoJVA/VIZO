<template>
  <div class="status-pill" :class="status">
    <template v-if="status === 'running'">
      <BaseSpinner small /> processing
    </template>
    <template v-else-if="status === 'completed'">
      ✓ ready
    </template>
    <template v-else>
      ✕ failed
    </template>
  </div>
</template>

<script setup lang="ts">
import BaseSpinner from '../../../shared/components/BaseSpinner.vue'

defineProps<{
  status: 'running' | 'completed' | 'failed'
}>()
</script>

<style scoped>
.status-pill { 
  padding: 6px 14px; 
  border-radius: 99px; 
  font-size: 0.7rem; 
  font-weight: 800; 
  text-transform: uppercase; 
  letter-spacing: 0.05em; 
  display: flex; 
  align-items: center; 
  gap: 6px; 
}
.status-pill.running { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); }
.status-pill.completed { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }
.status-pill.failed { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
</style>
