<template>
  <div class="trace-view min-h-screen bg-gradient-to-br from-green-50 to-blue-50 py-12 px-4">
    <div class="container mx-auto max-w-4xl">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="text-6xl mb-4">🌾</div>
        <h1 class="text-4xl font-bold text-gray-900 mb-2">Truy xuất Nguồn gốc</h1>
        <p class="text-gray-600">Mã vùng trồng: <span class="font-bold">{{ maVung }}</span></p>
      </div>
      
      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-primary-600"></div>
        <p class="mt-4 text-gray-600 text-lg">Đang tải thông tin...</p>
      </div>
      
      <!-- Error -->
      <div v-else-if="error" class="card bg-red-50 border-red-200">
        <div class="text-center py-8">
          <div class="text-6xl mb-4">⚠️</div>
          <h2 class="text-2xl font-bold text-red-700 mb-2">Không tìm thấy thông tin</h2>
          <p class="text-red-600">{{ error }}</p>
          <router-link to="/" class="btn-primary inline-block mt-6">
            Về trang chủ
          </router-link>
        </div>
      </div>
      
      <!-- Farm Info -->
      <div v-else>
        <!-- Basic Info Card -->
        <div class="card mb-6">
          <h2 class="text-2xl font-bold mb-4 flex items-center">
            <span class="mr-2">📍</span>
            Thông tin Vùng trồng
          </h2>
          <div class="grid md:grid-cols-2 gap-4">
            <div class="space-y-2">
              <div class="flex">
                <span class="font-medium text-gray-600 w-32">Mã vùng:</span>
                <span class="font-bold text-primary-700">{{ farmInfo.ma_vung }}</span>
              </div>
              <div class="flex">
                <span class="font-medium text-gray-600 w-32">Tên vùng:</span>
                <span>{{ farmInfo.ten_vung }}</span>
              </div>
              <div class="flex">
                <span class="font-medium text-gray-600 w-32">Diện tích:</span>
                <span>{{ farmInfo.dien_tich }} ha</span>
              </div>
              <div class="flex">
                <span class="font-medium text-gray-600 w-32">Người đại diện:</span>
                <span>{{ farmInfo.nguoi_dai_dien }}</span>
              </div>
            </div>
            <div class="space-y-2">
              <div class="flex">
                <span class="font-medium text-gray-600 w-32">Xã:</span>
                <span>{{ farmInfo.xa }}</span>
              </div>
              <div class="flex">
                <span class="font-medium text-gray-600 w-32">Huyện:</span>
                <span>{{ farmInfo.huyen }}</span>
              </div>
              <div class="flex">
                <span class="font-medium text-gray-600 w-32">Tỉnh:</span>
                <span>{{ farmInfo.tinh }}</span>
              </div>
              <div class="flex">
                <span class="font-medium text-gray-600 w-32">Thị trường:</span>
                <span>{{ farmInfo.thi_truong_xuat_khau }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- History Timeline -->
        <div class="card">
          <h2 class="text-2xl font-bold mb-4 flex items-center">
            <span class="mr-2">📋</span>
            Lịch sử Canh tác
            <span class="ml-auto text-sm font-normal text-gray-500">
              ({{ historyData.length }} hoạt động)
            </span>
          </h2>
          
          <div v-if="historyData.length === 0" class="text-center py-8 text-gray-500">
            Chưa có lịch sử canh tác
          </div>
          
          <!-- Timeline -->
          <div v-else class="space-y-4">
            <div
              v-for="(item, index) in historyData"
              :key="index"
              class="flex space-x-4 pb-4"
              :class="{ 'border-b': index < historyData.length - 1 }"
            >
              <!-- Timeline marker -->
              <div class="flex flex-col items-center">
                <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                  <span class="text-primary-700 font-bold">{{ index + 1 }}</span>
                </div>
                <div v-if="index < historyData.length - 1" class="w-0.5 flex-1 bg-gray-200 mt-2"></div>
              </div>
              
              <!-- Content -->
              <div class="flex-1">
                <div class="flex items-center justify-between mb-2">
                  <span class="font-bold text-gray-900">
                    {{ formatDate(item.ngay_thuc_hien) }}
                  </span>
                  <span v-if="item.nguoi_thuc_hien" class="text-sm text-gray-500">
                    👤 {{ item.nguoi_thuc_hien }}
                  </span>
                </div>
                <p class="text-gray-700">{{ item.chi_tiet || 'Không có mô tả' }}</p>
                <div v-if="item.lieu_luong && item.don_vi" class="mt-2 text-sm text-gray-600">
                  Liều lượng: {{ item.lieu_luong }} {{ item.don_vi }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- QR Code Section -->
        <div class="card mt-6 text-center">
          <h3 class="text-lg font-bold mb-4">Chia sẻ QR Code</h3>
          <img
            :src="qrCodeUrl"
            :alt="`QR Code ${maVung}`"
            class="mx-auto w-48 h-48 border-4 border-gray-200 rounded-lg"
          />
          <p class="text-sm text-gray-600 mt-4">
            Scan QR code để truy xuất thông tin này
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { qrService } from '../services/qrService'

const route = useRoute()
const maVung = computed(() => route.params.ma_vung)

const loading = ref(false)
const error = ref('')
const farmInfo = ref({})
const historyData = ref([])

const qrCodeUrl = computed(() => qrService.generateQR(maVung.value))

const fetchTraceData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await qrService.traceFarm(maVung.value)
    farmInfo.value = response.data.farm
    historyData.value = response.data.history || []
  } catch (err) {
    error.value = err.response?.data?.detail || `Không tìm thấy thông tin cho mã vùng ${maVung.value}`
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  fetchTraceData()
})
</script>
