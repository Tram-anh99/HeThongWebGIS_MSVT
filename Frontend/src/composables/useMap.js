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

    return {
        map,
        markers,
        geoJsonLayers,

        initMap,
        addMarker,
        addMarkers,
        addCircleMarkers,
        clearMarkers,
        flyTo,
        addGeoJsonLayer,
        loadGeoJson,
        clearGeoJsonLayers
    }
}
