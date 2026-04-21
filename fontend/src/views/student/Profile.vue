<template>
  <div class="bg-white rounded-xl shadow p-6">
    <h1 class="text-2xl font-bold mb-5">Profile</h1>
    <p class="text-gray-700">{{ auth.user?.fname }} {{ auth.user?.lname }}</p>
    <p class="text-sm text-gray-500">{{ auth.user?.email }}</p>
    <p class="text-sm text-gray-500">Department: {{ auth.user?.department }}</p>
    <p class="text-sm text-gray-500">Classroom: {{ auth.user?.classroom || '-' }}</p>
    <p class="text-sm text-gray-500">Level: {{ auth.user?.level ?? '-' }}</p>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>
