<template>
  <v-container>
    <h1 class="text-h4 mb-4">Exercise Library</h1>

    <!-- Filters -->
    <v-row class="mb-4" align="center">
      <v-col cols="12" sm="4">
        <v-select
          v-model="targetFilter"
          :items="targetOptions"
          label="Target Issue"
          clearable
          density="compact"
          variant="outlined"
        />
      </v-col>
      <v-col cols="12" sm="4">
        <v-select
          v-model="difficultyFilter"
          :items="difficultyOptions"
          label="Difficulty"
          clearable
          density="compact"
          variant="outlined"
        />
      </v-col>
      <v-col cols="12" sm="4">
        <v-select
          v-model="categoryFilter"
          :items="categoryOptions"
          label="Category"
          clearable
          density="compact"
          variant="outlined"
        />
      </v-col>
    </v-row>

    <!-- Recommended Section -->
    <template v-if="recommended.length && !targetFilter && !difficultyFilter && !categoryFilter">
      <h2 class="text-h6 mb-2">Recommended For You</h2>
      <v-row class="mb-6">
        <v-col
          v-for="exercise in recommended"
          :key="'rec-' + exercise.id"
          cols="12"
          sm="6"
          md="4"
        >
          <v-card
            elevation="3"
            height="100%"
            class="d-flex flex-column"
            style="border-left: 4px solid rgb(var(--v-theme-primary))"
          >
            <v-card-title class="text-wrap">{{ exercise.name }}</v-card-title>
            <v-card-subtitle>{{ exercise.category_name }}</v-card-subtitle>
            <v-card-text class="flex-grow-1">{{ exercise.description }}</v-card-text>
            <v-card-actions>
              <v-chip size="small" :color="difficultyColor(exercise.difficulty)" variant="outlined">
                {{ exercise.difficulty }}
              </v-chip>
              <v-chip size="small" class="ml-1" variant="tonal">
                {{ formatDuration(exercise.duration_seconds) }}
              </v-chip>
              <v-spacer />
              <v-btn size="small" variant="text" @click="openDetail(exercise)">Details</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
      <v-divider class="mb-4" />
      <h2 class="text-h6 mb-2">All Exercises</h2>
    </template>

    <!-- Exercise Grid -->
    <v-row v-if="exercises.length">
      <v-col
        v-for="exercise in exercises"
        :key="exercise.id"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card elevation="2" height="100%" class="d-flex flex-column">
          <v-card-title class="text-wrap">{{ exercise.name }}</v-card-title>
          <v-card-subtitle>{{ exercise.category_name }}</v-card-subtitle>
          <v-card-text class="flex-grow-1">{{ exercise.description }}</v-card-text>
          <v-card-actions>
            <v-chip size="small" :color="difficultyColor(exercise.difficulty)" variant="outlined">
              {{ exercise.difficulty }}
            </v-chip>
            <v-chip size="small" class="ml-1" variant="tonal">
              {{ formatDuration(exercise.duration_seconds) }}
            </v-chip>
            <v-spacer />
            <v-btn size="small" variant="text" @click="openDetail(exercise)">Details</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    <v-card v-else-if="!loading" elevation="2" class="pa-8 text-center text-medium-emphasis">
      No exercises match your filters.
    </v-card>

    <!-- Detail Dialog -->
    <v-dialog v-model="detailDialog" max-width="600">
      <v-card v-if="selectedExercise">
        <v-card-title class="text-wrap">{{ selectedExercise.name }}</v-card-title>
        <v-card-subtitle>
          {{ selectedExercise.category_name }} &middot;
          {{ selectedExercise.difficulty }} &middot;
          {{ targetLabel(selectedExercise.target_issue) }}
        </v-card-subtitle>
        <v-card-text>
          <p class="mb-4">{{ selectedExercise.description }}</p>
          <h4 class="text-subtitle-1 mb-2">Instructions</h4>
          <p class="text-body-2">{{ selectedExercise.instructions }}</p>
          <v-row class="mt-4">
            <v-col v-if="selectedExercise.duration_seconds" cols="6">
              <div class="text-caption text-medium-emphasis">Duration</div>
              <div>{{ formatDuration(selectedExercise.duration_seconds) }}</div>
            </v-col>
            <v-col v-if="selectedExercise.repetitions" cols="6">
              <div class="text-caption text-medium-emphasis">Repetitions</div>
              <div>{{ selectedExercise.repetitions }} reps</div>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="primary"
            :loading="completing"
            @click="markComplete(selectedExercise.id)"
          >
            Mark Complete
          </v-btn>
          <v-spacer />
          <v-btn variant="text" @click="detailDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Completion snackbar -->
    <v-snackbar v-model="snackbar" :timeout="2000" color="success">
      Exercise marked complete!
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '@/api'

const exercises = ref([])
const recommended = ref([])
const loading = ref(false)
const detailDialog = ref(false)
const selectedExercise = ref(null)
const completing = ref(false)
const snackbar = ref(false)

const targetFilter = ref(null)
const difficultyFilter = ref(null)
const categoryFilter = ref(null)

const targetOptions = [
  { title: 'Forward Head', value: 'forward_head' },
  { title: 'Shoulder Levelness', value: 'shoulder_level' },
  { title: 'Shoulder Rounding', value: 'shoulder_round' },
  { title: 'Spine Alignment', value: 'spine_align' },
  { title: 'General Posture', value: 'general' },
]

const difficultyOptions = [
  { title: 'Beginner', value: 'beginner' },
  { title: 'Intermediate', value: 'intermediate' },
  { title: 'Advanced', value: 'advanced' },
]

const categoryOptions = [
  { title: 'Stretching', value: 'Stretching' },
  { title: 'Strengthening', value: 'Strengthening' },
  { title: 'Mobility', value: 'Mobility' },
  { title: 'Awareness', value: 'Awareness' },
]

async function fetchExercises() {
  loading.value = true
  try {
    const params = {}
    if (targetFilter.value) params.target_issue = targetFilter.value
    if (difficultyFilter.value) params.difficulty = difficultyFilter.value
    if (categoryFilter.value) params.category = categoryFilter.value
    const { data } = await api.get('/exercises/', { params })
    exercises.value = data.results || data
  } catch {
    exercises.value = []
  } finally {
    loading.value = false
  }
}

async function fetchRecommended() {
  try {
    const { data } = await api.get('/exercises/recommended/')
    recommended.value = data.results || data
  } catch {
    recommended.value = []
  }
}

function openDetail(exercise) {
  selectedExercise.value = exercise
  detailDialog.value = true
}

async function markComplete(exerciseId) {
  completing.value = true
  try {
    await api.post('/exercises/log/', { exercise: exerciseId })
    snackbar.value = true
    detailDialog.value = false
  } catch {
    // ignore
  } finally {
    completing.value = false
  }
}

function formatDuration(seconds) {
  if (!seconds) return ''
  if (seconds >= 60) return `${Math.round(seconds / 60)} min`
  return `${seconds}s`
}

function difficultyColor(d) {
  if (d === 'beginner') return 'success'
  if (d === 'intermediate') return 'warning'
  return 'error'
}

function targetLabel(t) {
  const found = targetOptions.find((o) => o.value === t)
  return found ? found.title : t
}

watch([targetFilter, difficultyFilter, categoryFilter], fetchExercises)

onMounted(() => {
  fetchExercises()
  fetchRecommended()
})
</script>
