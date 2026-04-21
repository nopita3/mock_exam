<template>
  <div class="bg-white rounded-xl shadow p-6">
    <h1 class="text-2xl font-bold mb-5">Profile</h1>

    <p class="text-gray-700">{{ auth.user?.fname }} {{ auth.user?.lname }}</p>
    <p class="text-sm text-gray-500">{{ auth.user?.email }}</p>
    <p class="text-sm text-gray-500 mb-5">Department: {{ auth.user?.department }}</p>

    <h2 class="text-base font-semibold mb-3">Teacher Code</h2>
    <div class="flex flex-col gap-3 md:flex-row">
      <input
        v-model="complexCode"
        type="password"
        placeholder="Enter teacher registration code"
        class="input-field flex-1"
      />
      <button @click="saveCode" class="btn-primary md:w-40">Save Code</button>
    </div>
    <p class="text-xs text-gray-500 mt-2">This code is required for score operations.</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const complexCode = ref(localStorage.getItem('teacher_complex_code') || '')

function saveCode() {
  localStorage.setItem('teacher_complex_code', complexCode.value)
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
