/**
 * Authentication Service
 * API calls cho đăng nhập, đăng ký, và quản lý user
 */
import api from './api'

export const authService = {
    /**
     * Đăng nhập
     */
    login(credentials) {
        const formData = new FormData()
        formData.append('username', credentials.username)
        formData.append('password', credentials.password)

        return api.post('/auth/login', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    /**
     * Đăng ký người dùng mới
     */
    register(userData) {
        return api.post('/auth/register', userData)
    },

    /**
     * Lấy thông tin user hiện tại
     */
    getCurrentUser() {
        return api.get('/auth/me')
    },

    /**
     * Đăng xuất
     */
    logout() {
        return api.post('/auth/logout')
    }
}
