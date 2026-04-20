<template>
  <div class="min-h-screen flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-900 text-white flex flex-col">
      <div class="p-6 border-b border-slate-700">
        <h1 class="text-xl font-bold">Supervisor System</h1>
        <p class="text-sm text-slate-400 capitalize mt-1">{{ auth.role }}</p>
      </div>
      <nav class="flex-1 p-4 space-y-1">
        <RouterLink
          :to="`/${auth.role}`"
          class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-700 transition"
          :class="{ 'bg-slate-700': $route.name?.includes('Dashboard') }"
        >
          <LayoutDashboard class="w-5 h-5" />
          <span>Dashboard</span>
        </RouterLink>
      </nav>
      <div class="p-4 border-t border-slate-700">
        <div class="flex items-center gap-3 px-4 py-2">
          <User class="w-5 h-5" />
          <span class="text-sm truncate">{{ auth.user?.fname || 'User' }}</span>
        </div>
        <button
          @click="handleLogout"
          class="w-full mt-2 flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-red-600 transition text-sm"
        >
          <LogOut class="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 overflow-auto">
      <div class="p-8">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { LayoutDashboard, User, LogOut } from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>
