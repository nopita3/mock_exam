<template>
  <div class="min-h-screen bg-[#EBEBEB] lg:flex">
    <header class="lg:hidden flex items-center justify-between bg-[#231F20] text-white px-4 py-3 border-b border-white/10">
      <div>
        <h1 class="text-base font-semibold leading-tight">Teacher Operations</h1>
        <p class="text-xs text-[#EBEBEB] capitalize">{{ auth.role }}</p>
      </div>
      <button
        @click="mobileMenuOpen = !mobileMenuOpen"
        class="p-2 rounded-lg hover:bg-[#7A2123] transition"
        aria-label="Toggle teacher menu"
      >
        <Menu v-if="!mobileMenuOpen" class="w-5 h-5" />
        <X v-else class="w-5 h-5" />
      </button>
    </header>

    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 bg-black/40 z-30 lg:hidden"
      @click="closeMobileMenu"
    ></div>

    <aside
      :class="[
        'fixed inset-y-0 left-0 z-40 w-72 bg-[#231F20] text-white flex flex-col transform transition-transform duration-200 lg:static lg:translate-x-0',
        mobileMenuOpen ? 'translate-x-0' : '-translate-x-full',
      ]"
    >
      <div class="p-6 border-b border-white/10">
        <h1 class="text-xl font-bold">Teacher Operations</h1>
        <p class="text-sm text-[#EBEBEB] mt-1">One operation per menu</p>
      </div>

      <nav class="flex-1 p-4 space-y-2">
        <RouterLink
          to="/teacher/profile"
          @click="closeMobileMenu"
          class="menu-link"
          :class="{ 'menu-link-active': $route.name === 'TeacherProfile' }"
        >
          Profile
        </RouterLink>
        <RouterLink
          to="/teacher/upload-score"
          @click="closeMobileMenu"
          class="menu-link"
          :class="{ 'menu-link-active': $route.name === 'TeacherUploadExamScore' }"
        >
          Upload Exam Score
        </RouterLink>
        <RouterLink
          to="/teacher/student-information"
          @click="closeMobileMenu"
          class="menu-link"
          :class="{ 'menu-link-active': $route.name === 'TeacherStudentInformation' }"
        >
          Student Information
        </RouterLink>
      </nav>

      <div class="p-4 border-t border-white/10">
        <div class="flex items-center gap-3 px-4 py-2">
          <User class="w-5 h-5" />
          <span class="text-sm truncate">{{ auth.user?.fname || 'Teacher' }}</span>
        </div>
        <button
          @click="handleLogout"
          class="w-full mt-2 flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-[#7A2123] transition text-sm"
        >
          <LogOut class="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>

    <main class="flex-1 overflow-auto bg-[#EBEBEB]">
      <div class="p-4 md:p-8">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { User, LogOut, Menu, X } from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const mobileMenuOpen = ref(false)

function closeMobileMenu() {
  mobileMenuOpen.value = false
}

watch(
  () => route.fullPath,
  () => {
    closeMobileMenu()
  }
)

async function handleLogout() {
  closeMobileMenu()
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.menu-link {
  @apply flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium hover:bg-[#7A2123] transition;
}

.menu-link-active {
  @apply bg-[#7A2123];
}
</style>
