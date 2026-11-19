<template>
  <div class="layout-container" :class="[`role-${roleKey.toLowerCase()}`, { collapsed: isCollapsed }]" :style="themeVars">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo" @click="toggleCollapse" :title="isCollapsed ? '展开' : '收起'">
        <div class="logo-icon">
          <el-icon><School /></el-icon>
        </div>
        <transition name="slide-fade">
          <div class="logo-text" v-show="!isCollapsed">
            <h2>教室预约</h2>
            <span>{{ roleBadge.text }}工作台</span>
          </div>
        </transition>
        <transition name="rotate">
          <el-icon v-show="!isCollapsed" class="collapse-icon"><Fold /></el-icon>
        </transition>
      </div>

      <nav class="nav-menu">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="active"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <transition name="slide-fade">
            <span v-show="!isCollapsed">{{ item.title }}</span>
          </transition>
        </router-link>
      </nav>

      <!-- 侧边栏底部信息 -->
      <transition name="slide-fade">
        <div class="sidebar-footer" v-show="!isCollapsed">
          <div class="status-dot"></div>
          <span>系统运行正常</span>
        </div>
      </transition>
    </aside>

    <!-- 主内容区 -->
    <div class="main-area">
      <!-- 顶部栏 -->
      <header class="topbar">
        <div class="topbar-left">
          <div class="page-title-block">
            <h1>{{ currentTitle }}</h1>
            <transition name="breadcrumb-fade" mode="out-in">
              <nav class="breadcrumb" :key="route.fullPath">
                <span class="crumb">首页</span>
                <el-icon class="separator"><ArrowRight /></el-icon>
                <span class="crumb current">{{ currentTitle }}</span>
              </nav>
            </transition>
          </div>
        </div>

        <div class="topbar-right">
          <!-- 实时时钟 -->
          <transition name="slide-fade">
            <div class="clock-block" v-show="!isMobile">
              <el-icon><Clock /></el-icon>
              <span class="clock-date">{{ clockDate }}</span>
              <div class="clock-digits">
                <span
                  v-for="(ch, i) in clockTime.split('')"
                  :key="ch + '-' + i"
                  class="clock-digit"
                  :class="{ 'is-sep': ch === ':' }"
                >{{ ch }}</span>
              </div>
            </div>
          </transition>

          <!-- 通知图标 -->
          <div class="icon-btn" @click="ElMessage.info('暂无新通知')">
            <el-icon><Bell /></el-icon>
            <span class="badge"></span>
          </div>

          <!-- 主题切换 -->
          <div class="icon-btn" @click="themeStore.toggleTheme()" :title="themeStore.isDark ? '切换到浅色' : '切换到深色'">
            <el-icon>
              <Sunny v-if="themeStore.isDark" />
              <Moon v-else />
            </el-icon>
          </div>

          <!-- 全屏按钮 -->
          <div class="icon-btn" @click="toggleFullscreen">
            <el-icon>
              <FullScreen v-if="!isFullscreen" />
              <Aim v-else />
            </el-icon>
          </div>

          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-info">
              <div class="avatar">{{ userStore.displayName.charAt(0) }}</div>
              <transition name="slide-fade">
                <div class="user-detail" v-show="!isMobile">
                  <span class="user-name">{{ userStore.displayName }}</span>
                  <span class="user-role">{{ roleText }}</span>
                </div>
              </transition>
              <el-icon v-show="!isMobile"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  <span>个人中心</span>
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 内容区 -->
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="page-switch" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import { getRoleTheme, getRoleBadge, ROLE_TEXT } from '@/config/role'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

// 角色信息
const roleKey = computed(() => userStore.role || 'TEACHER')
const roleTheme = computed(() => getRoleTheme(roleKey.value))
const roleBadge = computed(() => getRoleBadge(roleKey.value))
const roleText = computed(() => ROLE_TEXT[roleKey.value] || '')

// 主题 CSS 变量
const themeVars = computed(() => ({
  '--role-primary': roleTheme.value.primary,
  '--role-secondary': roleTheme.value.secondary,
  '--role-gradient': roleTheme.value.gradient,
  '--role-soft': roleTheme.value.soft,
  '--role-rgb': hexToRgb(roleTheme.value.primary)
}))

// 十六进制转 rgb
function hexToRgb(hex) {
  const m = hex.replace('#', '').match(/.{2}/g)
  if (!m) return '99, 102, 241'
  return m.map(s => parseInt(s, 16)).join(', ')
}

// 侧边栏收起
const isCollapsed = ref(false)
const toggleCollapse = () => { isCollapsed.value = !isCollapsed.value }

// 移动端检测
const isMobile = ref(window.innerWidth < 768)
const onResize = () => { isMobile.value = window.innerWidth < 768 }

// 全屏
const isFullscreen = ref(false)
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen?.()
  } else {
    document.exitFullscreen?.()
  }
}
const onFsChange = () => { isFullscreen.value = !!document.fullscreenElement }

// 实时时钟
const currentTime = ref('')
const clockDate = ref('')
const clockTime = ref('')
const pad = n => String(n).padStart(2, '0')
let timer = null
const tick = () => {
  const d = new Date()
  currentTime.value = `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  clockDate.value = `${pad(d.getMonth()+1)}/${pad(d.getDate())}`
  clockTime.value = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

// 当前路由所属工作区根路径（如 /student）
const currentWorkspace = computed(() => {
  const top = route.path.split('/')[1]
  return '/' + (top || '')
})

// 菜单项取当前工作区下子路由
const menuItems = computed(() => {
  const ws = currentWorkspace.value
  const wsRoute = router.options.routes.find(r => r.path === ws && r.children)
  if (!wsRoute) return []
  return wsRoute.children.map(r => ({
    path: ws + '/' + r.path,
    title: r.meta?.title,
    icon: r.meta?.icon
  }))
})

const currentTitle = computed(() => route.meta.title || '教室预约系统')

const handleCommand = async (cmd) => {
  if (cmd === 'profile') {
    router.push(currentWorkspace.value + '/profile')
  } else if (cmd === 'logout') {
    try {
      await ElMessageBox.confirm('确定退出登录吗？', '提示', { type: 'warning' })
      await userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (e) { /* 取消 */ }
  }
}

onMounted(() => {
  tick()
  timer = setInterval(tick, 1000)
  window.addEventListener('resize', onResize)
  document.addEventListener('fullscreenchange', onFsChange)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  window.removeEventListener('resize', onResize)
  document.removeEventListener('fullscreenchange', onFsChange)
})
</script>

<style lang="scss" scoped>
.layout-container {
  display: flex;
  min-height: 100vh;
  position: relative;

  &.collapsed .sidebar {
    width: 72px;
    .nav-item { justify-content: center; padding: 10px 0; }
    .logo { justify-content: center; }
  }
  &.collapsed .main-area { margin-left: 72px; }
}

// 侧边栏 — 参考 vue-pure-admin 的实色面板设计
.sidebar {
  width: 240px;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 100;
  background: var(--card-bg);
  border-right: 1px solid var(--border-color);
  transition: width 0.2s ease;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px 16px;
  border-bottom: 1px solid var(--border-color-subtle);
  cursor: pointer;
  position: relative;
  margin-bottom: 8px;

  .logo-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: var(--role-primary, #6366f1);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(var(--role-rgb, 99, 102, 241), 0.25);
  }

  .logo-text {
    h2 { font-size: 15px; font-weight: 700; color: var(--text-primary); white-space: nowrap; letter-spacing: -0.01em; }
    span { font-size: 11px; color: var(--text-tertiary); white-space: nowrap; font-weight: 500; margin-top: 1px; display: block; }
  }

  .collapse-icon {
    position: absolute;
    right: 0;
    top: 12px;
    color: var(--text-quaternary);
    font-size: 14px;
    transition: color 0.15s ease;

    &:hover {
      color: var(--text-secondary);
    }
  }
}

.nav-menu {
  flex: 1;
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
  overflow-x: hidden;

  &::-webkit-scrollbar { width: 0; }
}

// 导航项 — 参考 vue-pure-admin 的 active 态视觉反馈
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.15s ease;
  font-weight: 500;
  font-size: 14px;
  position: relative;
  margin: 0 4px;

  .el-icon { font-size: 17px; flex-shrink: 0; }

  &:hover {
    background: var(--bg-muted);
    color: var(--text-primary);
  }

  &.active {
    background: rgba(var(--role-rgb, 99, 102, 241), 0.1);
    color: var(--role-primary, #6366f1);
    font-weight: 600;

    &::before {
      content: '';
      position: absolute;
      left: -4px;
      top: 50%;
      transform: translateY(-50%);
      width: 3px;
      height: 20px;
      border-radius: 9999px;
      background: var(--role-primary, #6366f1);
    }
  }
}

.sidebar-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  font-size: 12px;
  color: var(--text-tertiary);
  border-top: 1px solid var(--border-color-subtle);

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10b981;
  }
}

// 主内容区
.main-area {
  flex: 1;
  margin-left: 240px;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
  z-index: 1;
  transition: margin 0.2s ease;
}

// 顶栏 — 参考 Soybean Admin 的精简顶栏
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  margin-bottom: 20px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  box-shadow: var(--card-shadow);

  .page-title-block {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  h1 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
  }

  .breadcrumb {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: var(--text-tertiary);

    .crumb { color: var(--text-tertiary); }
    .crumb.current { color: var(--text-secondary); font-weight: 500; }
    .separator { font-size: 10px; color: var(--text-quaternary); }
  }
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.clock-block {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 8px;
  background: var(--bg-muted);
  color: var(--text-secondary);
  font-family: 'JetBrains Mono', monospace;
  font-weight: 500;
  font-size: 13px;

  .el-icon { font-size: 14px; color: var(--text-tertiary); }

  .clock-date {
    font-size: 11px;
    color: var(--text-tertiary);
    letter-spacing: 0.5px;
  }

  .clock-digits {
    display: flex;
    align-items: center;
    font-size: 13px;
    font-weight: 600;
  }

  .clock-digit {
    display: inline-block;
    min-width: 10px;
    text-align: center;
  }
}

.icon-btn {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.15s ease;
  position: relative;

  &:hover {
    background: var(--bg-muted);
    color: var(--text-primary);
  }

  .el-icon { font-size: 17px; }

  .badge {
    position: absolute;
    top: 6px;
    right: 6px;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #ef4444;
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px 4px 4px;
  border-radius: 8px;
  transition: background 0.15s ease;

  &:hover {
    background: var(--bg-muted);
  }
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--role-primary, #6366f1);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 13px;
  flex-shrink: 0;
}

.user-detail {
  display: flex;
  flex-direction: column;
  .user-name { font-size: 13px; font-weight: 600; color: var(--text-primary); white-space: nowrap; }
  .user-role { font-size: 11px; color: var(--text-tertiary); white-space: nowrap; }
}

.content {
  flex: 1;
}

// ==================== 过渡动画 ====================
// 页面切换
.page-switch-enter-active,
.page-switch-leave-active {
  transition: opacity 0.2s ease;
}
.page-switch-enter-from,
.page-switch-leave-to {
  opacity: 0;
}

// 滑入淡出
.slide-fade-enter-active {
  transition: opacity 0.2s ease;
}
.slide-fade-leave-active {
  transition: opacity 0.15s ease;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
}

// 面包屑
.breadcrumb-fade-enter-active,
.breadcrumb-fade-leave-active {
  transition: all 0.3s ease;
}
.breadcrumb-fade-enter-from { opacity: 0; transform: translateX(10px); }
.breadcrumb-fade-leave-to { opacity: 0; transform: translateX(-10px); }

// 旋转
.rotate-enter-active,
.rotate-leave-active {
  transition: all 0.3s;
}
.rotate-enter-from { opacity: 0; transform: rotate(-90deg); }
.rotate-leave-to { opacity: 0; transform: rotate(90deg); }

// 响应式
@media (max-width: 768px) {
  .sidebar { width: 72px; }
  .main-area { margin-left: 72px; padding: 16px; }
  .nav-item { justify-content: center; padding: 10px 0; }
  .topbar { padding: 12px 16px; }
  .topbar-right { gap: 4px; }
}
</style>
