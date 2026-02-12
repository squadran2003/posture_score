<template>
  <v-container>
    <v-row justify="center" class="mt-16">
      <v-col cols="12" md="8" class="text-center">
        <v-icon size="80" color="primary" class="mb-4">mdi-human</v-icon>
        <h1 class="text-h3 font-weight-bold mb-4">Fix Your Posture in Real-Time</h1>
        <p class="text-h6 text-medium-emphasis mb-8">
          PostureScore uses your webcam and AI to analyze your posture, give you a live score,
          and recommend exercises to improve.
        </p>
        <v-row justify="center" class="ga-4">
          <v-btn to="/register" color="primary" size="x-large" rounded="lg">
            Get Started Free
          </v-btn>
          <v-btn to="/login" variant="outlined" size="x-large" rounded="lg">
            Login
          </v-btn>
        </v-row>
      </v-col>
    </v-row>

    <v-row justify="center" class="mt-16">
      <v-col v-for="feature in features" :key="feature.title" cols="12" md="4">
        <v-card class="text-center pa-6" elevation="2" height="100%">
          <v-icon size="48" color="primary" class="mb-4">{{ feature.icon }}</v-icon>
          <v-card-title>{{ feature.title }}</v-card-title>
          <v-card-text>{{ feature.text }}</v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row justify="center" class="mt-16">
      <v-col cols="12" md="8">
        <h2 class="text-h4 font-weight-bold text-center mb-2">How to Use Live Analysis</h2>
        <p class="text-body-1 text-medium-emphasis text-center mb-6">
          Sit sideways to your webcam so it can see your ear, shoulder, and hip in profile.
        </p>
        <PostureDemo class="mb-10" />
        <v-card
          v-for="step in steps"
          :key="step.number"
          elevation="1"
          class="mb-4 pa-4"
        >
          <div class="d-flex align-start ga-4">
            <v-avatar :color="step.color" size="40" class="flex-shrink-0">
              <v-icon color="white" size="20">{{ step.icon }}</v-icon>
            </v-avatar>
            <div>
              <div class="text-overline" :class="`text-${step.color}`">Step {{ step.number }}</div>
              <div class="text-h6 mb-1">{{ step.title }}</div>
              <div class="text-body-2 text-medium-emphasis">{{ step.text }}</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-row justify="center" class="mt-8 mb-16">
      <v-col cols="12" md="6" class="text-center">
        <v-card color="primary" variant="tonal" class="pa-8">
          <h3 class="text-h5 font-weight-bold mb-2">Ready to improve your posture?</h3>
          <p class="text-body-1 mb-4">Sign up and start your first session in under a minute.</p>
          <v-btn to="/register" color="primary" size="large" rounded="lg">
            Get Started Free
          </v-btn>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import PostureDemo from '@/components/PostureDemo.vue'

const features = [
  {
    icon: 'mdi-camera',
    title: 'Live Analysis',
    text: 'Real-time posture scoring using your webcam. See exactly how your body aligns with your ideal posture.',
  },
  {
    icon: 'mdi-chart-line',
    title: 'Track Progress',
    text: 'Monitor your posture score over time. View trends, streaks, and detailed session history.',
  },
  {
    icon: 'mdi-dumbbell',
    title: 'Smart Exercises',
    text: 'Get personalized exercise recommendations based on your specific posture issues.',
  },
]

const steps = [
  {
    number: 1,
    icon: 'mdi-account-plus',
    color: 'primary',
    title: 'Create an Account',
    text: 'Sign up for free and log in to access all features.',
  },
  {
    number: 2,
    icon: 'mdi-webcam',
    color: 'blue',
    title: 'Position Yourself Sideways',
    text: 'Navigate to Live Analysis, grant webcam permission, then sit sideways (90\u00B0) to the camera so it sees your side profile — ear, shoulder, and hip.',
  },
  {
    number: 3,
    icon: 'mdi-human-handsup',
    color: 'teal',
    title: 'Calibrate Your Posture',
    text: 'Sit up straight in your best posture and hold still for about 3 seconds. The system captures your ideal side-profile alignment as a baseline.',
  },
  {
    number: 4,
    icon: 'mdi-chart-donut',
    color: 'green',
    title: 'Get Your Live Score',
    text: 'Once calibrated, you\'ll see a real-time score (0-100) with a breakdown across head position, shoulder levelness, shoulder rounding, and spine alignment. A skeleton overlay shows your current pose vs. your ideal.',
  },
  {
    number: 5,
    icon: 'mdi-dumbbell',
    color: 'orange',
    title: 'Follow Recommendations',
    text: 'After your session, check the recommended exercises tailored to your weak areas. Track your progress over time on the dashboard.',
  },
]
</script>
