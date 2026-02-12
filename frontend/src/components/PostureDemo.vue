<template>
  <div class="demo-wrapper">
    <svg viewBox="0 0 520 320" xmlns="http://www.w3.org/2000/svg" class="demo-svg">
      <!-- Background desk surface -->
      <rect x="0" y="240" width="520" height="80" fill="#f5f5f5" rx="4" />
      <line x1="0" y1="240" x2="520" y2="240" stroke="#e0e0e0" stroke-width="2" />

      <!-- Chair -->
      <rect x="260" y="140" width="80" height="100" rx="10" fill="#e0e0e0" stroke="#bdbdbd" stroke-width="1.5" />
      <rect x="270" y="230" width="60" height="14" rx="4" fill="#bdbdbd" />
      <!-- Chair back -->
      <rect x="330" y="90" width="14" height="150" rx="6" fill="#e0e0e0" stroke="#bdbdbd" stroke-width="1.5" />

      <!-- Laptop on desk to the left -->
      <g class="laptop">
        <!-- Laptop base -->
        <rect x="60" y="218" width="80" height="6" rx="2" fill="#616161" />
        <!-- Laptop screen -->
        <rect x="68" y="158" width="64" height="60" rx="3" fill="#424242" />
        <rect x="72" y="162" width="56" height="52" rx="2" fill="#1e88e5" opacity="0.3" />
        <!-- Webcam dot -->
        <circle cx="100" cy="156" r="3" class="webcam-dot" />
      </g>

      <!-- Scan beam from webcam -->
      <g class="scan-beam">
        <polygon points="103,156 300,80 300,240" fill="url(#scanGradient)" opacity="0.12" />
      </g>

      <!-- Side-profile person sitting on chair -->
      <g class="person">
        <!-- Head -->
        <circle cx="280" cy="100" r="22" fill="none" stroke="#455a64" stroke-width="2.5" class="body-line" />
        <!-- Ear landmark dot -->
        <circle cx="258" cy="100" r="0" class="landmark ear-lm" />

        <!-- Neck -->
        <line x1="280" y1="122" x2="290" y2="145" stroke="#455a64" stroke-width="2.5" class="body-line" />

        <!-- Shoulder -->
        <circle cx="290" cy="145" r="0" class="landmark shoulder-lm" />

        <!-- Torso (shoulder to hip) -->
        <path d="M290,145 Q295,180 292,210" fill="none" stroke="#455a64" stroke-width="2.5" class="body-line" />

        <!-- Hip -->
        <circle cx="292" cy="210" r="0" class="landmark hip-lm" />

        <!-- Upper leg (sitting) -->
        <line x1="292" y1="210" x2="270" y2="238" stroke="#455a64" stroke-width="2.5" class="body-line" />
        <!-- Lower leg -->
        <line x1="270" y1="238" x2="272" y2="280" stroke="#455a64" stroke-width="2.5" class="body-line" />

        <!-- Arm resting -->
        <path d="M290,150 Q278,180 275,205" fill="none" stroke="#455a64" stroke-width="2" class="body-line" />
      </g>

      <!-- Skeleton overlay lines (appear during analysis) -->
      <g class="skeleton-overlay">
        <line x1="258" y1="100" x2="290" y2="145" stroke="#4caf50" stroke-width="2" stroke-dasharray="4,3" />
        <line x1="290" y1="145" x2="292" y2="210" stroke="#4caf50" stroke-width="2" stroke-dasharray="4,3" />
      </g>

      <!-- Score badge -->
      <g class="score-badge">
        <rect x="380" y="80" width="100" height="56" rx="12" fill="#4caf50" />
        <text x="430" y="103" text-anchor="middle" fill="#fff" font-size="12" font-weight="500">Score</text>
        <text x="430" y="127" text-anchor="middle" fill="#fff" font-size="22" font-weight="700">92</text>
      </g>

      <!-- Instruction label -->
      <g class="setup-label">
        <text x="260" y="305" text-anchor="middle" fill="#757575" font-size="13" font-weight="500">
          Sit sideways to your webcam
        </text>
      </g>

      <!-- Gradient defs -->
      <defs>
        <linearGradient id="scanGradient" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="#1e88e5" stop-opacity="0.8" />
          <stop offset="100%" stop-color="#1e88e5" stop-opacity="0" />
        </linearGradient>
      </defs>
    </svg>
  </div>
</template>

<script setup>
</script>

<style scoped>
.demo-wrapper {
  max-width: 520px;
  margin: 0 auto;
}

.demo-svg {
  width: 100%;
  height: auto;
  border-radius: 16px;
  background: #fafafa;
  overflow: hidden;
}

/* === Webcam dot blink === */
.webcam-dot {
  fill: #4caf50;
  animation: blink 3s ease-in-out infinite;
}

@keyframes blink {
  0%, 45%, 100% { fill: #4caf50; r: 3; }
  50%, 95% { fill: #66bb6a; r: 4; }
}

/* === Scan beam sweeps in === */
.scan-beam {
  opacity: 0;
  animation: scanIn 6s ease-in-out infinite;
}

@keyframes scanIn {
  0%, 10% { opacity: 0; }
  15%, 85% { opacity: 1; }
  90%, 100% { opacity: 0; }
}

/* === Landmark dots appear === */
.landmark {
  fill: #f44336;
  animation: dotAppear 6s ease-out infinite;
}

@keyframes dotAppear {
  0%, 25% { r: 0; }
  35%, 85% { r: 6; }
  95%, 100% { r: 0; }
}

.ear-lm { animation-delay: 0s; }
.shoulder-lm { animation-delay: 0.15s; }
.hip-lm { animation-delay: 0.3s; }

/* === Skeleton lines appear === */
.skeleton-overlay {
  opacity: 0;
  animation: skeletonIn 6s ease-out infinite;
}

@keyframes skeletonIn {
  0%, 35% { opacity: 0; }
  45%, 80% { opacity: 1; }
  90%, 100% { opacity: 0; }
}

/* === Score badge slides in === */
.score-badge {
  opacity: 0;
  transform: translateY(10px);
  animation: badgeIn 6s ease-out infinite;
}

@keyframes badgeIn {
  0%, 45% { opacity: 0; transform: translateY(10px); }
  55%, 78% { opacity: 1; transform: translateY(0); }
  88%, 100% { opacity: 0; transform: translateY(10px); }
}

/* === Body lines subtle draw-in === */
.body-line {
  stroke-dasharray: 300;
  stroke-dashoffset: 300;
  animation: drawBody 6s ease-out infinite;
}

@keyframes drawBody {
  0%, 5% { stroke-dashoffset: 300; }
  18%, 85% { stroke-dashoffset: 0; }
  95%, 100% { stroke-dashoffset: 300; }
}
</style>
