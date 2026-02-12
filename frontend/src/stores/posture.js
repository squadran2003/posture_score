import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const usePostureStore = defineStore('posture', () => {
  const sessions = ref([])
  const currentSession = ref(null)
  const stats = ref(null)
  const loading = ref(false)

  async function fetchSessions() {
    loading.value = true
    try {
      const { data } = await api.get('/posture/sessions/')
      sessions.value = data.results || data
    } finally {
      loading.value = false
    }
  }

  async function fetchSession(id) {
    const { data } = await api.get(`/posture/sessions/${id}/`)
    currentSession.value = data
    return data
  }

  async function fetchStats() {
    const { data } = await api.get('/posture/stats/')
    stats.value = data
    return data
  }

  return { sessions, currentSession, stats, loading, fetchSessions, fetchSession, fetchStats }
})
