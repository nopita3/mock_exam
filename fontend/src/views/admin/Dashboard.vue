<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Admin Dashboard</h1>

    <!-- Profile Card -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-2">Profile</h2>
      <p class="text-gray-600">{{ auth.user?.fname }} {{ auth.user?.lname }}</p>
      <p class="text-sm text-gray-500">{{ auth.user?.email }}</p>
    </div>

    <!-- Complex Code -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-3">Admin Code</h2>
      <div class="flex gap-3">
        <input v-model="complexCode" type="password" placeholder="Enter admin registration code" class="input-field flex-1" />
        <button @click="saveCode" class="btn-primary">Save Code</button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow mb-6">
      <div class="flex border-b">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          class="px-4 py-3 text-sm font-medium transition"
          :class="activeTab === tab.key ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="p-6">
        <!-- Logs Tab -->
        <div v-if="activeTab === 'logs'">
          <button @click="fetchLogs" class="btn-primary mb-4" :disabled="!complexCode">Refresh Logs</button>
          <div v-if="logsLoading" class="text-center py-4">Loading...</div>
          <LogTable v-else :logs="logs" />
        </div>

        <!-- Scores Tab -->
        <div v-if="activeTab === 'scores'">
          <h3 class="font-semibold mb-3">Upload Scores</h3>
          <form @submit.prevent="handleUpload" class="space-y-3 mb-6">
            <div class="grid grid-cols-3 gap-3">
              <input v-model="upload.exam_name" type="text" placeholder="Exam name" required class="input-field" />
              <input v-model="upload.exam_round" type="text" placeholder="Round" required class="input-field" />
              <input v-model="upload.test_date" type="date" required class="input-field" />
            </div>
            <input type="file" @change="onFileChange" accept=".xlsx,.xls,.csv" class="text-sm" />
            <button type="submit" :disabled="uploading || !upload.file" class="btn-primary">
              {{ uploading ? 'Uploading...' : 'Upload' }}
            </button>
          </form>
          <p v-if="uploadResult" class="text-green-500 text-sm mb-4">{{ uploadResult }}</p>

          <button @click="fetchScores" class="btn-primary mb-4" :disabled="!complexCode">Refresh Scores</button>
          <div v-if="scoresLoading" class="text-center py-4">Loading...</div>
          <ScoreTable v-else :scores="scores" :showStudent="true" />
        </div>

        <!-- Students Tab -->
        <div v-if="activeTab === 'students'">
          <h3 class="font-semibold mb-3">Manage Students</h3>
          <p class="text-sm text-gray-500 mb-4">Use student user_id to update or delete.</p>
          <form @submit.prevent="handleUpdateStudent" class="space-y-3 mb-6">
            <input v-model="studentForm.student_user_id" type="text" placeholder="Student user_id" required class="input-field w-full" />
            <div class="grid grid-cols-2 gap-3">
              <input v-model="studentForm.fname" type="text" placeholder="First name" class="input-field" />
              <input v-model="studentForm.lname" type="text" placeholder="Last name" class="input-field" />
            </div>
            <input v-model="studentForm.nname" type="text" placeholder="Nickname" class="input-field w-full" />
            <select v-model="studentForm.department" class="input-field w-full">
              <option value="">Leave unchanged</option>
              <option value="Medical Science">Medical Science</option>
              <option value="Applied Science">Applied Science</option>
              <option value="Social Science">Social Science</option>
            </select>
            <div class="flex gap-3">
              <button type="submit" class="btn-primary" :disabled="!complexCode">Update Student</button>
              <button type="button" @click="handleDeleteStudent" class="btn-danger" :disabled="!complexCode">Delete Student</button>
            </div>
          </form>
          <p v-if="studentMsg" class="text-green-500 text-sm">{{ studentMsg }}</p>
          <p v-if="studentError" class="text-red-500 text-sm">{{ studentError }}</p>
        </div>

        <!-- Teachers Tab -->
        <div v-if="activeTab === 'teachers'">
          <h3 class="font-semibold mb-3">Manage Teachers</h3>
          <p class="text-sm text-gray-500 mb-4">Use teacher user_id to update or delete.</p>
          <form @submit.prevent="handleUpdateTeacher" class="space-y-3 mb-6">
            <input v-model="teacherForm.teacher_user_id" type="text" placeholder="Teacher user_id" required class="input-field w-full" />
            <div class="grid grid-cols-2 gap-3">
              <input v-model="teacherForm.fname" type="text" placeholder="First name" class="input-field" />
              <input v-model="teacherForm.lname" type="text" placeholder="Last name" class="input-field" />
            </div>
            <input v-model="teacherForm.nname" type="text" placeholder="Nickname" class="input-field w-full" />
            <div class="flex gap-3">
              <button type="submit" class="btn-primary" :disabled="!complexCode">Update Teacher</button>
              <button type="button" @click="handleDeleteTeacher" class="btn-danger" :disabled="!complexCode">Delete Teacher</button>
            </div>
          </form>
          <p v-if="teacherMsg" class="text-green-500 text-sm">{{ teacherMsg }}</p>
          <p v-if="teacherError" class="text-red-500 text-sm">{{ teacherError }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ScoreTable from '@/components/ScoreTable.vue'
import LogTable from '@/components/LogTable.vue'
import api from '@/api/client'

const auth = useAuthStore()
const complexCode = ref(localStorage.getItem('admin_complex_code') || '')
const activeTab = ref('logs')

const tabs = [
  { key: 'logs', label: 'Logs' },
  { key: 'scores', label: 'Scores' },
  { key: 'students', label: 'Students' },
  { key: 'teachers', label: 'Teachers' },
]

// Logs
const logs = ref([])
const logsLoading = ref(false)

async function fetchLogs() {
  if (!complexCode.value) return
  logsLoading.value = true
  try {
    const { data } = await api.get(`/admin/${complexCode.value}/logs`)
    logs.value = data.logs || []
  } catch {
    logs.value = []
  } finally {
    logsLoading.value = false
  }
}

// Scores
const scores = ref([])
const scoresLoading = ref(false)

async function fetchScores() {
  if (!complexCode.value) return
  scoresLoading.value = true
  try {
    const { data } = await api.get(`/admin/${complexCode.value}/score/students`)
    scores.value = data.scores || []
  } catch {
    scores.value = []
  } finally {
    scoresLoading.value = false
  }
}

const uploading = ref(false)
const uploadResult = ref('')
const upload = reactive({ exam_name: '', exam_round: '', test_date: '', file: null })

function onFileChange(e) { upload.file = e.target.files[0] }

async function handleUpload() {
  if (!complexCode.value) return
  uploading.value = true
  uploadResult.value = ''
  try {
    const formData = new FormData()
    formData.append('file', upload.file)
    formData.append('exam_name', upload.exam_name)
    formData.append('exam_round', upload.exam_round)
    formData.append('test_date', upload.test_date)
    const { data } = await api.post(`/admin/${complexCode.value}/score/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    uploadResult.value = `${data.inserted_rows} inserted, ${data.skipped_rows} skipped.`
    await fetchScores()
  } catch {
    uploadResult.value = 'Upload failed'
  } finally {
    uploading.value = false
  }
}

// Students
const studentForm = reactive({ student_user_id: '', fname: '', lname: '', nname: '', department: '' })
const studentMsg = ref('')
const studentError = ref('')

async function handleUpdateStudent() {
  if (!complexCode.value || !studentForm.student_user_id) return
  studentMsg.value = ''
  studentError.value = ''
  try {
    const body = { fname: studentForm.fname, lname: studentForm.lname, nname: studentForm.nname }
    if (studentForm.department) body.department = studentForm.department
    await api.put(`/admin/${complexCode.value}/student/${studentForm.student_user_id}`, body)
    studentMsg.value = 'Student updated successfully'
  } catch (e) {
    studentError.value = e.response?.data?.detail || 'Update failed'
  }
}

async function handleDeleteStudent() {
  if (!complexCode.value || !studentForm.student_user_id) return
  if (!confirm('Are you sure you want to delete this student?')) return
  studentMsg.value = ''
  studentError.value = ''
  try {
    await api.delete(`/admin/${complexCode.value}/student/${studentForm.student_user_id}`)
    studentMsg.value = 'Student deleted successfully'
  } catch (e) {
    studentError.value = e.response?.data?.detail || 'Delete failed'
  }
}

// Teachers
const teacherForm = reactive({ teacher_user_id: '', fname: '', lname: '', nname: '' })
const teacherMsg = ref('')
const teacherError = ref('')

async function handleUpdateTeacher() {
  if (!complexCode.value || !teacherForm.teacher_user_id) return
  teacherMsg.value = ''
  teacherError.value = ''
  try {
    const body = { fname: teacherForm.fname, lname: teacherForm.lname, nname: teacherForm.nname }
    await api.put(`/admin/${complexCode.value}/teacher/${teacherForm.teacher_user_id}`, body)
    teacherMsg.value = 'Teacher updated successfully'
  } catch (e) {
    teacherError.value = e.response?.data?.detail || 'Update failed'
  }
}

async function handleDeleteTeacher() {
  if (!complexCode.value || !teacherForm.teacher_user_id) return
  if (!confirm('Are you sure you want to delete this teacher?')) return
  teacherMsg.value = ''
  teacherError.value = ''
  try {
    await api.delete(`/admin/${complexCode.value}/teacher/${teacherForm.teacher_user_id}`)
    teacherMsg.value = 'Teacher deleted successfully'
  } catch (e) {
    teacherError.value = e.response?.data?.detail || 'Delete failed'
  }
}

function saveCode() {
  localStorage.setItem('admin_complex_code', complexCode.value)
}
</script>

<style scoped>
.input-field {
  @apply px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm;
}
.btn-primary {
  @apply bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium;
}
.btn-danger {
  @apply bg-red-600 text-white rounded-lg px-4 py-2 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium;
}
</style>
