<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Teacher Dashboard</h1>

    <!-- Profile Card -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-2">Profile</h2>
      <p class="text-gray-600">{{ auth.user?.fname }} {{ auth.user?.lname }}</p>
      <p class="text-sm text-gray-500">{{ auth.user?.email }}</p>
      <p class="text-sm text-gray-500">Department: {{ auth.user?.department }}</p>
    </div>

    <!-- Complex Code Input -->
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

    <!-- Upload Scores -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-3">Upload Exam Scores</h2>
      <form @submit.prevent="handleUpload" class="space-y-3">
        <div class="grid grid-cols-3 gap-3">
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

    <!-- All Student Scores -->
    <h2 class="text-lg font-semibold mb-3">All Student Scores</h2>
    <div v-if="scoresLoading" class="text-center py-8">Loading...</div>
    <ScoreTable v-else :scores="scores" :showStudent="true" />
    <p v-if="scoresError" class="text-red-500 text-sm mt-4">{{ scoresError }}</p>
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

async function fetchScores() {
  if (!complexCode.value) return
  scoresLoading.value = true
  try {
    const { data } = await api.get(`/teacher/${complexCode.value}/score/students`)
    scores.value = data.scores || []
  } catch (e) {
    scoresError.value = 'Failed to load scores'
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

onMounted(() => {
  if (complexCode.value) fetchScores()
  else scoresLoading.value = false
})
</script>

<style scoped>
.input-field {
  @apply px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm;
}
.btn-primary {
  @apply bg-indigo-600 text-white rounded-lg px-4 py-2 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium;
}
</style>
