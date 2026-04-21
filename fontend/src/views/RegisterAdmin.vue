<template>
  <AuthLayout>
    <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
      <button @click="$router.push('/login/admin')" class="text-sm text-gray-500 hover:text-gray-700 mb-4 inline-flex items-center gap-1">
        <ArrowLeft class="w-4 h-4" /> Back to Admin Login
      </button>
      <h2 class="text-2xl font-bold mb-2">Admin Registration</h2>
      <p class="text-sm text-gray-500 mb-6">This link is for the admin management team only.</p>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <input v-model="form.userID" type="text" placeholder="Admin ID" required class="input-field w-full" />
        <input v-model="form.complex_code" type="password" placeholder="Admin registration code" required class="input-field w-full" />
        <div class="grid grid-cols-2 gap-3">
          <input v-model="form.fname" type="text" placeholder="First name" required class="input-field" />
          <input v-model="form.lname" type="text" placeholder="Last name" required class="input-field" />
        </div>
        <input v-model="form.nname" type="text" placeholder="Nickname" required class="input-field w-full" />
        <input v-model="form.email" type="email" placeholder="Email (@essence.ac.th)" required class="input-field w-full" />
        <select v-model="form.department" required class="input-field w-full">
          <option value="" disabled>Select department</option>
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
        <button type="submit" :disabled="registering" class="btn-primary w-full">
          {{ registering ? 'Registering...' : 'Register Admin' }}
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
  complex_code: '',
  fname: '',
  lname: '',
  nname: '',
  email: '',
  department: 'physics',
})

async function handleRegister() {
  registering.value = true
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.post(`/admin/${form.complex_code}/regist`, {
      userID: form.userID,
      email: form.email,
      fname: form.fname,
      lname: form.lname,
      nname: form.nname,
      role: 'admin',
      department: form.department,
    })

    success.value = `Registered as ${data.fname} ${data.lname}. Login with Google using the same email.`
    form.userID = ''
    form.complex_code = ''
    form.fname = ''
    form.lname = ''
    form.nname = ''
    form.email = ''
  } catch (e) {
    error.value = e.response?.data?.detail || e.response?.data?.message || 'Registration failed. Check your code.'
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
