/**
 * History Service
 * API calls cho lịch sử canh tác
 */
import api from './api'

export const historyService = {
    /**
     * Lấy danh sách lịch sử canh tác
     */
    getHistory(params = {}) {
        return api.get('/history', { params })
    },

    /**
     * Lấy chi tiết lịch sử
     */
    getHistoryDetail(id) {
        return api.get(`/history/${id}`)
    },

    /**
     * Tạo lịch sử canh tác mới
     */
    createHistory(historyData) {
        return api.post('/history', historyData)
    },

    /**
     * Cập nhật lịch sử
     */
    updateHistory(id, historyData) {
        return api.put(`/history/${id}`, historyData)
    },

    /**
     * Xóa lịch sử
     */
    deleteHistory(id) {
        return api.delete(`/history/${id}`)
    }
}
