<template>
  <AuthLayout>
    <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
      <button @click="$router.push('/login')" class="text-sm text-gray-500 hover:text-gray-700 mb-4 inline-flex items-center gap-1">
        <ArrowLeft class="w-4 h-4" /> Back
      </button>
      <h2 class="text-2xl font-bold mb-6">Admin Login</h2>

      <!-- Google Sign-In -->
      <button
        @click="handleGoogleLogin"
        class="w-full flex items-center justify-center gap-3 border border-gray-300 rounded-lg px-4 py-3 hover:bg-gray-50 transition mb-4"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
        Sign in with Google
      </button>

      <RouterLink to="/register/admin" class="btn-primary w-full inline-flex justify-center">
        Register Admin Account
      </RouterLink>
      <p class="text-xs text-gray-500 mt-3">
        This page is for admin login only. Admin registration link should be managed by admin managers.
      </p>

      <p v-if="error" class="text-red-500 text-sm mt-4">{{ error }}</p>
      <p v-if="success" class="text-green-500 text-sm mt-4">{{ success }}</p>
    </div>
  </AuthLayout>

  <div v-if="showVerificationPrompt" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
    <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
      <h3 class="text-xl font-semibold mb-2">Verify your email</h3>
      <p class="text-sm text-gray-600 mb-4">{{ verificationMessage }}</p>
      <div class="flex flex-wrap gap-3 justify-end">
        <button class="btn-secondary" @click="showVerificationPrompt = false">Close</button>
        <button class="btn-primary" :disabled="resendingVerification" @click="resendVerificationEmail">
          {{ resendingVerification ? 'Sending...' : 'Resend verification email' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { ArrowLeft } from 'lucide-vue-next'
import api from '@/api/client'
import { signInWithGoogleIdToken } from '@/lib/googleSignIn'
import { decodeJwtPayload } from '@/lib/utils'

const router = useRouter()
const auth = useAuthStore()
const error = ref('')
const success = ref('')
const showVerificationPrompt = ref(false)
const verificationMessage = ref('')
const verificationEmail = ref('')
const resendingVerification = ref(false)

async function handleGoogleLogin() {
  error.value = ''
  success.value = ''
  showVerificationPrompt.value = false
  try {
    const idToken = await signInWithGoogleIdToken()
    verificationEmail.value = decodeJwtPayload(idToken)?.email || ''
    const user = await auth.loginWithGoogle(idToken)
    router.push(`/${user.role}`)
  } catch (e) {
    const detail = e.response?.data?.detail || e.message || 'Google login failed'
    if (String(detail).toLowerCase().includes('verified')) {
      verificationMessage.value = 'Your account is not verified yet. We can resend the verification email.'
      showVerificationPrompt.value = true
      return
    }
    error.value = detail
  }
}

async function resendVerificationEmail() {
  if (!verificationEmail.value) {
    error.value = 'Could not determine the verification email.'
    return
  }

  resendingVerification.value = true
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.post('/auth/resend-verification', { email: verificationEmail.value })
    verificationMessage.value = data.detail || 'Verification email sent again.'
    success.value = data.detail || 'Verification email sent again.'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to resend verification email.'
  } finally {
    resendingVerification.value = false
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
  @apply bg-white text-[#7A2123] border border-gray-300 rounded-lg px-4 py-2 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition text-sm font-medium;
}
</style>
