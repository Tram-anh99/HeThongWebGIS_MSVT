<template>
  <div class="webgis-view">
    <div class="container mx-auto px-4 py-6">
      <h1 class="text-3xl font-bold mb-6">Bản đồ Vùng trồng</h1>
      
      <!-- Map Container -->
      <div class="card p-0 overflow-hidden">
        <div id="map" style="height: 600px; width: 100%;"></div>
      </div>
      
      <!-- Farm List -->
      <div class="mt-6">
        <h2 class="text-2xl font-bold mb-4">Danh sách Vùng trồng ({{ farms.length }})</h2>
        
        <div v-if="loading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p class="mt-4 text-gray-600">Đang tải dữ liệu...</p>
        </div>
        
        <div v-else-if="error" class="p-4 bg-red-100 border border-red-300 text-red-700 rounded-lg">
          {{ error }}
        </div>
        
        <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="farm in farms"
            :key="farm.id"
            class="card hover:shadow-lg transition cursor-pointer"
            @click="viewFarmOnMap(farm)"
          >
            <h3 class="font-bold text-lg mb-2">{{ farm.ten_vung }}</h3>
            <p class="text-sm text-gray-600 mb-1">
              <span class="font-medium">Mã vùng:</span> {{ farm.ma_vung }}
            </p>
            <p class="text-sm text-gray-600 mb-1">
              <span class="font-medium">Diện tích:</span> {{ farm.dien_tich }} ha
            </p>
            <p class="text-sm text-gray-600">
              <span class="font-medium">Địa điểm:</span> {{ farm.xa_name }}, {{ farm.huyen_name }}, {{ farm.tinh_name }}
            </p>
            
            <div class="mt-3 flex space-x-2">
              <button
                @click.stop="viewFarmOnMap(farm)"
                class="text-sm btn-primary flex-1"
                title="Xem vị trí trên bản đồ"
              >
                📍 Xem bản đồ
              </button>
              <router-link
                :to="`/trace/${farm.ma_vung}`"
                class="text-sm btn-secondary flex-1 text-center"
                @click.stop
              >
                🔍 Truy xuất
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- QR Code Modal -->
    <div
      v-if="showQRModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click="showQRModal = false"
    >
      <div class="card max-w-md w-full" @click.stop>
        <h2 class="text-2xl font-bold mb-4">QR Code - {{ selectedFarm?.ten_vung }}</h2>
        <div class="text-center">
          <img
            :src="qrCodeUrl"
            :alt="`QR Code ${selectedFarm?.ma_vung}`"
            class="mx-auto border-4 border-gray-200 rounded-lg"
          />
          <p class="mt-4 text-gray-600">
            Scan QR code để xem thông tin truy xuất nguồn gốc
          </p>
        </div>
        <button
          @click="showQRModal = false"
          class="mt-4 w-full btn-secondary"
        >
          Đóng
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMap } from '../composables/useMap'
import { farmService } from '../services/farmService'
import { qrService } from '../services/qrService'
import { getProvinceCoords } from '../utils/provinceCoordinates'

const { initMap, addMarkers, addCircleMarkers, clearMarkers, flyTo, loadGeoJson } = useMap('map')

const farms = ref([])
const loading = ref(false)
const error = ref('')
const provinceBoundaryLayer = ref(null)

const showQRModal = ref(false)
const selectedFarm = ref(null)

const qrCodeUrl = computed(() => {
  if (!selectedFarm.value) return ''
  return qrService.generateQR(selectedFarm.value.ma_vung)
})

/**
 * Fetch farms from API
 */
const fetchFarms = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await farmService.getFarms({ page_size: 100 })
    farms.value = response.data.items || []
    
    // Add markers to map
    displayFarmsOnMap()
  } catch (err) {
    error.value = 'Không thể tải danh sách vùng trồng'
    console.error('Fetch farms error:', err)
  } finally {
    loading.value = false
  }
}

/**
 * Display farms on map
 */
const displayFarmsOnMap = () => {
  clearMarkers()
  
  const markers = farms.value.map((farm) => {
    let lat, lng
    
    // Use farm's GPS coordinates if available, otherwise use province centroid
    if (farm.latitude && farm.longitude) {
      lat = parseFloat(farm.latitude)
      lng = parseFloat(farm.longitude)
    } else {
      // Fallback to province coordinates with random offset
      const [baseLat, baseLng] = getProvinceCoords(farm.tinh_name)
      lat = baseLat + (Math.random() - 0.5) * 0.1
      lng = baseLng + (Math.random() - 0.5) * 0.1
    }
    
    // Generate QR code URL for this farm
    const qrUrl = qrService.generateQR(farm.ma_vung)
    
    // Create popup content with farm info and QR code
    const popup = `
      <div class="farm-popup-content" style="min-width: 250px;">
        <h3 class="font-bold text-lg mb-2">${farm.ten_vung}</h3>
        <div class="space-y-1 mb-3">
          <p class="text-sm"><strong>Mã vùng:</strong> ${farm.ma_vung}</p>
          <p class="text-sm"><strong>Diện tích:</strong> ${farm.dien_tich || 'N/A'} ha</p>
          <p class="text-sm"><strong>Địa điểm:</strong> ${farm.xa_name}, ${farm.huyen_name}, ${farm.tinh_name}</p>
          ${farm.nguoi_dai_dien ? `<p class="text-sm"><strong>Người đại diện:</strong> ${farm.nguoi_dai_dien}</p>` : ''}
        </div>
        <div class="text-center border-t pt-3">
          <p class="text-xs text-gray-600 mb-2">Mã QR truy xuất nguồn gốc:</p>
          <img src="${qrUrl}" alt="QR Code" class="mx-auto" style="width: 120px; height: 120px; border: 2px solid #e5e7eb; border-radius: 4px;" />
          <p class="text-xs text-gray-500 mt-2">Quét mã để xem thông tin chi tiết</p>
        </div>
      </div>
    `
    
    return { lat, lng, popup }
  })
  
  // Use circle markers instead of icon markers
  addCircleMarkers(markers)
}


/**
 * View farm on map
 */
const viewFarmOnMap = (farm) => {
  // Get real coordinates for the farm's province
  const [lat, lng] = getProvinceCoords(farm.tinh_name)
  flyTo(lat, lng, 13)
}

/**
 * Load Vietnam province boundaries
 */
const loadProvinceBoundaries = async () => {
  // Province boundary style - optimized for performance
  const style = (feature) => ({
    color: '#2563eb',      // Blue border
    weight: 1,           // Reduced from 1.5 for better performance
    opacity: 0.6,        // Reduced from 0.7
    fillColor: '#dbeafe',  // Light blue fill
    fillOpacity: 0.05,   // Reduced from 0.15
    smoothFactor: 1.5    // Add smooth factor for rendering optimization
  })

  const onEachFeature = (feature, layer) => {
    // Use NAME_1 field from shapefile (Vietnamese province names)
    const provinceName = feature.properties.NAME_1 || feature.properties.name || 'Unknown'
    layer.bindTooltip(provinceName, {
      permanent: false,
      direction: 'center',
      className: 'province-label'
    })

    // Highlight on hover
    layer.on('mouseover', function() {
      this.setStyle({
        weight: 3,
        fillOpacity: 0.3
      })
    })

    layer.on('mouseout', function() {
      this.setStyle({
        weight: 1.5,
        fillOpacity: 0.15
      })
    })
  }

  try {
    provinceBoundaryLayer.value = await loadGeoJson(
      '/data/63tinh-quandao.geojson',
      style,
      onEachFeature
    )
    console.log('63 province boundaries loaded successfully')
  } catch (error) {
    console.error('Failed to load province boundaries:', error)
  }
}

/**
 * Show QR code modal
 */
const showQRCode = (farm) => {
  selectedFarm.value = farm
  showQRModal.value = true
}

onMounted(async () => {
  await initMap([14.0583, 108.2772], 6) // Vietnam center
  
  // Load province boundaries first (base layer)
  await loadProvinceBoundaries()
  
  // Additional safety resize after all layers loaded
  setTimeout(() => {
    const mapContainer = document.getElementById('map')
    if (mapContainer && mapContainer._leaflet_map) {
      mapContainer._leaflet_map.invalidateSize()
      console.log('Final safety invalidateSize called')
    }
  }, 1000)
  
  // Then load farms on top
  await fetchFarms()
})
</script>

<style>
/* Global styles for Leaflet map - NOT scoped */
#map {
  height: 600px !important;
  width: 100% !important;
  min-height: 600px;
  border-radius: 8px;
}

.leaflet-container {
  height: 600px !important;
  width: 100% !important;
  border-radius: 8px;
  /* Enable GPU acceleration for smoother rendering */
  transform: translateZ(0);
  will-change: transform;
}
</style>

<style scoped>
/* Province label styling */
:deep(.province-label) {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #2563eb;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 12px;
  font-weight: 500;
  color: #1e40af;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Farm popup styling */
:deep(.farm-popup .leaflet-popup-content-wrapper) {
  border-radius: 8px;
  padding: 0;
}

:deep(.farm-popup .leaflet-popup-content) {
  margin: 12px;
  width: auto !important;
}

:deep(.farm-popup-content) {
  font-family: system-ui, -apple-system, sans-serif;
}

:deep(.farm-popup-content h3) {
  color: #1f2937;
  margin-bottom: 0.5rem;
}

:deep(.farm-popup-content strong) {
  color: #374151;
}

:deep(.farm-popup-content .border-t) {
  border-top: 1px solid #e5e7eb;
  padding-top: 0.75rem;
  margin-top: 0.75rem;
}

/* Smooth transitions for layer interactions */
:deep(.leaflet-interactive) {
  transition: all 0.2s ease;
}

/* Improve tile loading */
:deep(.leaflet-tile) {
  transform: translateZ(0);
}
</style>
