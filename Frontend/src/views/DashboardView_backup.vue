<template>
  <div class="dashboard-view">
    <!-- Header -->
    <div class="dashboard-header">
      <h1 class="dashboard-title">Bảng điều khiển Admin</h1>
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
        :value="kpiData.totalFarms"
        :loading="loading"
        icon="🌾"
        theme="primary"
        subtitle="vùng"
      />
      <KPICard
        title="Tổng diện tích"
        :value="kpiData.totalArea"
        :loading="loading"
        icon="📏"
        theme="success"
        subtitle="ha"
      />
      <KPICard
        title="Số vụ mùa đang hoạt động"
        :value="kpiData.activeSeasons"
        :loading="loading"
        icon="🌱"
        theme="info"
        subtitle="vụ"
      />
      <KPICard
        title="Cảnh báo chưa xử lý"
        :value="alertData.unresolved"
        :loading="loading"
        icon="⚠️"
        theme="warning"
        subtitle="cảnh báo"
      />
    </div>

    <!-- Chart Grid 1: 4 Columns -->
    <div class="charts-grid-4">
      <!-- Pie: Crops by Farm -->
      <div class="chart-card">
        <h3 class="chart-title">Cây trồng theo Mã vùng</h3>
        <div class="chart-container" style="height: 280px">
          <v-chart :option="cropsByFarmOption" :loading="chartsLoading" autoresize @click="handleChartClick('crops', $event)" />
        </div>
      </div>

      <!-- Pie: Fertilizer Usage -->
      <div class="chart-card">
        <h3 class="chart-title">Tỷ lệ Phân bón</h3>
        <div class="chart-container" style="height: 280px">
          <v-chart :option="fertilizerUsageOption" :loading="chartsLoading" autoresize />
        </div>
      </div>

      <!-- Pie: Pesticide Usage -->
      <div class="chart-card">
        <h3 class="chart-title">Tỷ lệ Thuốc BVTV</h3>
        <div class="chart-container" style="height: 280px">
          <v-chart :option="pesticideUsageOption" :loading="chartsLoading" autoresize />
        </div>
      </div>

      <!-- Map (Reduced Height) -->
      <div class="chart-card">
        <h3 class="chart-title">Bản đồ</h3>
        <div id="dashboard-map" style="height: 280px; width: 100%;"></div>
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

    <!-- Original Market Bar Chart -->
    <div class="chart-card full-width">
      <h3 class="chart-title">Phân bố Thị trường Xuất khẩu</h3>
      <div class="chart-container" style="height: 300px">
        <v-chart :option="marketDistributionOption" :loading="chartsLoading" autoresize />
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
import { ref, onMounted, computed } from 'vue'
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

import KPICard from '../components/dashboard/KPICard.vue'
import { analyticsService } from '../services/analyticsService'
import { useMap } from '../composables/useMap'
import { farmService } from '../services/farmService'

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

const fetchHarvestSchedule = async () => {
  try {
    const response = await analyticsService.getHarvestSchedule(30)
    harvestSchedule.value = response.data.data
  } catch (error) {
    console.error('Error fetching harvest schedule:', error)
  }
}

const refreshData = async () => {
  loading.value = true
  chartsLoading.value = true
  
  await Promise.all([
    fetchKPIData(),
    fetchAlertData(),
    fetchMarketData(),
    fetchInputUsageData(),
    fetchTopOwners(),
    fetchHarvestSchedule()
  ])
  
  loading.value = false
  chartsLoading.value = false
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
const { initMap, addCircleMarkers, loadGeoJson } = useMap('dashboard-map')

const initDashboardMap = async () => {
  try {
    // Initialize map centered on Vietnam
    await initMap([14.0583, 108.2772], 6)
    
    // Load province boundaries
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
        layer.bindTooltip(provinceName, {
          permanent: false,
          direction: 'center'
        })
      }
    )
    
    // Load farms and add markers
    const response = await farmService.getFarms({ page_size: 100 })
    const farms = response.data.items || []
    
    const markers = farms.map(farm => {
      let lat, lng
      
      if (farm.latitude && farm.longitude) {
        lat = parseFloat(farm.latitude)
        lng = parseFloat(farm.longitude)
      } else {
        // Use Vietnam center with random offset
        lat = 14.0583 + (Math.random() - 0.5) * 10
        lng = 108.2772 + (Math.random() - 0.5) * 10
      }
      
      const popup = `
        <div style="min-width: 200px;">
          <h4 style="margin: 0 0 8px 0; font-weight: 600;">${farm.ten_vung}</h4>
          <p style="margin: 4px 0; font-size: 13px;"><strong>Mã:</strong> ${farm.ma_vung}</p>
          <p style="margin: 4px 0; font-size: 13px;"><strong>Diện tích:</strong> ${farm.dien_tich || 'N/A'} ha</p>
        </div>
      `
      
      return { lat, lng, popup }
    })
    
    addCircleMarkers(markers)
  } catch (error) {
    console.error('Failed to initialize dashboard map:', error)
  }
}

// Lifecycle
onMounted(async () => {
  await refreshData()
  await initDashboardMap()
})
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
  align-items: center;
  margin-bottom: 2rem;
}

.dashboard-title {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
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
}
</style>
