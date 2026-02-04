/**
 * Analytics Service
 * API calls for admin dashboard analytics
 */
import api from './api'

export const analyticsService = {
    // ========== KPI Endpoints ==========

    /**
     * Get overall KPI metrics
     */
    getKPIOverview() {
        return api.get('/analytics/kpi/overview').then(response => {
            // Transform snake_case to camelCase
            return {
                ...response,
                data: {
                    totalFarms: response.data.total_farms,
                    totalArea: response.data.total_area,
                    activeSeasons: response.data.active_seasons,
                    totalFarmers: response.data.total_farmers
                }
            }
        })
    },

    /**
     * Get alert statistics
     */
    getAlertKPI() {
        return api.get('/analytics/kpi/alerts')
    },

    /**
     * Get farm distribution by market
     */
    getMarketDistribution() {
        return api.get('/analytics/kpi/markets')
    },

    // ========== Chart Data Endpoints ==========

    /**
     * Get crop distribution for pie chart
     */
    getCropDistribution() {
        return api.get('/analytics/charts/crop-distribution')
    },

    /**
     * Get input usage trends (fertilizer/pesticide)
     * @param {number} months - Number of months to look back
     */
    getInputUsageTrends(months = 6) {
        return api.get(`/analytics/charts/input-usage?months=${months}`)
    },

    /**
     * Get alert heatmap data
     */
    getAlertHeatmap() {
        return api.get('/analytics/charts/alert-heatmap')
    },

    // ========== Report Endpoints ==========

    /**
     * Get top farm owners by area
     * @param {number} limit - Number of results
     */
    getTopOwners(limit = 10) {
        return api.get(`/analytics/reports/top-owners?limit=${limit}`)
    },

    /**
     * Get upcoming harvest schedule
     * @param {number} daysAhead - Days to look ahead
     */
    getHarvestSchedule(daysAhead = 30) {
        return api.get(`/analytics/reports/harvest-schedule?days_ahead=${daysAhead}`)
    },

    /**
     * Get farm density by location
     */
    getFarmDensity() {
        return api.get('/analytics/spatial/farm-density')
    },

    // ========== New Advanced Chart Endpoints ==========

    /**
     * Get crop-market relationship for line chart
     */
    getCropMarketRelationship() {
        return api.get('/analytics/charts/crop-market-relationship')
    },

    /**
     * Get fruit-input correlation for combined chart
     */
    getFruitInputCorrelation() {
        return api.get('/analytics/charts/fruit-input-correlation')
    },

    /**
     * Get input usage frequency (fertilizer or pesticide)
     * @param {string} inputType - 'fertilizer' or 'pesticide'
     */
    getInputUsageFrequency(inputType) {
        return api.get(`/analytics/charts/input-usage-frequency?input_type=${inputType}`)
    },

    /**
     * Get revoked/resolved alerts list
     * @param {number} limit - Number of results
     */
    getRevokedAlerts(limit = 20) {
        return api.get(`/analytics/reports/revoked-alerts?limit=${limit}`)
    },

    /**
     * Get farms with layer visualization data
     */
    getFarmsWithLayers() {
        return api.get('/analytics/farms/with-layers')
    },

    /**
     * Get farms by province name
     */
    getFarmsByProvince(provinceName) {
        return api.get(`/analytics/farms/by-province/${encodeURIComponent(provinceName)}`)
    }
}
