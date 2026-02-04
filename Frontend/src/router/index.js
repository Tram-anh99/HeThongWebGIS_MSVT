/**
 * Vue Router Configuration
 * Định nghĩa routes cho ứng dụng
 */
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import('../views/HomeView.vue'),
        meta: { title: 'Trang chủ' }
    },
    {
        path: '/map',
        name: 'WebGIS',
        component: () => import('../views/WebGISView.vue'),
        meta: { title: 'Bản đồ WebGIS' }
    },
    {
        path: '/manage',
        name: 'Management',
        component: () => import('../views/ManagementView.vue'),
        meta: {
            title: 'Quản lý',
            requiresAuth: true
        }
    },
    {
        path: '/history',
        name: 'HistoryManagement',
        component: () => import('../views/HistoryManagementView.vue'),
        meta: {
            title: 'Quản lý Nhật ký canh tác',
            requiresAuth: true,
            role: 'farmer'
        }
    },
    {
        path: '/users',
        name: 'UserManagement',
        component: () => import('../views/UserManagementView.vue'),
        meta: {
            title: 'Quản lý Tài khoản',
            requiresAuth: true,
            role: 'admin'
        }
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('../views/DashboardView.vue'),
        meta: {
            title: 'Bảng điều khiển Admin',
            requiresAuth: true,
            role: 'admin'
        }
    },
    {
        path: '/trace/:ma_vung',
        name: 'Trace',
        component: () => import('../views/TraceView.vue'),
        meta: { title: 'Truy xuất nguồn gốc' }
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('../views/LoginView.vue'),
        meta: { title: 'Đăng nhập' }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation guard - Kiểm tra authentication & Role
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user_info')
    const user = userStr ? JSON.parse(userStr) : null

    // Update document title
    document.title = `${to.meta.title || 'WebGIS MSVT'} - Hệ thống Quản lý Mã số Vùng Trồng`

    // Check authentication
    if (to.meta.requiresAuth && !token) {
        next({ name: 'Login', query: { redirect: to.fullPath } })
    }
    // Check Role
    else if (to.meta.role && user && user.role !== to.meta.role) {
        // Redirect to Home if unauthorized
        next({ name: 'Home' })
    }
    // Redirect Login if authenticated
    else if (to.name === 'Login' && token) {
        next({ name: 'Home' })
    } else {
        next()
    }
})

export default router
