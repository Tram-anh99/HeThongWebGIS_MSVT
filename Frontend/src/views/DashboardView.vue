<template>
  <div class="dashboard-view">
    <!-- Header -->
    <div class="dashboard-header">
      <div>
        <h1 class="dashboard-title">
          {{ user && user.role === 'manager' ? 'Bảng điều khiển Chi cục' : 'Bảng điều khiển Admin' }}
        </h1>
        <p v-if="user && user.role === 'manager' && user.province_code" class="province-indicator">
          📍 Tỉnh/Thành phố: <strong>{{ user.province_code }}</strong>
        </p>
      </div>
      <div class="refresh-button">
        <button @click="refreshData" :disabled="loading" class="btn-refresh">
          <span>🔄</span>
          <span>Làm mới</span>
        </button>
      </div>
    </div>

    <!-- KPI Cards Row -->
    <div class="kpi-grid">
      <KPICard
        title="Tổng số vùng trồng"
        :value="computedKPIData.totalFarms"
        :loading="loading"
        icon="🌾"
        theme="primary"
        subtitle="vùng"
      />
      <KPICard
        title="Tổng diện tích"
        :value="computedKPIData.totalArea"
        :loading="loading"
        icon="📏"
        theme="success"
        subtitle="ha"
      />
      <KPICard
        title="Số vụ mùa đang hoạt động"
        :value="computedKPIData.activeSeasons"
        :loading="loading"
        icon="🌱"
        theme="info"
        subtitle="vụ"
      />
      <KPICard
        title="Tổng nông dân"
        :value="computedKPIData.totalFarmers"
        :loading="loading"
        icon="👨‍🌾"
        theme="warning"
        subtitle="người"
      />
    </div>

    <!-- Main Map Section: 2/3 + 1/3 Layout -->
    <div class="map-section">
      <!-- Map Container (2/3) -->
      <div class="map-container-large">
        <div class="chart-card" style="height: 600px">
          <h3 class="chart-title">Bản đồ Tương tác</h3>
          <div id="dashboard-map" style="height: 550px; width: 100%;"></div>
        </div>
      </div>

      <!-- Sidebar (1/3) -->
      <div class="sidebar">
        <!-- Layer Controls -->
        <div class="chart-card">
          <h3 class="chart-title">🗺️ Lớp bản đồ</h3>
          <div class="layer-controls">
            <label class="layer-toggle">
              <input type="checkbox" v-model="layers.farms" @change="toggleLayer('farms')">
              <span>📍 Vị trí vùng trồng</span>
            </label>
            <label class="layer-toggle">
              <input type="checkbox" v-model="layers.markets" @change="toggleLayer('markets')">
              <span>🌏 Thị trường xuất khẩu</span>
            </label>
            <div class="layer-legend" v-if="layers.markets">
              <div><span class="color-box" style="background: #ef4444"></span> Trung Quốc</div>
              <div><span class="color-box" style="background: #3b82f6"></span> USA</div>
              <div><span class="color-box" style="background: #10b981"></span> Úc/NZ</div>
              <div><span class="color-box" style="background: #9ca3af"></span> Khác</div>
            </div>
            <label class="layer-toggle">
              <input type="checkbox" v-model="layers.fertilizer" @change="toggleLayer('fertilizer')">
              <span>🌱 Phân bón (độ đậm)</span>
            </label>
            <label class="layer-toggle">
              <input type="checkbox" v-model="layers.pesticide" @change="toggleLayer('pesticide')">
              <span>🧪 Thuốc BVTV (kích thước)</span>
            </label>
          </div>
        </div>

        <!-- Farm List -->
        <div class="chart-card farm-list-card">
          <div class="farm-list-header">
            <h3 class="chart-title">
              {{ selectedProvince ? `📋 ${selectedProvince}` : '📋 Chọn tỉnh' }}
              <span v-if="provinceFarms.length > 0" class="province-badge">
                {{ provinceFarms.length }} vùng
              </span>
            </h3>
            <button v-if="filterActive" @click="clearFilter" class="clear-filter-btn">
              ✕ Xóa lọc
            </button>
          </div>
          
          <!-- Active Filters Display -->
          <div v-if="filterActive" class="active-filters">
            <div v-if="chartFilters.crop" class="filter-badge crop">
              <span class="filter-label">🌱 Cây trồng:</span>
              <span class="filter-value">{{ chartFilters.crop }}</span>
            </div>
            <div v-if="chartFilters.market" class="filter-badge market">
              <span class="filter-label">🌏 Thị trường:</span>
              <span class="filter-value">{{ chartFilters.market }}</span>
            </div>
            <div v-if="chartFilters.fertilizer" class="filter-badge fertilizer">
              <span class="filter-label">🌱 Phân bón:</span>
              <span class="filter-value">{{ chartFilters.fertilizer }}</span>
            </div>
            <div v-if="chartFilters.pesticide" class="filter-badge pesticide">
              <span class="filter-label">🧪 Thuốc BVTV:</span>
              <span class="filter-value">{{ chartFilters.pesticide }}</span>
            </div>
          </div>
          
          <div class="farm-list">
            <div v-if="provinceFarms.length === 0" class="empty-state">
              <p>Nhấp vào tỉnh trên bản đồ<br/>để xem danh sách vùng trồng</p>
            </div>
            <div v-else class="farm-items">
              <div v-for="farm in provinceFarms" :key="farm.id" 
                   class="farm-item"
                   :class="{ 'active': selectedFarm && selectedFarm.id === farm.id }"
                   @click="handleFarmListClick(farm)">
                <div class="farm-code">{{ farm.ma_vung }}</div>
                <div class="farm-name">{{ farm.ten_vung }}</div>
                <div class="farm-market">{{ farm.thi_truong_xuat_khau }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pie Charts Grid (3 columns below map) -->
    <div class="pie-charts-grid">
      <div class="chart-card">
        <h3 class="chart-title">Cây trồng theo Mã vùng</h3>
        <div class="chart-container" style="height: 300px">
          <v-chart :option="cropsByFarmOption" :loading="chartsLoading" autoresize @click="handleChartClick('crops', $event)" />
        </div>
      </div>

      <!-- Hidden: Tỷ lệ Phân bón pie chart
      <div class="chart-card">
        <h3 class="chart-title">Tỷ lệ Phân bón</h3>
        <div class="chart-container" style="height: 300px">
          <v-chart :option="fertilizerUsageOption" :loading="chartsLoading" autoresize @click="handleChartClick('fertilizer', $event)" />
        </div>
      </div>
      -->

      <!-- Hidden: Tỷ lệ Thuốc BVTV pie chart
      <div class="chart-card">
        <h3 class="chart-title">Tỷ lệ Thuốc BVTV</h3>
        <div class="chart-container" style="height: 300px">
          <v-chart :option="pesticideUsageOption" :loading="chartsLoading" autoresize @click="handleChartClick('pesticide', $event)" />
        </div>
      </div>
      -->
    </div>

    <div class="usage-charts-grid">
      <div class="chart-card">
        <h3 class="chart-title">📊 Sử dụng Phân bón (Hữu cơ / Vô cơ)</h3>
        <div class="chart-container" style="height: 350px">
          <v-chart :option="fertilizerVolumeOption" :loading="chartsLoading" autoresize @click="handleChartClick('fertilizer', $event)" />
        </div>
      </div>

      <div class="chart-card">
        <h3 class="chart-title">📊 Sử dụng Thuốc BVTV theo Loại</h3>
        <div class="chart-container" style="height: 350px">
          <v-chart :option="pesticideVolumeOption" :loading="chartsLoading" autoresize @click="handleChartClick('pesticide', $event)" />
        </div>
      </div>
    </div>

    <!-- Line Chart: Crop × Market Relationship -->
    <div class="chart-card full-width">
      <h3 class="chart-title">Mối quan hệ Cây trồng × Thị trường Xuất khẩu</h3>
      <div class="chart-container" style="height: 350px">
        <v-chart :option="cropMarketOption" :loading="chartsLoading" autoresize @click="handleChartClick('market', $event)" />
      </div>
    </div>

    <!-- Combined Chart: Fruits + Inputs -->
    <div class="chart-card full-width">
      <h3 class="chart-title">Phân bố Trái cây & Sử dụng Vật tư</h3>
      <div class="chart-container" style="height: 400px">
        <v-chart :option="fruitInputOption" :loading="chartsLoading" autoresize />
      </div>
    </div>

    <!-- Data Tables -->
    <div class="tables-grid">
      <!-- Top Owners Table -->
      <div class="table-card">
        <h3 class="table-title">🏆 Top Chủ sở hữu</h3>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Tên</th>
                <th>Email</th>
                <th>Số vùng</th>
                <th>Tổng diện tích (ha)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="owner in topOwners" :key="owner.user_id">
                <td>{{ owner.username }}</td>
                <td>{{ owner.email }}</td>
                <td>{{ owner.farm_count }}</td>
                <td>{{ owner.total_area.toFixed(2) }}</td>
              </tr>
              <tr v-if="topOwners.length === 0 && !loading">
                <td colspan="4" class="text-center">Chưa có dữ liệu</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Revoked Alerts Table -->
      <div class="table-card">
        <h3 class="table-title">🚨 Danh sách Mã vùng Cảnh báo Đã xử lý</h3>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Mã vùng</th>
                <th>Tên vùng</th>
                <th>Loại cảnh báo</th>
                <th>Mức độ</th>
                <th>Ngày xử lý</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in revokedAlerts" :key="item.ma_vung + item.ngay_tao">
                <td><strong>{{ item.ma_vung }}</strong></td>
                <td>{{ item.ten_vung }}</td>
                <td>{{ formatAlertType(item.loai_bao_dong) }}</td>
                <td>
                  <span :class="getSeverityBadge(item.muc_do)">{{ formatSeverity(item.muc_do) }}</span>
                </td>
                <td>{{ item.ngay_tao ? new Date(item.ngay_tao).toLocaleDateString('vi-VN') : 'N/A' }}</td>
              </tr>
              <tr v-if="revokedAlerts.length === 0 && !loading">
                <td colspan="5" class="text-center">Chưa có cảnh báo đã xử lý</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import L from 'leaflet'

import KPICard from '../components/dashboard/KPICard.vue'
import { analyticsService } from '../services/analyticsService'
import api from '../services/api'
import { useMap } from '../composables/useMap'
import { farmService } from '../services/farmService'
import { useAuth } from '../composables/useAuth'

// Get current user for province display
const { user } = useAuth()


// Register ECharts components
use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// State
const loading = ref(false)
const chartsLoading = ref(false)
const kpiData = ref({
  totalFarms: 0,
  totalArea: 0,
  activeSeasons: 0,
  totalFarmers: 0
})
const alertData = ref({
  total: 0,
  unresolved: 0
})
const marketData = ref([])
const inputUsageData = ref({ labels: [], series: [] })
const topOwners = ref([])
const harvestSchedule = ref([])

// New chart data
const cropMarketData = ref({ markets: [], series: [] })
const fruitInputData = ref({ fruits: [], fruit_counts: [], fertilizer_usage: [], pesticide_usage: [] })
const fertilizerUsageData = ref([])
const pesticideUsageData = ref([])
const revokedAlerts = ref([])
const cropsByFarmData = ref([])
const categorizedInputData = ref({ fertilizer_by_type: [], pesticide_by_type: [] })

// Layer and interaction state
const layers = ref({
  farms: true,
  markets: false,
  fertilizer: false,
  pesticide: false
})

// Filter state
const selectedProvince = ref(null)
const provinceFarms = ref([])
const selectedFarm = ref(null)
const farmsData = ref([])  // Farms with layer data (fertilizer/pesticide usage)
const allFarms = ref([])   // All farms for filtering
const filterActive = ref(false)  // Track if any filter is active
const chartFilters = ref({
  crop: null,
  market: null,
  fertilizer: null,
  pesticide: null
})

// Computed filtered data based on selection
const filteredFarms = computed(() => {
  let result = allFarms.value
  
  // Farm-level filter takes priority
  if (selectedFarm.value) {
    return [selectedFarm.value]
  }
  
  // Province-level filter
  if (selectedProvince.value) {
    result = result.filter(farm => farm.tinh_name === selectedProvince.value)
  }
  
  // Chart filters: Crop type
  if (chartFilters.value.crop) {
    result = result.filter(farm => {
      return farm.cay_trong?.ten_cay === chartFilters.value.crop
    })
  }
  
  // Chart filters: Export market
  if (chartFilters.value.market) {
    result = result.filter(farm => {
      return farm.thi_truong_xuat_khau === chartFilters.value.market
    })
  }
  
  // Chart filters: Fertilizer type
  if (chartFilters.value.fertilizer) {
    result = result.filter(farm => {
      return farm.phan_bon?.ten_phan_bon === chartFilters.value.fertilizer
    })
  }
  
  // Chart filters: Pesticide type
  if (chartFilters.value.pesticide) {
    result = result.filter(farm => {
      return farm.thuoc_bvtv?.ten_thuoc === chartFilters.value.pesticide
    })
  }
  
  return result
})

// Computed KPI data based on filtered farms
const computedKPIData = computed(() => {
  const farms = filteredFarms.value
  
  return {
    totalFarms: farms.length,
    totalArea: farms.reduce((sum, f) => sum + (parseFloat(f.dien_tich) || 0), 0).toFixed(2),
    activeSeasons: farms.reduce((sum, f) => sum + (f.active_seasons || 0), 0),
    totalFarmers: farms.reduce((sum, f) => sum + (parseInt(f.nong_dan_count) || 0), 0)
  }
})

// ECharts Options
const cropDistributionOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 10,
    data: ['Sầu riêng', 'Lúa', 'Xoài', 'Cà phê', 'Khác']
  },
  series: [
    {
      name: 'Cây trồng',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: [
        { value: 335, name: 'Sầu riêng', itemStyle: { color: '#667eea' } },
        { value: 310, name: 'Lúa', itemStyle: { color: '#10b981' } },
        { value: 234, name: 'Xoài', itemStyle: { color: '#f59e0b' } },
        { value: 135, name: 'Cà phê', itemStyle: { color: '#ef4444' } },
        { value: 148, name: 'Khác', itemStyle: { color: '#6b7280' } }
      ]
    }
  ]
}))

const marketDistributionOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: marketData.value.map(m => m.market)
  },
  yAxis: {
    type: 'value',
    name: 'Số vùng trồng'
  },
  series: [
    {
      name: 'Số vùng',
      type: 'bar',
      data: marketData.value.map(m => m.farm_count),
      itemStyle: {
        color: '#3b82f6',
        borderRadius: [8, 8, 0, 0]
      },
      barWidth: '60%'
    }
  ]
}))

const inputUsageOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['Phân bón', 'Thuốc BVTV']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: inputUsageData.value.labels
  },
  yAxis: {
    type: 'value',
    name: 'Số lần sử dụng'
  },
  series: inputUsageData.value.series.map((s, idx) => ({
    name: s.name,
    type: 'line',
    smooth: true,
    data: s.data,
    itemStyle: {
      color: idx === 0 ? '#10b981' : '#ef4444'
    },
    areaStyle: {
      opacity: 0.2
    }
  }))
}))


// ========== New Advanced Charts ==========

// Computed chart data based on filtered farms
const filteredCropsByFarmData = computed(() => {
  const farms = filteredFarms.value
  if (farms.length === 0) return []
  
  // Group by crop type (cay_trong name)
  const cropCounts = {}
  farms.forEach(farm => {
    // If cay_trong is object, use ten_cay. If string/id (legacy), handle gracefully
    let cropName = 'Khác'
    if (farm.cay_trong && typeof farm.cay_trong === 'object') {
      cropName = farm.cay_trong.ten_cay || 'Khác'
    } else if (farm.cay_trong_name) {
       cropName = farm.cay_trong_name
    }
    
    cropCounts[cropName] = (cropCounts[cropName] || 0) + 1
  })
  
  return Object.entries(cropCounts)
    .sort((a, b) => b[1] - a[1]) // Sort by count desc
    .map(([name, value]) => ({
      name,
      value
    }))
})

const cropsByFarmOption = computed(() => ({
  tooltip: { 
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    formatter: '{b}: {c} vùng'
  },
  grid: {
    left: '15%',
    right: '10%',
    top: '10%',
    bottom: '5%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    name: 'Số lượng vùng',
    axisLabel: {
      fontSize: 12
    }
  },
  yAxis: {
    type: 'category',
    data: filteredCropsByFarmData.value.map(d => d.name),
    axisLabel: {
      fontSize: 12,
      interval: 0,
      formatter: (value) => {
        return value.length > 15 ? value.substring(0, 13) + '...' : value
      }
    }
  },
  series: [{
    name: 'Cây trồng',
    type: 'bar',
    data: filteredCropsByFarmData.value.length > 0 ? filteredCropsByFarmData.value.map(d => d.value) : [1],
    itemStyle: {
      color: (params) => {
        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
        return colors[params.dataIndex % colors.length]
      },
      borderRadius: [0, 4, 4, 0]
    },
    label: {
      show: true,
      position: 'right',
      formatter: '{c}',
      fontSize: 11
    },
    barWidth: '60%'
  }]
}))

// Computed filtered fertilizer usage based on current selection
const filteredFertilizerUsageData = computed(() => {
  const farms = filteredFarms.value
  if (farms.length === 0) return []
  
  // Aggregate fertilizer volume into ranges
  // Group by fertilizer type
  const counts = {}
  
  farms.forEach(farm => {
    let name = 'Chưa xác định'
    if (farm.phan_bon && typeof farm.phan_bon === 'object') {
       name = farm.phan_bon.ten_phan_bon || 'Chưa xác định'
    } else if (farm.fertilizer_volume > 0) {
       // Fallback for old data with volume but no type
       name = 'Khác' 
    } else {
       return // Skip if no fertilizer used
    }
    
    counts[name] = (counts[name] || 0) + 1
  })
  
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([name, value]) => ({ name, value }))
})

const fertilizerUsageOption = computed(() => ({
  tooltip: { 
    trigger: 'item', 
    formatter: '{b}: {c} vùng ({d}%)' 
  },
  legend: { 
    type: 'scroll',  // Enable scrollbar
    orient: 'vertical',
    right: '10%',  // Move to right
    top: '10%',
    bottom: '10%',
    textStyle: { 
      fontSize: 12,
      width: 150,  // Max width before wrapping
      overflow: 'break'  // Allow text to wrap
    },
    formatter: (name) => {
      const item = filteredFertilizerUsageData.value.find(d => d.name === name)
      return item ? `${name}: ${item.value}` : name
    }
  },
  grid: {
    left: '5%',
    right: '30%',
    top: '10%',
    bottom: '10%'
  },
  series: [{
    name: 'Phân bón', 
    type: 'pie', 
    center: ['40%', '50%'],  // Match chart 1
    radius: '60%',  // Match chart 1 (solid pie)
    label: {
      show: false
    },
    labelLine: {
      show: false
    },
    data: filteredFertilizerUsageData.value.length > 0 
      ? filteredFertilizerUsageData.value 
      : [{ value: 1, name: 'Không có dữ liệu' }],
    emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
  }]
}))

// Computed filtered pesticide usage based on current selection
const filteredPesticideUsageData = computed(() => {
  const farms = filteredFarms.value
  if (farms.length === 0) return []
  
  // Aggregate pesticide volume into ranges
  // Group by pesticide type
  const counts = {}
  
  farms.forEach(farm => {
    let name = 'Chưa xác định'
    if (farm.thuoc_bvtv && typeof farm.thuoc_bvtv === 'object') {
       name = farm.thuoc_bvtv.ten_thuoc || 'Chưa xác định'
    } else if (farm.pesticide_volume > 0) {
       // Fallback for old data
       name = 'Khác'
    } else {
       return // Skip if no pesticide used
    }
    
    counts[name] = (counts[name] || 0) + 1
  })
  
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([name, value]) => ({ name, value }))
})

const pesticideUsageOption = computed(() => ({
  tooltip: { 
    trigger: 'item', 
    formatter: '{b}: {c} vùng ({d}%)' 
  },
  legend: { 
    type: 'scroll',  // Enable scrollbar
    orient: 'vertical',
    right: '10%',  // Move to right
    top: '10%',
    bottom: '10%',
    textStyle: { 
      fontSize: 12,
      width: 150,  // Max width before wrapping
      overflow: 'break'  // Allow text to wrap
    },
    formatter: (name) => {
      const item = filteredPesticideUsageData.value.find(d => d.name === name)
      return item ? `${name}: ${item.value}` : name
    }
  },
  grid: {
    left: '5%',
    right: '30%',
    top: '10%',
    bottom: '10%'
  },
  series: [{
    name: 'Thuốc BVTV', 
    type: 'pie', 
    center: ['40%', '50%'],  // Match chart 1
    radius: '60%',  // Match chart 1 (solid pie)
    label: {
      show: false
    },
    labelLine: {
      show: false
    },
    data: filteredPesticideUsageData.value.length > 0 
      ? filteredPesticideUsageData.value 
      : [{ value: 1, name: 'Không có dữ liệu' }],
    emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
  }]
}))

// Computed fertilizer volume data aggregated by type
// Use categorized backend data - Organic vs Inorganic
const filteredFertilizerVolumeData = computed(() => {
  if (!categorizedInputData.value.fertilizer_by_type) return []
  return categorizedInputData.value.fertilizer_by_type.map(item => ({
    type: item.type,
    value: item.value
  }))
})

const fertilizerVolumeOption = computed(() => ({
  tooltip: { 
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    formatter: '{b}: {c} kg'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '5%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: filteredFertilizerVolumeData.value.map(d => d.type),
    axisLabel: { 
      fontSize: 14,
      fontWeight: '500'
    }
  },
  yAxis: {
    type: 'value',
    name: 'Khối lượng (kg)',
    axisLabel: { formatter: '{value}' }
  },
  series: [{
    name: 'Phân bón',
    type: 'bar',
    data: filteredFertilizerVolumeData.value.map(d => d.value),
    itemStyle: {
      color: (params) => {
        // Hữu cơ = green, Vô cơ = blue
        return params.name === 'Hữu cơ' ? '#10b981' : '#3b82f6'
      },
      borderRadius: [4, 4, 0, 0]
    },
    label: {
      show: true,
      position: 'top',
      formatter: '{c} kg',
      fontSize: 11
    }
  }]
}))

// Use categorized backend data - by pesticide types
const filteredPesticideVolumeData = computed(() => {
  if (!categorizedInputData.value.pesticide_by_type) return []
  return categorizedInputData.value.pesticide_by_type.map(item => ({
    type: item.type,
    value: item.value
  }))
})

const pesticideVolumeOption = computed(() => ({
  tooltip: { 
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    formatter: '{b}: {c} lít'
  },
  grid: {
    left: '5%',
    right: '5%',
    bottom: '5%',
    top: '5%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    name: 'Tổng lượng (lít)',
    axisLabel: { formatter: '{value}' }
  },
  yAxis: {
    type: 'category',
    data: filteredPesticideVolumeData.value.map(d => d.type),
    axisLabel: {
      fontSize: 12,
      interval: 0, // Show all labels
      formatter: (value) => {
        // Truncate long labels
        return value.length > 25 ? value.substring(0, 23) + '...' : value
      }
    }
  },
  series: [{
    name: 'Thuốc BVTV',
    type: 'bar',
    data: filteredPesticideVolumeData.value.map(d => d.value),
    itemStyle: {
      color: '#f59e0b',
      borderRadius: [0, 4, 4, 0]
    },
    label: {
      show: true,
      position: 'right',
      formatter: '{c} lít',
      fontSize: 11
    }
  }]
}))

// Compute Crop x Market data from filtered farms
const filteredCropMarketData = computed(() => {
  const farms = filteredFarms.value
  if (farms.length === 0) {
    return { markets: [], series: [] }
  }
  
  // Get unique markets and crops - extract crop names properly
  const markets = [...new Set(farms.map(f => f.thi_truong_xuat_khau || 'Khác'))].sort()
  
  // Extract crop names from objects
  const cropNames = farms.map(f => {
    if (f.cay_trong && typeof f.cay_trong === 'object') {
      return f.cay_trong.ten_cay || 'Khác'
    } else if (f.cay_trong_name) {
      return f.cay_trong_name
    }
    return 'Khác'
  })
  const crops = [...new Set(cropNames)].sort()
  
  // Build series data for each crop
  const series = crops.map(cropName => {
    const data = markets.map(market => {
      return farms.filter(f => {
        let farmCropName = 'Khác'
        if (f.cay_trong && typeof f.cay_trong === 'object') {
          farmCropName = f.cay_trong.ten_cay || 'Khác'
        } else if (f.cay_trong_name) {
          farmCropName = f.cay_trong_name
        }
        
        return farmCropName === cropName && 
               (f.thi_truong_xuat_khau || 'Khác') === market
      }).length
    })
    
    return {
      name: cropName,
      type: 'line',
      data: data,
      smooth: true
    }
  })
  
  return { markets, series }
})

const cropMarketOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { 
    type: 'scroll',  // Enable scrollbar
    data: filteredCropMarketData.value.series.map(s => s.name), 
    bottom: '5%',
    textStyle: { fontSize: 12 }
  },
  grid: { left: '5%', right: '5%', bottom: '15%', top: '5%', containLabel: true },
  xAxis: { 
    type: 'category', 
    boundaryGap: false, 
    data: filteredCropMarketData.value.markets 
  },
  yAxis: { type: 'value', name: 'Số vùng trồng' },
  series: filteredCropMarketData.value.series
}))

// Compute Fruit x Input data from filtered farms
const filteredFruitInputData = computed(() => {
  const farms = filteredFarms.value
  if (farms.length === 0) {
    return { fruits: [], fruit_counts: [], fertilizer_usage: [], pesticide_usage: [] }
  }
  
  // Group by crop type - extract crop name properly
  const cropStats = {}
  farms.forEach(farm => {
    let cropName = 'Khác'
    if (farm.cay_trong && typeof farm.cay_trong === 'object') {
      cropName = farm.cay_trong.ten_cay || 'Khác'
    } else if (farm.cay_trong_name) {
      cropName = farm.cay_trong_name
    }
    
    if (!cropStats[cropName]) {
      cropStats[cropName] = {
        count: 0,
        totalFertilizer: 0,
        totalPesticide: 0
      }
    }
    cropStats[cropName].count++
    cropStats[cropName].totalFertilizer += parseFloat(farm.fertilizer_volume) || 0
    cropStats[cropName].totalPesticide += parseFloat(farm.pesticide_volume) || 0
  })
  
  // Sort by count and get arrays
  const sortedCrops = Object.entries(cropStats)
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 10) // Top 10 crops
  
  return {
    fruits: sortedCrops.map(([crop]) => crop),
    fruit_counts: sortedCrops.map(([_, stats]) => stats.count),
    fertilizer_usage: sortedCrops.map(([_, stats]) => 
      Math.round(stats.totalFertilizer / stats.count)
    ),
    pesticide_usage: sortedCrops.map(([_, stats]) => 
      Math.round(stats.totalPesticide / stats.count)
    )
  }
})

const fruitInputOption = computed(() => ({
  tooltip: { 
    trigger: 'axis', 
    axisPointer: { type: 'cross', crossStyle: { color: '#999' } } 
  },
  legend: { 
    type: 'scroll',  // Enable scrollbar
    data: ['Số vùng trồng', 'Phân bón TB (kg)', 'Thuốc BVTV TB (kg)'], 
    bottom: '5%',
    textStyle: { fontSize: 12 }
  },
  grid: { left: '5%', right: '5%', bottom: '15%', top: '5%', containLabel: true },
  xAxis: { 
    type: 'category', 
    data: filteredFruitInputData.value.fruits, 
    axisPointer: { type: 'shadow' } 
  },
  yAxis: [
    { type: 'value', name: 'Số vùng', axisLabel: { formatter: '{value}' } },
    { type: 'value', name: 'Vật tư (kg)', axisLabel: { formatter: '{value}' } }
  ],
  series: [
    { 
      name: 'Số vùng trồng', 
      type: 'bar', 
      data: filteredFruitInputData.value.fruit_counts, 
      itemStyle: { color: '#5470c6' } 
    },
    { 
      name: 'Phân bón TB (kg)', 
      type: 'line', 
      yAxisIndex: 1, 
      data: filteredFruitInputData.value.fertilizer_usage, 
      itemStyle: { color: '#91cc75' } 
    },
    { 
      name: 'Thuốc BVTV TB (kg)', 
      type: 'line', 
      yAxisIndex: 1, 
      data: filteredFruitInputData.value.pesticide_usage, 
      itemStyle: { color: '#fac858' } 
    }
  ]
}))

// Methods
const fetchKPIData = async () => {
  try {
    const response = await analyticsService.getKPIOverview()
    kpiData.value = response.data
  } catch (error) {
    console.error('Error fetching KPI data:', error)
  }
}

const fetchAlertData = async () => {
  try {
    const response = await analyticsService.getAlertKPI()
    alertData.value = response.data
  } catch (error) {
    console.error('Error fetching alert data:', error)
  }
}

const fetchMarketData = async () => {
  try {
    const response = await analyticsService.getMarketDistribution()
    marketData.value = response.data
  } catch (error) {
    console.error('Error fetching market data:', error)
  }
}

const fetchInputUsageData = async () => {
  try {
    const response = await analyticsService.getInputUsageTrends(6)
    inputUsageData.value = response.data
  } catch (error) {
    console.error('Error fetching input usage data:', error)
  }
}

const fetchTopOwners = async () => {
  try {
    const response = await analyticsService.getTopOwners(10)
    topOwners.value = response.data.data
  } catch (error) {
    console.error('Error fetching top owners:', error)
  }
}




const fetchFertilizerUsage = async () => {
  try {
    const response = await analyticsService.getInputUsageFrequency('fertilizer')
    fertilizerUsageData.value = response.data.data
  } catch (error) {
    console.log('Fertilizer data:', error.message)
  }
}

const fetchPesticideUsage = async () => {
  try {
    const response = await analyticsService.getInputUsageFrequency('pesticide')
    pesticideUsageData.value = response.data.data
  } catch (error) {
    console.log('Pesticide data:', error.message)
  }
}

const fetchCategorizedInputData = async () => {
  try {
    // Pass province and farm filters
    const provinceName = selectedProvince.value
    const farmId = selectedFarm.value?.id
    const response = await analyticsService.getCategorizedInputUsage(provinceName, farmId)
    categorizedInputData.value = response.data
  } catch (error) {
    console.error('Error fetching categorized input data:', error)
    categorizedInputData.value = { fertilizer_by_type: [], pesticide_by_type: [] }
  }
}

const fetchRevokedAlerts = async () => {
  try {
    const response = await analyticsService.getRevokedAlerts(20)
    revokedAlerts.value = response.data.data
  } catch (error) {
    console.error('Error fetching revoked alerts:', error)
  }
}

const fetchHarvestSchedule = async () => {
  try {
    const response = await analyticsService.getHarvestSchedule(30)
    harvestSchedule.value = response.data.data
  } catch (error) {
    console.error('Error fetching harvest schedule:', error)
  }
}


const formatAlertType = (type) => {
  const types = {
    benh_hai: 'Bệnh hại', thien_tai: 'Thiên tai',
    mua_kho: 'Mùa khô', suy_dinh_duong: 'Suy dinh dưỡng', khac: 'Khác'
  }
  return types[type] || type
}

const formatSeverity = (severity) => {
  const levels = {
    thap: 'Thấp', trung_binh: 'Trung bình', cao: 'Cao', rat_cao: 'Rất cao'
  }
  return levels[severity] || severity
}

const getSeverityBadge = (severity) => {
  const badges = {
    thap: 'badge badge-success', trung_binh: 'badge badge-info',
    cao: 'badge badge-warning', rat_cao: 'badge badge-error'
  }
  return badges[severity] || 'badge'
}

const handleChartClick = (chartType, event) => {
  const name = event.name
  if (!name) return
  
  console.log(`Chart clicked - Type: ${chartType}, Name: ${name}`)
  
  // Toggle filter: if same item clicked, clear it; otherwise set it
  if (chartFilters.value[chartType] === name) {
    chartFilters.value[chartType] = null
  } else {
    chartFilters.value[chartType] = name
  }
  
  // Update filter active state
  filterActive.value = selectedProvince.value !== null || 
    selectedFarm.value !== null ||
    Object.values(chartFilters.value).some(v => v !== null)
  
  console.log('Active filters:', {
    province: selectedProvince.value,
    farm: selectedFarm.value,
    charts: chartFilters.value
  })
}

// NEW: Layer and Interaction Methods
const toggleLayer = (layerName) => {
  console.log(`Toggle layer: ${layerName} = ${layers.value[layerName]}`)
  
  // Handle farm layer visibility toggle
  if (layerName === 'farms') {
    if (layers.value.farms) {
      // Show all farm markers (respecting current filters)
      const filteredIds = new Set(filteredFarms.value.map(f => f.id))
      farmMarkers.value.forEach(({ marker, farm }) => {
        if (filteredIds.has(farm.id)) {
          marker.addTo(map.value)
        }
      })
    } else {
      // Hide all farm markers
      farmMarkers.value.forEach(({ marker }) => {
        marker.remove()
      })
    }
  }
  
  // Update all marker styles based on active layers
  updateMarkerStyles()
}

// Handle farm marker click on map
const handleFarmClick = (farm) => {
  selectedFarm.value = farm
  selectedProvince.value = farm.tinh_name
  filterActive.value = true
  
  // Fetch farms in the same province
  fetchProvinceFarms(farm.tinh_name)
  
  console.log('Farm marker clicked:', farm)
}

// Handle farm click from the list (zoom to farm)
const handleFarmListClick = (farm) => {
  selectedFarm.value = farm
  filterActive.value = true
  
  // Zoom map to the farm location using Leaflet flyTo
  if (map.value && farm.latitude && farm.longitude) {
    map.value.flyTo([farm.latitude, farm.longitude], 13, {
      animate: true,
      duration: 1.5  // Duration in seconds for Leaflet
    })
  }
  
  console.log('Farm selected from list, zooming to:', farm)
}

// Handle province click on map
const handleProvinceClick = (provinceName) => {
  selectedProvince.value = provinceName
  selectedFarm.value = null  // Clear farm selection
  filterActive.value = true
  fetchProvinceFarms(provinceName)
}

// Fetch farms for a specific province
const fetchProvinceFarms = async (provinceName) => {
  try {
    const response = await analyticsService.getFarmsByProvince(provinceName)
    provinceFarms.value = response.data.farms
  } catch (error) {
    console.error('Error fetching province farms:', error)
    provinceFarms.value = []
  }
}

// Clear all filters
const clearFilter = () => {
  selectedProvince.value = null
  selectedFarm.value = null
  provinceFarms.value = []
  chartFilters.value = {
    crop: null,
    market: null,
    fertilizer: null,
    pesticide: null
  }
  filterActive.value = false
  
  // Reset map view to Vietnam using Leaflet flyTo
  if (map.value) {
    map.value.flyTo([14.0583, 108.2772], 5.5, {
      animate: true,
      duration: 1.5
    })
  }
  
  console.log('Filters cleared')
}

const fetchFarmsWithLayers = async () => {
  try {
    const response = await analyticsService.getFarmsWithLayers()
    farmsData.value = response.data.data
    return farmsData.value
  } catch (error) {
    console.error('Error fetching farms with layers:', error)
    return []
  }
}

// Generate farming journal demo data for all farms
const generateFarmingJournalData = (farms) => {
  const activities = ['Làm đất', 'Gieo trồng', 'Bón phân', 'Tưới nước', 'Kiểm tra sâu bệnh', 'Thu hoạch']
  const notes = [
    'Hoàn tất quá trình, đất đã sẵn sàng cho gieo trồng',
    'Điều kiện thời tiết tốt, phù hợp cho hoạt động',
    'Cần theo dõi thêm trong vài ngày tới',
    'Kết quả khả quan, tiếp tục theo kế hoạch',
    'Đã áp dụng đúng quy trình kỹ thuật',
    'Chất lượng đạt chuẩn, tiến độ đúng kế hoạch'
  ]
  
  return farms.map(farm => {
    // Generate 3-6 random activities per farm
    const numActivities = 3 + Math.floor(Math.random() * 4)
    const farmingJournal = []
    
    for (let i = 0; i < numActivities; i++) {
      // Random date within last 60 days
      const daysAgo = Math.floor(Math.random() * 60)
      const activityDate = new Date()
      activityDate.setDate(activityDate.getDate() - daysAgo)
      
      farmingJournal.push({
        id: `journal-${farm.id || farm.ma_vung}-${i}`,
        farm_id: farm.id || farm.ma_vung,
        date: activityDate.toISOString().split('T')[0],
        activity: activities[Math.floor(Math.random() * activities.length)],
        notes: notes[Math.floor(Math.random() * notes.length)],
        created_at: activityDate.toISOString()
      })
    }
    
    // Sort by date descending (newest first)
    farmingJournal.sort((a, b) => new Date(b.date) - new Date(a.date))
    
    return {
      ...farm,
      farming_journal: farmingJournal,
      recent_activities_count: farmingJournal.length
    }
  })
}

const refreshData = async () => {
  loading.value = true
  chartsLoading.value = true
  
  try {
    await Promise.all([
      fetchKPIData(), fetchAlertData(), fetchMarketData(),
      fetchInputUsageData(), fetchTopOwners(),
      fetchRevokedAlerts(),
      fetchCategorizedInputData(),
      fetchFertilizerUsage(), fetchPesticideUsage()
    ])
  } catch (error) {
    console.error('Error refreshing data:', error)
  } finally {
    loading.value = false
    chartsLoading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('vi-VN')
}

const getBadgeClass = (days) => {
  if (days <= 7) return 'badge-danger'
  if (days <= 14) return 'badge-warning'
  return 'badge-success'
}

// Map initialization
const { 
  initMap, 
  loadGeoJson,
  map
} = useMap('dashboard-map')

// Store farm markers for dynamic styling
const farmMarkers = ref([])

// Market color mapping
const getMarketColor = (market) => {
  const colors = {
    'Trung Quốc': '#ef4444',
    'USA': '#3b82f6',
    'Úc/NZ': '#10b981',
    'Úc': '#10b981',
    'New Zealand': '#10b981'
  }
  return colors[market] || '#9ca3af'
}

// Update marker styles based on active layers
const updateMarkerStyles = () => {
  farmMarkers.value.forEach(({ marker, farm }) => {
    // Base style (gray, normal opacity, normal size)
    let fillColor = '#9ca3af'  // Gray
    let fillOpacity = 0.6
    let radius = 6
    
    // Step 1: Determine base color from Markets layer or default gray
    if (layers.value.markets) {
      fillColor = getMarketColor(farm.thi_truong_xuat_khau)
    }
    
    // Step 2: Adjust opacity based on Fertilizer layer
    // If fertilizer layer is active, modulate the opacity based on fertilizer volume
    // Higher fertilizer volume = higher opacity (darker/more opaque)
    if (layers.value.fertilizer) {
      const maxVolume = Math.max(...farmsData.value.map(f => f.fertilizer_volume || 0))
      const volume = farm.fertilizer_volume || 0
      
      if (maxVolume > 0 && volume > 0) {
        // Calculate intensity (0 to 1)
        const intensity = volume / maxVolume
        
        // Map fertilizer intensity to opacity: 0.3 (light) to 0.95 (dark)
        fillOpacity = 0.3 + (intensity * 0.65)
      } else {
        // No fertilizer data - very low opacity (transparent)
        fillOpacity = 0.2
      }
    }
    
    // Step 3: Adjust size based on Pesticide layer
    if (layers.value.pesticide) {
      const maxVolume = Math.max(...farmsData.value.map(f => f.pesticide_volume || 0))
      const volume = farm.pesticide_volume || 0
      
      if (maxVolume > 0 && volume > 0) {
        // Scale radius from 5px (min) to 18px (max) for better visibility
        radius = 5 + (volume / maxVolume) * 13
      } else {
        radius = 5  // Minimum size for no data
      }
    }
    
    // Update marker style
    marker.setStyle({
      radius: radius,
      fillColor: fillColor,
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: fillOpacity
    })
  })
}

const initDashboardMap = async () => {
  try {
    // Initialize map centered on Vietnam
    await initMap([14.0583, 108.2772], 6)
    
    // Load province boundaries with click handler
    await loadGeoJson(
      '/data/63tinh-quandao.geojson',
      {
        color: '#2563eb',
        weight: 1,
        opacity: 0.5,
        fillColor: '#dbeafe',
        fillOpacity: 0.1
      },
      (feature, layer) => {
        const provinceName = feature.properties.NAME_1 || 'Unknown'
        
        // Add tooltip
        layer.bindTooltip(provinceName, {
          permanent: false,
          direction: 'center'
        })
        
        // Add click handler for province selection
        layer.on('click', () => {
          console.log('Province clicked:', provinceName)
          handleProvinceClick(provinceName)
        })
        
        // Add hover effects
        layer.on('mouseover', function() {
          this.setStyle({
            fillOpacity: 0.3,
            weight: 2
          })
        })
        
        layer.on('mouseout', function() {
          this.setStyle({
            fillOpacity: 0.1,
            weight: 1
          })
        })
      }
    )
    
    // Load farms data with usage information (max page_size is 100)
    const response = await farmService.getFarms({ page_size: 100 })
    const farms = response.data.items || []
    
    // Filter only farms with valid coordinates and prepare data
    const farmsWithData = farms
      .filter(farm => {
        // Only include farms with valid latitude and longitude
        if (!farm.latitude || !farm.longitude) return false
        const lat = parseFloat(farm.latitude)
        const lng = parseFloat(farm.longitude)
        // Basic validation: check if coordinates are valid numbers and within reasonable bounds
        return !isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0
      })
      .map(farm => ({
        ...farm,
        latitude: parseFloat(farm.latitude),
        longitude: parseFloat(farm.longitude),
        // Parse volume data as floats to handle backend returning strings
        fertilizer_volume: parseFloat(farm.fertilizer_volume) || 0,
        pesticide_volume: parseFloat(farm.pesticide_volume) || 0
      }))
    
    console.log(`Loaded ${farms.length} farms, ${farmsWithData.length} have valid coordinates`)
    
    // Add farming journal demo data to all farms
    const farmsWithJournals = generateFarmingJournalData(farmsWithData)
    
    // Store farms data globally for layer switching
    farmsData.value = farmsWithJournals
    allFarms.value = farmsWithJournals  // Populate allFarms for charts and filtering
    
    // Create markers for all farms (single layer, dynamic styling)
    farmMarkers.value = farmsWithJournals.map(farm => {
      const marker = L.circleMarker([farm.latitude, farm.longitude], {
        radius: 6,
        fillColor: '#9ca3af',  // Default gray
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.6
      }).addTo(map.value)
      
      // Popup content
      marker.bindPopup(`
        <div style="min-width: 200px">
          <h3 style="margin: 0 0 8px 0; color: #1f2937; font-size: 16px">${farm.ma_vung}</h3>
          <p style="margin: 4px 0; color: #6b7280">${farm.ten_vung || 'N/A'}</p>
          <p style="margin: 4px 0; font-size: 14px"><strong>Tỉnh:</strong> ${farm.tinh_name}</p>
          <p style="margin: 4px 0; font-size: 14px"><strong>Thị trường:</strong> ${farm.thi_truong_xuat_khau || 'N/A'}</p>
          <p style="margin: 4px 0; font-size: 14px"><strong>Phân bón:</strong> ${farm.fertilizer_volume.toFixed(1)} kg</p>
          <p style="margin: 4px 0; font-size: 14px"><strong>Thuốc BVTV:</strong> ${farm.pesticide_volume.toFixed(1)} lít</p>
        </div>
      `)
      
      // Click handler
      marker.on('click', () => handleFarmClick(farm))
      
      // Hover effects
      marker.on('mouseover', function() {
        this.setStyle({ weight: 3 })
      })
      
      marker.on('mouseout', function() {
        this.setStyle({ weight: 2 })
      })
      
      return { marker, farm }
    })
    
    console.log(`Created ${farmMarkers.value.length} farm markers`)
    
    // Force map to recalculate size after all layers are added
    setTimeout(() => {
      if (map.value) {
        map.value.invalidateSize()
        console.log('Map size invalidated after marker creation')
      }
    }, 300)
    
  } catch (error) {
    console.error('Failed to initialize dashboard map:', error)
  }
}

// Lifecycle
onMounted(async () => {
  await refreshData()
  await initDashboardMap()
})

// Watch for filter changes and update map markers reactively
watch([filteredFarms, selectedFarm, () => layers.value.farms], async ([newFilteredFarms, newSelectedFarm, farmsLayerEnabled]) => {
  if (!map.value || farmMarkers.value.length === 0) return
  
  // Hide all markers first
  farmMarkers.value.forEach(({ marker }) => {
    marker.remove()
  })
  
  // Only show markers if farms layer is enabled
  if (!farmsLayerEnabled) {
    console.log('Farms layer is disabled, hiding all farm markers')
    return
  }
  
  // Show markers only for filtered farms
  const filteredIds = new Set(newFilteredFarms.map(f => f.id))
  const markersToShow = farmMarkers.value.filter(({ farm }) => filteredIds.has(farm.id))
  
  markersToShow.forEach(({ marker, farm }) => {
    marker.addTo(map.value)
    
    // Highlight selected farm marker with special styling
    if (newSelectedFarm && newSelectedFarm.id === farm.id) {
      marker.setStyle({
        radius: 10,
        fillColor: '#3b82f6',  // Blue for selected farm
        weight: 3,
        fillOpacity: 0.9
      })
    } else {
      // Reset to default style based on active layers
      let fillColor = '#9ca3af'  // Default gray
      let fillOpacity = 0.6
      let radius = 6
      
      // Step 1: Determine base color from Markets layer or default gray
      if (layers.value.markets) {
        fillColor = getMarketColor(farm.thi_truong_xuat_khau)
      }
      
      // Step 2: Adjust opacity based on Fertilizer layer
      if (layers.value.fertilizer) {
        const maxVolume = Math.max(...newFilteredFarms.map(f => f.fertilizer_volume || 0))
        const volume = farm.fertilizer_volume || 0
        
        if (maxVolume > 0 && volume > 0) {
          const intensity = volume / maxVolume
          // Map fertilizer intensity to opacity: 0.3 (light) to 0.95 (dark)
          fillOpacity = 0.3 + (intensity * 0.65)
        } else {
          // No fertilizer data - very low opacity (transparent)
          fillOpacity = 0.2
        }
      }
      
      // Step 3: Adjust size based on Pesticide layer
      if (layers.value.pesticide) {
        const maxVolume = Math.max(...newFilteredFarms.map(f => f.pesticide_volume || 0))
        const volume = farm.pesticide_volume || 0
        
        if (maxVolume > 0 && volume > 0) {
          // Scale radius from 5px (min) to 18px (max)
          radius = 5 + (volume / maxVolume) * 13
        } else {
          radius = 5  // Minimum size for no data
        }
      }
      
      marker.setStyle({
        radius: radius,
        fillColor: fillColor,
        weight: 2,
        fillOpacity: fillOpacity
      })
    }
  })
  
  console.log(`Map updated: showing ${markersToShow.length} of ${farmMarkers.value.length} farms`)
}, { deep: true })

// Watch for province/farm selection changes and refetch categorized data
watch([selectedProvince, selectedFarm], async () => {
  console.log('Filter changed, refetching categorized data...')
  await fetchCategorizedInputData()
}, { immediate: false })
</script>

<style scoped>
.dashboard-view {
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

.province-indicator {
  margin-top: 0.5rem;
  font-size: 1rem;
  color: var(--primary-600);
  font-weight: 500;
}

.province-indicator strong {
  color: var(--primary-700);
  font-weight: 700;
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

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 2fr 3fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.right-column {
  display: flex;
  flex-direction: column;
}

/* Charts */
.chart-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-card.full-width {
  margin-bottom: 2rem;
}

.chart-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 1rem 0;
}

.chart-container {
  width: 100%;
}

/* Map Placeholder */
.map-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 100%;
}

.map-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-radius: 8px;
  border: 2px dashed #667eea;
  min-height: 400px;
}

.map-placeholder p {
  font-size: 1.5rem;
  margin: 0.5rem 0;
}

.map-hint {
  font-size: 1rem !important;
  color: #6b7280;
}

/* Tables */
.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 1.5rem;
}

.table-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.table-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 1rem 0;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f9fafb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
  font-size: 0.875rem;
}

.data-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
  color: #6b7280;
}

.data-table tr:hover {
  background: #f9fafb;
}

.text-center {
  text-align: center;
  color: #9ca3af;
  font-style: italic;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.badge-success {
  background: #dcfce7;
  color: #16a34a;
}

.badge-warning {
  background: #fef3c7;
  color: #d97706;
}

.badge-danger {
  background: #fee2e2;
  color: #dc2626;
}

/* Responsive */
@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .tables-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-view {
    padding: 1rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid-4 {
    grid-template-columns: 1fr;
  }
}

/* 4-Column Charts Grid */
.charts-grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 1280px) {
  .charts-grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* ========== New Map-Centric Layout ========== */

/* Map Section: 2/3 + 1/3 Grid */
.map-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.map-container-large {
  min-height: 600px;
}

.map-container-large .chart-card {
  display: flex;
  flex-direction: column;
}

.map-container-large #dashboard-map {
  flex: 1;
}

/* Sidebar */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Layer Controls */
.layer-controls {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.layer-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background 0.2s;
}

.layer-toggle:hover {
  background: #f3f4f6;
}

.layer-toggle input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.layer-legend {
  margin-left: 2rem;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 6px;
  font-size: 0.875rem;
}

.layer-legend div {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
}

.color-box {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 1px solid #e5e7eb;
}

/* Farm List */
.farm-list-card {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  max-height: 400px; /* Reduced height to match map */
  overflow: hidden;
}

.farm-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.province-badge {
  font-size: 0.85em;
  font-weight: normal;
  color: #6b7280;
  margin-left: 8px;
  padding: 2px 8px;
  background: #f3f4f6;
  border-radius: 12px;
}

.clear-filter-btn {
  padding: 0.5rem 1rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.clear-filter-btn:hover {
  background: #dc2626;
  transform: scale(1.05);
}

/* Active Filters Display */
.active-filters {
  padding: 0.75rem;
  background: #f3f4f6;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
  border-left: 3px solid;
}

.filter-badge.crop {
  border-left-color: #10b981;
}

.filter-badge.market {
  border-left-color: #3b82f6;
}

.filter-badge.fertilizer {
  border-left-color: #10b981;
}

.filter-badge.pesticide {
  border-left-color: #f59e0b;
}

.filter-label {
  font-weight: 600;
  color: #6b7280;
  white-space: nowrap;
}

.filter-value {
  color: #111827;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
}


.farm-list {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.farm-items {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Scrollbar styling */
.farm-items::-webkit-scrollbar {
  width: 8px;
}

.farm-items::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.farm-items::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.farm-items::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.farm-item {
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.farm-item:hover {
  background: #f3f4f6;
  transform: translateX(4px);
}

.farm-item.active {
  background: #dbeafe;
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
}

.farm-code {
  font-weight: 700;
  color: #1f2937;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.farm-name {
  color: #6b7280;
  font-size: 0.813rem;
  margin-bottom: 0.25rem;
}

.farm-market {
  color: #9ca3af;
  font-size: 0.75rem;
}

.empty-state {
  text-align: center;
  padding: 2rem 1rem;
  color: #9ca3af;
}

.empty-state p {
  line-height: 1.6;
}

/* Pie Charts Grid (3 columns) */
.pie-charts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

/* Bar Charts Grid (2 columns for fertilizer and pesticide usage) */
.usage-charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 1280px) {
  .map-section {
    grid-template-columns: 1fr;
  }
  
  .pie-charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .usage-charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .pie-charts-grid {
    grid-template-columns: 1fr;
  }
  
  .usage-charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
