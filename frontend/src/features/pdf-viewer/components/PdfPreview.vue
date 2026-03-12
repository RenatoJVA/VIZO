<template>
  <transition name="fade">
    <div v-if="pdfUrl" class="pdf-section">
      <div class="pdf-toolbar">
        <div class="pdf-toolbar-left">
          <span class="result-badge">{{ metric?.toUpperCase() || 'PLOT' }}</span>
          <span class="pdf-filename">Previewing Analysis</span>
        </div>
        <a class="btn-download" :href="pdfUrl" :download="`${metric || 'plot'}.pdf`">
          ↓ Download PDF
        </a>
      </div>

      <div class="pdf-viewer">
        <canvas ref="pdfCanvas"></canvas>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = defineProps<{
  pdfUrl: string | null
  metric: string | null
}>()

const pdfCanvas = ref<HTMLCanvasElement | null>(null)

watch(() => props.pdfUrl, async (newUrl) => {
  if (newUrl) {
    await nextTick()
    renderPdf(newUrl)
  }
})

async function renderPdf(url: string) {
  try {
    // @ts-ignore
    const pdfjsLib = await import(/* @vite-ignore */ 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.3.136/pdf.min.mjs')
    pdfjsLib.GlobalWorkerOptions.workerSrc =
      'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.3.136/pdf.worker.min.mjs'

    const pdf = await pdfjsLib.getDocument(url).promise
    const page = await pdf.getPage(1)

    const container = pdfCanvas.value!.parentElement!
    const viewport = page.getViewport({ scale: 1 })
    const scale = (container.clientWidth - 48) / viewport.width
    const scaled = page.getViewport({ scale })

    const canvas = pdfCanvas.value!
    if (canvas) {
      canvas.width = scaled.width
      canvas.height = scaled.height

      await page.render({
        canvasContext: canvas.getContext('2d')!,
        viewport: scaled,
      }).promise
    }
  } catch (e) {
    console.warn("Render error", e)
  }
}
</script>

<style scoped>
.pdf-section { border-radius: var(--radius); overflow: hidden; border: 1px solid var(--border); background: var(--surface); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.3); }
.pdf-toolbar { display: flex; align-items: center; justify-content: space-between; padding: 14px 24px; border-bottom: 1px solid var(--border); }
.result-badge { background: var(--accent); color: #fff; padding: 4px 12px; border-radius: 8px; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.05em; }
.btn-download { padding: 8px 20px; background: #fff; color: #000; border-radius: 10px; text-decoration: none; font-size: 0.85rem; font-weight: 700; transition: background 0.2s; }
.btn-download:hover { background: #e2e8f0; }

.pdf-viewer { background: #0f172a; padding: 40px; display: flex; justify-content: center; }
.pdf-viewer canvas { max-width: 100%; border-radius: 8px; box-shadow: 0 0 40px rgba(0,0,0,0.5); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.4s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
