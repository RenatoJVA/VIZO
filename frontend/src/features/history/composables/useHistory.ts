import { ref, computed } from 'vue'
import { 
  fetchHistory as apiFetchHistory, 
  deleteJob as apiDeleteJob,
  clearHistory as apiClearHistory 
} from '../api/history'

export function useHistory() {
  const jobHistory = ref<Record<string, any>>({})
  const loading = ref(false)
  const error = ref<string | null>(null)

  const sortedJobs = computed(() => {
    return Object.values(jobHistory.value).sort((a: any, b: any) => {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    })
  })

  async function fetchHistory() {
    loading.value = true
    try {
      jobHistory.value = await apiFetchHistory()
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function deleteJob(jobId: string) {
    try {
      await apiDeleteJob(jobId)
      delete jobHistory.value[jobId]
    } catch (e: any) {
      error.value = e.message
    }
  }

  async function clearHistory() {
    try {
      await apiClearHistory()
      jobHistory.value = {}
    } catch (e: any) {
      error.value = e.message
    }
  }

  return {
    jobHistory,
    sortedJobs,
    loading,
    error,
    fetchHistory,
    deleteJob,
    clearHistory
  }
}
