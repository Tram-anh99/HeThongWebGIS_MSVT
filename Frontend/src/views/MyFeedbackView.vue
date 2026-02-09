<template>
  <div class="feedback-view">
    <div class="header">
      <h2>{{ $t('feedback.myFeedback') }}</h2>
      <button @click="showForm = true" class="btn-new">
        + {{ $t('feedback.newFeedback') }}
      </button>
    </div>

    <!-- Feedback Form Modal -->
    <div v-if="showForm" class="modal-overlay" @click="showForm = false">
      <div @click.stop>
        <FeedbackForm @close="showForm = false" @success="loadFeedback" />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">{{ $t('common.loading') }}...</div>

    <!-- Feedback List -->
    <div v-else-if="feedbackList.length > 0" class="feedback-list">
      <div v-for="item in feedbackList" :key="item.id" class="feedback-card">
        <div class="card-header">
          <span class="category-badge" :class="`category-${item.category}`">
            {{ $t(`feedback.categories.${item.category}`) }}
          </span>
          <span class="status-badge" :class="`status-${item.status}`">
            {{ $t(`feedback.statuses.${item.status}`) }}
          </span>
        </div>
        
        <h3>{{ item.subject }}</h3>
        <p class="message">{{ item.message }}</p>
        
        <div class="meta">
          <span>{{ $t('feedback.submittedAt') }}: {{ formatDate(item.created_at) }}</span>
        </div>

        <div v-if="item.admin_response" class="admin-response">
          <h4>{{ $t('feedback.adminResponse') }}:</h4>
          <p>{{ item.admin_response }}</p>
          <div class="meta">
            <span>{{ $t('feedback.respondedAt') }}: {{ formatDate(item.responded_at) }}</span>
          </div>
        </div>
        <div v-else class="no-response">
          {{ $t('feedback.noResponse') }}
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>{{ $t('common.noResults') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { feedbackService } from '../services/feedbackService'
import FeedbackForm from '../components/FeedbackForm.vue'

const loading = ref(false)
const showForm = ref(false)
const feedbackList = ref([])

const loadFeedback = async () => {
  loading.value = true
  try {
    const res = await feedbackService.getMyFeedback()
    feedbackList.value = res.data.items || []
  } catch (error) {
    console.error('Error loading feedback:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadFeedback()
})
</script>

<style scoped>
.feedback-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h2 {
  margin: 0;
  color: #1f2937;
}

.btn-new {
  padding: 0.75rem 1.5rem;
  background: #16a34a;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-new:hover {
  background: #15803d;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.feedback-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.category-badge,
.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.category-bug { background: #fee2e2; color: #991b1b; }
.category-feature_request { background: #dbeafe; color: #1e40af; }
.category-question { background: #fef3c7; color: #92400e; }
.category-other { background: #f3f4f6; color: #374151; }

.status-new { background: #dbeafe; color: #1e40af; }
.status-in_progress { background: #fef3c7; color: #92400e; }
.status-resolved { background: #d1fae5; color: #065f46; }
.status-closed { background: #f3f4f6; color: #6b7280; }

.feedback-card h3 {
  margin: 0 0 0.75rem 0;
  color: #111827;
}

.message {
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.meta {
  font-size: 0.875rem;
  color: #6b7280;
}

.admin-response {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f0fdf4;
  border-left: 4px solid #16a34a;
  border-radius: 0.25rem;
}

.admin-response h4 {
  margin: 0 0 0.5rem 0;
  color: #15803d;
  font-size: 0.875rem;
}

.admin-response p {
  margin: 0;
  color: #166534;
}

.no-response {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 0.25rem;
  color: #6b7280;
  font-style: italic;
  font-size: 0.875rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}
</style>
