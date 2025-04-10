import { defineBoot } from '#q-app/wrappers'
import axios from 'axios'

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)





const api = axios.create({
  baseURL: process.env.API_BASE_URL || 'https://inventory-w5rc.onrender.com/api/',
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})
// const api = axios.create({
//   baseURL: process.env.API_BASE_URL || 'http://127.0.0.1:8000/api/',
//   timeout: 10000, // 10 second timeout
//   headers: {
//     'Content-Type': 'application/json',
//     'Accept': 'application/json'
//   }
// })

// Request interceptor for auth token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor for global error handling
api.interceptors.response.use(
  response => {
    // You can modify successful responses here
    return response
  },
  error => {
    if (error.response) {
      const { status } = error.response
      
      switch (status) {
        case 401: // Unauthorized
          // Handle token expiration or invalid auth
          if (window.location.pathname !== '/login') {
            Notify.create({
              type: 'negative',
              message: 'Session expired. Please login again.'
            })
            // Clear auth data
            localStorage.removeItem('token')
            localStorage.removeItem('shop_name')
            localStorage.removeItem('first_name')
            localStorage.removeItem('last_name')
            // Redirect to login
            window.location.href = '/login'
          }
          break
          
        case 403: // Forbidden
          Notify.create({
            type: 'warning',
            message: 'You are not authorized for this action.'
          })
          break
          
        case 404: // Not Found
          Notify.create({
            type: 'warning',
            message: 'Resource not found.'
          })
          break
          
        case 500: // Server Error
          Notify.create({
            type: 'negative',
            message: 'Server error occurred. Please try again later.'
          })
          break
          
        default:
          // Handle other errors
          Notify.create({
            type: 'negative',
            message: error.response.data?.detail || 
                    error.response.data?.message || 
                    'An error occurred'
          })
      }
    } else if (error.request) {
      // The request was made but no response was received
      Notify.create({
        type: 'negative',
        message: 'Network error. Please check your connection.'
      })
    } else {
      // Something happened in setting up the request
      Notify.create({
        type: 'negative',
        message: 'Request error. Please try again.'
      })
    }
    
    return Promise.reject(error)
  }
)

export default ({ app }) => {
  // Make axios available globally as this.$axios and this.$api
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
}

export { api }

