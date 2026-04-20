<template>
  <div class="bg-white rounded-lg shadow overflow-hidden">
    <div v-if="logs.length === 0" class="p-8 text-center text-gray-500">
      No logs found.
    </div>
    <table v-else class="w-full">
      <thead class="bg-gray-50 border-b">
        <tr>
          <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">Path</th>
          <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">Result</th>
          <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">Description</th>
        </tr>
      </thead>
      <tbody class="divide-y">
        <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50">
          <td class="px-4 py-3 text-sm font-mono">{{ log.uri_path }}</td>
          <td class="px-4 py-3 text-sm">
            <span
              class="px-2 py-1 rounded-full text-xs font-medium"
              :class="log.result ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
            >
              {{ log.result ? 'Success' : 'Failed' }}
            </span>
          </td>
          <td class="px-4 py-3 text-sm">{{ log.description }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  logs: { type: Array, default: () => [] },
})
</script>
