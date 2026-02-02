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
          <div class="hidden md:flex items-center space-x-1">
            <router-link
              to="/"
              class="px-4 py-2 rounded-lg hover:bg-primary-600 transition"
              :class="{ 'bg-primary-600': $route.path === '/' }"
            >
              Trang chủ
            </router-link>
            <router-link
              to="/map"
              class="px-4 py-2 rounded-lg hover:bg-primary-600 transition"
              :class="{ 'bg-primary-600': $route.path === '/map' }"
            >
              Bản đồ
            </router-link>
            <router-link
              v-if="isAuthenticated"
              to="/manage"
              class="px-4 py-2 rounded-lg hover:bg-primary-600 transition"
              :class="{ 'bg-primary-600': $route.path === '/manage' }"
            >
              Quản lý
            </router-link>
            <router-link
              v-if="isAuthenticated && user && user.role === 'admin'"
              to="/users"
              class="px-4 py-2 rounded-lg hover:bg-primary-600 transition"
              :class="{ 'bg-primary-600': $route.path === '/users' }"
            >
              Tài khoản
            </router-link>
          </div>
          
          <!-- User Menu -->
          <div class="flex items-center space-x-2">
            <div v-if="isAuthenticated && user" class="hidden md:block text-sm">
              <div class="font-medium">{{ user.full_name || user.username }}</div>
              <div class="text-xs text-primary-100">{{ user.role }}</div>
            </div>
            <button
              v-if="isAuthenticated"
              @click="handleLogout"
              class="px-4 py-2 bg-white text-primary-700 rounded-lg hover:bg-primary-50 transition font-medium"
            >
              Đăng xuất
            </button>
            <router-link
              v-else
              to="/login"
              class="px-4 py-2 bg-white text-primary-700 rounded-lg hover:bg-primary-50 transition font-medium"
            >
              Đăng nhập
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
import { useAuth } from './composables/useAuth'

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
