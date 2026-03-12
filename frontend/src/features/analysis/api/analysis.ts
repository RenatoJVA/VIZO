import { API_BASE_URL } from '../../../core/config'

export async function generatePlot(files: File[]) {
  const form = new FormData()
  for (const f of files) form.append('files', f)

  const res = await fetch(`${API_BASE_URL}/plot`, {
    method: 'POST',
    body: form,
  })
  
  if (!res.ok) {
    const data = await res.json()
    throw new Error(data.detail ?? `HTTP ${res.status}`)
  }

  return res.json()
}

export async function fetchJobResult(jobId: string) {
  const res = await fetch(`${API_BASE_URL}/jobs/${jobId}/result`)
  if (!res.ok) throw new Error("Could not get PDF")
  return res.blob()
}
