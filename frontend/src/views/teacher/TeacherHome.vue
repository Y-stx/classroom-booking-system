<template>
  <div class="teacher-home">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner glass-card teacher-theme">
      <div class="banner-content">
        <div class="banner-text">
          <span class="role-badge">教师</span>
          <h2>{{ greeting }}，{{ userStore.displayName }}</h2>
          <p>{{ dateStr }} · {{ weekStr }} · 本周已使用 {{ weekUsage }} 次</p>
        </div>
        <div class="banner-stats">
          <div class="quick-stat">
            <span class="qs-value">{{ myReservations.length }}</span>
            <span class="qs-label">我的预约</span>
          </div>
          <div class="divider"></div>
          <div class="quick-stat">
            <span class="qs-value warn">{{ pendingCount }}</span>
            <span class="qs-label">待审批</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div class="quick-entry">
      <div class="entry-card glass-card" v-for="(entry, i) in entries" :key="entry.path"
           :style="{ '--i': i }" @click="$router.push(entry.path)">
        <div class="entry-icon">
          <el-icon><component :is="entry.icon" /></el-icon>
        </div>
        <div class="entry-text">
          <h3>{{ entry.title }}</h3>
          <p>{{ entry.desc }}</p>
        </div>
        <el-icon class="entry-arrow"><ArrowRight /></el-icon>
      </div>
    </div>

    <!-- 我的预约统计 -->
    <div class="block-card glass-card">
      <div class="block-header">
        <div>
          <h3>我的预约统计</h3>
          <span class="block-sub">实时统计</span>
        </div>
      </div>
      <div class="stats-row">
        <div class="stat-block" v-for="(s, i) in reservationStats" :key="s.label" :style="{ '--i': i }">
          <div class="stat-icon" :style="{ background: s.soft, color: s.color }">
            <el-icon><component :is="s.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value" :style="{ color: s.color }">{{ s.value }}</span>
            <span class="stat-label">{{ s.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 即将到来的预约 -->
    <div class="block-card glass-card">
      <div class="block-header">
        <div>
          <h3>即将到来的预约</h3>
          <span class="block-sub">点击查看详情并签到</span>
        </div>
        <el-button text type="primary" @click="$router.push('/teacher/reservations')">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <div class="upcoming-list" v-if="upcomingList.length">
        <div v-for="item in upcomingList" :key="item.id" class="upcoming-item"
             @click="$router.push('/teacher/reservations')">
          <div class="upcoming-left">
            <div class="countdown-block" :class="item.status?.toLowerCase()">
              <span class="cd-value">{{ getCountdown(item.startTime) }}</span>
              <span class="cd-label">{{ getCountdownLabel(item.startTime, item.status) }}</span>
            </div>
            <div class="upcoming-info">
              <div class="upcoming-title">{{ item.title }}</div>
              <div class="upcoming-meta">
                <span><el-icon><School /></el-icon> {{ item.classroomName }}</span>
                <span><el-icon><Clock /></el-icon> {{ formatTime(item.startTime) }}</span>
                <span class="status-tag" :class="item.status?.toLowerCase()">{{ statusText(item.status) }}</span>
              </div>
            </div>
          </div>
          <el-icon class="upcoming-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
      <div v-else class="empty-block">
        <el-icon><Calendar /></el-icon>
        <p>暂无即将到来的预约</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  ArrowRight, Trophy, School, Clock, Calendar,
  Document, Check, Warning, CircleClose
} from '@element-plus/icons-vue'
import { reservationApi } from '@/api'

const userStore = useUserStore()
const myReservations = ref([])

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 9) return '早上好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const dateStr = computed(() => {
  const d = new Date()
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}/${pad(d.getMonth()+1)}/${pad(d.getDate())}`
})

const weekStr = computed(() => ['星期日','星期一','星期二','星期三','星期四','星期五','星期六'][new Date().getDay()])

const weekUsage = computed(() => {
  const now = new Date()
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  return myReservations.value.filter(r => {
    const t = new Date(r.startTime?.replace(' ', 'T'))
    return t >= weekAgo
  }).length
})

const pendingCount = computed(() => myReservations.value.filter(r => r.status === 'PENDING').length)

const entries = [
  { title: '教室预约', desc: '浏览可用教室并发起预约', icon: 'School', path: '/teacher/classrooms' },
  { title: '我的预约', desc: '查看预约状态与签到签退', icon: 'Document', path: '/teacher/reservations' },
  { title: '使用登记', desc: '签到签退与设备状况填报', icon: 'EditPen', path: '/teacher/usage' }
]

const reservationStats = computed(() => [
  { label: '待审批', value: myReservations.value.filter(r => r.status === 'PENDING').length, icon: 'Clock', color: '#d97706', soft: 'rgba(245, 158, 11, 0.12)' },
  { label: '已通过', value: myReservations.value.filter(r => r.status === 'APPROVED').length, icon: 'Check', color: '#059669', soft: 'rgba(16, 185, 129, 0.12)' },
  { label: '已完成', value: myReservations.value.filter(r => r.status === 'COMPLETED').length, icon: 'CircleCheck', color: '#2563eb', soft: 'rgba(59, 130, 246, 0.12)' },
  { label: '已驳回', value: myReservations.value.filter(r => r.status === 'REJECTED').length, icon: 'CircleClose', color: '#dc2626', soft: 'rgba(239, 68, 68, 0.12)' }
])

const upcomingList = computed(() => {
  const now = new Date()
  return myReservations.value
    .filter(r => ['PENDING', 'APPROVED'].includes(r.status))
    .filter(r => new Date((r.startTime || '').replace(' ', 'T')) > now)
    .sort((a, b) => new Date(a.startTime) - new Date(b.startTime))
    .slice(0, 5)
})

const statusText = (s) => ({ PENDING: '待审批', APPROVED: '已通过', REJECTED: '已驳回', COMPLETED: '已完成', CANCELLED: '已取消' }[s] || s)

const formatTime = (t) => {
  if (!t) return ''
  return t.replace('T', ' ').substring(0, 16)
}

const getCountdown = (startTime) => {
  if (!startTime) return '--'
  const start = new Date(startTime.replace(' ', 'T'))
  const now = new Date()
  const diff = start - now

  if (diff < 0) return '0'
  const hours = Math.floor(diff / (60 * 60 * 1000))
  const days = Math.floor(hours / 24)
  if (days > 0) return `${days}天`
  if (hours > 0) return `${hours}时`
  const minutes = Math.floor(diff / (60 * 1000))
  return `${minutes}分`
}

const getCountdownLabel = (startTime, status) => {
  if (status === 'PENDING') return '待审批'
  if (status === 'APPROVED') {
    const start = new Date(startTime?.replace(' ', 'T'))
    const now = new Date()
    if (start - now > 0) return '后开始'
    return '进行中'
  }
  return ''
}

const loadData = async () => {
  try {
    const res = await reservationApi.getMyList({ page: 1, pageSize: 100 })
    myReservations.value = res.data.list || []
  } catch (e) {
    // 忽略
  }
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.teacher-home {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.teacher-theme {
  --role-color: #6366f1;
  --role-color-rgb: 99, 102, 241;
  --role-soft: rgba(var(--role-color-rgb), 0.12);
}

.welcome-banner {
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(var(--role-color-rgb), 0.07), transparent 60%);
  animation: bannerIn 0.5s ease;

  .banner-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .role-badge {
    display: inline-block;
    padding: 2px 10px;
    background: var(--role-color);
    color: white;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 8px;
  }

  .banner-text {
    h2 {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 4px;
      letter-spacing: -0.01em;
    }
    p { font-size: 14px; color: var(--text-secondary); }
  }

  .banner-stats {
    display: flex;
    align-items: center;
    gap: 24px;

    .quick-stat {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;

      .qs-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--role-color);
        font-variant-numeric: tabular-nums;
        &.warn { color: #f59e0b; }
      }
      .qs-label { font-size: 12px; color: var(--text-tertiary); }
    }
    .divider { width: 1px; height: 36px; background: var(--border-color); }
  }
}

@keyframes bannerIn { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

.quick-entry {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.entry-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: cardIn 0.4s calc(var(--i) * 0.04s) ease both;

  &:hover {
    box-shadow: var(--card-shadow-hover);
    border-color: rgba(var(--role-color-rgb), 0.35);

    .entry-icon { transform: scale(1.06); }
    .entry-arrow { opacity: 1; transform: translateX(0); }
  }

  .entry-icon {
    width: 48px; height: 48px;
    border-radius: 12px;
    background: var(--role-soft);
    color: var(--role-color);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
    transition: transform 0.3s ease;
  }

  .entry-text {
    flex: 1;
    h3 { font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 2px; }
    p { font-size: 12px; color: var(--text-tertiary); }
  }

  .entry-arrow {
    color: var(--text-tertiary);
    opacity: 0;
    transform: translateX(-8px);
    transition: all 0.25s;
  }
}

@keyframes cardIn { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

.block-card {
  padding: 24px;
  animation: cardIn 0.5s ease;

  .block-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h3 { font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 2px; }
    .block-sub { font-size: 12px; color: var(--text-tertiary); }
  }
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-block {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  animation: cardIn 0.4s calc(var(--i) * 0.04s) ease both;

  .stat-icon {
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
  }

  .stat-info {
    display: flex;
    flex-direction: column;

    .stat-value {
      font-size: 22px;
      font-weight: 700;
      color: var(--text-primary);
      font-variant-numeric: tabular-nums;
    }
    .stat-label { font-size: 12px; color: var(--text-tertiary); }
  }
}

// 即将到来
.upcoming-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upcoming-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-radius: 10px;
  background: rgba(var(--role-color-rgb), 0.04);
  border: 1px solid rgba(var(--role-color-rgb), 0.1);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: cardIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) both;

  &:hover {
    background: rgba(var(--role-color-rgb), 0.08);
    border-color: rgba(var(--role-color-rgb), 0.3);
    transform: translateX(4px);

    .upcoming-arrow { opacity: 1; transform: translateX(0); }
  }

  .upcoming-left {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .countdown-block {
    width: 60px;
    text-align: center;
    padding: 6px;
    border-radius: 8px;
    background: rgba(var(--role-color-rgb), 0.1);
    color: var(--role-color);

    &.approved { background: rgba(16, 185, 129, 0.1); color: #10b981; }
    &.pending { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }

    .cd-value {
      display: block;
      font-size: 16px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }
    .cd-label {
      display: block;
      font-size: 10px;
    }
  }

  .upcoming-info {
    flex: 1;

    .upcoming-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 6px;
    }
    .upcoming-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      font-size: 12px;
      color: var(--text-secondary);

      span { display: flex; align-items: center; gap: 4px; }
      .el-icon { font-size: 13px; color: var(--text-tertiary); }
    }
  }

  .upcoming-arrow {
    color: var(--role-color);
    opacity: 0;
    transform: translateX(-8px);
    transition: all 0.3s;
  }
}

// 状态标签和空状态使用 global.scss 中的全局 .status-tag / .empty-state

@media (max-width: 768px) {
  .quick-entry { grid-template-columns: 1fr; }
  .stats-row { grid-template-columns: 1fr 1fr; }
  .banner-stats { display: none; }
}
</style>
