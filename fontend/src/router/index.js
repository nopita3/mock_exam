import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginPage.vue'),
  },
  {
    path: '/login/student',
    name: 'LoginStudent',
    component: () => import('@/views/LoginStudent.vue'),
  },
  {
    path: '/login/teacher',
    name: 'LoginTeacher',
    component: () => import('@/views/LoginTeacher.vue'),
  },
  {
    path: '/login/admin',
    name: 'LoginAdmin',
    component: () => import('@/views/LoginAdmin.vue'),
  },
  {
    path: '/auth/verification-complete',
    name: 'VerificationComplete',
    component: () => import('@/views/VerificationComplete.vue'),
  },
  {
    path: '/student',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true, role: 'student' },
    children: [
      {
        path: '',
        name: 'StudentDashboard',
        component: () => import('@/views/student/Dashboard.vue'),
      },
    ],
  },
  {
    path: '/teacher',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
    children: [
      {
        path: '',
        name: 'TeacherDashboard',
        component: () => import('@/views/teacher/Dashboard.vue'),
      },
    ],
  },
  {
    path: '/admin',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return next('/login')
  }

  if (to.meta.requiresAuth && to.meta.role) {
    if (!auth.user) {
      try {
        await auth.fetchProfile()
      } catch {
        auth.clearToken()
        return next('/login')
      }
    }

    if (auth.role !== to.meta.role) {
      return next(`/${auth.role}`)
    }
  }

  if (auth.isLoggedIn && to.path.startsWith('/login')) {
    if (auth.user) {
      return next(`/${auth.role}`)
    }
    try {
      await auth.fetchProfile()
      return next(`/${auth.role}`)
    } catch {
      auth.clearToken()
    }
  }

  next()
})

export default router
