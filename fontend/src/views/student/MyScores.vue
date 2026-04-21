<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">My Scores</h1>
    <div v-if="loading" class="text-center py-8">Loading...</div>
    <ScoreTable v-else :scores="scores" />
    <p v-if="error" class="text-red-500 text-sm mt-4">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ScoreTable from '@/components/ScoreTable.vue'
import api from '@/api/client'

const scores = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/student/score/self')
    scores.value = data.scores || []
  } catch {
    error.value = 'Failed to load scores'
  } finally {
    loading.value = false
  }
})
</script>
