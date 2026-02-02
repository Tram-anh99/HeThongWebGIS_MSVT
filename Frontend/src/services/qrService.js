/**
 * QR Code Service
 * API calls cho QR code và truy xuất nguồn gốc
 */
import api from './api'

export const qrService = {
    /**
     * Tạo QR code cho vùng trồng
     */
    generateQR(maVung) {
        return `http://localhost:8000/api/qr/generate/${maVung}`
    },

    /**
     * Truy xuất thông tin vùng trồng (public)
     */
    traceFarm(maVung) {
        return api.get(`/qr/trace/${maVung}`)
    }
}
