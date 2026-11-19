<template>
  <div
    class="login-container"
    :class="['tab-' + activeTab, { 'is-loading': loading, 'theme-dark': themeStore.isDark }]"
  >
    <!-- 主题切换按钮 -->
    <div class="theme-toggle" @click="themeStore.toggleTheme()">
      <el-icon>
        <Sunny v-if="themeStore.isDark" />
        <Moon v-else />
      </el-icon>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card glass-card">
      <!-- 顶部状态条 -->
      <div class="card-status-bar">
        <span class="status-dot"></span>
        <span class="status-text">SYSTEM ONLINE</span>
        <span class="status-id">v2.6.09</span>
      </div>

        <!-- 角色 Tab 切换 -->
        <div class="role-tabs">
          <button
            class="role-tab"
            :class="{ active: activeTab === 'student' }"
            @click="activeTab = 'student'"
          >
            <el-icon><Reading /></el-icon>
            <span>学生登录</span>
          </button>
          <button
            class="role-tab"
            :class="{ active: activeTab === 'teacher' }"
            @click="activeTab = 'teacher'"
          >
            <el-icon><Trophy /></el-icon>
            <span>教师/管理员</span>
          </button>
          <span class="tab-indicator" :class="{ 'tab-right': activeTab === 'teacher' }"></span>
        </div>

        <div class="login-header">
          <!-- 代码注释风格副标 -->
          <div class="code-comment">// CLASSROOM · RESERVATION · SYSTEM</div>

          <div class="logo-icon">
            <el-icon>
              <component :is="activeTab === 'student' ? 'Reading' : 'Trophy'" />
            </el-icon>
          </div>
          <h1>教室预约与使用登记系统</h1>
          <p>{{ activeTab === 'student' ? 'STUDENT PORTAL' : 'TEACHER & ADMIN PORTAL' }}</p>
        </div>

        <!-- 角色说明 -->
        <transition name="role-fade" mode="out-in">
          <div class="role-desc" :key="activeTab">
            <span class="desc-bracket">[</span>
            <template v-if="activeTab === 'student'">
              <el-icon><Calendar /></el-icon>
              <span>预约教室 · 查看预约 · 签到签退</span>
            </template>
            <template v-else>
              <el-icon><Checked /></el-icon>
              <span>教室预约 · 审批管理 · 使用登记</span>
            </template>
            <span class="desc-bracket">]</span>
          </div>
        </transition>

        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              size="large"
              :prefix-icon="User"
              clearable
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
              @keyup="checkCapsLock"
            />
            <transition name="fade">
              <div v-if="capsLockOn" class="caps-warning">
                <el-icon><WarningFilled /></el-icon>
                <span>大写锁定已开启</span>
              </div>
            </transition>
          </el-form-item>
          <el-form-item>
            <button type="submit" class="login-btn" :disabled="loading">
              <el-icon v-if="loading" class="is-loading"><Loading /></el-icon>
              <span>{{ loading ? '登录中...' : '登 录' }}</span>
            </button>
          </el-form-item>
        </el-form>

        <!-- 测试账号快捷区 -->
        <div class="login-tips">
          <div class="tips-header">
            <el-icon><Key /></el-icon>
            <p>{{ activeTab === 'student' ? '学生测试账号' : '教师/管理员测试账号' }}</p>
          </div>
          <div class="account-list">
            <template v-if="activeTab === 'student'">
              <div class="account-item" @click="fillAccount('student01', '123456')">
                <span class="role student">学生</span>
                <span class="account-name">student01 / 123456</span>
                <span class="account-arrow"><el-icon><ArrowRight /></el-icon></span>
              </div>
            </template>
            <template v-else>
              <div class="account-item" @click="fillAccount('teacher01', '123456')">
                <span class="role teacher">教师</span>
                <span class="account-name">teacher01 / 123456</span>
                <span class="account-arrow"><el-icon><ArrowRight /></el-icon></span>
              </div>
              <div class="account-item" @click="fillAccount('admin', 'admin123')">
                <span class="role admin">管理员</span>
                <span class="account-name">admin / admin123</span>
                <span class="account-arrow"><el-icon><ArrowRight /></el-icon></span>
              </div>
            </template>
          </div>
        </div>
      </div>

    <!-- 页脚信息 -->
    <div class="login-footer">
      <span>© 2026 教室预约与使用登记系统 · Built with Vue + SpringBoot</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  User, Lock, WarningFilled, Loading, ArrowRight, Key,
  Reading, Trophy, Calendar, Checked
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const themeStore = useThemeStore()
const formRef = ref()
const loading = ref(false)
const capsLockOn = ref(false)
const activeTab = ref('student') // 默认学生登录

const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const fillAccount = (u, p) => {
  form.username = u
  form.password = p
  ElMessage.success('已自动填充账号信息')
}

const checkCapsLock = (e) => {
  capsLockOn.value = e.getModifierState && e.getModifierState('CapsLock')
}

const handleLogin = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      // login 返回角色对应首屏路径
      const homePath = await userStore.login(form.username, form.password)
      ElMessage.success('登录成功，欢迎回来！')
      // 支持 redirect 回跳（401 拦截器记录的来源路径）
      const redirect = route.query.redirect
      if (redirect && typeof redirect === 'string' && redirect.startsWith('/')) {
        router.push(redirect)
      } else {
        router.push(homePath)
      }
    } catch (e) {
      // 错误已由拦截器处理
    } finally {
      loading.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 20px;
  background: var(--bg-page);
  transition: background 0.3s ease;

  // 角色强调色（学生=青，教师/管理员=靛）
  --accent: #6366f1;
  --accent-soft: rgba(99, 102, 241, 0.08);
  --accent-rgb: 99, 102, 241;

  &.tab-student {
    --accent: #06b6d4;
    --accent-soft: rgba(6, 182, 212, 0.08);
    --accent-rgb: 6, 182, 212;
  }
}

.login-card {
  width: 420px;
  max-width: 100%;
  padding: 28px 36px 36px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  position: relative;
  box-shadow: var(--card-shadow-hover);
  animation: cardIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  transition: background 0.3s, border-color 0.3s;
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

// 顶部状态条
.card-status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 14px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
  font-size: 12px;
  color: var(--text-tertiary);
  letter-spacing: 0.5px;

  .status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
  }
  .status-id {
    margin-left: auto;
  }
}

// 角色 Tab
.role-tabs {
  display: flex;
  position: relative;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 4px;
  margin-bottom: 24px;

  .role-tab {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 10px;
    border: none;
    background: transparent;
    color: var(--text-tertiary);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    border-radius: 8px;
    position: relative;
    z-index: 1;
    transition: color 0.25s;

    .el-icon { font-size: 16px; }

    &.active {
      color: #fff;
      font-weight: 600;
    }
  }

  .tab-indicator {
    position: absolute;
    top: 4px;
    left: 4px;
    width: calc(50% - 4px);
    height: calc(100% - 8px);
    background: var(--accent);
    border-radius: 6px;
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 0;

    &.tab-right {
      transform: translateX(100%);
    }
  }
}

// 头部
.login-header {
  text-align: center;
  margin-bottom: 20px;

  .code-comment {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-tertiary);
    letter-spacing: 1.5px;
    margin-bottom: 16px;
  }

  .logo-icon {
    width: 56px; height: 56px;
    margin: 0 auto 14px;
    border-radius: 8px;
    background: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 24px;
    box-shadow: 0 4px 12px rgba(var(--accent-rgb), 0.3);
  }

  h1 {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 6px;
    letter-spacing: -0.01em;
  }

  p {
    font-size: 11px;
    color: var(--text-secondary);
    letter-spacing: 2px;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
  }
}

// 角色说明
.role-desc {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--accent-soft);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 24px;
  font-size: 12px;
  color: var(--text-secondary);

  .el-icon { color: var(--accent); font-size: 14px; }
  .desc-bracket { color: var(--accent); font-weight: 700; }
}

.role-fade-enter-active,
.role-fade-leave-active {
  transition: all 0.25s ease;
}
.role-fade-enter-from { opacity: 0; transform: translateX(10px); }
.role-fade-leave-to { opacity: 0; transform: translateX(-10px); }

:deep(.el-input__wrapper) {
  padding: 6px 14px;
  border-radius: 12px;
  transition: all 0.25s ease;
  background: var(--bg-surface);
  box-shadow: none !important;
  border: 1px solid var(--border-color);

  &:hover { border-color: color-mix(in srgb, var(--accent) 40%, var(--border-color-strong)); }
  &.is-focus {
    background: var(--bg-surface-strong);
    border-color: var(--accent);
  }
}

:deep(.el-input__inner) {
  color: var(--text-primary) !important;
  &::placeholder { color: var(--text-tertiary) !important; }
}

:deep(.el-input__prefix .el-icon) {
  color: var(--text-tertiary);
  transition: color 0.25s;
}
:deep(.is-focus .el-input__prefix .el-icon) {
  color: var(--accent);
}

.caps-warning {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  padding: 4px 8px;
  font-size: 12px;
  color: #d97706;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 6px;

  .el-icon { font-size: 14px; }
}

// 登录按钮（实色主色）
.login-btn {
  width: 100%;
  padding: 13px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  letter-spacing: 2px;
  transition: all 0.25s ease;

  &:hover:not(:disabled) {
    filter: brightness(0.96);
    box-shadow: 0 6px 18px color-mix(in srgb, var(--accent) 35%, transparent);
  }
  &:active:not(:disabled) { transform: scale(0.99); }
  &:disabled { opacity: 0.7; cursor: not-allowed; }
}

// 测试账号区
.login-tips {
  margin-top: 20px;
  padding: 16px;
  background: rgba(var(--primary-rgb), 0.04);
  border: 1px solid var(--border-color);
  border-radius: 12px;

  .tips-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 12px;
    color: var(--text-secondary);

    .el-icon { font-size: 14px; color: var(--primary); }
    p { font-size: 12px; font-weight: 500; }
  }

  .account-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .account-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    color: var(--text-primary);
    cursor: pointer;
    padding: 8px 12px;
    border-radius: 8px;
    background: var(--bg-surface);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid transparent;

    &:hover {
      background: var(--accent-soft);
      border-color: color-mix(in srgb, var(--accent) 35%, transparent);

      .account-arrow { opacity: 1; transform: translateX(0); }
    }

    .account-name {
      flex: 1;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: var(--text-secondary);
    }

    .account-arrow {
      opacity: 0;
      transform: translateX(-8px);
      transition: all 0.25s;
      color: var(--accent);
    }

    .role {
      display: inline-block;
      padding: 2px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;

      &.admin { background: rgba(139, 92, 246, 0.14); color: #7c3aed; }
      &.teacher { background: rgba(99, 102, 241, 0.14); color: #4f46e5; }
      &.student { background: rgba(6, 182, 212, 0.14); color: #0e7490; }
    }
  }
}

.login-footer {
  position: absolute;
  bottom: 24px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 11px;
  color: var(--text-tertiary);
  z-index: 1;
  letter-spacing: 0.5px;
}

// 主题切换按钮
.theme-toggle {
  position: fixed;
  top: 24px;
  right: 24px;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-primary);
  font-size: 18px;
  z-index: 10;
  transition: all 0.2s ease;

  &:hover {
    background: var(--accent-soft);
    border-color: var(--accent);
    color: var(--accent);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 480px) {
  .login-card { padding: 20px 18px 28px; }
  .role-tab span { display: none; }
  .code-comment { font-size: 9px; }
}
</style>
