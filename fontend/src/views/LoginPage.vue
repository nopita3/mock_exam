<template>
  <AuthLayout>
    <div class="max-w-2xl w-full">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Supervisor Tracking System</h1>
        <p class="text-gray-500 mt-2">Select your role to continue</p>
      </div>
      <div class="grid gap-4 sm:grid-cols-3">
        <RouterLink
          to="/login/student"
          class="bg-white rounded-xl shadow-md p-6 text-center hover:shadow-lg hover:scale-105 transition cursor-pointer border-2 border-transparent hover:border-blue-500"
        >
          <GraduationCap class="w-12 h-12 mx-auto text-blue-500 mb-3" />
          <h2 class="text-lg font-semibold">Student</h2>
          <p class="text-sm text-gray-500 mt-1">View your exam scores</p>
        </RouterLink>
        <RouterLink
          to="/login/teacher"
          class="bg-white rounded-xl shadow-md p-6 text-center hover:shadow-lg hover:scale-105 transition cursor-pointer border-2 border-transparent hover:border-indigo-500"
        >
          <BookOpen class="w-12 h-12 mx-auto text-indigo-500 mb-3" />
          <h2 class="text-lg font-semibold">Teacher</h2>
          <p class="text-sm text-gray-500 mt-1">Manage scores & students</p>
        </RouterLink>
        <RouterLink
          to="/login/admin"
          class="bg-white rounded-xl shadow-md p-6 text-center hover:shadow-lg hover:scale-105 transition cursor-pointer border-2 border-transparent hover:border-red-500"
        >
          <Shield class="w-12 h-12 mx-auto text-red-500 mb-3" />
          <h2 class="text-lg font-semibold">Admin</h2>
          <p class="text-sm text-gray-500 mt-1">Full system access</p>
        </RouterLink>
      </div>
    </div>
  </AuthLayout>
</template>

<script setup>
import AuthLayout from '@/layouts/AuthLayout.vue'
import { GraduationCap, BookOpen, Shield } from 'lucide-vue-next'
</script>
