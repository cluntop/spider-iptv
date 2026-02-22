import axios from 'axios'
import Cookies from 'js-cookie'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加认证token
apiClient.interceptors.request.use(
  config => {
    const token = Cookies.get('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 认证服务
export const authService = {
  // 登录
  login: async (username, password) => {
    try {
      // 模拟登录响应
      // 实际项目中应该调用真实的登录API
      if (username === 'admin' && password === 'admin123') {
        const token = 'mock-token-' + Date.now()
        const user = {
          id: 1,
          username: 'admin',
          email: 'admin@example.com',
          role: 'admin',
          permissions: ['all']
        }
        
        // 存储token和用户信息
        Cookies.set('token', token, { expires: 7 })
        localStorage.setItem('user', JSON.stringify(user))
        
        return { success: true, token, user }
      } else {
        throw new Error('用户名或密码错误')
      }
    } catch (error) {
      throw new Error(error.message || '登录失败')
    }
  },
  
  // 登出
  logout: async () => {
    try {
      // 清除存储的token和用户信息
      Cookies.remove('token')
      localStorage.removeItem('user')
      return { success: true }
    } catch (error) {
      throw new Error(error.message || '登出失败')
    }
  },
  
  // 获取当前用户信息
  getCurrentUser: async () => {
    try {
      // 从本地存储获取用户信息
      const userStr = localStorage.getItem('user')
      if (userStr) {
        return JSON.parse(userStr)
      }
      
      // 模拟API调用获取用户信息
      // 实际项目中应该调用真实的API
      // const response = await apiClient.get('/auth/me')
      // return response.data
      
      return null
    } catch (error) {
      throw new Error(error.message || '获取用户信息失败')
    }
  },
  
  // 检查是否已登录
  isAuthenticated: () => {
    const token = Cookies.get('token')
    return !!token
  },
  
  // 获取认证token
  getToken: () => {
    return Cookies.get('token')
  }
}

export const { login, logout, getCurrentUser, isAuthenticated, getToken } = authService
