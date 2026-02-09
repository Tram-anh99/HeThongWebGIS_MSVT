<template>
  <div class="feedback-management">
    <div class="header">
      <h2>{{ $t('feedback.allFeedback') }}</h2>
      <div class="stats" v-if="stats">
        <span class="stat">{{ $t('feedback.statuses.new') }}: <strong>{{ stats.new }}</strong></span>
        <span class="stat">{{ $t('common.loading') }}: <strong>{{ stats.in_progress }}</strong></span>
        <span class="stat">{{ $t('feedback.statuses.resolved') }}: <strong>{{ stats.resolved }}</strong></span>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <select v-model="filters.status" @change="loadFeedback">
        <option value="">{{ $t('feedback.status') }}: {{ $t('common.filter') }}</option>
        <option value="new">{{ $t('feedback.statuses.new') }}</option>
        <option value="in_progress">{{ $t('feedback.statuses.in_progress') }}</option>
        <option value="resolved">{{ $t('feedback.statuses.resolved') }}</option>
        <option value="closed">{{ $t('feedback.statuses.closed') }}</option>
      </select>

      <select v-model="filters.category" @change="loadFeedback">
        <option value="">{{ $t('feedback.category') }}: {{ $t('common.filter') }}</option>
        <option value="bug">{{ $t('feedback.categories.bug') }}</option>
        <option value="feature_request">{{ $t('feedback.categories.feature_request') }}</option>
        <option value="question">{{ $t('feedback.categories.question') }}</option>
        <option value="other">{{ $t('feedback.categories.other') }}</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading">{{ $t('common.loading') }}...</div>

    <!-- Feedback List -->
    <div v-else-if="feedbackList.length > 0" class="feedback-list">
      <div v-for="item in feedbackList" :key="item.id" class="feedback-item">
        <div class="item-header">
          <div>
            <h3>{{ item.subject }}</h3>
            <p class="user-info" v-if="item.user">
              {{ item.user.full_name || item.user.username }} ({{ item.user.role }})
            </p>
          </div>
          <div class="badges">
            <span class="category-badge" :class="`category-${item.category}`">
              {{ $t(`feedback.categories.${item.category}`) }}
            </span>
            <span class="status-badge" :class="`status-${item.status}`">
              {{ $t(`feedback.statuses.${item.status}`) }}
            </span>
          </div>
        </div>

        <p class="message">{{ item.message }}</p>
        <p class="meta">{{ $t('feedback.submittedAt') }}: {{ formatDate(item.created_at) }}</p>

        <!-- Admin Response Section -->
        <div class="response-section">
          <div v-if="item.admin_response" class="existing-response">
            <strong>{{ $t('feedback.adminResponse') }}:</strong>
            <p>{{ item.admin_response }}</p>
            <p class="meta">{{ $t('feedback.respondedAt') }}: {{ formatDate(item.responded_at) }}</p>
          </div>

          <!-- Response Form -->
          <div v-if="respondingTo !== item.id" class="actions">
            <button @click="respondingTo = item.id" class="btn-respond">
              {{ item.admin_response ? $t('common.edit') : $t('feedback.adminResponse') }}
            </button>
            <select v-model="item.status" @change="updateStatus(item)" class="status-select">
              <option value="new">{{ $t('feedback.statuses.new') }}</option>
              <option value="in_progress">{{ $t('feedback.statuses.in_progress') }}</option>
              <option value="resolved">{{ $t('feedback.statuses.resolved') }}</option>
              <option value="closed">{{ $t('feedback.statuses.closed') }}</option>
            </select>
          </div>

          <div v-else class="response-form">
            <textarea 
              v-model="responseText" 
              :placeholder="$t('feedback.adminResponse')"
              rows="4"
            ></textarea>
            <div class="form-actions">
              <button @click="respondingTo = null" class="btn-cancel">{{ $t('common.cancel') }}</button>
              <button @click="submitResponse(item)" class="btn-submit">{{ $t('common.save') }}</button>
            </div>
          </div>
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

const loading = ref(false)
const feedbackList = ref([])
const stats = ref(null)
const filters = ref({ status: '', category: '' })
const respondingTo = ref(null)
const responseText = ref('')

const loadFeedback = async () => {
  loading.value = true
  try {
    const res = await feedbackService.getAllFeedback(filters.value)
    feedbackList.value = res.data.items || []
  } catch (error) {
    console.error('Error loading feedback:', error)
    alert('Error loading feedback')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await feedbackService.getStats()
    stats.value = res.data
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const submitResponse = async (item) => {
  if (!responseText.value.trim()) {
    alert('Please enter a response')
    return
  }

  try {
    await feedbackService.updateFeedback(item.id, {
      admin_response: responseText.value,
      status: 'in_progress'
    })
    alert('Response submitted successfully')
    responseText.value = ''
    respondingTo.value = null
    loadFeedback()
    loadStats()
  } catch (error) {
    alert('Error submitting response: ' + (error.response?.data?.detail || error.message))
  }
}

const updateStatus = async (item) => {
  try {
    await feedbackService.updateFeedback(item.id, { status: item.status })
    loadStats()
  } catch (error) {
    alert('Error updating status: ' + (error.response?.data?.detail || error.message))
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadFeedback()
  loadStats()
})
</script>

<style scoped>
.feedback-management {
  max-width: 1400px;
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

.stats {
  display: flex;
  gap: 2rem;
}

.stat {
  color: #6b7280;
  font-size: 0.875rem;
}

.stat strong {
  color: #111827;
  font-size: 1.125rem;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.filters select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
}

.loading, .empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.feedback-item {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.item-header h3 {
  margin: 0 0 0.25rem 0;
  color: #111827;
}

.user-info {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}

.badges {
  display: flex;
  gap: 0.5rem;
}

.category-badge, .status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  white-space: nowrap;
}

.category-bug { background: #fee2e2; color: #991b1b; }
.category-feature_request { background: #dbeafe; color: #1e40af; }
.category-question { background: #fef3c7; color: #92400e; }
.category-other { background: #f3f4f6; color: #374151; }

.status-new { background: #dbeafe; color: #1e40af; }
.status-in_progress { background: #fef3c7; color: #92400e; }
.status- resolved { background: #d1fae5; color: #065f46; }
.status-closed { background: #f3f4f6; color: #6b7280; }

.message {
  color: #4b5563;
  line-height: 1.6;
  margin: 1rem 0;
}

.meta {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0.5rem 0;
}

.response-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.existing-response {
  padding: 1rem;
  background: #f0fdf4;
  border-left: 4px solid #16a34a;
  border-radius: 0.25rem;
  margin-bottom: 1rem;
}

.existing-response p {
  margin: 0.5rem 0 0 0;
  color: #166534;
}

.actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn-respond {
  padding: 0.5rem 1rem;
  background: #16a34a;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
}

.btn-respond:hover {
  background: #15803d;
}

.status-select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
}

.response-form textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-family: inherit;
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  justify-content: flex-end;
}

.btn-cancel, .btn-submit {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-cancel {
  background: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn-submit {
  background: #16a34a;
  color: white;
  border: none;
}

.btn-submit:hover {
  background: #15803d;
}
</style>
