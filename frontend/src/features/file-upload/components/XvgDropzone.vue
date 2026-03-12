<template>
  <div class="dropzone" :class="{ dragover: isDragging, hasFiles: files.length > 0 }"
    @dragover.prevent="isDragging = true" @dragleave="isDragging = false" @drop.prevent="onDrop"
    @click="fileInput?.click()">
    <input ref="fileInput" type="file" multiple accept=".xvg" style="display:none" @change="onFileChange" />
    <div v-if="files.length === 0" class="drop-prompt">
      <div class="drop-icon">↑</div>
      <p>Drop <strong>.xvg</strong> files here or click to browse</p>
      <p class="hint">Puedes subir múltiples métricas a la vez (ej. rmsd y rmsf)</p>
    </div>
    <div v-else class="file-list">
      <div v-for="(f, i) in files" :key="i" class="file-chip">
        <span class="chip-icon">▤</span>
        <span class="chip-name">{{ f.name }}</span>
        <button class="chip-remove" @click.stop="removeFile(i)">×</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  files: File[]
}>()

const emit = defineEmits(['update:files'])

const isDragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) addFiles(Array.from(input.files))
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  if (e.dataTransfer?.files) addFiles(Array.from(e.dataTransfer.files))
}

function addFiles(newFiles: File[]) {
  const updatedFiles = [...props.files]
  const existing = new Set(updatedFiles.map(f => f.name))
  updatedFiles.push(...newFiles.filter(f => !existing.has(f.name)))
  emit('update:files', updatedFiles)
}

function removeFile(i: number) {
  const updatedFiles = [...props.files]
  updatedFiles.splice(i, 1)
  emit('update:files', updatedFiles)
}
</script>

<style scoped>
.dropzone {
  border: 2px dashed var(--border); 
  border-radius: var(--radius); 
  padding: 40px; 
  cursor: pointer; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 140px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  background: rgba(30, 41, 59, 0.5);
}
.dropzone:hover, .dropzone.dragover { 
  border-color: var(--accent); 
  background: rgba(236, 72, 153, 0.05); 
  transform: scale(1.01); 
}
.drop-prompt { text-align: center; color: var(--muted); }
.drop-icon { font-size: 2rem; margin-bottom: 12px; color: var(--accent); }
.hint { margin-top: 8px; font-size: 0.8rem; opacity: 0.7; }

.file-list { display: flex; flex-wrap: wrap; gap: 10px; }
.file-chip {
  display: flex; 
  align-items: center; 
  gap: 8px; 
  background: var(--surface); 
  border: 1px solid var(--border);
  border-radius: 10px; 
  padding: 6px 14px; 
  font-size: 0.85rem; 
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}
.chip-name { max-width: 200px; overflow: hidden; text-overflow: ellipsis; }
.chip-remove { background: none; border: none; color: var(--muted); cursor: pointer; font-size: 1.2rem; }
.chip-remove:hover { color: var(--accent); }
</style>
