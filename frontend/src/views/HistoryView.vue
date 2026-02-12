<template>
  <v-container>
    <h1 class="text-h4 mb-4">Session History</h1>

    <v-card elevation="2" :loading="postureStore.loading">
      <v-list v-if="postureStore.sessions.length">
        <v-list-item
          v-for="session in postureStore.sessions"
          :key="session.id"
          class="py-3"
        >
          <v-list-item-title>
            {{ formatDate(session.started_at) }}
          </v-list-item-title>
          <v-list-item-subtitle>
            Duration: {{ formatDuration(session.started_at, session.ended_at) }}
          </v-list-item-subtitle>
          <template #append>
            <v-chip
              :color="getChipColor(session.average_score)"
              class="ml-2"
            >
              {{ session.average_score?.toFixed(1) ?? '--' }}
            </v-chip>
          </template>
        </v-list-item>
      </v-list>
      <v-card-text v-else class="text-center text-medium-emphasis pa-8">
        No sessions recorded yet.
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue'
import { usePostureStore } from '@/stores/posture'

const postureStore = usePostureStore()

onMounted(() => {
  postureStore.fetchSessions()
})

function formatDate(iso) {
  return new Date(iso).toLocaleString()
}

function formatDuration(start, end) {
  if (!end) return 'In progress'
  const ms = new Date(end) - new Date(start)
  const mins = Math.floor(ms / 60000)
  const secs = Math.floor((ms % 60000) / 1000)
  return `${mins}m ${secs}s`
}

function getChipColor(score) {
  if (!score) return 'grey'
  if (score >= 85) return 'success'
  if (score >= 70) return 'light-green'
  if (score >= 55) return 'amber'
  if (score >= 40) return 'orange'
  return 'error'
}
</script>
