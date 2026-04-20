<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Admin Dashboard</h1>

    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-2">Profile</h2>
      <p class="text-gray-600">{{ auth.user?.fname }} {{ auth.user?.lname }}</p>
      <p class="text-sm text-gray-500">{{ auth.user?.email }}</p>
    </div>

    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-3">Admin Code</h2>
      <div class="flex gap-3">
        <input v-model="complexCode" type="password" placeholder="Enter admin registration code" class="input-field flex-1" />
        <button @click="saveCode" class="btn-primary">Save Code</button>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow mb-6">
      <div class="flex border-b overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          class="px-4 py-3 text-sm font-medium transition whitespace-nowrap"
          :class="activeTab === tab.key ? 'border-b-2 border-[#7A2123] text-[#7A2123]' : 'text-gray-500 hover:text-[#231F20]'"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="p-6 space-y-6">
        <div v-if="activeTab === 'logs'">
          <button @click="fetchLogs" class="btn-primary mb-4" :disabled="!complexCode">Refresh Logs</button>
          <div v-if="logsLoading" class="text-center py-4">Loading...</div>
          <LogTable v-else :logs="logs" />
        </div>

        <div v-if="activeTab === 'scores'" class="space-y-6">
          <div>
            <h3 class="font-semibold mb-3">Upload Scores</h3>
            <form @submit.prevent="handleUpload" class="space-y-3 mb-6">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
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
          </div>

          <div>
            <div class="flex items-center justify-between gap-3 mb-3">
              <h3 class="font-semibold">All Student Scores</h3>
              <button @click="fetchScores" class="btn-primary" :disabled="!complexCode">Refresh Scores</button>
            </div>
            <div v-if="scoresLoading" class="text-center py-4">Loading...</div>
            <ScoreTable v-else :scores="scores" :showStudent="true" />
          </div>

          <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between mb-4">
              <div class="flex-1">
                <h3 class="font-semibold mb-1">Lookup and Edit Scores</h3>
                <p class="text-sm text-gray-500">Enter studentID to pull the current score rows before editing or deleting.</p>
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

        <div v-if="activeTab === 'students'" class="space-y-6">
          <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h3 class="font-semibold mb-1">Lookup and Edit Student</h3>
            <p class="text-sm text-gray-500 mb-4">Load the current row first, then update or delete it.</p>
            <div class="flex flex-col gap-3 md:flex-row md:items-end">
              <input v-model="studentForm.user_id" type="text" placeholder="StudentID" class="input-field flex-1" />
              <button @click="loadStudentProfile" class="btn-primary" :disabled="!complexCode || studentLoading">
                {{ studentLoading ? 'Loading...' : 'Load Student' }}
              </button>
            </div>
            <p v-if="studentError" class="text-red-500 text-sm mt-4">{{ studentError }}</p>
            <p v-if="studentMessage" class="text-green-600 text-sm mt-4">{{ studentMessage }}</p>
          </div>

          <form @submit.prevent="handleUpdateStudent" class="space-y-3 bg-white rounded-lg border border-gray-200 p-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input v-model="studentForm.fname" type="text" placeholder="First name" class="input-field" />
              <input v-model="studentForm.lname" type="text" placeholder="Last name" class="input-field" />
            </div>
            <input v-model="studentForm.nname" type="text" placeholder="Nickname" class="input-field w-full" />
            <input v-model="studentForm.email" type="email" placeholder="Email" class="input-field w-full" />
            <select v-model="studentForm.department" class="input-field w-full">
              <option value="">Leave unchanged</option>
              <option value="Medical Science">Medical Science</option>
              <option value="Applied Science">Applied Science</option>
              <option value="Social Science">Social Science</option>
            </select>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input v-model="studentForm.classroom" type="text" maxlength="1" placeholder="Classroom (A-Z)" class="input-field" />
              <input v-model.number="studentForm.level" type="number" min="0" max="9" placeholder="Level (0-9)" class="input-field" />
            </div>
            <div class="flex flex-wrap gap-3 pt-2">
              <button type="submit" class="btn-primary" :disabled="!complexCode || !studentForm.user_id">Update Student</button>
              <button type="button" @click="handleDeleteStudent" class="btn-danger" :disabled="!complexCode || !studentForm.user_id">Delete Student</button>
              <button type="button" @click="clearStudentForm" class="btn-secondary">Clear</button>
            </div>
          </form>
        </div>

        <div v-if="activeTab === 'teachers'" class="space-y-6">
          <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h3 class="font-semibold mb-1">Lookup and Edit Teacher</h3>
            <p class="text-sm text-gray-500 mb-4">Load the current row first, then update or delete it.</p>
            <div class="flex flex-col gap-3 md:flex-row md:items-end">
              <input v-model="teacherForm.user_id" type="text" placeholder="TeacherID" class="input-field flex-1" />
              <button @click="loadTeacherProfile" class="btn-primary" :disabled="!complexCode || teacherLoading">
                {{ teacherLoading ? 'Loading...' : 'Load Teacher' }}
              </button>
            </div>
            <p v-if="teacherError" class="text-red-500 text-sm mt-4">{{ teacherError }}</p>
            <p v-if="teacherMessage" class="text-green-600 text-sm mt-4">{{ teacherMessage }}</p>
          </div>

          <form @submit.prevent="handleUpdateTeacher" class="space-y-3 bg-white rounded-lg border border-gray-200 p-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input v-model="teacherForm.fname" type="text" placeholder="First name" class="input-field" />
              <input v-model="teacherForm.lname" type="text" placeholder="Last name" class="input-field" />
            </div>
            <input v-model="teacherForm.nname" type="text" placeholder="Nickname" class="input-field w-full" />
            <input v-model="teacherForm.email" type="email" placeholder="Email" class="input-field w-full" />
            <select v-model="teacherForm.department" class="input-field w-full">
              <option value="">Leave unchanged</option>
              <option value="physics">Physics</option>
              <option value="chemistry">Chemistry</option>
              <option value="biology">Biology</option>
              <option value="mathematics">Mathematics</option>
              <option value="Thai">Thai</option>
              <option value="English">English</option>
              <option value="social">Social</option>
              <option value="computer">Computer</option>
              <option value="care supervisor">Care Supervisor</option>
            </select>
            <div class="flex flex-wrap gap-3 pt-2">
              <button type="submit" class="btn-primary" :disabled="!complexCode || !teacherForm.user_id">Update Teacher</button>
              <button type="button" @click="handleDeleteTeacher" class="btn-danger" :disabled="!complexCode || !teacherForm.user_id">Delete Teacher</button>
              <button type="button" @click="clearTeacherForm" class="btn-secondary">Clear</button>
            </div>
          </form>
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

function saveCode() {
  localStorage.setItem('admin_complex_code', complexCode.value)
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

function clearStudentForm() {
  studentForm.user_id = ''
  studentForm.email = ''
  studentForm.fname = ''
  studentForm.lname = ''
  studentForm.nname = ''
  studentForm.department = ''
  studentForm.classroom = ''
  studentForm.level = null
}

function clearTeacherForm() {
  teacherForm.user_id = ''
  teacherForm.email = ''
  teacherForm.fname = ''
  teacherForm.lname = ''
  teacherForm.nname = ''
  teacherForm.department = ''
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
const uploading = ref(false)
const uploadResult = ref('')
const upload = reactive({ exam_name: '', exam_round: '', test_date: '', file: null })
const scoreLookupStudentId = ref('')
const scoreLookupLoading = ref(false)
const scoreLookupMessage = ref('')
const scoreLookupError = ref('')
const scoreEditor = reactive({ user_id: '', rows: [] })

function onFileChange(e) {
  upload.file = e.target.files[0]
}

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

async function loadScoreEditor() {
  if (!complexCode.value || !scoreLookupStudentId.value) return
  scoreLookupLoading.value = true
  scoreLookupMessage.value = ''
  scoreLookupError.value = ''
  try {
    const { data } = await api.get(`/admin/${complexCode.value}/score/student/${scoreLookupStudentId.value}`)
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
    const { data } = await api.put(`/admin/${complexCode.value}/score/student/${scoreEditor.user_id}`, payload)
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
    await api.delete(`/admin/${complexCode.value}/score/student/${scoreEditor.user_id}`)
    clearScoreEditor()
    scoreLookupMessage.value = 'Scores deleted successfully.'
    await fetchScores()
  } catch (e) {
    scoreLookupError.value = e.response?.data?.detail || 'Delete failed'
  }
}

// Students
const studentLoading = ref(false)
const studentMessage = ref('')
const studentError = ref('')
const studentForm = reactive({
  user_id: '',
  email: '',
  fname: '',
  lname: '',
  nname: '',
  department: '',
  classroom: '',
  level: null,
})

async function loadStudentProfile() {
  if (!complexCode.value || !studentForm.user_id) return
  studentLoading.value = true
  studentError.value = ''
  studentMessage.value = ''
  try {
    const { data } = await api.get(`/admin/${complexCode.value}/student/${studentForm.user_id}`)
    studentForm.user_id = data.user_id
    studentForm.email = data.email
    studentForm.fname = data.fname
    studentForm.lname = data.lname
    studentForm.nname = data.nname
    studentForm.department = data.department || ''
    studentForm.classroom = data.classroom || ''
    studentForm.level = data.level ?? null
    studentMessage.value = 'Student loaded successfully.'
  } catch (e) {
    studentError.value = e.response?.data?.detail || 'Failed to load student'
  } finally {
    studentLoading.value = false
  }
}

async function handleUpdateStudent() {
  if (!complexCode.value || !studentForm.user_id) return
  studentMessage.value = ''
  studentError.value = ''
  try {
    const body = {
      email: studentForm.email || undefined,
      fname: studentForm.fname || undefined,
      lname: studentForm.lname || undefined,
      nname: studentForm.nname || undefined,
      department: studentForm.department || undefined,
      classroom: studentForm.classroom?.trim() ? studentForm.classroom.trim().toUpperCase() : undefined,
      level: Number.isInteger(studentForm.level) ? studentForm.level : undefined,
    }
    await api.put(`/admin/${complexCode.value}/student/${studentForm.user_id}`, body)
    studentMessage.value = 'Student updated successfully.'
  } catch (e) {
    studentError.value = e.response?.data?.detail || 'Update failed'
  }
}

async function handleDeleteStudent() {
  if (!complexCode.value || !studentForm.user_id) return
  if (!confirm('Are you sure you want to delete this student?')) return
  studentMessage.value = ''
  studentError.value = ''
  try {
    await api.delete(`/admin/${complexCode.value}/student/${studentForm.user_id}`)
    clearStudentForm()
    studentMessage.value = 'Student deleted successfully.'
  } catch (e) {
    studentError.value = e.response?.data?.detail || 'Delete failed'
  }
}

// Teachers
const teacherLoading = ref(false)
const teacherMessage = ref('')
const teacherError = ref('')
const teacherForm = reactive({
  user_id: '',
  email: '',
  fname: '',
  lname: '',
  nname: '',
  department: '',
})

async function loadTeacherProfile() {
  if (!complexCode.value || !teacherForm.user_id) return
  teacherLoading.value = true
  teacherError.value = ''
  teacherMessage.value = ''
  try {
    const { data } = await api.get(`/admin/${complexCode.value}/teacher/${teacherForm.user_id}`)
    teacherForm.user_id = data.user_id
    teacherForm.email = data.email
    teacherForm.fname = data.fname
    teacherForm.lname = data.lname
    teacherForm.nname = data.nname
    teacherForm.department = data.department || ''
    teacherMessage.value = 'Teacher loaded successfully.'
  } catch (e) {
    teacherError.value = e.response?.data?.detail || 'Failed to load teacher'
  } finally {
    teacherLoading.value = false
  }
}

async function handleUpdateTeacher() {
  if (!complexCode.value || !teacherForm.user_id) return
  teacherMessage.value = ''
  teacherError.value = ''
  try {
    const body = {
      email: teacherForm.email || undefined,
      fname: teacherForm.fname || undefined,
      lname: teacherForm.lname || undefined,
      nname: teacherForm.nname || undefined,
      department: teacherForm.department || undefined,
    }
    await api.put(`/admin/${complexCode.value}/teacher/${teacherForm.user_id}`, body)
    teacherMessage.value = 'Teacher updated successfully.'
  } catch (e) {
    teacherError.value = e.response?.data?.detail || 'Update failed'
  }
}

async function handleDeleteTeacher() {
  if (!complexCode.value || !teacherForm.user_id) return
  if (!confirm('Are you sure you want to delete this teacher?')) return
  teacherMessage.value = ''
  teacherError.value = ''
  try {
    await api.delete(`/admin/${complexCode.value}/teacher/${teacherForm.user_id}`)
    clearTeacherForm()
    teacherMessage.value = 'Teacher deleted successfully.'
  } catch (e) {
    teacherError.value = e.response?.data?.detail || 'Delete failed'
  }
}
</script>

<style scoped>
.input-field {
  @apply px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#7A2123] focus:border-transparent text-sm;
}
.btn-primary {
  @apply bg-[#7A2123] text-white rounded-lg px-4 py-2 hover:bg-[#5f191b] disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium;
}
.btn-secondary {
  @apply bg-white text-[#231F20] border border-gray-300 rounded-lg px-4 py-2 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium;
}
.btn-danger {
  @apply bg-[#231F20] text-white rounded-lg px-4 py-2 hover:bg-black disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium;
}
</style>
