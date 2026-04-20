<template>
  <AuthLayout>
    <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
      <button @click="$router.push('/login')" class="text-sm text-gray-500 hover:text-gray-700 mb-4 inline-flex items-center gap-1">
        <ArrowLeft class="w-4 h-4" /> Back
      </button>
      <h2 class="text-2xl font-bold mb-6">Student Login</h2>

      <!-- Google Sign-In -->
      <div id="g_id_onload" ref="googleSignInRef"></div>
      <button
        @click="handleGoogleLogin"
        class="w-full flex items-center justify-center gap-3 border border-gray-300 rounded-lg px-4 py-3 hover:bg-gray-50 transition mb-4"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
        Sign in with Google
      </button>

      <div class="relative my-6">
        <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-gray-200"></div></div>
        <div class="relative flex justify-center text-sm"><span class="px-4 bg-white text-gray-500">or register with email</span></div>
      </div>

      <!-- Registration Form -->
      <form @submit.prevent="handleRegister" class="space-y-4">
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
        <button type="submit" :disabled="registering" class="btn-primary w-full">
          {{ registering ? 'Registering...' : 'Register' }}
        </button>
      </form>

      <p v-if="error" class="text-red-500 text-sm mt-4">{{ error }}</p>
      <p v-if="success" class="text-green-500 text-sm mt-4">{{ success }}</p>
    </div>
  </AuthLayout>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { ArrowLeft } from 'lucide-vue-next'
import api from '@/api/client'

const router = useRouter()
const auth = useAuthStore()
const registering = ref(false)
const error = ref('')
const success = ref('')

const form = reactive({
  fname: '',
  lname: '',
  nname: '',
  email: '',
  department: 'Medical Science',
})

function handleGoogleLogin() {
  error.value = 'Google login requires a configured Client ID. Please set VITE_GOOGLE_CLIENT_ID in .env.local'
}

async function handleRegister() {
  registering.value = true
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.post('/student/regist', {
      ...form,
      role: 'student',
    })
    success.value = `Registered as ${data.fname} ${data.lname}. You can now login with Google using the same email.`
    form.fname = ''
    form.lname = ''
    form.nname = ''
    form.email = ''
  } catch (e) {
    error.value = e.response?.data?.detail || e.response?.data?.message || 'Registration failed'
  } finally {
    registering.value = false
  }
}
</script>

<style scoped>
.input-field {
  @apply px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm;
}
.btn-primary {
  @apply bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium;
}
</style>
