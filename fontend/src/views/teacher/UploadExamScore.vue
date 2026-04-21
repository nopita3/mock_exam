<template>
  <div class="bg-white rounded-xl shadow p-6">
    <h1 class="text-2xl font-bold mb-5">Upload Exam Score</h1>

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

    <p v-if="uploadResult" class="text-green-600 text-sm mt-2">{{ uploadResult }}</p>
    <p v-if="uploadError" class="text-red-500 text-sm mt-2">{{ uploadError }}</p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import api from '@/api/client'

const uploading = ref(false)
const uploadResult = ref('')
const uploadError = ref('')
const upload = reactive({
  exam_name: '',
  exam_round: '',
  test_date: '',
  file: null,
})

function onFileChange(e) {
  upload.file = e.target.files[0]
}

function getComplexCode() {
  return localStorage.getItem('teacher_complex_code') || ''
}

async function handleUpload() {
  const complexCode = getComplexCode()
  if (!complexCode) {
    uploadError.value = 'Please save your teacher code in Profile first.'
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

    const { data } = await api.post(`/teacher/${complexCode}/score/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    uploadResult.value = `Uploaded: ${data.inserted_rows} scores inserted, ${data.skipped_rows} skipped.`
    upload.exam_name = ''
    upload.exam_round = ''
    upload.test_date = ''
    upload.file = null
  } catch (e) {
    uploadError.value = e.response?.data?.detail || 'Upload failed'
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.input-field {
  @apply px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#231F20] focus:border-transparent text-sm;
}
.btn-primary {
  @apply bg-[#231F20] text-white rounded-lg px-4 py-2 hover:bg-black disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium;
}
</style>
