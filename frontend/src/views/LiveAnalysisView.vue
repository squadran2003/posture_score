<template>
  <v-container fluid class="pa-4">
    <!-- Error Alert -->
    <v-alert v-if="socketError || webcamError" type="error" class="mb-4" closable>
      {{ socketError || webcamError }}
    </v-alert>

    <v-row>
      <!-- Left: Camera Feed + Overlay -->
      <v-col cols="12" md="8">
        <v-card elevation="4" class="overflow-hidden">
          <!-- Zoom Controls -->
          <div class="zoom-controls">
            <v-btn icon size="small" variant="tonal" @click="zoomIn" :disabled="zoom >= 3">
              <v-icon>mdi-magnify-plus</v-icon>
            </v-btn>
            <span class="zoom-label text-body-2">{{ Math.round(zoom * 100) }}%</span>
            <v-btn icon size="small" variant="tonal" @click="zoomOut" :disabled="zoom <= 1">
              <v-icon>mdi-magnify-minus</v-icon>
            </v-btn>
            <v-btn v-if="zoom > 1" icon size="small" variant="tonal" @click="zoomReset">
              <v-icon>mdi-magnify-close</v-icon>
            </v-btn>
          </div>
          <div
            class="video-container"
            ref="containerRef"
            :style="{ overflow: zoom > 1 ? 'auto' : 'hidden' }"
          >
            <div
              class="video-zoom-wrapper"
              :style="{ transform: `scale(${zoom})`, transformOrigin: 'center center' }"
            >
              <video
                ref="videoEl"
                autoplay
                playsinline
                muted
                class="video-feed"
              />
              <canvas ref="overlayCanvas" class="overlay-canvas" />
            </div>

            <!-- Calibration overlay -->
            <div v-if="posture.calibrating.value" class="calibration-overlay">
              <div class="calibration-content">
                <v-progress-circular
                  :model-value="posture.calibrationProgress.value * 100"
                  :size="120"
                  :width="8"
                  color="white"
                >
                  {{ Math.round(posture.calibrationProgress.value * 100) }}%
                </v-progress-circular>
                <p class="text-h6 mt-4">Hold your best posture...</p>
              </div>
            </div>

            <!-- State overlay when not active -->
            <div v-if="!webcam.isActive.value && stage === 'idle'" class="idle-overlay">
              <v-icon size="80" color="white">mdi-camera-off</v-icon>
              <p class="text-h6 mt-2">Camera not active</p>
            </div>
          </div>

          <!-- Controls -->
          <v-card-actions class="justify-center pa-4">
            <template v-if="stage === 'idle'">
              <v-btn color="primary" size="large" @click="begin" prepend-icon="mdi-play">
                Start Session
              </v-btn>
            </template>
            <template v-else-if="stage === 'waiting_calibration'">
              <v-btn color="secondary" size="large" @click="calibrate" prepend-icon="mdi-tune">
                Calibrate Posture
              </v-btn>
              <v-btn variant="outlined" class="ml-2" @click="skipCalibration">
                Skip
              </v-btn>
            </template>
            <template v-else-if="stage === 'calibrating'">
              <v-btn disabled size="large">Calibrating...</v-btn>
            </template>
            <template v-else-if="stage === 'analyzing'">
              <v-btn color="error" size="large" @click="finish" prepend-icon="mdi-stop">
                End Session
              </v-btn>
            </template>
            <template v-else-if="stage === 'done'">
              <v-btn color="primary" size="large" @click="reset" prepend-icon="mdi-restart">
                New Session
              </v-btn>
              <v-btn to="/dashboard" variant="outlined" class="ml-2">
                Dashboard
              </v-btn>
            </template>
          </v-card-actions>
        </v-card>
      </v-col>

      <!-- Right: Score Panel -->
      <v-col cols="12" md="4">
        <!-- Overall Score -->
        <v-card elevation="4" class="pa-4 text-center mb-4">
          <h3 class="text-h6 mb-2">Posture Score</h3>
          <div
            class="text-h1 font-weight-bold"
            :style="{ color: scoreColor }"
          >
            {{ displayScore }}
          </div>
          <p class="text-body-1 mt-1" :style="{ color: scoreColor }">
            {{ scoreLabel }}
          </p>
        </v-card>

        <!-- Component Breakdown -->
        <v-card v-if="details" elevation="2" class="pa-4 mb-4">
          <h4 class="text-subtitle-1 mb-3">Breakdown</h4>
          <div v-for="comp in components" :key="comp.key" class="mb-3">
            <div class="d-flex justify-space-between text-body-2 mb-1">
              <span>{{ comp.label }}</span>
              <span>{{ Math.round(details[comp.key]) }}</span>
            </div>
            <v-progress-linear
              :model-value="details[comp.key]"
              :color="getBarColor(details[comp.key])"
              height="8"
              rounded
            />
          </div>
        </v-card>

        <!-- Issues -->
        <v-card v-if="issues.length" elevation="2" class="pa-4 mb-4">
          <h4 class="text-subtitle-1 mb-2">Issues Detected</h4>
          <v-chip
            v-for="issue in issues"
            :key="issue"
            color="warning"
            variant="tonal"
            class="ma-1"
            size="small"
          >
            {{ issue }}
          </v-chip>
        </v-card>

        <!-- Session Summary (after end) -->
        <v-card v-if="posture.sessionSummary.value" elevation="2" class="pa-4">
          <h4 class="text-subtitle-1 mb-2">Session Summary</h4>
          <v-list density="compact">
            <v-list-item>
              <v-list-item-title>Average Score</v-list-item-title>
              <template #append>
                {{ posture.sessionSummary.value.average_score?.toFixed(1) ?? '--' }}
              </template>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Duration</v-list-item-title>
              <template #append>
                {{ formatDuration(posture.sessionSummary.value.duration_seconds) }}
              </template>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Frames Analyzed</v-list-item-title>
              <template #append>
                {{ posture.sessionSummary.value.total_frames_analyzed }}
              </template>
            </v-list-item>
          </v-list>
        </v-card>

        <!-- Recommended Exercises (after session ends) -->
        <v-card v-if="recommendedExercises.length" elevation="2" class="pa-4 mt-4">
          <h4 class="text-subtitle-1 mb-2">Recommended Exercises</h4>
          <v-list density="compact">
            <v-list-item
              v-for="ex in recommendedExercises"
              :key="ex.id"
              :title="ex.name"
              :subtitle="ex.description"
              to="/exercises"
            >
              <template #prepend>
                <v-icon color="primary" size="small">mdi-dumbbell</v-icon>
              </template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { useWebcam } from '@/composables/useWebcam'
import { usePostureSocket } from '@/composables/usePostureSocket'
import api from '@/api'

const webcam = useWebcam()
const posture = usePostureSocket()

const videoEl = ref(null)
const overlayCanvas = ref(null)
const containerRef = ref(null)
const zoom = ref(1)
const stage = ref('idle') // idle | waiting_calibration | calibrating | analyzing | done
const recommendedExercises = ref([])

const webcamError = computed(() => webcam.error.value)
const socketError = computed(() => posture.error.value)

const displayScore = computed(() => {
  const r = posture.latestResult.value
  if (!r || r.score === undefined) return '--'
  return Math.round(r.score)
})

const details = computed(() => posture.latestResult.value?.details || null)
const issues = computed(() => posture.latestResult.value?.issues || [])

const scoreLabel = computed(() => {
  const s = displayScore.value
  if (s === '--') return 'Waiting...'
  if (s >= 85) return 'Excellent'
  if (s >= 70) return 'Good'
  if (s >= 55) return 'Fair'
  if (s >= 40) return 'Needs Work'
  return 'Poor'
})

const scoreColor = computed(() => {
  const s = displayScore.value
  if (s === '--') return '#9E9E9E'
  if (s >= 85) return '#4CAF50'
  if (s >= 70) return '#8BC34A'
  if (s >= 55) return '#FFC107'
  if (s >= 40) return '#FF9800'
  return '#F44336'
})

const components = [
  { key: 'head_position', label: 'Head Position' },
  { key: 'shoulder_levelness', label: 'Shoulder Levelness' },
  { key: 'shoulder_rounding', label: 'Shoulder Rounding' },
  { key: 'spine_alignment', label: 'Spine Alignment' },
]

// Connections for drawing skeleton
const CONNECTIONS = [
  ['left_ear', 'right_ear'],
  ['left_ear', 'left_shoulder'],
  ['right_ear', 'right_shoulder'],
  ['left_shoulder', 'right_shoulder'],
  ['left_shoulder', 'left_hip'],
  ['right_shoulder', 'right_hip'],
  ['left_hip', 'right_hip'],
]

function zoomIn() { zoom.value = Math.min(zoom.value + 0.25, 3) }
function zoomOut() { zoom.value = Math.max(zoom.value - 0.25, 1) }
function zoomReset() { zoom.value = 1 }

function getBarColor(score) {
  if (score >= 85) return 'success'
  if (score >= 70) return 'light-green'
  if (score >= 55) return 'amber'
  if (score >= 40) return 'orange'
  return 'error'
}

function formatDuration(seconds) {
  if (!seconds) return '--'
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  return `${m}m ${s}s`
}

// ── Drawing ──────────────────────────────────────────────

function drawOverlay() {
  const canvas = overlayCanvas.value
  const video = videoEl.value
  if (!canvas || !video) return

  canvas.width = video.videoWidth || 640
  canvas.height = video.videoHeight || 480
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  const result = posture.latestResult.value
  const ideal = posture.idealLandmarks.value

  // Draw ideal skeleton (ghost)
  if (ideal) {
    drawSkeleton(ctx, ideal, canvas.width, canvas.height, 'rgba(76, 175, 80, 0.35)', 4)
    drawPoints(ctx, ideal, canvas.width, canvas.height, 'rgba(76, 175, 80, 0.4)', 5)
  }

  // Draw current skeleton
  if (result?.landmarks) {
    const color = scoreColor.value
    drawSkeleton(ctx, result.landmarks, canvas.width, canvas.height, color, 3)
    drawPoints(ctx, result.landmarks, canvas.width, canvas.height, color, 6)
  }
}

function drawSkeleton(ctx, landmarks, w, h, color, lineWidth) {
  ctx.strokeStyle = color
  ctx.lineWidth = lineWidth
  ctx.lineCap = 'round'

  for (const [a, b] of CONNECTIONS) {
    const lmA = landmarks[a]
    const lmB = landmarks[b]
    if (!lmA || !lmB) continue
    ctx.beginPath()
    ctx.moveTo(lmA.x * w, lmA.y * h)
    ctx.lineTo(lmB.x * w, lmB.y * h)
    ctx.stroke()
  }
}

function drawPoints(ctx, landmarks, w, h, color, radius) {
  ctx.fillStyle = color
  for (const name of Object.keys(landmarks)) {
    const lm = landmarks[name]
    if (!lm) continue
    ctx.beginPath()
    ctx.arc(lm.x * w, lm.y * h, radius, 0, Math.PI * 2)
    ctx.fill()
  }
}

// Redraw whenever the result changes
let animFrame = null
function drawLoop() {
  drawOverlay()
  animFrame = requestAnimationFrame(drawLoop)
}

// ── Session Lifecycle ────────────────────────────────────

async function begin() {
  // Start webcam
  await webcam.start(videoEl.value)
  if (!webcam.isActive.value) return

  // Connect WebSocket
  posture.connect()

  // Wait for connection then start session
  const checkOpen = setInterval(() => {
    if (posture.connected.value) {
      clearInterval(checkOpen)
      posture.startSession()
      stage.value = 'waiting_calibration'
      // Start drawing loop
      animFrame = requestAnimationFrame(drawLoop)
    }
  }, 100)

  // Timeout after 5s
  setTimeout(() => clearInterval(checkOpen), 5000)
}

function calibrate() {
  stage.value = 'calibrating'
  posture.startCalibration()
  // Start sending frames for calibration
  posture.startFrameLoop(() => webcam.captureFrame(videoEl.value), 15)
}

function skipCalibration() {
  stage.value = 'analyzing'
  posture.startFrameLoop(() => webcam.captureFrame(videoEl.value), 15)
}

async function finish() {
  posture.stopFrameLoop()
  posture.endSession()
  stage.value = 'done'
  // Fetch fresh recommendations based on this session's data
  try {
    const { data } = await api.get('/exercises/recommended/?limit=4')
    recommendedExercises.value = data.results || data
  } catch {
    recommendedExercises.value = []
  }
}

function reset() {
  posture.disconnect()
  webcam.stop()
  stage.value = 'idle'
  recommendedExercises.value = []
  if (animFrame) {
    cancelAnimationFrame(animFrame)
    animFrame = null
  }
  // Clear the overlay
  const canvas = overlayCanvas.value
  if (canvas) {
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
  }
}

// Watch for calibration complete → transition to analyzing
watch(
  () => posture.calibrating.value,
  (val, oldVal) => {
    if (oldVal && !val && stage.value === 'calibrating') {
      // Calibration just finished — frames are already being sent, continue analyzing
      stage.value = 'analyzing'
    }
  },
)

onUnmounted(() => {
  if (animFrame) cancelAnimationFrame(animFrame)
  posture.disconnect()
  webcam.stop()
})
</script>

<style scoped>
.zoom-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.04);
}

.zoom-label {
  min-width: 40px;
  text-align: center;
  font-weight: 500;
}

.video-container {
  position: relative;
  width: 100%;
  max-height: 70vh;
  background: #000;
}

.video-zoom-wrapper {
  position: relative;
  width: 100%;
  transition: transform 0.2s ease;
}

.video-feed {
  display: block;
  width: 100%;
  height: auto;
  transform: scaleX(-1);
}

.overlay-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  transform: scaleX(-1);
}

.calibration-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.calibration-content {
  text-align: center;
  color: white;
}

.idle-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
}
</style>
