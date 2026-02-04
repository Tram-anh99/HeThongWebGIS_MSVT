/**
 * useMap Composable
 * Quản lý Leaflet map logic
 */
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import L from 'leaflet'

// Fix Leaflet default icon paths
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

export function useMap(mapContainerId) {
    const map = ref(null)
    const markers = ref([])

    /**
     * Khởi tạo map
     */
    const initMap = async (center = [14.0583, 108.2772], zoom = 6) => {
        if (!map.value) {
            map.value = L.map(mapContainerId).setView(center, zoom)

            // Store map reference on DOM element for external access
            const container = document.getElementById(mapContainerId)
            if (container) {
                container._leaflet_map = map.value
            }

            // Add tile layer
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(map.value)

            // Fix rendering issue - force layout recalculation then invalidate size
            await nextTick()

            // Dispatch resize event to force browser to complete layout calculation
            window.dispatchEvent(new Event('resize'))

            // Use double RAF to ensure invalidateSize runs AFTER paint cycle
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    if (map.value) {
                        map.value.invalidateSize()
                        console.log('Map invalidateSize called after RAF')
                    }
                })
            })
        }

        return map.value
    }

    /**
     * Thêm marker
     */
    const addMarker = (lat, lng, popupContent = '') => {
        if (!map.value) return null

        const marker = L.marker([lat, lng]).addTo(map.value)

        if (popupContent) {
            marker.bindPopup(popupContent)
        }

        markers.value.push(marker)
        return marker
    }

    /**
     * Thêm nhiều markers
     */
    const addMarkers = (locations) => {
        locations.forEach(loc => {
            addMarker(loc.lat, loc.lng, loc.popup)
        })

        // Fit bounds to show all markers
        if (markers.value.length > 0) {
            const group = L.featureGroup(markers.value)
            map.value.fitBounds(group.getBounds().pad(0.1))
        }
    }

    /**
     * Xóa tất cả markers
     */
    const clearMarkers = () => {
        markers.value.forEach(marker => {
            map.value.removeLayer(marker)
        })
        markers.value = []
    }

    /**
     * Thêm circle markers (điểm tròn thay vì icon)
     * Dùng cho hiển thị các vùng trồng trên bản đồ
     */
    const addCircleMarkers = (locations) => {
        if (!map.value) return

        locations.forEach(loc => {
            // Create circle marker (điểm tròn)
            const circleMarker = L.circleMarker([loc.lat, loc.lng], {
                radius: 8,              // Kích thước điểm
                fillColor: '#3b82f6',   // Màu xanh dương
                color: '#ffffff',       // Viền trắng
                weight: 2,              // Độ dày viền
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map.value)

            // Bind popup with farm info
            if (loc.popup) {
                circleMarker.bindPopup(loc.popup, {
                    maxWidth: 300,
                    className: 'farm-popup'
                })
            }

            // Hover effects
            circleMarker.on('mouseover', function () {
                this.setStyle({
                    radius: 10,
                    fillOpacity: 1
                })
            })

            circleMarker.on('mouseout', function () {
                this.setStyle({
                    radius: 8,
                    fillOpacity: 0.8
                })
            })

            // Store click handler if provided
            if (loc.onClick) {
                circleMarker.on('click', loc.onClick)
            }

            markers.value.push(circleMarker)
        })

        // Fit bounds to show all markers
        if (markers.value.length > 0) {
            const group = L.featureGroup(markers.value)
            map.value.fitBounds(group.getBounds().pad(0.1))
        }
    }

    /**
     * Fly to location
     */
    const flyTo = (lat, lng, zoom = 13) => {
        if (map.value) {
            map.value.flyTo([lat, lng], zoom, {
                duration: 1.5
            })
        }
    }

    /**
     * Cleanup
     */
    onUnmounted(() => {
        if (map.value) {
            map.value.remove()
            map.value = null
        }
    })

    // GeoJSON layers
    const geoJsonLayers = ref([])

    /**
     * Add GeoJSON layer
     */
    const addGeoJsonLayer = (geojsonData, style = {}, onEachFeature = null) => {
        if (!map.value) return null

        const defaultStyle = {
            color: '#2563eb',
            weight: 2,
            opacity: 0.6,
            fillColor: '#dbeafe',
            fillOpacity: 0.1
        }

        const layer = L.geoJSON(geojsonData, {
            style: { ...defaultStyle, ...style },
            onEachFeature: onEachFeature
        }).addTo(map.value)

        geoJsonLayers.value.push(layer)
        return layer
    }

    /**
     * Load GeoJSON from URL
     */
    const loadGeoJson = async (url, style = {}, onEachFeature = null) => {
        try {
            const response = await fetch(url)
            const data = await response.json()
            return addGeoJsonLayer(data, style, onEachFeature)
        } catch (error) {
            console.error('Failed to load GeoJSON:', error)
            return null
        }
    }

    /**
     * Clear all GeoJSON layers
     */
    const clearGeoJsonLayers = () => {
        geoJsonLayers.value.forEach(layer => {
            map.value.removeLayer(layer)
        })
        geoJsonLayers.value = []
    }

    // ========== LAYER GROUPS FOR INTERACTIVE DASHBOARD ==========
    const layerGroups = ref({
        farms: null,
        markets: null,
        fertilizer: null,
        pesticide: null,
        provinces: null
    })

    /**
     * Create layer group for farms (default view)
     */
    const createFarmsLayer = (farms, onFarmClick = null) => {
        if (layerGroups.value.farms) {
            map.value.removeLayer(layerGroups.value.farms)
        }

        const farmMarkers = farms.map(farm => {
            const marker = L.circleMarker([farm.latitude, farm.longitude], {
                radius: 8,
                fillColor: '#3b82f6',
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            })

            marker.bindPopup(`
                <div style="min-width: 200px">
                    <h3 style="margin: 0 0 8px 0; color: #1f2937; font-size: 16px">${farm.ma_vung}</h3>
                    <p style="margin: 4px 0; color: #6b7280">${farm.ten_vung || 'N/A'}</p>
                    <p style="margin: 4px 0; font-size: 14px"><strong>Tỉnh:</strong> ${farm.tinh_name}</p>
                    <p style="margin: 4px 0; font-size: 14px"><strong>Thị trường:</strong> ${farm.thi_truong_xuat_khau || 'N/A'}</p>
                </div>
            `)

            if (onFarmClick) {
                marker.on('click', () => onFarmClick(farm))
            }

            return marker
        })

        layerGroups.value.farms = L.layerGroup(farmMarkers)
        return layerGroups.value.farms
    }

    /**
     * Create layer group for markets (color-coded)
     */
    const createMarketsLayer = (farms, onFarmClick = null) => {
        if (layerGroups.value.markets) {
            map.value.removeLayer(layerGroups.value.markets)
        }

        const marketColors = {
            'Trung Quốc': '#ef4444',
            'USA': '#3b82f6',
            'Úc/NZ': '#10b981',
            'Úc': '#10b981',
            'New Zealand': '#10b981'
        }

        const marketMarkers = farms.map(farm => {
            const color = marketColors[farm.thi_truong_xuat_khau] || '#9ca3af'

            const marker = L.circleMarker([farm.latitude, farm.longitude], {
                radius: 8,
                fillColor: color,
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            })

            marker.bindPopup(`
                <div style="min-width: 200px">
                    <h3 style="margin: 0 0 8px 0">${farm.ma_vung}</h3>
                    <p style="margin: 4px 0"><strong>Thị trường:</strong> 
                        <span style="color: ${color}; font-weight: bold">${farm.thi_truong_xuat_khau || 'Khác'}</span>
                    </p>
                </div>
            `)

            if (onFarmClick) {
                marker.on('click', () => onFarmClick(farm))
            }

            return marker
        })

        layerGroups.value.markets = L.layerGroup(marketMarkers)
        return layerGroups.value.markets
    }

    /**
     * Create layer group for fertilizer usage (opacity-based)
     */
    const createFertilizerLayer = (farmsWithUsage, onFarmClick = null) => {
        if (layerGroups.value.fertilizer) {
            map.value.removeLayer(layerGroups.value.fertilizer)
        }

        const maxUsage = Math.max(...farmsWithUsage.map(f => f.fertilizer_usage || 0).filter(v => v > 0)) || 1

        const fertilizerMarkers = farmsWithUsage.map(farm => {
            const usage = farm.fertilizer_usage || 0
            const opacity = usage > 0 ? 0.3 + (usage / maxUsage) * 0.7 : 0.3

            const marker = L.circleMarker([farm.latitude, farm.longitude], {
                radius: 8,
                fillColor: '#10b981',
                color: '#ffffff',
                weight: 1,
                opacity: 1,
                fillOpacity: opacity
            })

            marker.bindPopup(`
                <div style="min-width: 200px">
                    <h3 style="margin: 0 0 8px 0">${farm.ma_vung}</h3>
                    <p style="margin: 4px 0"><strong>Phân bón:</strong> ${usage.toFixed(1)} lượt sử dụng</p>
                    <p style="margin: 4px 0; font-size: 12px; color: #6b7280">Độ đậm: ${(opacity * 100).toFixed(0)}%</p>
                </div>
            `)

            if (onFarmClick) {
                marker.on('click', () => onFarmClick(farm))
            }

            return marker
        })

        layerGroups.value.fertilizer = L.layerGroup(fertilizerMarkers)
        return layerGroups.value.fertilizer
    }

    /**
     * Create layer group for pesticide usage (size-based)
     */
    const createPesticideLayer = (farmsWithUsage, onFarmClick = null) => {
        if (layerGroups.value.pesticide) {
            map.value.removeLayer(layerGroups.value.pesticide)
        }

        const maxUsage = Math.max(...farmsWithUsage.map(f => f.pesticide_usage || 0).filter(v => v > 0)) || 1

        const pesticideMarkers = farmsWithUsage.map(farm => {
            const usage = farm.pesticide_usage || 0
            const radius = usage > 0 ? 5 + (usage / maxUsage) * 10 : 5

            const marker = L.circleMarker([farm.latitude, farm.longitude], {
                radius: radius,
                fillColor: '#f59e0b',
                color: '#ffffff',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.6
            })

            marker.bindPopup(`
                <div style="min-width: 200px">
                    <h3 style="margin: 0 0 8px 0">${farm.ma_vung}</h3>
                    <p style="margin: 4px 0"><strong>Thuốc BVTV:</strong> ${usage.toFixed(1)} lượt sử dụng</p>
                    <p style="margin: 4px 0; font-size: 12px; color: #6b7280">Kích thước: ${radius.toFixed(1)}px</p>
                </div>
            `)

            if (onFarmClick) {
                marker.on('click', () => onFarmClick(farm))
            }

            return marker
        })

        layerGroups.value.pesticide = L.layerGroup(pesticideMarkers)
        return layerGroups.value.pesticide
    }

    /**
     * Load province boundaries and add click handlers
     */
    const loadProvinceBoundaries = async (onProvinceClick = null) => {
        try {
            // Load Vietnam province GeoJSON
            const response = await fetch('/data/vietnam-provinces.json')
            const data = await response.json()

            if (layerGroups.value.provinces) {
                map.value.removeLayer(layerGroups.value.provinces)
            }

            layerGroups.value.provinces = L.geoJSON(data, {
                style: {
                    color: '#2563eb',
                    weight: 2,
                    opacity: 0.4,
                    fillColor: '#dbeafe',
                    fillOpacity: 0.05
                },
                onEachFeature: (feature, layer) => {
                    const provinceName = feature.properties.name || feature.properties.NAME_1

                    layer.on('mouseover', function () {
                        this.setStyle({
                            fillOpacity: 0.2,
                            weight: 3
                        })
                    })

                    layer.on('mouseout', function () {
                        this.setStyle({
                            fillOpacity: 0.05,
                            weight: 2
                        })
                    })

                    if (onProvinceClick) {
                        layer.on('click', () => {
                            onProvinceClick(provinceName)
                        })
                    }

                    layer.bindTooltip(provinceName, {
                        permanent: false,
                        direction: 'center',
                        className: 'province-tooltip'
                    })
                }
            }).addTo(map.value)

            return layerGroups.value.provinces
        } catch (error) {
            console.error('Failed to load province boundaries:', error)
            return null
        }
    }

    /**
     * Toggle layer visibility
     */
    const toggleLayerVisibility = (layerName, visible) => {
        const layer = layerGroups.value[layerName]
        if (!layer || !map.value) return

        if (visible) {
            map.value.addLayer(layer)
        } else {
            map.value.removeLayer(layer)
        }
    }

    return {
        map,
        markers,
        geoJsonLayers,
        layerGroups,

        initMap,
        addMarker,
        addMarkers,
        addCircleMarkers,
        clearMarkers,
        flyTo,
        addGeoJsonLayer,
        loadGeoJson,
        clearGeoJsonLayers,

        // New layer methods
        createFarmsLayer,
        createMarketsLayer,
        createFertilizerLayer,
        createPesticideLayer,
        loadProvinceBoundaries,
        toggleLayerVisibility
    }
}
