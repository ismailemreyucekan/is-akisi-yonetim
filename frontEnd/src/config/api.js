// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3002'

export const API_ENDPOINTS = {
  workflows: `${API_BASE_URL}/api/workflows`,
  health: `${API_BASE_URL}/api/health`,
}

export default API_BASE_URL

