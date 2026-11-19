import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000
})

// 防止多个 401 并发时重复跳转登录页
let isRedirectingToLogin = false

// 请求拦截器 - 自动添加 Token
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器 - 统一处理
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.success === false) {
      ElMessage.error(res.message || '操作失败')
      return Promise.reject(new Error(res.message))
    }
    return res
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        // 仅提示一次，避免并发 401 触发多次弹窗
        if (!isRedirectingToLogin) {
          isRedirectingToLogin = true
          ElMessage.error(data?.message || '登录已失效，请重新登录')
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          // 记录来源路径，登录后可回跳
          const currentPath = router.currentRoute.value.fullPath
          const redirect = currentPath && currentPath !== '/login' ? `?redirect=${encodeURIComponent(currentPath)}` : ''
          // 使用 SPA 路由跳转，避免整页刷新中止其他请求导致 ERR_ABORTED
          router.replace(`/login${redirect}`).finally(() => {
            isRedirectingToLogin = false
          })
        }
      } else if (status === 403) {
        ElMessage.error(data?.message || '无权限执行此操作')
      } else if (status === 400) {
        ElMessage.error(data?.message || '请求参数错误')
      } else {
        ElMessage.error(data?.message || '服务器错误')
      }
    } else {
      ElMessage.error('网络连接异常')
    }
    return Promise.reject(error)
  }
)

export default request
