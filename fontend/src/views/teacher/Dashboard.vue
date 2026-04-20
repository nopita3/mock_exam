<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Teacher Dashboard</h1>

    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-2">Profile</h2>
      <p class="text-gray-600">{{ auth.user?.fname }} {{ auth.user?.lname }}</p>
      <p class="text-sm text-gray-500">{{ auth.user?.email }}</p>
      <p class="text-sm text-gray-500">Department: {{ auth.user?.department }}</p>
    </div>

    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-3">Teacher Code</h2>
      <div class="flex gap-3">
        <input
          v-model="complexCode"
          type="password"
          placeholder="Enter teacher registration code"
          class="input-field flex-1"
        />
        <button @click="saveCode" class="btn-primary">Save Code</button>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-3">Upload Exam Scores</h2>
      <form @submit.prevent="handleUpload" class="space-y-3">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input v-model="upload.exam_name" type="text" placeholder="Exam name" required class="input-field" />
          <input v-model="upload.exam_round" type="text" placeholder="Round" required class="input-field" />
          <input v-model="upload.test_date" type="date" required class="input-field" />
        </div>
        <input type="file" @change="onFileChange" accept=".xlsx,.xls,.csv" class="text-sm" />
        <button type="submit" :disabled="uploading || !upload.file" class="btn-primary">
          {{ uploading ? 'Uploading...' : 'Upload Scores' }}
        </button>
      </form>
      <p v-if="uploadResult" class="text-green-500 text-sm mt-2">{{ uploadResult }}</p>
      <p v-if="uploadError" class="text-red-500 text-sm mt-2">{{ uploadError }}</p>
    </div>

    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <div class="flex items-center justify-between gap-3 mb-3">
        <h2 class="text-lg font-semibold">All Student Scores</h2>
        <button @click="fetchScores" class="btn-secondary" :disabled="!complexCode">Refresh</button>
      </div>
      <div v-if="scoresLoading" class="text-center py-8">Loading...</div>
      <ScoreTable v-else :scores="scores" :showStudent="true" />
      <p v-if="scoresError" class="text-red-500 text-sm mt-4">{{ scoresError }}</p>
    </div>

    <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
      <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between mb-4">
        <div class="flex-1">
          <h2 class="text-lg font-semibold mb-1">Lookup and Edit Student Scores</h2>
          <p class="text-sm text-gray-500">Enter studentID to load the current score rows before editing or deleting.</p>
        </div>
        <div class="flex flex-1 gap-3 md:justify-end">
          <input v-model="scoreLookupStudentId" type="text" placeholder="StudentID" class="input-field flex-1 md:max-w-xs" />
          <button @click="loadScoreEditor" class="btn-primary" :disabled="!complexCode || scoreLookupLoading">
            {{ scoreLookupLoading ? 'Loading...' : 'Load' }}
          </button>
        </div>
      </div>

      <p v-if="scoreLookupError" class="text-red-500 text-sm mb-4">{{ scoreLookupError }}</p>
      <p v-if="scoreLookupMessage" class="text-green-600 text-sm mb-4">{{ scoreLookupMessage }}</p>

      <div v-if="scoreEditor.user_id" class="space-y-4">
        <div class="flex flex-wrap gap-3">
          <button @click="addScoreRow" class="btn-secondary">Add Row</button>
          <button @click="handleUpdateScores" class="btn-primary" :disabled="!scoreEditor.rows.length">Update Scores</button>
          <button @click="handleDeleteScores" class="btn-danger" :disabled="!scoreEditor.user_id">Delete All Scores</button>
          <button @click="clearScoreEditor" class="btn-secondary">Clear</button>
        </div>

        <div v-if="!scoreEditor.rows.length" class="rounded-lg border border-dashed border-gray-300 bg-white p-4 text-sm text-gray-500">
          No score rows loaded.
        </div>

        <div v-for="(row, index) in scoreEditor.rows" :key="row.exam_id || index" class="rounded-lg border border-gray-200 bg-white p-4 space-y-3">
          <div class="flex items-center justify-between gap-3">
            <p class="text-sm font-medium text-gray-700">Row {{ index + 1 }}</p>
            <button @click="removeScoreRow(index)" class="text-sm text-red-600 hover:text-red-700">Remove</button>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
            <input v-model="row.exam_name" type="text" placeholder="Exam name" class="input-field" />
            <input v-model="row.exam_round" type="text" placeholder="Round" class="input-field" />
            <input v-model="row.test_date" type="date" class="input-field" />
            <input v-model.number="row.score" type="number" step="0.01" placeholder="Score" class="input-field" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ScoreTable from '@/components/ScoreTable.vue'
import api from '@/api/client'

const auth = useAuthStore()
const complexCode = ref(localStorage.getItem('teacher_complex_code') || '')
const scores = ref([])
const scoresLoading = ref(true)
const scoresError = ref('')
const uploading = ref(false)
const uploadResult = ref('')
const uploadError = ref('')
const scoreLookupStudentId = ref('')
const scoreLookupLoading = ref(false)
const scoreLookupMessage = ref('')
const scoreLookupError = ref('')
const scoreEditor = reactive({ user_id: '', rows: [] })

const upload = reactive({
  exam_name: '',
  exam_round: '',
  test_date: '',
  file: null,
})

function saveCode() {
  localStorage.setItem('teacher_complex_code', complexCode.value)
}

function onFileChange(e) {
  upload.file = e.target.files[0]
}

function toInputDate(value) {
  if (!value) return ''
  if (value.includes('-')) return value
  const parts = value.split('/')
  if (parts.length !== 3) return value
  const [day, month, year] = parts
  return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
}

function normalizeScoreRows(rows) {
  return rows.map((row) => ({
    ...row,
    test_date: toInputDate(row.test_date),
    score: Number(row.score),
  }))
}

function clearScoreEditor() {
  scoreLookupStudentId.value = ''
  scoreEditor.user_id = ''
  scoreEditor.rows = []
}

function addScoreRow() {
  scoreEditor.rows.push({ exam_name: '', exam_round: '', test_date: '', score: 0 })
}

function removeScoreRow(index) {
  scoreEditor.rows.splice(index, 1)
}

async function fetchScores() {
  if (!complexCode.value) return
  scoresLoading.value = true
  scoresError.value = ''
  try {
    const { data } = await api.get(`/teacher/${complexCode.value}/score/students`)
    scores.value = data.scores || []
  } catch (e) {
    scoresError.value = e.response?.data?.detail || 'Failed to load scores'
    scores.value = []
  } finally {
    scoresLoading.value = false
  }
}

async function handleUpload() {
  if (!complexCode.value) {
    uploadError.value = 'Please enter and save your teacher code first'
    return
  }
  uploading.value = true
  uploadError.value = ''
  uploadResult.value = ''
  try {
    const formData = new FormData()
    formData.append('file', upload.file)
    formData.append('exam_name', upload.exam_name)
    formData.append('exam_round', upload.exam_round)
    formData.append('test_date', upload.test_date)

    const { data } = await api.post(`/teacher/${complexCode.value}/score/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    uploadResult.value = `Uploaded: ${data.inserted_rows} scores inserted, ${data.skipped_rows} skipped.`
    upload.exam_name = ''
    upload.exam_round = ''
    upload.test_date = ''
    upload.file = null
    await fetchScores()
  } catch (e) {
    uploadError.value = e.response?.data?.detail || 'Upload failed'
  } finally {
    uploading.value = false
  }
}

async function loadScoreEditor() {
  if (!complexCode.value || !scoreLookupStudentId.value) return
  scoreLookupLoading.value = true
  scoreLookupMessage.value = ''
  scoreLookupError.value = ''
  try {
    const { data } = await api.get(`/teacher/${complexCode.value}/score/student/${scoreLookupStudentId.value}`)
    scoreEditor.user_id = data.user_id
    scoreEditor.rows = normalizeScoreRows(data.scores || [])
    scoreLookupMessage.value = `Loaded ${scoreEditor.rows.length} score row(s).`
  } catch (e) {
    scoreEditor.user_id = ''
    scoreEditor.rows = []
    scoreLookupError.value = e.response?.data?.detail || 'Failed to load scores'
  } finally {
    scoreLookupLoading.value = false
  }
}

async function handleUpdateScores() {
  if (!complexCode.value || !scoreEditor.user_id || !scoreEditor.rows.length) return
  scoreLookupMessage.value = ''
  scoreLookupError.value = ''
  try {
    const payload = {
      scores: scoreEditor.rows.map((row) => ({
        exam_name: row.exam_name,
        exam_round: row.exam_round,
        test_date: row.test_date,
        score: Number(row.score),
      })),
    }
    const { data } = await api.put(`/teacher/${complexCode.value}/score/student/${scoreEditor.user_id}`, payload)
    scoreEditor.rows = normalizeScoreRows(data.scores || [])
    scoreLookupMessage.value = 'Scores updated successfully.'
    await fetchScores()
  } catch (e) {
    scoreLookupError.value = e.response?.data?.detail || 'Update failed'
  }
}

async function handleDeleteScores() {
  if (!complexCode.value || !scoreEditor.user_id) return
  if (!confirm('Are you sure you want to delete all scores for this student?')) return
  scoreLookupMessage.value = ''
  scoreLookupError.value = ''
  try {
    await api.delete(`/teacher/${complexCode.value}/score/student/${scoreEditor.user_id}`)
    clearScoreEditor()
    scoreLookupMessage.value = 'Scores deleted successfully.'
    await fetchScores()
  } catch (e) {
    scoreLookupError.value = e.response?.data?.detail || 'Delete failed'
  }
}

onMounted(() => {
  if (complexCode.value) fetchScores()
  else scoresLoading.value = false
})
</script>

<style scoped>
.input-field {
  @apply px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#231F20] focus:border-transparent text-sm;
}
.btn-primary {
  @apply bg-[#231F20] text-white rounded-lg px-4 py-2 hover:bg-black disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium;
}
.btn-secondary {
  @apply bg-white text-[#231F20] border border-gray-300 rounded-lg px-4 py-2 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium;
}
.btn-danger {
  @apply bg-[#7A2123] text-white rounded-lg px-4 py-2 hover:bg-[#5f191b] disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium;
}
</style>
