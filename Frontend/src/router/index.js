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
            title: 'Bảng điều khiển',
            requiresAuth: true,
            roles: ['admin', 'manager']
        }
    },
    {
        path: '/farmer-dashboard',
        name: 'FarmerDashboard',
        component: () => import('../views/FarmerDashboardView.vue'),
        meta: {
            title: 'Bảng điều khiển Nông dân',
            requiresAuth: true,
            role: 'farmer'
        }
    },
    {
        path: '/feedback',
        name: 'MyFeedback',
        component: () => import('../views/MyFeedbackView.vue'),
        meta: {
            title: 'Góp ý của tôi',
            requiresAuth: true
        }
    },
    {
        path: '/admin/feedback',
        name: 'FeedbackManagement',
        component: () => import('../views/FeedbackManagementView.vue'),
        meta: {
            title: 'Quản lý Góp ý',
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
    // Check Role (supports both single role and roles array)
    else if (user) {
        if (to.meta.role && user.role !== to.meta.role) {
            // Single role check
            next({ name: 'Home' })
        } else if (to.meta.roles && !to.meta.roles.includes(user.role)) {
            // Multiple roles check
            next({ name: 'Home' })
        } else if (to.name === 'Login') {
            // Redirect authenticated users away from login
            next({ name: 'Home' })
        } else {
            next()
        }
    }
    // Redirect Login if authenticated (and user object might be null but token exists)
    else if (to.name === 'Login' && token) {
        next({ name: 'Home' })
    } else {
        next()
    }
})

export default router
