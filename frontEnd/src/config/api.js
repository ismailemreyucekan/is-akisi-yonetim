// API Base URL
// Varsayılan olarak Python FastAPI backend portu (3001) kullanılır.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001'

export const API_ENDPOINTS = {
  workflows: `${API_BASE_URL}/api/workflows`,
  issues: `${API_BASE_URL}/api/issues`,
  health: `${API_BASE_URL}/api/health`,
}

export default API_BASE_URL

