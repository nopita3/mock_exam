import { defineStore } from 'pinia'
import api from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
    user: null,
    loading: false,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    role: (state) => state.user?.role || null,
    isAdmin: (state) => state.user?.role === 'admin',
    isTeacher: (state) => state.user?.role === 'teacher',
    isStudent: (state) => state.user?.role === 'student',
  },

  actions: {
    setToken(token) {
      this.token = token
      localStorage.setItem('access_token', token)
    },

    clearToken() {
      this.token = null
      this.user = null
      localStorage.removeItem('access_token')
    },

    async loginWithGoogle(idToken) {
      const { data } = await api.post('/auth/google', { id_token: idToken })
      this.setToken(data.access_token)
      await this.fetchProfile()
      return this.user
    },

    async fetchProfile() {
      this.loading = true
      try {
        const { data } = await api.get('/auth/profile')
        this.user = data
        return data
      } finally {
        this.loading = false
      }
    },

    async logout() {
      this.clearToken()
    },
  },
})
