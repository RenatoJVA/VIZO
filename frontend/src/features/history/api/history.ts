import { API_BASE_URL } from '../../../core/config'

export async function fetchHistory() {
  const res = await fetch(`${API_BASE_URL}/jobs`)
  if (!res.ok) throw new Error('Error loading history')
  return res.json()
}

export async function deleteJob(jobId: string) {
  const res = await fetch(`${API_BASE_URL}/jobs/${jobId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Error deleting job')
}

export async function clearHistory() {
  const res = await fetch(`${API_BASE_URL}/jobs/clear-all`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Error clearing history')
}
