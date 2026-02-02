<template>
  <div class="login-view min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 py-12 px-4">
    <div class="card max-w-md w-full">
      <div class="text-center mb-8">
        <div class="text-6xl mb-4">🌾</div>
        <h1 class="text-3xl font-bold text-gray-900">Đăng nhập</h1>
        <p class="text-gray-600 mt-2">WebGIS MSVT - Hệ thống Quản lý Vùng trồng</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Tên đăng nhập
          </label>
          <input
            v-model="formData.username"
            type="text"
            required
            class="input-field"
            placeholder="Nhập tên đăng nhập"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Mật khẩu
          </label>
          <input
            v-model="formData.password"
            type="password"
            required
            class="input-field"
            placeholder="Nhập mật khẩu"
          />
        </div>
        
        <div v-if="error" class="p-3 bg-red-100 border border-red-300 text-red-700 rounded-lg text-sm">
          {{ error }}
        </div>
        
        <button
          type="submit"
          :disabled="loading"
          class="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading">Đang đăng nhập...</span>
          <span v-else">Đăng nhập</span>
        </button>
      </form>
      
      <div class="mt-6 text-center text-sm text-gray-600">
        <p>Demo credentials:</p>
        <p class="font-mono mt-1">admin / 123456</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const route = useRoute()
const { login } = useAuth()

const formData = ref({
  username: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  
  try {
    await login(formData.value)
    // Redirect to requested page or home
    const redirect = route.query.redirect || '/manage'
    router.push(redirect)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.'
  } finally {
    loading.value = false
  }
}
</script>
