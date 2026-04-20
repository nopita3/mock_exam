<template>
  <div class="bg-white rounded-lg shadow overflow-hidden">
    <div v-if="scores.length === 0" class="p-8 text-center text-gray-500">
      No scores found.
    </div>
    <table v-else class="w-full">
      <thead class="bg-gray-50 border-b">
        <tr>
          <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">Exam</th>
          <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">Round</th>
          <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">Date</th>
          <template v-if="showStudent">
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">Student</th>
          </template>
          <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">Score</th>
        </tr>
      </thead>
      <tbody class="divide-y">
        <tr v-for="s in scores" :key="s.exam_id" class="hover:bg-gray-50">
          <td class="px-4 py-3 text-sm">{{ s.exam_name }}</td>
          <td class="px-4 py-3 text-sm capitalize">{{ s.exam_round }}</td>
          <td class="px-4 py-3 text-sm">{{ s.test_date }}</td>
          <template v-if="showStudent">
            <td class="px-4 py-3 text-sm">{{ s.student_id }}</td>
          </template>
          <td class="px-4 py-3 text-sm font-semibold">{{ s.score }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  scores: { type: Array, default: () => [] },
  showStudent: { type: Boolean, default: false },
})
</script>
