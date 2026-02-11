<template>
  <div class="farmer-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div>
        <h1 class="dashboard-title">Bảng điều khiển Nông dân</h1>
        <p class="farmer-name">{{ user ? user.full_name || user.username : '' }}</p>
      </div>
      <button @click="refreshData" :disabled="loading" class="btn-refresh">
        <span>🔄</span>
        <span>Làm mới</span>
      </button>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <KPICard
        title="Số vùng trồng của tôi"
        :value="kpiData.total_farms"
        icon="🌾"
        color="#10b981"
        unit="vùng"
      />
      <KPICard
        title="Tổng diện tích"
        :value="kpiData.total_area"
        icon="📐"
        color="#3b82f6"
        unit="ha"
      />
      <KPICard
        title="Vụ mùa hoạt động"
        :value="kpiData.active_seasons"
        icon="🌱"
        color="#f59e0b"
        unit="vụ"
      />
    </div>

    <!-- Map and Charts Section -->
    <div class="content-grid">
      <!-- Left Column: Map + Timeline -->
      <div class="map-section">
        <h2 class="section-title">🗺️ Bản đồ vùng trồng</h2>
        <div id="farmer-map" class="map-container"></div>
      </div>

      <!-- Right Column: Charts -->
      <div class="charts-section">
        <!-- Farm List -->
        <div class="chart-card">
          <h3 class="chart-title">🌾 Danh sách vùng trồng</h3>
          <div v-if="farmsMapData.length > 0" class="farm-list">
            <div 
              @click="selectFarm(null)" 
              :class="['farm-item', { 'selected': selectedFarm === null }]"
            >
              <div class="farm-info">
                <strong>📊 Tất cả vùng</strong>
                <span class="farm-meta">{{ farmsMapData.length }} vùng - {{ totalArea }} ha</span>
              </div>
            </div>
            <div 
              v-for="farm in farmsMapData" 
              :key="farm.id"
              @click="selectFarm(farm)"
              :class="['farm-item', { 'selected': selectedFarm?.id === farm.id }]"
            >
              <div class="farm-info">
                <strong>{{ farm.ten_vung }}</strong>
                <span class="farm-crop">{{ farm.cay_trong || 'Chưa rõ' }}</span>
              </div>
              <span class="farm-area">{{ farm.dien_tich }} ha</span>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>Chưa có vùng trồng</p>
          </div>
        </div>

        <!-- Export Market Chart -->
        <div class="chart-card">
          <h3 class="chart-title">🌍 Thị trường xuất khẩu</h3>
          <div v-if="exportMarketData.length > 0" class="chart-wrapper">
            <v-chart :option="exportMarketOption" autoresize />
          </div>
          <div v-else class="empty-state">
            <p>Chưa có dữ liệu thị trường</p>
          </div>
        </div>

        <!-- Combined Input Usage Line Chart -->
        <div class="chart-card">
          <h3 class="chart-title">📈 Sử dụng đầu vào (Phân bón & Thuốc BVTV)</h3>
          <div v-if="hasInputUsageData" class="chart-wrapper">
            <v-chart :option="combinedInputUsageOption" autoresize />
          </div>
          <div v-else class="empty-state">
            <p>Chưa có dữ liệu sử dụng đầu vào</p>
          </div>
        </div>

      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Đang tải dữ liệu...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

import KPICard from '../components/dashboard/KPICard.vue'
import { useAuth } from '../composables/useAuth'
import api from '../services/api'

// Register ECharts components
use([CanvasRenderer, PieChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const { user } = useAuth()

// Data
const loading = ref(false)
const kpiData = ref({
  total_farms: 0,
  total_area: 0,
  active_seasons: 0
})
const cropChartData = ref([])
const exportMarketData = ref([])
const inputUsageData = ref({
  fertilizer_by_name: [],
  pesticide_by_type: []
})
const farmsMapData = ref([])
const cultivationTimeline = ref([])
const selectedFarm = ref(null)
let map = null
let farmMarkers = []

// Chart Options
const cropDistributionOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} vùng ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center'
  },
  series: [
    {
      name: 'Cây trồng',
      type: 'pie',
      radius: '70%',
      data: cropChartData.value.map(c => ({
        name: c.crop_type,
        value: c.farm_count
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}))

const exportMarketOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} vùng ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center'
  },
  series: [
    {
      name: 'Thị trường',
      type: 'pie',
      radius: '70%',
      data: exportMarketData.value.map(m => ({
        name: m.market,
        value: m.farm_count
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}))

const hasInputUsageData = computed(() => {
  return (inputUsageData.value.fertilizer_by_name && inputUsageData.value.fertilizer_by_name.length > 0) ||
         (inputUsageData.value.pesticide_by_type && inputUsageData.value.pesticide_by_type.length > 0)
})

const combinedInputUsageOption = computed(() => {
  // Combine categories from both fertilizer and pesticide
  const categories = []
  const fertilizerData = []
  const pesticideData = []
  
  // Add fertilizer data
  inputUsageData.value.fertilizer_by_name.forEach(f => {
    categories.push(`PB: ${f.name}`)
    fertilizerData.push(f.volume)
    pesticideData.push(null) // No pesticide value for fertilizer category
  })
  
  // Add pesticide data
  inputUsageData.value.pesticide_by_type.forEach(p => {
    categories.push(`TBVTV: ${p.type}`)
    pesticideData.push(p.volume)
    fertilizerData.push(null) // No fertilizer value for pesticide category
  })
  
  return {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = params[0].name + '<br/>'
        params.forEach(param => {
          if (param.value !== null) {
            const unit = param.seriesName.includes('Phân bón') ? 'kg' : 'lít'
            result += `${param.marker} ${param.seriesName}: ${param.value} ${unit}<br/>`
          }
        })
        return result
      }
    },
    legend: {
      data: ['Phân bón', 'Thuốc BVTV'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        rotate: 45,
        interval: 0,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      name: 'Khối lượng'
    },
    series: [
      {
        name: 'Phân bón',
        type: 'line',
        data: fertilizerData,
        smooth: true,
        lineStyle: {
          color: '#10b981',
          width: 3
        },
        itemStyle: {
          color: '#10b981'
        },
        connectNulls: false,
        label: {
          show: true,
          position: 'top',
          formatter: '{c} kg'
        }
      },
      {
        name: 'Thuốc BVTV',
        type: 'line',
        data: pesticideData,
        smooth: true,
        lineStyle: {
          color: '#f59e0b',
          width: 3
        },
        itemStyle: {
          color: '#f59e0b'
        },
        connectNulls: false,
        label: {
          show: true,
          position: 'top',
          formatter: '{c} L'
        }
      }
    ]
  }
})


// Methods
const fetchKPIData = async () => {
  try {
    const response = await api.get('/analytics/farmer/kpi')
    kpiData.value = response.data
  } catch (error) {
    console.error('Error fetching KPI data:', error)
  }
}

const fetchCropDistribution = async () => {
  try {
    const response = await api.get('/analytics/farmer/crop-distribution')
    cropChartData.value = response.data
  } catch (error) {
    console.error('Error fetching crop distribution:', error)
  }
}

const fetchFarmsMap = async () => {
  try {
    const response = await api.get('/analytics/farmer/farms-map')
    farmsMapData.value = response.data.data
    initMap()
  } catch (error) {
    console.error('Error fetching farms map data:', error)
  }
}

const fetchCultivationTimeline = async () => {
  try {
    const params = selectedFarm.value ? { farm_id: selectedFarm.value.id } : {}
    const response = await api.get('/analytics/farmer/cultivation-timeline', { params })
    // Backend now returns array directly, not wrapped in {activities: [...]}
    cultivationTimeline.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('Error fetching cultivation timeline:', error)
    cultivationTimeline.value = []
  }
}

const fetchExportMarkets = async () => {
  try {
    const response = await api.get('/analytics/farmer/export-markets')
    exportMarketData.value = response.data
  } catch (error) {
    console.error('Error fetching export markets:', error)
  }
}

const totalArea = computed(() => {
  return farmsMapData.value.reduce((sum, farm) => sum + (farm.dien_tich || 0), 0).toFixed(1)
})

const selectFarm = async (farm) => {
  selectedFarm.value = farm
  
  // Update map
  if (map) {
    if (farm && farm.latitude && farm.longitude) {
      // Zoom to selected farm
      map.setView([farm.latitude, farm.longitude], 14)
      
      // Highlight selected marker
      farmMarkers.forEach(marker => {
        const isFarmMarker = marker.farmId === farm.id
        marker.setIcon(L.icon({
          iconUrl: isFarmMarker 
            ? 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png'
            : 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
          iconSize: isFarmMarker ? [30, 50] : [25, 41],
          iconAnchor: isFarmMarker ? [15, 50] : [12, 41],
          popupAnchor: [1, -34],
          shadowSize: [41, 41]
        }))
      })
    } else {
      // Reset to show all farms
      if (farmsMapData.value.length > 0) {
        const bounds = L.latLngBounds(farmsMapData.value.filter(f => f.latitude && f.longitude).map(f => [f.latitude, f.longitude]))
        map.fitBounds(bounds, { padding: [50, 50] })
      }
      
      // Reset all markers to default
      farmMarkers.forEach(marker => {
        marker.setIcon(L.icon({
          iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
          popupAnchor: [1, -34],
          shadowSize: [41, 41]
        }))
      })
    }
  }
  
  // Refresh filtered data
  await Promise.all([
    fetchInputUsage(),
    fetchCultivationTimeline()
  ])
}

const fetchInputUsage = async () => {
  try {
    const params = selectedFarm.value ? { farm_id: selectedFarm.value.id } : {}
    const response = await api.get('/analytics/farmer/input-usage', { params })
    inputUsageData.value = response.data
  } catch (error) {
    console.error('Error fetching input usage:', error)
  }
}

const initMap = () => {
  if (map) {
    map.remove()
  }
  farmMarkers = []

  const mapElement = document.getElementById('farmer-map')
  if (!mapElement) return

  // Default center (Vietnam)
  let center = [16.0544, 108.2022]
  let zoom = 6

  // If farmer has farms, center on all farms
  if (farmsMapData.value.length > 0) {
    const farmsWithCoords = farmsMapData.value.filter(f => f.latitude && f.longitude)
    if (farmsWithCoords.length > 0) {
      const bounds = L.latLngBounds(farmsWithCoords.map(f => [f.latitude, f.longitude]))
      map = L.map('farmer-map')
      map.fitBounds(bounds, { padding: [50, 50] })
    } else {
      map = L.map('farmer-map').setView(center, zoom)
    }
  } else {
    map = L.map('farmer-map').setView(center, zoom)
  }

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map)

  // Add markers for farms
  farmsMapData.value.forEach(farm => {
    if (farm.latitude && farm.longitude) {
      const marker = L.marker([farm.latitude, farm.longitude], {
        icon: L.icon({
          iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
          popupAnchor: [1, -34],
          shadowSize: [41, 41]
        })
      }).addTo(map)
      
      marker.farmId = farm.id
      marker.bindPopup(`
        <div class="farm-popup">
          <h4>${farm.ten_vung}</h4>
          <p><strong>Mã vùng:</strong> ${farm.ma_vung}</p>
          <p><strong>Cây trồng:</strong> ${farm.cay_trong || 'Chưa xác định'}</p>
          <p><strong>Diện tích:</strong> ${farm.dien_tich} ha</p>
        </div>
      `)
      
      marker.on('click', () => selectFarm(farm))
      farmMarkers.push(marker)
    }
  })
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('vi-VN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchKPIData(),
      fetchCropDistribution(),
      fetchExportMarkets(),
      fetchInputUsage(),
      fetchFarmsMap(),
      fetchCultivationTimeline()
    ])
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.farmer-dashboard {
  padding: 2rem;
  background: #f9fafb;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 1rem;
}

.dashboard-title {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.farmer-name {
  margin-top: 0.5rem;
  font-size: 1rem;
  color: #6b7280;
  font-weight: 500;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-refresh:hover:not(:disabled) {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.map-section, .charts-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1rem;
}

.map-container {
  height: 500px;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.chart-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.chart-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.chart-wrapper {
  height: 300px;
}

.timeline-list {
  max-height: 400px;
  overflow-y: auto;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.timeline-item:last-child {
  border-bottom: none;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  background: #667eea;
  border-radius: 50%;
  margin-top: 0.25rem;
  flex-shrink: 0;
}

.timeline-content {
  flex: 1;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.timeline-date {
  font-size: 0.875rem;
  color: #6b7280;
}

.activity-type {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #e0e7ff;
  color: #667eea;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.timeline-description p {
  margin: 0.5rem 0 0 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #9ca3af;
}

/* Farm List Styles */
.farm-list {
  max-height: 400px;
  overflow-y: auto;
}

.farm-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s;
}

.farm-item:hover {
  background: #f9fafb;
}

.farm-item.selected {
  background: #e0e7ff;
  border-left: 4px solid #667eea;
}

.farm-item:last-child {
  border-bottom: none;
}

.farm-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.farm-info strong {
  color: #1f2937;
  font-size: 1rem;
}

.farm-crop {
  font-size: 0.875rem;
  color: #6b7280;
}

.farm-meta {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.farm-area {
  font-weight: 600;
  color: #10b981;
  font-size: 0.875rem;
}


.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  z-index: 9999;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
