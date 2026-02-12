import { ref, onUnmounted } from 'vue'

export function useWebcam() {
  const videoRef = ref(null)
  const stream = ref(null)
  const isActive = ref(false)
  const error = ref(null)

  async function start(videoEl) {
    try {
      error.value = null
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
        audio: false,
      })
      stream.value = mediaStream
      if (videoEl) {
        videoEl.srcObject = mediaStream
        await videoEl.play()
      }
      isActive.value = true
    } catch (e) {
      error.value = e.message || 'Could not access camera'
      isActive.value = false
    }
  }

  function stop() {
    if (stream.value) {
      stream.value.getTracks().forEach((t) => t.stop())
      stream.value = null
    }
    isActive.value = false
  }

  function captureFrame(videoEl) {
    if (!videoEl || videoEl.readyState < 2) return null
    const canvas = document.createElement('canvas')
    canvas.width = videoEl.videoWidth
    canvas.height = videoEl.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(videoEl, 0, 0)
    // Return base64 JPEG without the data URI prefix
    return canvas.toDataURL('image/jpeg', 0.7).split(',')[1]
  }

  onUnmounted(stop)

  return { videoRef, stream, isActive, error, start, stop, captureFrame }
}
