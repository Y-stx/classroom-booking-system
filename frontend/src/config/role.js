// =====================================================
// 角色配置常量
// 路径、配色、徽章集中管理，避免硬编码
// =====================================================

// 角色首屏路径
export const ROLE_HOME = {
  STUDENT: '/student/home',
  TEACHER: '/teacher/home',
  ADMIN: '/admin/home'
}

// 角色主题配色
export const ROLE_THEME = {
  STUDENT: {
    primary: '#06b6d4',
    secondary: '#3b82f6',
    gradient: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
    soft: 'rgba(6, 182, 212, 0.15)',
    softText: 'rgba(6, 182, 212, 0.12)'
  },
  TEACHER: {
    primary: '#6366f1',
    secondary: '#8b5cf6',
    gradient: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
    soft: 'rgba(99, 102, 241, 0.15)',
    softText: 'rgba(99, 102, 241, 0.12)'
  },
  ADMIN: {
    primary: '#8b5cf6',
    secondary: '#ec4899',
    gradient: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)',
    soft: 'rgba(139, 92, 246, 0.15)',
    softText: 'rgba(139, 92, 246, 0.12)'
  }
}

// 角色徽章
export const ROLE_BADGE = {
  STUDENT: { text: '学生', color: '#06b6d4' },
  TEACHER: { text: '教师', color: '#6366f1' },
  ADMIN: { text: '管理员', color: '#8b5cf6' }
}

// 角色中文名
export const ROLE_TEXT = {
  ADMIN: '管理员',
  TEACHER: '教师',
  STUDENT: '学生'
}

// 获取角色首屏路径
export const getRoleHome = (role) => ROLE_HOME[role] || '/login'

// 获取角色主题
export const getRoleTheme = (role) => ROLE_THEME[role] || ROLE_THEME.TEACHER

// 获取角色徽章
export const getRoleBadge = (role) => ROLE_BADGE[role] || { text: '', color: '#94a3b8' }
