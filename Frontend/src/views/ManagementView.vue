<template>
  <div class="management-view">
    <div class="container mx-auto px-4 py-6">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">Quản lý Vùng trồng</h1>
        <button
          v-if="user && user.role === 'admin'"
          @click="openAddModal"
          class="btn-primary"
        >
          + Thêm Vùng trồng
        </button>
      </div>
      
      <!-- Filters -->
      <div class="card mb-6">
        <div class="grid md:grid-cols-3 gap-4">
          <input
            v-model="filters.search"
            type="text"
            placeholder="Tìm kiếm theo mã vùng, tên..."
            class="input-field"
            @input="handleSearch"
          />
          <input
            v-model="filters.tinh"
            type="text"
            placeholder="Lọc theo tỉnh..."
            class="input-field"
            @input="handleSearch"
          />
          <button
            @click="clearFilters"
            class="btn-secondary"
          >
            Xóa bộ lọc
          </button>
        </div>
      </div>
      
      <!-- Farm Table -->
      <div class="card overflow-x-auto">
        <div v-if="loading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p class="mt-4 text-gray-600">Đang tải dữ liệu...</p>
        </div>
        
        <table v-else class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mã vùng</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tên vùng</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Diện tích (ha)</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Người đại diện</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Địa điểm</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Thao tác</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="farm in farms" :key="farm.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ farm.ma_vung }}</td>
              <td class="px-4 py-3 text-sm text-gray-600">{{ farm.ten_vung }}</td>
              <td class="px-4 py-3 text-sm text-gray-600">{{ farm.dien_tich }}</td>
              <td class="px-4 py-3 text-sm text-gray-600">{{ farm.nguoi_dai_dien }}</td>
              <td class="px-4 py-3 text-sm text-gray-600">{{ farm.tinh_name }}</td>
              <td class="px-4 py-3 text-sm flex gap-2">
                <!-- Everyone can view history -->
                <button
                  @click="viewHistory(farm)"
                  class="text-green-600 hover:text-green-800 font-medium flex items-center gap-1"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  Nhật ký
                </button>
                
                <!-- Quick add history button removed - history is read-only -->

                
                <!-- Admin Only Actions -->
                <template v-if="user && user.role === 'admin'">
                  <button
                    @click="editFarm(farm)"
                    class="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Sửa
                  </button>
                  <button
                    @click="deleteFarm(farm)"
                    class="text-red-600 hover:text-red-800 font-medium"
                  >
                    Xóa
                  </button>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!loading && farms.length === 0" class="text-center py-8 text-gray-500">
          Không có dữ liệu
        </div>
      </div>
      
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="mt-6 flex justify-center space-x-2">
        <button
          v-for="page in totalPages"
          :key="page"
          @click="currentPage = page; fetchFarms()"
          class="px-4 py-2 rounded-lg font-medium transition"
          :class="page === currentPage ? 'bg-primary-600 text-white' : 'bg-gray-200 hover:bg-gray-300'"
        >
          {{ page }}
        </button>
      </div>
    </div>
    
    <!-- Modals -->
    <!-- Farm Add/Edit Modal (Existing logic) -->
    <div
      v-if="showAddModal || showEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click="closeModals"
    >
      <div class="card max-w-2xl w-full max-h-[90vh] overflow-y-auto" @click.stop>
        <h2 class="text-2xl font-bold mb-4">
          {{ showEditModal ? 'Chỉnh sửa Vùng trồng' : 'Thêm Vùng trồng mới' }}
        </h2>
        
        <form @submit.prevent="submitForm" class="space-y-4">
          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Mã vùng *</label>
              <input v-model="formData.ma_vung" type="text" required class="input-field" :disabled="showEditModal" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tên vùng *</label>
              <input v-model="formData.ten_vung" type="text" required class="input-field" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Diện tích (ha)</label>
              <input v-model="formData.dien_tich" type="number" step="0.01" class="input-field" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Người đại diện</label>
              <input v-model="formData.nguoi_dai_dien" type="text" class="input-field" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tỉnh</label>
              <select v-model="formData.tinh_name" class="input-field" @change="onProvinceChange">
                <option value="">-- Chọn tỉnh --</option>
                <option v-for="province in provinces" :key="province" :value="province">
                  {{ province }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Huyện</label>
              <select v-model="formData.huyen_name" class="input-field" :disabled="!formData.tinh_name">
                <option value="">-- Chọn huyện --</option>
                <option v-for="district in districts" :key="district" :value="district">
                  {{ district }}
                </option>
              </select>
              <p v-if="!formData.tinh_name" class="text-xs text-gray-500 mt-1">Vui lòng chọn tỉnh trước</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Xã</label>
              <input v-model="formData.xa_name" type="text" class="input-field" placeholder="Nhập tên xã/phường" />
              <p class="text-xs text-gray-500 mt-1">Nhập thủ công tên xã/phường</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Thị trường xuất khẩu</label>
              <select v-model="formData.thi_truong_xuat_khau" class="input-field">
                <option value="">-- Chọn thị trường --</option>
                <option value="Trung Quốc">Trung Quốc</option>
                <option value="USA">USA</option>
                <option value="Úc/NZ">Úc/NZ</option>
                <option value="Nhật Bản">Nhật Bản</option>
                <option value="Hàn Quốc">Hàn Quốc</option>
                <option value="EU">EU</option>
                <option value="Đông Nam Á">Đông Nam Á</option>
                <option value="Khác">Khác</option>
              </select>
            </div>
            
            <!-- Loại cây trồng -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Loại cây trồng</label>
              <select v-model="formData.cay_trong_id" class="input-field">
                <option :value="null">-- Chọn loại cây --</option>
                <option v-for="crop in crops" :key="crop.id" :value="crop.id">
                  {{ crop.ten_cay }}
                </option>
              </select>
            </div>
            
            <!-- GPS Coordinates Section -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Vĩ độ (Latitude)
                <span class="text-xs text-gray-500 ml-1">- Tùy chọn</span>
              </label>
              <input 
                v-model="formData.latitude" 
                type="number" 
                step="0.000001" 
                placeholder="VD: 10.762622" 
                class="input-field"
                min="-90"
                max="90"
              />
              <p class="text-xs text-gray-500 mt-1">Nhập tọa độ GPS để hiển thị chính xác trên bản đồ</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Kinh độ (Longitude)
                <span class="text-xs text-gray-500 ml-1">- Tùy chọn</span>
              </label>
              <input 
                v-model="formData.longitude" 
                type="number" 
                step="0.000001" 
                placeholder="VD: 106.660172" 
                class="input-field"
                min="-180"
                max="180"
              />
              <p class="text-xs text-gray-500 mt-1">Kinh độ từ -180 đến 180 độ</p>
            </div>
            
            <div v-if="user && user.role === 'admin'">
              <label class="block text-sm font-medium text-gray-700 mb-1">Chủ sở hữu (Nông dân)</label>
              <select v-model="formData.chu_so_huu_id" class="input-field">
                <option :value="null">-- Chọn nông dân --</option>
                <option v-for="f in farmers" :key="f.id" :value="f.id">
                  {{ f.full_name || f.username }} ({{ f.username }})
                </option>
              </select>
            </div>
          </div>
          
          <div v-if="formError" class="p-3 bg-red-100 border border-red-300 text-red-700 rounded-lg text-sm">
            {{ formError }}
          </div>
          
          <div class="flex space-x-3">
            <button type="submit" class="btn-primary flex-1" :disabled="formLoading">
              {{ formLoading ? 'Đang lưu...' : 'Lưu' }}
            </button>
            <button type="button" @click="closeModals" class="btn-secondary flex-1">
              Hủy
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- History List Modal -->
    <HistoryListModal
      v-if="showHistoryModal && selectedFarm"
      :farm="selectedFarm"
      ref="historyListRef"
      @close="showHistoryModal = false"
      @add="openAddHistory"
      @edit="openEditHistory"
    />

    <!-- History Form Modal -->
    <HistoryFormModal
      v-if="showAddHistoryModal && selectedFarm"
      :farm-id="selectedFarm.id"
      :initial-data="selectedHistoryItem"
      @close="closeHistoryForm"
      @saved="refreshHistory"
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { farmService } from '../services/farmService'
import { userService } from '../services/userService'
import { categoryService } from '../services/categoryService'
import { useAuth } from '../composables/useAuth'
import HistoryListModal from '../components/HistoryListModal.vue'
import HistoryFormModal from '../components/HistoryFormModal.vue'

const { user } = useAuth()
const farmers = ref([])
const crops = ref([])
const provinces = ref([])
const districts = ref([])

const fetchFarmers = async () => {
  try {
    const res = await userService.getUsers({ role: 'farmer', page_size: 100 })
    farmers.value = res.data.items
  } catch (e) { console.error(e) }
}

const fetchCrops = async () => {
  try {
    const res = await categoryService.getCrops()
    crops.value = res.data
  } catch (e) { console.error(e) }
}

const fetchProvinces = async () => {
  try {
    // Load provinces from GeoJSON file
    const response = await fetch('/data/63tinh-quandao.geojson')
    const data = await response.json()
    const provinceNames = data.features.map(f => f.properties.NAME_1).sort()
    provinces.value = [...new Set(provinceNames)]
  } catch (e) {
    console.error('Error loading provinces:', e)
    // Fallback to common provinces
    provinces.value = ['Hà Nội', 'TP. Hồ Chí Minh', 'Đà Nẵng', 'Cần Thơ', 'Hải Phòng']
  }
}

const onProvinceChange = () => {
  // Reset district when province changes
  formData.value.huyen_name = ''
  formData.value.xa_name = ''
  
  // For now, set common district names
  // In a full implementation, this would come from a database or API
  const commonDistricts = [
    'Quận 1', 'Quận 2', 'Quận 3', 'Quận 4', 'Quận 5',
    'Quận 6', 'Quận 7', 'Quận 8', 'Quận 9', 'Quận 10',
    'Quận 11', 'Quận 12', 'Quận Bình Thạnh', 'Quận Gò Vấp',
    'Quận Phú Nhuận', 'Quận Tân Bình', 'Quận Tân Phú',
    'Huyện Bình Chánh', 'Huyện Củ Chi', 'Huyện Hóc Môn',
    'Huyện Nhà Bè', 'Huyện Cần Giờ'
  ]
  districts.value = commonDistricts
}

const openAddModal = () => {
  if (user.value?.role === 'admin') fetchFarmers()
  fetchCrops()
  fetchProvinces()
  showAddModal.value = true
}

const farms = ref([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)

const filters = ref({
  search: '',
  tinh: ''
})

// Farm Modals State
const showAddModal = ref(false)
const showEditModal = ref(false)
const selectedFarm = ref(null)
const formLoading = ref(false)
const formError = ref('')

// History Modals State
const showHistoryModal = ref(false)
const showAddHistoryModal = ref(false)
const selectedHistoryItem = ref(null)
const historyListRef = ref(null)

const formData = ref({
  ma_vung: '',
  ten_vung: '',
  dien_tich: null,
  nguoi_dai_dien: '',
  xa_name: '',
  huyen_name: '',
  tinh_name: '',
  thi_truong_xuat_khau: '',
  cay_trong_id: null,
  latitude: null,
  longitude: null
})

const fetchFarms = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: 20,
      search: filters.value.search || undefined,
      tinh: filters.value.tinh || undefined
    }
    const response = await farmService.getFarms(params)
    farms.value = response.data.items
    totalPages.value = response.data.total_pages
  } catch (err) {
    console.error('Fetch farms error:', err)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchFarms()
}

const clearFilters = () => {
  filters.value = { search: '', tinh: '' }
  handleSearch()
}

const editFarm = (farm) => {
  selectedFarm.value = farm
  if (user.value?.role === 'admin') fetchFarmers()
  fetchCrops()
  fetchProvinces()
  formData.value = { ...farm }
  // If province is set, load districts
  if (farm.tinh_name) {
    onProvinceChange()
  }
  showEditModal.value = true
}

const deleteFarm = async (farm) => {
  if (!confirm(`Xác nhận xóa vùng trồng "${farm.ten_vung}"?`)) return
  
  try {
    await farmService.deleteFarm(farm.id)
    fetchFarms()
  } catch (err) {
    alert('Lỗi khi xóa vùng trồng: ' + (err.response?.data?.detail || err.message))
  }
}

const submitForm = async () => {
  formError.value = ''
  formLoading.value = true
  
  try {
    if (showEditModal.value) {
      await farmService.updateFarm(selectedFarm.value.id, formData.value)
    } else {
      await farmService.createFarm(formData.value)
    }
    closeModals()
    fetchFarms()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Lỗi khi lưu dữ liệu'
  } finally {
    formLoading.value = false
  }
}

const closeModals = () => {
  showAddModal.value = false
  showEditModal.value = false
  selectedFarm.value = null
  // Reset form
  formData.value = {
    ma_vung: '',
    ten_vung: '',
    dien_tich: null,
    nguoi_dai_dien: '',
    xa_name: '',
    huyen_name: '',
    tinh_name: '',
    thi_truong_xuat_khau: '',
    cay_trong_id: null,
    latitude: null,
    longitude: null,
    chu_so_huu_id: null
  }
  formError.value = ''
}

// History Logic
const viewHistory = (farm) => {
  selectedFarm.value = farm
  showHistoryModal.value = true
}

const quickAddHistory = (farm) => {
  selectedFarm.value = farm
  selectedHistoryItem.value = null
  showAddHistoryModal.value = true
}

const openAddHistory = () => {
  selectedHistoryItem.value = null
  showAddHistoryModal.value = true
}

const openEditHistory = (record) => {
  selectedHistoryItem.value = { ...record }
  showAddHistoryModal.value = true
}

const closeHistoryForm = () => {
  showAddHistoryModal.value = false
  selectedHistoryItem.value = null
}

const refreshHistory = () => {
  if (historyListRef.value) {
    historyListRef.value.fetchHistory()
  }
}

onMounted(() => {
  fetchFarms()
})
</script>
