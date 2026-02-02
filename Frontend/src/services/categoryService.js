/**
 * Category Service
 * API calls cho danh mục (crops, fertilizers, pesticides, seeds)
 */
import api from './api'

export const categoryService = {
    /**
     * Lấy danh sách loại cây trồng
     */
    getCrops() {
        return api.get('/categories/crops')
    },

    /**
     * Lấy danh sách loại hoạt động
     */
    getActivities() {
        return api.get('/categories/activities')
    },

    /**
     * Lấy danh sách phân bón
     */
    getFertilizers(limit = 100) {
        return api.get('/categories/fertilizers', { params: { limit } })
    },

    /**
     * Lấy danh sách thuốc BVTV
     */
    getPesticides(limit = 100) {
        return api.get('/categories/pesticides', { params: { limit } })
    },

    /**
     * Lấy danh sách giống cây
     */
    getSeeds(limit = 100) {
        return api.get('/categories/seeds', { params: { limit } })
    }
}
