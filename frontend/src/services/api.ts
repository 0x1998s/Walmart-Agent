// 🛒 沃尔玛AI Agent平台 - API服务
// Walmart AI Agent Platform - API Service

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { message } from 'antd'
import { useAuthStore } from '@/stores/authStore'

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1'

class ApiService {
  private instance: AxiosInstance

  constructor() {
    this.instance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        // 添加认证token
        const { token } = useAuthStore.getState()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // 添加请求ID用于追踪
        config.headers['X-Request-ID'] = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

        console.log(`🔄 API请求: ${config.method?.toUpperCase()} ${config.url}`, config.data)
        return config
      },
      (error) => {
        console.error('❌ 请求拦截器错误:', error)
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`✅ API响应: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
        return response.data
      },
      (error) => {
        console.error('❌ API响应错误:', error)

        // 处理不同的错误状态码
        if (error.response) {
          const { status, data } = error.response

          switch (status) {
            case 401:
              message.error('登录已过期，请重新登录')
              useAuthStore.getState().logout()
              window.location.href = '/login'
              break
            case 403:
              message.error('权限不足，无法访问该资源')
              break
            case 404:
              message.error('请求的资源不存在')
              break
            case 429:
              message.error('请求过于频繁，请稍后重试')
              break
            case 500:
              message.error('服务器内部错误，请稍后重试')
              break
            case 502:
            case 503:
            case 504:
              message.error('服务暂时不可用，请稍后重试')
              break
            default:
              message.error(data?.detail || data?.message || '请求失败，请稍后重试')
          }
        } else if (error.request) {
          // 网络错误
          message.error('网络连接失败，请检查网络设置')
        } else {
          // 其他错误
          message.error('请求发生未知错误')
        }

        return Promise.reject(error)
      }
    )
  }

  // GET请求
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.get(url, config)
  }

  // POST请求
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.post(url, data, config)
  }

  // PUT请求
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.put(url, data, config)
  }

  // DELETE请求
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.delete(url, config)
  }

  // PATCH请求
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.patch(url, data, config)
  }

  // 文件上传
  async upload<T = any>(
    url: string,
    file: File,
    onProgress?: (progressEvent: any) => void,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const formData = new FormData()
    formData.append('file', file)

    return this.instance.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers,
      },
      onUploadProgress: onProgress,
    })
  }

  // 批量上传文件
  async uploadMultiple<T = any>(
    url: string,
    files: File[],
    onProgress?: (progressEvent: any) => void,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const formData = new FormData()
    files.forEach((file, index) => {
      formData.append(`files`, file)
    })

    return this.instance.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers,
      },
      onUploadProgress: onProgress,
    })
  }

  // 下载文件
  async download(url: string, filename?: string, config?: AxiosRequestConfig): Promise<void> {
    const response = await this.instance.get(url, {
      ...config,
      responseType: 'blob',
    })

    // 创建下载链接
    const blob = new Blob([response.data])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  }

  // 流式请求（用于聊天等场景）
  async stream(
    url: string,
    data?: any,
    onMessage?: (chunk: string) => void,
    config?: AxiosRequestConfig
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      const { token } = useAuthStore.getState()
      
      fetch(`${API_BASE_URL}${url}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
          ...(config?.headers as Record<string, string> || {}),
        },
        body: JSON.stringify(data),
      })
        .then(async (response) => {
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
          }

          const reader = response.body?.getReader()
          if (!reader) {
            throw new Error('Response body is not readable')
          }

          const decoder = new TextDecoder()
          let buffer = ''

          try {
            while (true) {
              const { done, value } = await reader.read()
              if (done) break

              buffer += decoder.decode(value, { stream: true })
              const lines = buffer.split('\n')
              buffer = lines.pop() || ''

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  const data = line.slice(6)
                  if (data === '[DONE]') {
                    resolve()
                    return
                  }
                  try {
                    const parsed = JSON.parse(data)
                    onMessage?.(parsed.content || data)
                  } catch {
                    onMessage?.(data)
                  }
                }
              }
            }
            resolve()
          } catch (error) {
            reject(error)
          }
        })
        .catch(reject)
    })
  }

  // 健康检查
  async healthCheck(): Promise<{ status: string; timestamp: number }> {
    return this.get('/health')
  }

  // 获取API信息
  async getApiInfo(): Promise<any> {
    return this.get('/')
  }
}

// 创建API服务实例
export const api = new ApiService()

// 导出常用的API方法
export default api
