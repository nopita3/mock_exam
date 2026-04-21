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
    meta: { publicRole: 'student' },
    component: () => import('@/views/LoginStudent.vue'),
  },
  {
    path: '/login/teacher',
    name: 'LoginTeacher',
    meta: { publicRole: 'teacher' },
    component: () => import('@/views/LoginTeacher.vue'),
  },
  {
    path: '/login/admin',
    name: 'LoginAdmin',
    meta: { publicRole: 'admin' },
    component: () => import('@/views/LoginAdmin.vue'),
  },
  {
    path: '/register/student',
    name: 'RegisterStudent',
    meta: { publicRole: 'student' },
    component: () => import('@/views/RegisterStudent.vue'),
  },
  {
    path: '/register/teacher',
    name: 'RegisterTeacher',
    meta: { publicRole: 'teacher' },
    component: () => import('@/views/RegisterTeacher.vue'),
  },
  {
    path: '/register/admin',
    name: 'RegisterAdmin',
    meta: { publicRole: 'admin' },
    component: () => import('@/views/RegisterAdmin.vue'),
  },
  {
    path: '/auth/verification-complete',
    name: 'VerificationComplete',
    component: () => import('@/views/VerificationComplete.vue'),
  },
  {
    path: '/student',
    component: () => import('@/layouts/StudentOperationLayout.vue'),
    meta: { requiresAuth: true, role: 'student' },
    redirect: '/student/profile',
    children: [
      {
        path: 'profile',
        name: 'StudentProfile',
        component: () => import('@/views/student/Profile.vue'),
      },
      {
        path: 'my-scores',
        name: 'StudentMyScores',
        component: () => import('@/views/student/MyScores.vue'),
      },
    ],
  },
  {
    path: '/teacher',
    component: () => import('@/layouts/TeacherOperationLayout.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
    redirect: '/teacher/profile',
    children: [
      {
        path: 'profile',
        name: 'TeacherProfile',
        component: () => import('@/views/teacher/Profile.vue'),
      },
      {
        path: 'upload-score',
        name: 'TeacherUploadExamScore',
        component: () => import('@/views/teacher/UploadExamScore.vue'),
      },
      {
        path: 'student-information',
        name: 'TeacherStudentInformation',
        component: () => import('@/views/teacher/StudentInformation.vue'),
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

  if (to.meta.publicRole && auth.isLoggedIn) {
    if (!auth.user) {
      try {
        await auth.fetchProfile()
      } catch {
        auth.clearToken()
        return next('/login')
      }
    }

    if (auth.role !== to.meta.publicRole) {
      return next(`/${auth.role}`)
    }
  }

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
