import { ref, onUnmounted } from 'vue'

export function usePostureSocket() {
  const ws = ref(null)
  const connected = ref(false)
  const sessionId = ref(null)
  const calibrating = ref(false)
  const calibrationProgress = ref(0)
  const latestResult = ref(null)
  const idealLandmarks = ref(null)
  const sessionSummary = ref(null)
  const error = ref(null)

  let frameInterval = null

  function connect() {
    const token = localStorage.getItem('access_token')
    if (!token) {
      error.value = 'Not authenticated'
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.VITE_WS_URL || 'localhost:8000'
    const url = `${protocol}//${host}/ws/posture/analyze/?token=${token}`

    ws.value = new WebSocket(url)

    ws.value.onopen = () => {
      connected.value = true
      error.value = null
    }

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleMessage(data)
    }

    ws.value.onerror = () => {
      error.value = 'WebSocket connection error'
    }

    ws.value.onclose = (event) => {
      connected.value = false
      if (event.code === 4001) {
        error.value = 'Authentication failed'
      }
    }
  }

  function handleMessage(data) {
    switch (data.type) {
      case 'session_started':
        sessionId.value = data.session_id
        break
      case 'calibration_started':
        calibrating.value = true
        calibrationProgress.value = 0
        break
      case 'calibration_progress':
        calibrationProgress.value = data.progress
        if (data.landmarks) {
          latestResult.value = { landmarks: data.landmarks, landmarks_detected: true }
        }
        break
      case 'calibration_complete':
        calibrating.value = false
        calibrationProgress.value = 1
        idealLandmarks.value = data.ideal_landmarks
        break
      case 'posture_result':
        latestResult.value = data
        if (data.ideal_landmarks) {
          idealLandmarks.value = data.ideal_landmarks
        }
        break
      case 'session_ended':
        sessionSummary.value = data.summary
        break
      case 'error':
        error.value = data.message
        break
    }
  }

  function send(data) {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(data))
    }
  }

  function startSession() {
    send({ action: 'start_session' })
  }

  function startCalibration() {
    send({ action: 'calibrate' })
  }

  function sendFrame(base64Frame) {
    send({ action: 'frame', frame: base64Frame })
  }

  function endSession() {
    send({ action: 'end_session' })
  }

  function startFrameLoop(captureFunc, fps = 15) {
    stopFrameLoop()
    const interval = 1000 / fps
    frameInterval = setInterval(() => {
      const frame = captureFunc()
      if (frame) {
        sendFrame(frame)
      }
    }, interval)
  }

  function stopFrameLoop() {
    if (frameInterval) {
      clearInterval(frameInterval)
      frameInterval = null
    }
  }

  function disconnect() {
    stopFrameLoop()
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    connected.value = false
    sessionId.value = null
    calibrating.value = false
    latestResult.value = null
    idealLandmarks.value = null
    sessionSummary.value = null
  }

  onUnmounted(disconnect)

  return {
    connected,
    sessionId,
    calibrating,
    calibrationProgress,
    latestResult,
    idealLandmarks,
    sessionSummary,
    error,
    connect,
    startSession,
    startCalibration,
    sendFrame,
    endSession,
    startFrameLoop,
    stopFrameLoop,
    disconnect,
  }
}
