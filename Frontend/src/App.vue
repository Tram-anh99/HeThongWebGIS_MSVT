<template>
  <div id="app" class="min-h-screen flex flex-col">
    <!-- Navbar -->
    <nav class="bg-primary-700 text-white shadow-lg">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between h-16">
          <!-- Logo & Title -->
          <router-link to="/" class="flex items-center space-x-3 hover:opacity-90 transition">
            <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
              <span class="text-primary-700 font-bold text-xl">🌾</span>
            </div>
            <div>
              <div class="font-bold text-lg">WebGIS MSVT</div>
              <div class="text-xs text-primary-100">Hệ thống Quản lý Vùng Trồng</div>
            </div>
          </router-link>
          
          <!-- Navigation Menu -->
          <div class="hidden md:flex items-center space-x-6 whitespace-nowrap">
            <router-link
              to="/"
              class="px-4 py-2 rounded-lg hover:bg-primary-600 transition"
              :class="{ 'bg-primary-600': $route.path === '/' }"
            >
              {{ $t('nav.home') }}
            </router-link>
            <router-link
              to="/map"
              class="px-4 py-2 rounded-lg hover:bg-primary-600 transition"
              :class="{ 'bg-primary-600': $route.path === '/map' }"
            >
              {{ $t('nav.map') }}
            </router-link>
            <router-link
              v-if="isAuthenticated"
              to="/manage"
              class="px-4 py-2 rounded-lg hover:bg-primary-600 transition"
              :class="{ 'bg-primary-600': $route.path === '/manage' }"
            >
              {{ $t('nav.management') }}
            </router-link>
            <!-- Feedback for farmers only -->
            <router-link
              v-if="isAuthenticated && user && user.role === 'farmer'"
              to="/feedback"
              class="px-4 py-2 rounded-lg hover:bg-primary-600 transition"
              :class="{ 'bg-primary-600': $route.path === '/feedback' }"
            >
              {{ $t('nav.feedback') }}
            </router-link>
            <router-link
              v-if="isAuthenticated && user && user.role === 'admin'"
              to="/dashboard"
              class="px-4 py-2 rounded-lg hover:bg-primary-600 transition"
              :class="{ 'bg-primary-600': $route.path === '/dashboard' }"
            >
              {{ $t('nav.dashboard') }}
            </router-link>
            <!-- Admin feedback management -->
            <router-link
              v-if="isAuthenticated && user && user.role === 'admin'"
              to="/admin/feedback"
              class="px-4 py-2 rounded-lg hover:bg-primary-600 transition whitespace-nowrap"
              :class="{ 'bg-primary-600': $route.path === '/admin/feedback' }"
            >
              {{ $t('nav.farmerFeedback') }}
            </router-link>
          </div>
          
          <!-- User Menu -->
          <div class="flex items-center space-x-4">
            <!-- Language Switcher Icons -->
            <LanguageSwitcher />
            
            <!-- Account Icon -->
            <router-link
              v-if="isAuthenticated && user"
              to="/users"
              class="text-white hover:text-primary-100 transition relative group"
              :title="user.full_name || user.username"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-8 h-8">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <!-- Tooltip below on hover -->
              <span class="absolute top-full right-0 mt-2 px-3 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                {{ user.full_name || user.username }}
              </span>
            </router-link>
            
            <!-- Logout Button -->
            <button
              v-if="isAuthenticated"
              @click="handleLogout"
              class="px-4 py-2 bg-white text-primary-700 rounded-lg hover:bg-primary-50 transition font-medium whitespace-nowrap"
            >
              {{ $t('nav.logout') }}
            </button>
            <router-link
              v-else
              to="/login"
              class="px-4 py-2 bg-white text-primary-700 rounded-lg hover:bg-primary-50 transition font-medium"
            >
              {{ $t('auth.login') }}
            </router-link>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Main Content -->
    <main class="flex-1">
      <router-view />
    </main>
    
    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-6">
      <div class="container mx-auto px-4 text-center">
        <p>&copy; 2026 WebGIS MSVT. All rights reserved.</p>
        <p class="text-sm text-gray-400 mt-2">Hệ thống Quản lý Mã số Vùng Trồng</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from './composables/useAuth'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

const { t } = useI18n()

const { user, isAuthenticated, fetchCurrentUser, logout } = useAuth()

onMounted(async () => {
  if (isAuthenticated.value) {
    try {
      await fetchCurrentUser()
    } catch (error) {
      console.error('Failed to fetch user:', error)
    }
  }
})

const handleLogout = () => {
  logout()
}
</script>

<style>
#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
