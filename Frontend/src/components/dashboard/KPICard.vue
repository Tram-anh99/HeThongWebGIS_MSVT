<template>
  <div class="kpi-card" :class="`theme-${theme}`">
    <div class="card-header">
      <div class="icon-container">
        <span class="icon">{{ icon }}</span>
      </div>
      <h3 class="title">{{ title }}</h3>
    </div>
    
    <div class="card-body">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>
      
      <div v-else class="value-container">
        <div class="value">{{ formattedValue }}</div>
        <div v-if="subtitle" class="subtitle">{{ subtitle }}</div>
        
        <div v-if="trend" class="trend" :class="trendClass">
          <span class="trend-icon">{{ trendIcon }}</span>
          <span class="trend-value">{{ trend }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: '📊'
  },
  theme: {
    type: String,
    default: 'primary', // primary, success, warning, danger
    validator: (value) => ['primary', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  trend: {
    type: Number,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  format: {
    type: String,
    default: 'number', // number, currency, percentage
    validator: (value) => ['number', 'currency', 'percentage'].includes(value)
  }
})

const formattedValue = computed(() => {
  if (props.loading) return '---'
  
  const val = props.value
  
  switch (props.format) {
    case 'currency':
      return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
      }).format(val)
    
    case 'percentage':
      return `${val}%`
    
    case 'number':
    default:
      return new Intl.NumberFormat('vi-VN').format(val)
  }
})

const trendClass = computed(() => {
  if (!props.trend) return ''
  return props.trend > 0 ? 'trend-up' : 'trend-down'
})

const trendIcon = computed(() => {
  if (!props.trend) return ''
  return props.trend > 0 ? '↗' : '↘'
})
</script>

<style scoped>
.kpi-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.kpi-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.icon-container {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.theme-primary .icon-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.theme-success .icon-container {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.theme-warning .icon-container {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.theme-danger .icon-container {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.theme-info .icon-container {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  margin: 0;
  line-height: 1.4;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem 0;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.value-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.value {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  line-height: 1;
}

.subtitle {
  font-size: 0.875rem;
  color: #9ca3af;
}

.trend {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  width: fit-content;
}

.trend-up {
  background: #dcfce7;
  color: #16a34a;
}

.trend-down {
  background: #fee2e2;
  color: #dc2626;
}

.trend-icon {
  font-size: 1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .kpi-card {
    padding: 1.25rem;
  }
  
  .value {
    font-size: 1.75rem;
  }
  
  .icon-container {
    width: 40px;
    height: 40px;
  }
}
</style>
