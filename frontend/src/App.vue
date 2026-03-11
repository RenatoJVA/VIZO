<template>
  <div class="app">
    <header class="header">
      <div class="header-inner">
        <span class="logo">⬡</span>
        <h1>MD <em>Analysis</em></h1>
        <p class="subtitle">Upload XVG files</p>
      </div>
    </header>

    <main class="main">
      <!-- ── Drop zone ── -->
      <div class="dropzone" :class="{ dragover: isDragging, hasFiles: files.length > 0 }"
        @dragover.prevent="isDragging = true" @dragleave="isDragging = false" @drop.prevent="onDrop"
        @click="$refs.fileInput.click()">
        <input ref="fileInput" type="file" multiple accept=".xvg" style="display:none" @change="onFileChange" />
        <div v-if="files.length === 0" class="drop-prompt">
          <div class="drop-icon">↑</div>
          <p>Drop <strong>.xvg</strong> files here or click to browse</p>
          <p class="hint">All files must share the same metric (e.g. <code>-rmsd.xvg</code>)</p>
        </div>
        <div v-else class="file-list">
          <div v-for="(f, i) in files" :key="i" class="file-chip">
            <span class="chip-icon">▤</span>
            <span class="chip-name">{{ f.name }}</span>
            <button class="chip-remove" @click.stop="removeFile(i)">×</button>
          </div>
        </div>
      </div>

      <!-- ── Actions ── -->
      <div class="actions">
        <button class="btn-generate" :disabled="files.length === 0 || loading" @click="generatePlot">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Generate PDF</span>
        </button>
        <button v-if="files.length > 0" class="btn-clear" @click="clearAll">
          Clear
        </button>
      </div>

      <!-- ── Error ── -->
      <div v-if="error" class="error-box">
        <strong>Error:</strong> {{ error }}
      </div>

      <!-- ── PDF Viewer ── -->
      <transition name="fade">
        <div v-if="pdfUrl" class="pdf-section">

          <!-- Toolbar propia — sin la barra horrible del navegador -->
          <div class="pdf-toolbar">
            <div class="pdf-toolbar-left">
              <span class="result-badge">{{ detectedMetric?.toUpperCase() }}</span>
              <span class="pdf-filename">{{ downloadName }}</span>
            </div>
            <a class="btn-download" :href="pdfUrl" :download="downloadName">
              ↓ Download PDF
            </a>
          </div>

          <!-- PDF.js renderiza aquí, en canvas limpio -->
          <div class="pdf-viewer">
            <canvas ref="pdfCanvas"></canvas>
          </div>

        </div>
      </transition>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const files = ref<File[]>([])
const pdfUrl = ref<string | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const isDragging = ref(false)
const pdfCanvas = ref<HTMLCanvasElement | null>(null)

const detectedMetric = computed(() => {
  if (!files.value.length) return null
  const name = files.value[0].name
  const metrics = ['rmsd', 'rmsf', 'rg', 'sasa', 'hbnum']
  return metrics.find(m => name.endsWith(`-${m}.xvg`)) ?? 'plot'
})
const downloadName = computed(() => `${detectedMetric.value}.pdf`)

// ── Archivos ──────────────────────────────────────────────────────
function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) addFiles(Array.from(input.files))
}
function onDrop(e: DragEvent) {
  isDragging.value = false
  if (e.dataTransfer?.files) addFiles(Array.from(e.dataTransfer.files))
}
function addFiles(newFiles: File[]) {
  const existing = new Set(files.value.map(f => f.name))
  files.value.push(...newFiles.filter(f => !existing.has(f.name)))
  pdfUrl.value = null
  error.value = null
}
function removeFile(i: number) {
  files.value.splice(i, 1)
  pdfUrl.value = null
}
function clearAll() {
  files.value = []
  pdfUrl.value = null
  error.value = null
}

// ── Fetch al backend ──────────────────────────────────────────────
async function generatePlot() {
  if (!files.value.length) return
  loading.value = true
  error.value = null
  pdfUrl.value = null

  const form = new FormData()
  for (const f of files.value) form.append('files', f)

  try {
    const res = await fetch('http://127.0.0.1:8000/plot', {
      method: 'POST',
      body: form,
    })
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail ?? `HTTP ${res.status}`)
    }

    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    pdfUrl.value = url

    // Pequeño delay para que Vue monte el canvas antes de renderizar
    await nextTick()
    await renderPdf(url)

  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// ── PDF.js: renderizar en canvas sin toolbars ─────────────────────
// En lugar del <iframe> (que muestra la toolbar del navegador),
// usamos PDF.js para dibujar el PDF directamente en un <canvas>.
// Resultado: control total sobre cómo se ve.
async function renderPdf(url: string) {
  // Cargamos PDF.js desde CDN solo cuando se necesita
  const pdfjsLib = await import('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.3.136/pdf.min.mjs') as any
  pdfjsLib.GlobalWorkerOptions.workerSrc =
    'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.3.136/pdf.worker.min.mjs'

  const pdf = await pdfjsLib.getDocument(url).promise
  const page = await pdf.getPage(1)

  // Calcular escala para llenar el ancho del contenedor
  const container = pdfCanvas.value!.parentElement!
  const viewport = page.getViewport({ scale: 1 })
  const scale = (container.clientWidth - 48) / viewport.width  // 48 = padding 24px×2
  const scaled = page.getViewport({ scale })

  const canvas = pdfCanvas.value!
  canvas.width = scaled.width
  canvas.height = scaled.height

  await page.render({
    canvasContext: canvas.getContext('2d')!,
    viewport: scaled,
  }).promise
}

// nextTick: espera a que Vue termine de actualizar el DOM
// Necesario para que el <canvas> exista antes de que PDF.js lo use
import { nextTick } from 'vue'
</script>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --bg: #0b0c0f;
  --surface: #13151a;
  --border: #1e2028;
  --accent: #c52a91;
  --accent2: #8d25a7;
  --text: #e8e8f0;
  --muted: #6b6d80;
  --radius: 12px;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'DM Sans', system-ui, sans-serif;
  min-height: 100vh;
}

.header {
  border-bottom: 1px solid var(--border);
  padding: 24px 40px;
}

.header-inner {
  display: flex;
  align-items: baseline;
  gap: 14px;
}

.logo {
  font-size: 1.5rem;
  color: var(--accent);
}

.header h1 {
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.header h1 em {
  font-style: normal;
  color: var(--accent);
}

.subtitle {
  margin-left: auto;
  color: var(--muted);
  font-size: 0.82rem;
}

.main {
  max-width: 960px;
  margin: 40px auto;
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Dropzone */
.dropzone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 40px 32px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dropzone:hover,
.dropzone.dragover {
  border-color: var(--accent);
  background: rgba(197, 42, 145, 0.04);
}

.dropzone.hasFiles {
  padding: 16px 20px;
  justify-content: flex-start;
  align-items: flex-start;
}

.drop-prompt {
  text-align: center;
  color: var(--muted);
}

.drop-icon {
  font-size: 1.8rem;
  margin-bottom: 10px;
  color: var(--accent);
}

.drop-prompt p {
  font-size: 0.9rem;
  line-height: 1.8;
}

.drop-prompt strong {
  color: var(--text);
}

.hint {
  font-size: 0.76rem;
  margin-top: 4px;
}

code {
  background: rgba(255, 255, 255, 0.07);
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 0.76rem;
}

.file-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.file-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 5px 10px;
  font-size: 0.8rem;
}

.chip-icon {
  color: var(--accent);
}

.chip-name {
  color: var(--text);
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chip-remove {
  background: none;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 1rem;
  padding: 0 2px;
}

.chip-remove:hover {
  color: var(--accent);
}

/* Actions */
.actions {
  display: flex;
  gap: 10px;
}

.btn-generate {
  flex: 1;
  padding: 13px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: var(--radius);
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-generate:hover:not(:disabled) {
  opacity: 0.88;
  transform: translateY(-1px);
}

.btn-generate:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.btn-clear {
  padding: 13px 20px;
  background: transparent;
  color: var(--muted);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 0.88rem;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s;
}

.btn-clear:hover {
  color: var(--text);
  border-color: var(--muted);
}

.spinner {
  width: 15px;
  height: 15px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Error */
.error-box {
  background: rgba(220, 40, 40, 0.08);
  border: 1px solid rgba(220, 40, 40, 0.3);
  border-radius: var(--radius);
  padding: 12px 16px;
  font-size: 0.85rem;
  color: #f87171;
}

/* PDF Section */
.pdf-section {
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid var(--border);
}

/* Toolbar personalizada */
.pdf-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.pdf-toolbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.result-badge {
  background: rgba(197, 42, 145, 0.15);
  color: var(--accent);
  border: 1px solid rgba(197, 42, 145, 0.3);
  border-radius: 5px;
  padding: 2px 8px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.pdf-filename {
  color: var(--muted);
  font-size: 0.82rem;
}

.btn-download {
  padding: 7px 16px;
  background: var(--accent2);
  color: #fff;
  border-radius: 7px;
  text-decoration: none;
  font-size: 0.82rem;
  font-weight: 600;
  transition: opacity 0.2s;
}

.btn-download:hover {
  opacity: 0.85;
}

/* Canvas: fondo blanco como papel, sin scrollbar, sin toolbar */
.pdf-viewer {
  background: #efefef;
  padding: 24px;
  display: flex;
  justify-content: center;
}

.pdf-viewer canvas {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 3px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.2);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>