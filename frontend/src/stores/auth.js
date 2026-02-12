import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!localStorage.getItem('access_token'))

  async function login(username, password) {
    const { data } = await api.post('/auth/login/', { username, password })
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    await fetchProfile()
  }

  async function register(username, email, password) {
    await api.post('/auth/register/', { username, email, password, password_confirm: password })
    await login(username, password)
  }

  async function fetchProfile() {
    try {
      const { data } = await api.get('/auth/profile/')
      user.value = data
    } catch {
      user.value = null
    }
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
  }

  // Hydrate on store creation if token exists
  if (isAuthenticated.value) {
    fetchProfile()
  }

  return { user, loading, isAuthenticated, login, register, fetchProfile, logout }
})
