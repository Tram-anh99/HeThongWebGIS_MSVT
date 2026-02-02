<template>
  <div class="user-management-view">
    <div class="container mx-auto px-4 py-6">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">Quản lý Tài khoản</h1>
        <button @click="openAddModal" class="btn-primary">
          + Thêm Tài khoản
        </button>
      </div>

      <!-- Filters -->
      <div class="card mb-6 p-4">
        <div class="flex gap-4">
          <input
            v-model="filters.search"
            type="text"
            placeholder="Tìm theo Username, Email, Tên..."
            class="input-field flex-1"
            @input="handleSearch"
          />
          <select v-model="filters.role" class="input-field w-48" @change="handleSearch">
            <option value="">-- Tất cả vai trò --</option>
            <option value="farmer">Nông dân</option>
            <option value="admin">Quản trị viên</option>
          </select>
        </div>
      </div>

      <!-- Table -->
      <div class="card overflow-x-auto">
        <div v-if="loading" class="text-center py-8">
           <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
           <p class="mt-2 text-gray-500">Đang tải...</p>
        </div>

        <table v-else class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left">Username</th>
              <th class="px-4 py-3 text-left">Họ tên</th>
              <th class="px-4 py-3 text-left">Email</th>
              <th class="px-4 py-3 text-left">Vai trò</th>
              <th class="px-4 py-3 text-left">Trạng thái</th>
              <th class="px-4 py-3 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
             <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50">
               <td class="px-4 py-3 font-medium">{{ u.username }}</td>
               <td class="px-4 py-3">{{ u.full_name }}</td>
               <td class="px-4 py-3 text-gray-500">{{ u.email }}</td>
               <td class="px-4 py-3">
                 <span class="px-2 py-1 rounded text-xs font-bold"
                   :class="u.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'">
                   {{ u.role === 'admin' ? 'Quản trị' : 'Nông dân' }}
                 </span>
               </td>
               <td class="px-4 py-3">
                 <span class="text-green-600" v-if="u.is_active">Hoạt động</span>
                 <span class="text-red-600" v-else>Đã khóa</span>
               </td>
               <td class="px-4 py-3 text-right space-x-2">
                 <button @click="openEditModal(u)" class="text-blue-600 hover:underline">Sửa</button>
                 <button @click="deleteUser(u)" class="text-red-600 hover:underline" :disabled="u.role==='admin'">Xóa</button>
               </td>
             </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="mt-4 flex justify-center gap-2">
         <button 
           v-for="p in totalPages" 
           :key="p"
           @click="currentPage = p; fetchUsers()"
           class="px-3 py-1 rounded border"
           :class="p === currentPage ? 'bg-primary-600 text-white' : 'bg-white hover:bg-gray-100'"
         >
           {{ p }}
         </button>
      </div>
    </div>

    <!-- Modal Form -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="card w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">{{ isEdit ? 'Cập nhật Tài khoản' : 'Thêm Tài khoản mới' }}</h2>
        
        <form @submit.prevent="submitForm" class="space-y-3">
           <div>
             <label class="block text-sm font-medium mb-1">Username *</label>
             <input v-model="form.username" type="text" required class="input-field" :disabled="isEdit" />
           </div>

           <div>
             <label class="block text-sm font-medium mb-1">Họ tên</label>
             <input v-model="form.full_name" type="text" class="input-field" />
           </div>

           <div>
             <label class="block text-sm font-medium mb-1">Email</label>
             <input v-model="form.email" type="email" class="input-field" />
           </div>

           <div>
             <label class="block text-sm font-medium mb-1">Vai trò</label>
             <select v-model="form.role" class="input-field">
               <option value="farmer">Nông dân</option>
               <option value="admin">Quản trị viên</option>
             </select>
           </div>
           
           <div>
             <label class="block text-sm font-medium mb-1">
               {{ isEdit ? 'Mật khẩu mới (Để trống nếu không đổi)' : 'Mật khẩu *' }}
             </label>
             <input v-model="form.password" type="password" class="input-field" :required="!isEdit" />
           </div>

           <div v-if="error" class="text-red-600 text-sm">{{ error }}</div>

           <div class="flex space-x-3 pt-2">
             <button type="submit" class="btn-primary flex-1" :disabled="submitting">
               {{ submitting ? 'Đang lưu...' : 'Lưu lại' }}
             </button>
             <button type="button" @click="closeModal" class="btn-secondary flex-1">Hủy</button>
           </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { userService } from '../services/userService'

const users = ref([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)

const filters = ref({ search: '', role: '' })

// Modal
const showModal = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const error = ref('')
const selectedId = ref(null)

const form = ref({
  username: '',
  full_name: '',
  email: '',
  password: '',
  role: 'farmer'
})

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: 20,
      search: filters.value.search || undefined,
      role: filters.value.role || undefined
    }
    const res = await userService.getUsers(params)
    users.value = res.data.items
    totalPages.value = res.data.total_pages
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

// Actions
const openAddModal = () => {
  isEdit.value = false
  form.value = { username: '', full_name: '', email: '', password: '', role: 'farmer' }
  error.value = ''
  showModal.value = true
}

const openEditModal = (u) => {
  isEdit.value = true
  selectedId.value = u.id
  form.value = { 
    username: u.username, 
    full_name: u.full_name, 
    email: u.email, 
    password: '', 
    role: u.role 
  }
  error.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const submitForm = async () => {
  submitting.value = true
  error.value = ''
  try {
    if (isEdit.value) {
      await userService.updateUser(selectedId.value, form.value)
    } else {
      await userService.createUser(form.value)
    }
    closeModal()
    fetchUsers()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Lỗi xử lý'
  } finally {
    submitting.value = false
  }
}

const deleteUser = async (u) => {
  if (!confirm(`Bạn có chắc muốn xóa/khóa tài khoản ${u.username}?`)) return
  try {
    await userService.deleteUser(u.id)
    fetchUsers()
  } catch (err) {
    alert(err.response?.data?.detail || 'Lỗi khi xóa')
  }
}

onMounted(() => {
  fetchUsers()
})
</script>
