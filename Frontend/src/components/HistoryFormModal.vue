<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4" @click="$emit('close')">
    <div class="card w-full max-w-lg overflow-y-auto max-h-[90vh]" @click.stop>
      <h2 class="text-xl font-bold mb-4">
        {{ isEdit ? 'Cập nhật Nhật ký' : 'Ghi Nhật ký mới' }}
      </h2>
      
      <form @submit.prevent="submitForm" class="space-y-4">
        <!-- Date -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Ngày thực hiện *</label>
          <input v-model="formData.ngay_thuc_hien" type="date" required class="input-field" />
        </div>

        <!-- Activity Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Hoạt động *</label>
          <select v-model="formData.loai_hoat_dong_id" required class="input-field">
            <option value="">-- Chọn hoạt động --</option>
            <option v-for="act in categories.activities" :key="act.id" :value="act.id">
              {{ act.ten_hoat_dong }}
            </option>
          </select>
        </div>

        <!-- Details -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Chi tiết / Ghi chú *</label>
          <textarea v-model="formData.chi_tiet" required rows="3" class="input-field" placeholder="Mô tả công việc..."></textarea>
        </div>

        <!-- Inputs Group -->
        <div class="bg-gray-50 p-3 rounded-lg space-y-3">
          <h3 class="text-sm font-bold text-gray-700">Vật tư sử dụng (nếu có)</h3>
          
          <!-- Fertilizer -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Phân bón</label>
            <select v-model="formData.phan_bon_id" class="input-field text-sm">
              <option :value="null">-- Không dùng --</option>
              <option v-for="item in categories.fertilizers" :key="item.id" :value="item.id">
                {{ item.ten_phan_bon }}
              </option>
            </select>
          </div>

          <!-- Pesticide -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Thuốc BVTV</label>
            <select v-model="formData.thuoc_bvtv_id" class="input-field text-sm">
              <option :value="null">-- Không dùng --</option>
              <option v-for="item in categories.pesticides" :key="item.id" :value="item.id">
                {{ item.ten_thuoc }}
              </option>
            </select>
          </div>

          <!-- Dosage -->
          <div class="flex gap-2">
            <div class="flex-1">
              <label class="block text-xs font-medium text-gray-600 mb-1">Liều lượng</label>
              <input v-model="formData.lieu_luong" type="text" class="input-field text-sm" placeholder="VD: 50 kg" />
            </div>
            <div class="w-1/3">
              <label class="block text-xs font-medium text-gray-600 mb-1">Đơn vị</label>
              <input v-model="formData.don_vi" type="text" class="input-field text-sm" placeholder="kg/ha" />
            </div>
          </div>
        </div>
        
        <!-- Executor -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Người thực hiện</label>
          <input v-model="formData.nguoi_thuc_hien" type="text" class="input-field" placeholder="Tên người làm" />
        </div>

        <!-- Error Msg -->
        <div v-if="error" class="text-red-600 text-sm bg-red-50 p-2 rounded">
          {{ error }}
        </div>

        <!-- Actions -->
        <div class="flex space-x-3 pt-2">
          <button type="submit" class="btn-primary flex-1" :disabled="loading">
            {{ loading ? 'Đang lưu...' : 'Lưu lại' }}
          </button>
          <button type="button" @click="$emit('close')" class="btn-secondary flex-1">
            Hủy bỏ
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { historyService } from '../services/historyService'
import { categoryService } from '../services/categoryService'

const props = defineProps({
  farmId: { type: Number, required: true },
  initialData: { type: Object, default: null }
})

const emit = defineEmits(['close', 'saved'])

const loading = ref(false)
const error = ref('')
const categories = ref({
  activities: [],
  fertilizers: [],
  pesticides: []
})

const isEdit = computed(() => !!props.initialData)

// Default Form Data
const formData = ref({
  vung_trong_id: props.farmId,
  loai_hoat_dong_id: '',
  ngay_thuc_hien: new Date().toISOString().split('T')[0],
  chi_tiet: '',
  phan_bon_id: null,
  thuoc_bvtv_id: null,
  lieu_luong: '',
  don_vi: 'kg/ha',
  nguoi_thuc_hien: ''
})

// Check categories cache or store? For now just fetch
const fetchCategories = async () => {
  try {
    const [actRes, fertRes, pestRes] = await Promise.all([
      categoryService.getActivities(),
      categoryService.getFertilizers(),
      categoryService.getPesticides()
    ])
    categories.value.activities = actRes.data
    categories.value.fertilizers = fertRes.data
    categories.value.pesticides = pestRes.data
  } catch (err) {
    console.error('Error fetching categories:', err)
  }
}

const submitForm = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const payload = {
      ...formData.value,
      vung_trong_id: props.farmId // Ensure correct farm ID
    }
    
    if (isEdit.value) {
      await historyService.updateHistory(props.initialData.id, payload)
    } else {
      await historyService.createHistory(payload)
    }
    
    emit('saved')
    emit('close')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Lỗi khi lưu dữ liệu'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCategories()
  
  if (props.initialData) {
    // Fill form data
    formData.value = {
      ...props.initialData,
      // Ensure IDs are valid numbers matches for selects
      loai_hoat_dong_id: props.initialData.loai_hoat_dong_id,
      phan_bon_id: props.initialData.phan_bon_id,
      thuoc_bvtv_id: props.initialData.thuoc_bvtv_id,
      // Format date for input[type=date]
      ngay_thuc_hien: props.initialData.ngay_thuc_hien?.split('T')[0]
    }
  }
})
</script>
