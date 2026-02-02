/**
 * useAuth Composable
 * Quản lý authentication state và logic
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/authService'

const user = ref(null)
const token = ref(localStorage.getItem('access_token'))

export function useAuth() {
    const router = useRouter()

    const isAuthenticated = computed(() => !!token.value)

    /**
     * Đăng nhập
     */
    const login = async (credentials) => {
        try {
            const response = await authService.login(credentials)
            token.value = response.data.access_token
            user.value = response.data.user
            localStorage.setItem('access_token', token.value)
            return { success: true, user: user.value }
        } catch (error) {
            console.error('Login error:', error)
            throw error
        }
    }

    /**
     * Đăng ký
     */
    const register = async (userData) => {
        try {
            const response = await authService.register(userData)
            return { success: true, user: response.data }
        } catch (error) {
            console.error('Register error:', error)
            throw error
        }
    }

    /**
     * Lấy thông tin user hiện tại
     */
    const fetchCurrentUser = async () => {
        try {
            const response = await authService.getCurrentUser()
            user.value = response.data
            return user.value
        } catch (error) {
            console.error('Fetch user error:', error)
            logout()
            throw error
        }
    }

    /**
     * Đăng xuất
     */
    const logout = () => {
        token.value = null
        user.value = null
        localStorage.removeItem('access_token')
        router.push('/login')
    }

    return {
        user,
        token,
        isAuthenticated,
        login,
        register,
        fetchCurrentUser,
        logout
    }
}
