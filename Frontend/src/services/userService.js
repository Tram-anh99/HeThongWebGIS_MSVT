/**
 * User Service (Admin)
 */
import api from './api'

export const userService = {
    /**
     * Lấy danh sách users
     */
    getUsers(params = {}) {
        return api.get('/users', { params })
    },

    /**
     * Tạo user mới
     */
    createUser(data) {
        return api.post('/users', data)
    },

    /**
     * Cập nhật user
     */
    updateUser(id, data) {
        return api.put(`/users/${id}`, data)
    },

    /**
     * Xóa user
     */
    deleteUser(id) {
        return api.delete(`/users/${id}`)
    }
}
