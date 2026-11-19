import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getRoleHome } from '@/config/role'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true }
  },

  // ==================== 学生工作区 ====================
  {
    path: '/student',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/student/home',
    meta: { roles: ['STUDENT'] },
    children: [
      { path: 'home', name: 'StudentHome', component: () => import('@/views/student/StudentHome.vue'), meta: { title: '学生工作台', icon: 'House' } },
      { path: 'classrooms', name: 'StudentClassrooms', component: () => import('@/views/ClassroomList.vue'), meta: { title: '教室预约', icon: 'School' } },
      { path: 'reservations', name: 'StudentReservations', component: () => import('@/views/ReservationList.vue'), meta: { title: '我的预约', icon: 'Calendar' } },
      { path: 'usage', name: 'StudentUsage', component: () => import('@/views/UsageLogList.vue'), meta: { title: '使用登记', icon: 'Document' } },
      { path: 'profile', name: 'StudentProfile', component: () => import('@/views/Profile.vue'), meta: { title: '个人中心', icon: 'User' } }
    ]
  },

  // ==================== 教师工作区 ====================
  {
    path: '/teacher',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/teacher/home',
    meta: { roles: ['TEACHER'] },
    children: [
      { path: 'home', name: 'TeacherHome', component: () => import('@/views/teacher/TeacherHome.vue'), meta: { title: '教师工作台', icon: 'House' } },
      { path: 'classrooms', name: 'TeacherClassrooms', component: () => import('@/views/ClassroomList.vue'), meta: { title: '教室预约', icon: 'School' } },
      { path: 'reservations', name: 'TeacherReservations', component: () => import('@/views/ReservationList.vue'), meta: { title: '我的预约', icon: 'Calendar' } },
      { path: 'usage', name: 'TeacherUsage', component: () => import('@/views/UsageLogList.vue'), meta: { title: '使用登记', icon: 'Document' } },
      { path: 'profile', name: 'TeacherProfile', component: () => import('@/views/Profile.vue'), meta: { title: '个人中心', icon: 'User' } }
    ]
  },

  // ==================== 管理员工作区 ====================
  {
    path: '/admin',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/admin/home',
    meta: { roles: ['ADMIN'] },
    children: [
      { path: 'home', name: 'AdminHome', component: () => import('@/views/admin/AdminHome.vue'), meta: { title: '管理工作台', icon: 'House' } },
      { path: 'approvals', name: 'AdminApprovals', component: () => import('@/views/ApprovalCenter.vue'), meta: { title: '审批中心', icon: 'Checked' } },
      { path: 'system', name: 'AdminSystem', component: () => import('@/views/SystemManage.vue'), meta: { title: '系统管理', icon: 'Setting' } },
      { path: 'usage', name: 'AdminUsage', component: () => import('@/views/UsageLogList.vue'), meta: { title: '使用登记', icon: 'Document' } },
      { path: 'no-shows', name: 'AdminNoShows', component: () => import('@/views/admin/NoShowList.vue'), meta: { title: '爽约记录', icon: 'WarningFilled' } },
      { path: 'profile', name: 'AdminProfile', component: () => import('@/views/Profile.vue'), meta: { title: '个人中心', icon: 'User' } }
    ]
  },

  // 兼容旧路径，自动重定向至角色首屏
  {
    path: '/',
    redirect: () => {
      const userStore = useUserStore()
      return userStore.isLoggedIn ? getRoleHome(userStore.role) : '/login'
    }
  },
  {
    path: '/dashboard',
    redirect: () => {
      const userStore = useUserStore()
      return userStore.isLoggedIn ? getRoleHome(userStore.role) : '/login'
    }
  },
  // 兼容旧路径（直接访问旧路径时重定向）
  { path: '/classrooms', redirect: '/' },
  { path: '/reservations', redirect: '/' },
  { path: '/approvals', redirect: '/' },
  { path: '/system', redirect: '/' },
  { path: '/usage', redirect: '/' },
  { path: '/profile', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 公共路径放行
  if (to.meta.public) {
    // 已登录访问登录页时重定向至角色首屏
    if (userStore.isLoggedIn && to.path === '/login') {
      next(getRoleHome(userStore.role))
    } else {
      next()
    }
    return
  }

  // 未登录拦截
  if (!userStore.isLoggedIn) {
    next('/login')
    return
  }

  // 角色校验：父路由 meta.roles 与子路由 meta.roles 合并校验
  const requiredRoles = to.matched.reduce((acc, r) => {
    return r.meta?.roles ? [...new Set([...acc, ...r.meta.roles])] : acc
  }, [])

  if (requiredRoles.length && !requiredRoles.includes(userStore.role)) {
    // 无权限访问，跳转至本人角色首屏
    next(getRoleHome(userStore.role))
    return
  }

  next()
})

export default router
