<template>
  <v-container>
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h4">Dashboard</h1>
        <p class="text-medium-emphasis">
          Welcome back{{ authStore.user?.username ? ', ' + authStore.user.username : '' }}
        </p>
      </v-col>
      <v-col cols="auto" class="d-flex align-center">
        <v-btn to="/analyze" color="primary" size="large" prepend-icon="mdi-play">
          Start Analysis
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <!-- Score Summary -->
      <v-col cols="12" md="4">
        <v-card elevation="2" class="pa-4 text-center">
          <v-card-title>Latest Score</v-card-title>
          <div class="text-h2 font-weight-bold" :class="scoreColor">
            {{ latestScore ?? '--' }}
          </div>
          <v-card-text class="text-medium-emphasis">
            {{ scoreLabel }}
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Quick Stats -->
      <v-col cols="12" md="4">
        <v-card elevation="2" class="pa-4 text-center">
          <v-card-title>Sessions This Week</v-card-title>
          <div class="text-h2 font-weight-bold text-primary">
            {{ postureStore.stats?.session_count ?? '--' }}
          </div>
          <v-card-text class="text-medium-emphasis">
            Avg: {{ postureStore.stats?.average_score?.toFixed(1) ?? '--' }}
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Quick Action -->
      <v-col cols="12" md="4">
        <v-card elevation="2" class="pa-4 text-center">
          <v-card-title>Score Trend</v-card-title>
          <div class="text-h2 font-weight-bold">
            <v-icon v-if="trend > 0" color="success" size="48">mdi-trending-up</v-icon>
            <v-icon v-else-if="trend < 0" color="error" size="48">mdi-trending-down</v-icon>
            <v-icon v-else color="grey" size="48">mdi-minus</v-icon>
          </div>
          <v-card-text class="text-medium-emphasis">
            {{ trend > 0 ? 'Improving' : trend < 0 ? 'Declining' : 'No data yet' }}
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recommended Exercises -->
    <v-row v-if="recommended.length" class="mt-4">
      <v-col>
        <v-card elevation="2">
          <v-card-title>
            Recommended Exercises
            <v-btn
              to="/exercises"
              variant="text"
              size="small"
              class="ml-2"
            >
              View All
            </v-btn>
          </v-card-title>
          <v-row class="pa-4" no-gutters>
            <v-col
              v-for="ex in recommended.slice(0, 3)"
              :key="ex.id"
              cols="12"
              md="4"
              class="pa-2"
            >
              <v-card variant="outlined" height="100%">
                <v-card-title class="text-subtitle-1 text-wrap">{{ ex.name }}</v-card-title>
                <v-card-text class="text-body-2">{{ ex.description }}</v-card-text>
                <v-card-actions>
                  <v-chip size="x-small" color="primary" variant="tonal">
                    {{ targetLabel(ex.target_issue) }}
                  </v-chip>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent Sessions -->
    <v-row class="mt-4">
      <v-col>
        <v-card elevation="2">
          <v-card-title>Recent Sessions</v-card-title>
          <v-list v-if="postureStore.sessions.length">
            <v-list-item
              v-for="session in postureStore.sessions.slice(0, 5)"
              :key="session.id"
              :to="`/history`"
            >
              <v-list-item-title>
                {{ new Date(session.started_at).toLocaleDateString() }}
                {{ new Date(session.started_at).toLocaleTimeString() }}
              </v-list-item-title>
              <v-list-item-subtitle>
                Score: {{ session.average_score?.toFixed(1) ?? 'N/A' }}
              </v-list-item-subtitle>
              <template #append>
                <v-chip
                  :color="getChipColor(session.average_score)"
                  size="small"
                >
                  {{ session.average_score?.toFixed(0) ?? '--' }}
                </v-chip>
              </template>
            </v-list-item>
          </v-list>
          <v-card-text v-else class="text-center text-medium-emphasis">
            No sessions yet. Start your first analysis!
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePostureStore } from '@/stores/posture'
import api from '@/api'

const authStore = useAuthStore()
const postureStore = usePostureStore()
const recommended = ref([])

const targetLabels = {
  forward_head: 'Forward Head',
  shoulder_level: 'Shoulder Levelness',
  shoulder_round: 'Shoulder Rounding',
  spine_align: 'Spine Alignment',
  general: 'General Posture',
}

function targetLabel(t) {
  return targetLabels[t] || t
}

onMounted(async () => {
  postureStore.fetchSessions()
  postureStore.fetchStats()
  try {
    const { data } = await api.get('/exercises/recommended/?limit=3')
    recommended.value = data.results || data
  } catch {
    // exercises not seeded yet
  }
})

const latestScore = computed(() => {
  const s = postureStore.sessions[0]
  return s?.average_score ? Math.round(s.average_score) : null
})

const scoreColor = computed(() => {
  const s = latestScore.value
  if (s === null) return ''
  if (s >= 85) return 'text-success'
  if (s >= 70) return 'text-light-green'
  if (s >= 55) return 'text-amber'
  if (s >= 40) return 'text-orange'
  return 'text-error'
})

const scoreLabel = computed(() => {
  const s = latestScore.value
  if (s === null) return 'Start a session to get your score'
  if (s >= 85) return 'Excellent'
  if (s >= 70) return 'Good'
  if (s >= 55) return 'Fair'
  if (s >= 40) return 'Needs Work'
  return 'Poor'
})

const trend = computed(() => {
  const daily = postureStore.stats?.daily_scores
  if (!daily || daily.length < 2) return 0
  const recent = daily[daily.length - 1].avg_score
  const prev = daily[daily.length - 2].avg_score
  return recent - prev
})

function getChipColor(score) {
  if (!score) return 'grey'
  if (score >= 85) return 'success'
  if (score >= 70) return 'light-green'
  if (score >= 55) return 'amber'
  if (score >= 40) return 'orange'
  return 'error'
}
</script>
