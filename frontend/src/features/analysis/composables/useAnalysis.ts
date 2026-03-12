import { ref } from 'vue'
import { generatePlot as apiGeneratePlot, fetchJobResult } from '../api/analysis'

export function useAnalysis(fetchHistory: () => Promise<void>, jobHistory: any) {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const activeJobs = ref(new Set<string>())
  const pollingInterval = ref<number | null>(null)
  const currentJobId = ref<string | null>(null)
  const currentMetric = ref<string | null>(null)
  const pdfUrl = ref<string | null>(null)

  async function generatePlot(files: File[]) {
    if (!files.length) return
    loading.value = true
    error.value = null

    try {
      const data = await apiGeneratePlot(files)
      if (data.jobs && data.jobs.length > 0) {
        data.jobs.forEach((j: any) => activeJobs.value.add(j.job_id))
        currentJobId.value = data.jobs[0].job_id
        startGlobalPolling()
      }
      return true
    } catch (e: any) {
      error.value = e.message
      return false
    } finally {
      loading.value = false
    }
  }

  function startGlobalPolling() {
    if (pollingInterval.value) return
    
    pollingInterval.value = window.setInterval(async () => {
      await fetchHistory()
      
      let stillRunning = false
      for (const jobId of Array.from(activeJobs.value)) {
        const job = jobHistory.value[jobId]
        if (job) {
          if (job.status === 'completed') {
            activeJobs.value.delete(jobId)
            if (jobId === currentJobId.value) {
              await loadJobResult(jobId)
            }
          } else if (job.status === 'failed') {
            activeJobs.value.delete(jobId)
          } else {
            stillRunning = true
          }
        }
      }
      
      if (!stillRunning && activeJobs.value.size === 0) {
        clearInterval(pollingInterval.value!)
        pollingInterval.value = null
      }
    }, 1500)
  }

  async function loadJobResult(jobId: string) {
    try {
      const blob = await fetchJobResult(jobId)
      const url = URL.createObjectURL(blob)
      
      pdfUrl.value = url
      currentJobId.value = jobId
      currentMetric.value = jobHistory.value[jobId]?.metric || 'plot'
    } catch (e: any) {
      error.value = e.message
    }
  }

  return {
    loading,
    error,
    currentJobId,
    currentMetric,
    pdfUrl,
    generatePlot,
    loadJobResult,
    activeJobs
  }
}
