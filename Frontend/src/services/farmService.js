/**
 * Farm Service
 * API calls cho quản lý vùng trồng
 */
import api from './api'

export const farmService = {
    /**
     * Lấy danh sách vùng trồng
     */
    getFarms(params = {}) {
        return api.get('/farms', { params })
    },

    /**
     * Lấy chi tiết vùng trồng
     */
    getFarm(id) {
        return api.get(`/farms/${id}`)
    },

    /**
     * Tạo vùng trồng mới
     */
    createFarm(farmData) {
        return api.post('/farms', farmData)
    },

    /**
     * Cập nhật vùng trồng
     */
    updateFarm(id, farmData) {
        return api.put(`/farms/${id}`, farmData)
    },

    /**
     * Xóa vùng trồng
     */
    deleteFarm(id) {
        return api.delete(`/farms/${id}`)
    },

    /**
     * Lấy lịch sử canh tác của vùng trồng
     */
    getFarmHistory(id) {
        return api.get(`/farms/${id}/history`)
    }
}
