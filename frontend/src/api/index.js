import request from './request'

// 认证 API
export const authApi = {
  login: (data) => request.post('/auth/login', data),
  logout: () => request.post('/auth/logout'),
  getInfo: () => request.get('/auth/info')
}

// 教室 API
export const classroomApi = {
  getList: (params) => request.get('/classrooms', { params }),
  getAvailable: (startTime, endTime) => request.get('/classrooms/available', { params: { startTime, endTime } }),
  getDetail: (id) => request.get(`/classrooms/${id}`),
  create: (data) => request.post('/classrooms', data),
  update: (id, data) => request.put(`/classrooms/${id}`, data),
  remove: (id) => request.delete(`/classrooms/${id}`),
  updateStatus: (id, status) => request.patch(`/classrooms/${id}/status`, null, { params: { status } })
}

// 预约 API
export const reservationApi = {
  create: (data) => request.post('/reservations', data),
  getMyList: (params) => request.get('/reservations/my', { params }),
  getAll: (params) => request.get('/reservations', { params }),
  getDetail: (id) => request.get(`/reservations/${id}`),
  cancel: (id, reason) => request.put(`/reservations/${id}/cancel`, { reason }),
  batchCreate: (data) => request.post('/reservations/batch', data),
  getNoShows: () => request.get('/reservations/no-shows')
}

// 审批 API
export const approvalApi = {
  getPending: (params) => request.get('/approvals/pending', { params }),
  approve: (id) => request.post(`/approvals/${id}/approve`),
  reject: (id, reason) => request.post(`/approvals/${id}/reject`, { rejectReason: reason })
}

// 使用登记 API
export const usageApi = {
  checkIn: (reservationId) => request.post('/usage/check-in', { reservationId }),
  checkOut: (data) => request.post('/usage/check-out', data),
  getList: (params) => request.get('/usage/list', { params })
}

// 概览 API
export const dashboardApi = {
  getStats: () => request.get('/dashboard/stats'),
  getClassroomUsage: () => request.get('/dashboard/usage/classroom'),
  getWeeklyUsage: (weeks = 8) => request.get('/dashboard/usage/weekly', { params: { weeks } })
}

// 用户管理 API
export const userApi = {
  getList: (params) => request.get('/users', { params }),
  create: (data) => request.post('/users', data),
  update: (id, data) => request.put(`/users/${id}`, data),
  remove: (id) => request.delete(`/users/${id}`),
  updatePassword: (oldPassword, newPassword) => request.put('/users/password', null, { params: { oldPassword, newPassword } })
}
