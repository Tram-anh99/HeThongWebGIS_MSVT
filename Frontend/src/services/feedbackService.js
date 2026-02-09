/**
 * Feedback Service
 * API calls for feedback submission and management
 */
import api from './api'

export const feedbackService = {
    /**
     * Submit new feedback
     */
    createFeedback(data) {
        return api.post('/feedback/', data)
    },

    /**
     * Get user's own feedback list
     */
    getMyFeedback(params = {}) {
        return api.get('/feedback/', { params })
    },

    /**
     * Get all feedback (Admin only)
     */
    getAllFeedback(params = {}) {
        return api.get('/feedback/all', { params })
    },

    /**
     * Get single feedback by ID
     */
    getFeedback(id) {
        return api.get(`/feedback/${id}`)
    },

    /**
     * Update feedback
     */
    updateFeedback(id, data) {
        return api.put(`/feedback/${id}`, data)
    },

    /**
     * Delete feedback
     */
    deleteFeedback(id) {
        return api.delete(`/feedback/${id}`)
    },

    /**
     * Get feedback statistics (Admin only)
     */
    getStats() {
        return api.get('/feedback/stats/counts')
    }
}
