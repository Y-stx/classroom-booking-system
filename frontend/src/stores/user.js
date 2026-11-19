import { defineStore } from 'pinia'
import { authApi } from '@/api'
import { getRoleHome } from '@/config/role'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    role: (state) => state.user?.role || '',
    isAdmin: (state) => state.user?.role === 'ADMIN',
    isTeacher: (state) => state.user?.role === 'TEACHER',
    isStudent: (state) => state.user?.role === 'STUDENT',
    displayName: (state) => state.user?.name || '未登录',
    // 角色对应的首屏路径
    homePath: (state) => getRoleHome(state.user?.role)
  },
  actions: {
    async login(username, password) {
      const res = await authApi.login({ username, password })
      this.token = res.data.token
      this.user = res.data.user
      localStorage.setItem('token', this.token)
      localStorage.setItem('user', JSON.stringify(this.user))
      // 返回角色对应首屏路径
      return getRoleHome(this.user.role)
    },
    async logout() {
      try { await authApi.logout() } catch (e) { /* ignore */ }
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
    async fetchUserInfo() {
      const res = await authApi.getInfo()
      this.user = { ...this.user, ...res.data }
      localStorage.setItem('user', JSON.stringify(this.user))
    }
  }
})
