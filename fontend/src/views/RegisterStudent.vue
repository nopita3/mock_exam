<template>
  <AuthLayout>
    <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
      <button @click="$router.push('/login/student')" class="text-sm text-gray-500 hover:text-gray-700 mb-4 inline-flex items-center gap-1">
        <ArrowLeft class="w-4 h-4" /> Back to Student Login
      </button>
      <h2 class="text-2xl font-bold mb-2">Student Registration</h2>
      <p class="text-sm text-gray-500 mb-6">Use only the registration link shared by your teacher.</p>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <input v-model="form.userID" type="text" placeholder="Student ID" required class="input-field w-full" />
        <div class="grid grid-cols-2 gap-3">
          <input v-model="form.fname" type="text" placeholder="First name" required class="input-field" />
          <input v-model="form.lname" type="text" placeholder="Last name" required class="input-field" />
        </div>
        <input v-model="form.nname" type="text" placeholder="Nickname" required class="input-field w-full" />
        <input v-model="form.email" type="email" placeholder="Email (@essence.ac.th)" required class="input-field w-full" />
        <select v-model="form.department" required class="input-field w-full">
          <option value="" disabled>Select department</option>
          <option value="Medical Science">Medical Science</option>
          <option value="Applied Science">Applied Science</option>
          <option value="Social Science">Social Science</option>
        </select>
        <div class="grid grid-cols-2 gap-3">
          <input
            v-model="form.classroom"
            type="text"
            maxlength="1"
            placeholder="Classroom (A-Z)"
            class="input-field"
          />
          <input
            v-model.number="form.level"
            type="number"
            min="0"
            max="9"
            placeholder="Level (0-9)"
            class="input-field"
          />
        </div>
        <button type="submit" :disabled="registering" class="btn-primary w-full">
          {{ registering ? 'Registering...' : 'Register Student' }}
        </button>
      </form>

      <p v-if="error" class="text-red-500 text-sm mt-4">{{ error }}</p>
      <p v-if="success" class="text-green-500 text-sm mt-4">{{ success }}</p>
    </div>
  </AuthLayout>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'
import AuthLayout from '@/layouts/AuthLayout.vue'
import api from '@/api/client'

const registering = ref(false)
const error = ref('')
const success = ref('')

const form = reactive({
  userID: '',
  fname: '',
  lname: '',
  nname: '',
  email: '',
  department: 'Medical Science',
  classroom: '',
  level: null,
})

async function handleRegister() {
  registering.value = true
  error.value = ''
  success.value = ''
  try {
    const classroom = form.classroom?.trim() ? form.classroom.trim().toUpperCase() : null
    const level = Number.isInteger(form.level) ? form.level : null

    if (level !== null && (level < 0 || level >= 10)) {
      throw new Error('Level must be an integer from 0 to 9')
    }

    const { data } = await api.post('/student/regist', {
      ...form,
      role: 'student',
      classroom,
      level,
    })

    success.value = `Registered as ${data.fname} ${data.lname}. You can now login with Google using the same email.`
    form.userID = ''
    form.fname = ''
    form.lname = ''
    form.nname = ''
    form.email = ''
    form.classroom = ''
    form.level = null
  } catch (e) {
    error.value = e.response?.data?.detail || e.response?.data?.message || 'Registration failed'
  } finally {
    registering.value = false
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
</style>
