<template>
  <div class="feedback-form">
    <div class="form-header">
      <h3>{{ $t('feedback.newFeedback') }}</h3>
      <button @click="$emit('close')" class="close-btn">×</button>
    </div>

    <form @submit.prevent="submitFeedback">
      <!-- Category -->
      <div class="form-group">
        <label>{{ $t('feedback.category') }}</label>
        <select v-model="formData.category" required>
          <option value="bug">{{ $t('feedback.categories.bug') }}</option>
          <option value="feature_request">{{ $t('feedback.categories.feature') }}</option>
          <option value="question">{{ $t('feedback.categories.question') }}</option>
          <option value="other">{{ $t('feedback.categories.other') }}</option>
        </select>
      </div>

      <!-- Subject -->
      <div class="form-group">
        <label>{{ $t('feedback.subject') }}</label>
        <input 
          v-model="formData.subject" 
          type="text" 
          :placeholder="$t('feedback.subject')"
          minlength="5"
          maxlength="200"
          required
        />
      </div>

      <!-- Message -->
      <div class="form-group">
        <label>{{ $t('feedback.message') }}</label>
        <textarea 
          v-model="formData.message" 
          :placeholder="$t('feedback.message')"
          rows="6"
          minlength="10"
          required
        ></textarea>
      </div>

      <!-- Actions -->
      <div class="form-actions">
        <button type="button" @click="$emit('close')" class="btn-cancel">
          {{ $t('common.cancel') }}
        </button>
        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? $t('common.loading') : $t('feedback.submit') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { feedbackService } from '../services/feedbackService'

const emit = defineEmits(['close', 'success'])

const loading = ref(false)
const formData = ref({
  category: 'other',
  subject: '',
  message: ''
})

const submitFeedback = async () => {
  loading.value = true
  try {
    await feedbackService.createFeedback(formData.value)
    alert('Feedback submitted successfully!')
    emit('success')
    emit('close')
  } catch (error) {
    alert('Error submitting feedback: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.feedback-form {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  max-width: 600px;
  margin: 0 auto;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.form-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #6b7280;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 2rem;
  height: 2rem;
}

.close-btn:hover {
  color: #ef4444;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1);
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn-cancel,
.btn-submit {
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn-cancel:hover {
  background: #f9fafb;
}

.btn-submit {
  background: #16a34a;
  border: none;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: #15803d;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
