<template>
  <v-app>
    <v-app-bar color="primary" density="comfortable">
      <v-app-bar-nav-icon
        v-if="authStore.isAuthenticated"
        @click="drawer = !drawer"
      />
      <v-app-bar-title>
        <router-link to="/" class="text-decoration-none" style="color: inherit">
          PostureScore
        </router-link>
      </v-app-bar-title>
      <v-spacer />
      <v-btn icon @click="toggleTheme">
        <v-icon>{{ isDark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>
      <template v-if="authStore.isAuthenticated">
        <v-btn to="/analyze" variant="text">Analyze</v-btn>
        <v-btn icon @click="handleLogout">
          <v-icon>mdi-logout</v-icon>
        </v-btn>
      </template>
      <template v-else>
        <v-btn to="/login" variant="text">Login</v-btn>
        <v-btn to="/register" variant="outlined">Sign Up</v-btn>
      </template>
    </v-app-bar>

    <v-navigation-drawer
      v-if="authStore.isAuthenticated"
      v-model="drawer"
      temporary
    >
      <v-list nav>
        <v-list-item
          prepend-icon="mdi-view-dashboard"
          title="Dashboard"
          to="/dashboard"
        />
        <v-list-item
          prepend-icon="mdi-human"
          title="Live Analysis"
          to="/analyze"
        />
        <v-list-item
          prepend-icon="mdi-history"
          title="History"
          to="/history"
        />
        <v-list-item
          prepend-icon="mdi-dumbbell"
          title="Exercises"
          to="/exercises"
        />
        <v-divider class="my-2" />
        <v-list-item
          prepend-icon="mdi-logout"
          title="Logout"
          @click="handleLogout"
          base-color="error"
        />
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from 'vuetify'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const theme = useTheme()
const drawer = ref(false)

// Initialize theme: localStorage > system preference > light
const THEME_KEY = 'posture-score-theme'
const saved = localStorage.getItem(THEME_KEY)
if (saved === 'dark' || saved === 'light') {
  theme.global.name.value = saved
} else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
  theme.global.name.value = 'dark'
}

const isDark = computed(() => theme.global.name.value === 'dark')

function toggleTheme() {
  const next = isDark.value ? 'light' : 'dark'
  theme.global.name.value = next
  localStorage.setItem(THEME_KEY, next)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
