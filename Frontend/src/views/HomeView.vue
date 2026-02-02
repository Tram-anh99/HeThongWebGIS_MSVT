<template>
  <div class="home-view">
    <!-- Hero Section -->
    <div class="bg-gradient-to-r from-primary-600 to-primary-800 text-white py-20">
      <div class="container mx-auto px-4 text-center">
        <h1 class="text-5xl font-bold mb-4">
          🌾 Hệ thống WebGIS MSVT
        </h1>
        <p class="text-xl mb-8 text-primary-100">
          Quản lý và Truy xuất nguồn gốc Vùng trồng
        </p>
        <div class="flex justify-center space-x-4">
          <router-link to="/map" class="px-8 py-3 bg-white text-primary-700 rounded-lg font-bold hover:bg-primary-50 transition shadow-lg">
            Xem Bản đồ
          </router-link>
          <router-link to="/manage" class="px-8 py-3 bg-primary-500 text-white rounded-lg font-bold hover:bg-primary-400 transition border-2 border-white">
            Quản lý Vùng trồng
          </router-link>
        </div>
      </div>
    </div>
    
    <!-- Features Section -->
    <div class="container mx-auto px-4 py-16">
      <h2 class="text-3xl font-bold text-center mb-12">Tính năng chính</h2>
      
      <div class="grid md:grid-cols-3 gap-8">
        <!-- Feature 1 -->
        <div class="card text-center">
          <div class="text-5xl mb-4">🗺️</div>
          <h3 class="text-xl font-bold mb-2">Bản đồ WebGIS</h3>
          <p class="text-gray-600">
            Hiển thị vị trí vùng trồng trên bản đồ tương tác với Leaflet.js
          </p>
        </div>
        
        <!-- Feature 2 -->
        <div class="card text-center">
          <div class="text-5xl mb-4">📋</div>
          <h3 class="text-xl font-bold mb-2">Quản lý Canh tác</h3>
          <p class="text-gray-600">
            Ghi nhận lịch sử canh tác, sử dụng phân bón, thuốc BVTV
          </p>
        </div>
        
        <!-- Feature 3 -->
        <div class="card text-center">
          <div class="text-5xl mb-4">📱</div>
          <h3 class="text-xl font-bold mb-2">QR Code Truy xuất</h3>
          <p class="text-gray-600">
            Scan QR code để xem thông tin và lịch sử canh tác vùng trồng
          </p>
        </div>
      </div>
    </div>
    
    <!-- Stats Section -->
    <div class="bg-gray-100 py-16">
      <div class="container mx-auto px-4">
        <div class="grid md:grid-cols-4 gap-8 text-center">
          <div>
            <div class="text-4xl font-bold text-primary-600">{{ stats.farms }}</div>
            <div class="text-gray-600 mt-2">Vùng trồng</div>
          </div>
          <div>
            <div class="text-4xl font-bold text-primary-600">{{ stats.crops }}</div>
            <div class="text-gray-600 mt-2">Loại cây</div>
          </div>
          <div>
            <div class="text-4xl font-bold text-primary-600">{{ stats.fertilizers }}</div>
            <div class="text-gray-600 mt-2">Phân bón</div>
          </div>
          <div>
            <div class="text-4xl font-bold text-primary-600">{{ stats.pesticides }}</div>
            <div class="text-gray-600 mt-2">Thuốc BVTV</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const stats = ref({
  farms: 181,
  crops: 9,
  fertilizers: 2095,
  pesticides: 4572
})

onMounted(() => {
  // Could fetch real stats from API
})
</script>
