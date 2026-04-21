<template>
  <div class="space-y-4">
    <h1 class="text-2xl font-bold">Student Information</h1>

    <div class="bg-white rounded-xl shadow p-3">
      <div class="-mx-1 overflow-x-auto pb-1 md:mx-0 md:overflow-visible md:pb-0">
        <div class="flex gap-2 px-1 min-w-max md:min-w-0 md:grid md:grid-cols-2 md:px-0">
          <button @click="activeStudentOperation = 'all'" :class="subMenuButtonClass('all')">
            Get All Student Score
          </button>
          <button @click="activeStudentOperation = 'edit'" :class="subMenuButtonClass('edit')">
            Lookup and Edit Student Scores
          </button>
        </div>
      </div>
    </div>

    <div v-if="activeStudentOperation === 'all'" class="bg-white rounded-xl shadow p-6">
      <div class="flex items-center justify-between gap-3 mb-3">
        <h2 class="text-lg font-semibold">All Student Scores</h2>
        <button @click="fetchScores" class="btn-secondary" :disabled="scoresLoading">Refresh</button>
      </div>
      <div v-if="scoresLoading" class="text-center py-8">Loading...</div>
      <ScoreTable v-else :scores="scores" :showStudent="true" />
      <p v-if="scoresError" class="text-red-500 text-sm mt-4">{{ scoresError }}</p>
    </div>

    <div v-if="activeStudentOperation === 'edit'" class="bg-gray-50 rounded-xl p-4 border border-gray-200">
      <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between mb-4">
        <div class="flex-1">
          <h2 class="text-lg font-semibold mb-1">Lookup and Edit Student Scores</h2>
          <p class="text-sm text-gray-500">Enter studentID to load the current score rows before editing or deleting.</p>
        </div>
        <div class="flex flex-1 gap-3 md:justify-end">
          <input v-model="scoreLookupStudentId" type="text" placeholder="StudentID" class="input-field flex-1 md:max-w-xs" />
          <button @click="loadScoreEditor" class="btn-primary" :disabled="scoreLookupLoading">
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
import { reactive, ref, onMounted } from 'vue'
import api from '@/api/client'
import ScoreTable from '@/components/ScoreTable.vue'

const activeStudentOperation = ref('all')
const scores = ref([])
const scoresLoading = ref(false)
const scoresError = ref('')
const scoreLookupStudentId = ref('')
const scoreLookupLoading = ref(false)
const scoreLookupMessage = ref('')
const scoreLookupError = ref('')
const scoreEditor = reactive({ user_id: '', rows: [] })

function getComplexCode() {
  return localStorage.getItem('teacher_complex_code') || ''
}

function ensureCode() {
  if (!getComplexCode()) {
    const message = 'Please save your teacher code in Profile first.'
    scoresError.value = message
    scoreLookupError.value = message
    return false
  }
  return true
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

function subMenuButtonClass(name) {
  const isActive = activeStudentOperation.value === name
  return [
    'rounded-lg px-4 py-3 text-sm font-medium transition whitespace-nowrap min-w-[220px] md:min-w-0 md:w-full',
    isActive ? 'bg-[#7A2123] text-white' : 'bg-gray-100 text-[#231F20] hover:bg-gray-200',
  ]
}

async function fetchScores() {
  if (!ensureCode()) return
  const complexCode = getComplexCode()
  scoresLoading.value = true
  scoresError.value = ''
  try {
    const { data } = await api.get(`/teacher/${complexCode}/score/students`)
    scores.value = data.scores || []
  } catch (e) {
    scoresError.value = e.response?.data?.detail || 'Failed to load scores'
    scores.value = []
  } finally {
    scoresLoading.value = false
  }
}

async function loadScoreEditor() {
  if (!scoreLookupStudentId.value || !ensureCode()) return
  const complexCode = getComplexCode()
  scoreLookupLoading.value = true
  scoreLookupMessage.value = ''
  scoreLookupError.value = ''
  try {
    const { data } = await api.get(`/teacher/${complexCode}/score/student/${scoreLookupStudentId.value}`)
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
  if (!scoreEditor.user_id || !scoreEditor.rows.length || !ensureCode()) return
  const complexCode = getComplexCode()
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
    const { data } = await api.put(`/teacher/${complexCode}/score/student/${scoreEditor.user_id}`, payload)
    scoreEditor.rows = normalizeScoreRows(data.scores || [])
    scoreLookupMessage.value = 'Scores updated successfully.'
    await fetchScores()
  } catch (e) {
    scoreLookupError.value = e.response?.data?.detail || 'Update failed'
  }
}

async function handleDeleteScores() {
  if (!scoreEditor.user_id || !ensureCode()) return
  if (!confirm('Are you sure you want to delete all scores for this student?')) return
  const complexCode = getComplexCode()
  scoreLookupMessage.value = ''
  scoreLookupError.value = ''
  try {
    await api.delete(`/teacher/${complexCode}/score/student/${scoreEditor.user_id}`)
    clearScoreEditor()
    scoreLookupMessage.value = 'Scores deleted successfully.'
    await fetchScores()
  } catch (e) {
    scoreLookupError.value = e.response?.data?.detail || 'Delete failed'
  }
}

onMounted(() => {
  if (getComplexCode()) {
    fetchScores()
  }
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
