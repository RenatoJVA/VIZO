<template>
  <div class="app">
    <AppHeader />

    <main class="main">
      <XvgDropzone v-model:files="files" />

      <AnalysisControls :loading="analysisLoading" :has-files="files.length > 0" :disabled="files.length === 0"
        @generate="handleGenerate" @clear="files = []" />

      <div v-if="analysisError || historyError" class="error-box">
        <strong>Error:</strong> {{ analysisError || historyError }}
      </div>

      <PdfPreview :pdf-url="pdfUrl" :metric="currentMetric" />

      <JobHistory :jobs="sortedJobs" :current-job-id="currentJobId" @view="loadJobResult" @delete="deleteJob"
        @clear="clearHistory" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppHeader from './shared/components/AppHeader.vue'
import XvgDropzone from './features/file-upload/components/XvgDropzone.vue'
import AnalysisControls from './features/analysis/components/AnalysisControls.vue'
import PdfPreview from './features/pdf-viewer/components/PdfPreview.vue'
import JobHistory from './features/history/components/JobHistory.vue'

import { useHistory } from './features/history/composables/useHistory'
import { useAnalysis } from './features/analysis/composables/useAnalysis'

const files = ref<File[]>([])

const {
  jobHistory,
  sortedJobs,
  error: historyError,
  fetchHistory,
  deleteJob,
  clearHistory
} = useHistory()

const {
  loading: analysisLoading,
  error: analysisError,
  currentJobId,
  currentMetric,
  pdfUrl,
  generatePlot,
  loadJobResult
} = useAnalysis(fetchHistory, jobHistory)

async function handleGenerate() {
  const success = await generatePlot(files.value)
  if (success) {
    files.value = []
  }
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.main {
  max-width: 1000px;
  margin: 40px auto;
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.error-box {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius);
  padding: 16px;
  color: #f87171;
  font-size: 0.9rem;
}
</style>