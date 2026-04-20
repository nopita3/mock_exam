<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">My Scores</h1>

    <!-- Profile Card -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-lg font-semibold mb-2">Profile</h2>
      <p class="text-gray-600">{{ auth.user?.fname }} {{ auth.user?.lname }}</p>
      <p class="text-sm text-gray-500">{{ auth.user?.email }}</p>
      <p class="text-sm text-gray-500">Department: {{ auth.user?.department }}</p>
      <p class="text-sm text-gray-500">Classroom: {{ auth.user?.classroom || '-' }}</p>
      <p class="text-sm text-gray-500">Level: {{ auth.user?.level ?? '-' }}</p>
    </div>

    <!-- Scores -->
    <div v-if="loading" class="text-center py-8">Loading...</div>
    <ScoreTable v-else :scores="scores" />
    <p v-if="error" class="text-red-500 text-sm mt-4">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ScoreTable from '@/components/ScoreTable.vue'
import api from '@/api/client'

const auth = useAuthStore()
const scores = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/student/score/self')
    scores.value = data.scores || []
  } catch (e) {
    error.value = 'Failed to load scores'
  } finally {
    loading.value = false
  }
})
</script>
