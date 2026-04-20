<template>
  <AuthLayout>
    <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
      <h1 class="text-2xl font-bold mb-3">Verifying your account</h1>
      <p class="text-sm text-gray-500" v-if="loading">Please wait while we activate your account.</p>
      <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>
      <p v-else class="text-sm text-green-600">Account verified. Redirecting...</p>
    </div>
  </AuthLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AuthLayout from '@/layouts/AuthLayout.vue'
import api from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  const token = route.query.token
  if (!token || Array.isArray(token)) {
    loading.value = false
    error.value = 'Missing verification token.'
    return
  }

  try {
    const { data } = await api.get('/auth/verify', { params: { token } })
    auth.setToken(data.access_token)
    const profile = await auth.fetchProfile()
    await router.replace(`/${profile.role}`)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Verification failed.'
  } finally {
    loading.value = false
  }
})
</script>
