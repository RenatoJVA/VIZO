<template>
  <section class="history-section">
    <div class="history-header">
      <h2>Analysis History</h2>
      <div>

        <a :href="`${API_BASE_URL}/jobs/download-all`" class="btn-zip" title="Download all completed PDF analysis">
          ↓ Download All (.zip)
        </a>
        <button @click="$emit('clear')" class="btn-clear">Clear History</button>
      </div>
      </div>

    <div v-if="jobs.length === 0" class="empty-history">
      No previous analysis found.
    </div>


    <div v-else class="history-list">
      <div v-for="job in jobs" :key="job.id" class="job-card" :class="job.status">
        <div class="job-info">
          <span class="job-id">#{{ job.id }}</span>
          <span class="job-metric">{{ job.metric.toUpperCase() }}</span>
          <span class="job-date">{{ formatDate(job.created_at) }}</span>
        </div>

        <div class="job-status-area">
          <StatusPill :status="job.status" />
        </div>

        <div class="job-actions">
          <a v-if="job.status === 'completed'" :href="`${API_BASE_URL}/jobs/${job.id}/download`" class="btn-zip"
            title="Download ZIP">
            ↓
          </a>
          <button v-if="job.status === 'completed'" @click="$emit('view', job.id)" class="btn-view"
            :class="{ active: currentJobId === job.id }">
            View
          </button>
          <button @click="$emit('delete', job.id)" class="btn-delete">🗑</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import StatusPill from './StatusPill.vue'
import { API_BASE_URL } from '../../../core/config'

defineProps<{
  jobs: any[]
  currentJobId: string | null
}>()

defineEmits(['view', 'delete', 'clear'])

function formatDate(iso: string) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.history-section {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 30px;
  background: rgba(30, 41, 59, 0.3);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.job-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  transition: all 0.2s;
}

.job-card:hover {
  border-color: var(--accent2);
  transform: translateX(6px);
}

.job-id {
  font-family: monospace;
  color: var(--accent2);
  font-weight: bold;
  font-size: 0.75rem;
}

.job-metric {
  font-size: 1.1rem;
  font-weight: 800;
  margin: 2px 0;
}

.job-date {
  font-size: 0.75rem;
  color: var(--muted);
}

.job-info {
  display: flex;
  flex-direction: column;
}

.job-actions {
  display: flex;
  gap: 10px;
}

.btn-view,
.btn-zip,
.btn-delete,
.btn-clear {
  padding: 10px 18px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid var(--border);
  background: rgba(15, 23, 42, 0.5);
  color: var(--text);
  text-decoration: none;
  transition: all 0.2s;
}

.btn-view.active {
  border-color: var(--accent);
  background: var(--accent);
}

.btn-view:hover:not(.active) {
  background: var(--surface);
  border-color: var(--muted);
}

.btn-delete:hover {
  border-color: #ef4444;
  color: #ef4444;
}

.empty-history {
  text-align: center;
  color: var(--muted);
  padding: 20px;
}

.storage-hint {
  color: var(--muted);
  font-size: 0.8rem;
}

.btn-download {
  padding: 8px 20px;
  background: #fff;
  color: #000;
  border-radius: 10px;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 700;
  transition: background 0.2s;
}

.btn-download:hover {
  background: #e2e8f0;
}

</style>
