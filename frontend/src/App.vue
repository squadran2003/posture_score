<template>
  <v-app>
    <v-app-bar color="primary" density="comfortable">
      <v-app-bar-nav-icon
        v-if="authStore.isAuthenticated"
        @click="drawer = !drawer"
      />
      <v-app-bar-title>
        <router-link to="/" class="text-white text-decoration-none">
          PostureScore
        </router-link>
      </v-app-bar-title>
      <v-spacer />
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
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const drawer = ref(false)

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
