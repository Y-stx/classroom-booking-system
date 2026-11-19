<template>
  <div class="student-home">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner glass-card student-theme">
      <div class="banner-content">
        <div class="banner-text">
          <span class="role-badge">学生</span>
          <h2>{{ greeting }}，{{ userStore.displayName }}</h2>
          <p>{{ dateStr }} · {{ weekStr }}</p>
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

    <!-- 今日可用教室 -->
    <div class="block-card glass-card">
      <div class="block-header">
        <div>
          <h3>今日可用教室</h3>
          <span class="block-sub">点击查看详情并预约</span>
        </div>
        <el-button text type="primary" @click="$router.push('/student/classrooms')">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <div class="classroom-grid" v-if="availableRooms.length">
        <div v-for="room in availableRooms" :key="room.id" class="room-chip"
             @click="goReserve(room)">
          <div class="room-head">
            <span class="room-name">{{ room.name }}</span>
            <span class="room-type">{{ typeText(room.type) }}</span>
          </div>
          <div class="room-meta">
            <span><el-icon><Location /></el-icon> {{ room.building }} {{ room.floor }}F</span>
            <span><el-icon><User /></el-icon> {{ room.capacity }}人</span>
          </div>
        </div>
      </div>
      <div v-else class="empty-block">
        <el-icon><Box /></el-icon>
        <p>暂无可用教室</p>
      </div>
    </div>

    <!-- 最近预约时间轴 -->
    <div class="block-card glass-card">
      <div class="block-header">
        <div>
          <h3>我的最近预约</h3>
          <span class="block-sub">最新 5 条</span>
        </div>
        <el-button text type="primary" @click="$router.push('/student/reservations')">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <div class="timeline" v-if="myReservations.length">
        <div v-for="(item, i) in myReservations" :key="item.id" class="timeline-item">
          <span class="time-dot" :class="item.status?.toLowerCase()"></span>
          <div class="time-content">
            <div class="time-title">{{ item.title }}</div>
            <div class="time-meta">
              <span><el-icon><School /></el-icon> {{ item.classroomName }}</span>
              <span><el-icon><Clock /></el-icon> {{ formatTime(item.startTime) }}</span>
              <span class="status-tag" :class="item.status?.toLowerCase()">{{ statusText(item.status) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty-block">
        <el-icon><Document /></el-icon>
        <p>暂无预约记录</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  ArrowRight, Reading, Location, User, School, Clock,
  Document, Box, Calendar, Check, EditPen
} from '@element-plus/icons-vue'
import { classroomApi, reservationApi } from '@/api'

const router = useRouter()
const userStore = useUserStore()
const myReservations = ref([])
const availableRooms = ref([])

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

const pendingCount = computed(() => myReservations.value.filter(r => r.status === 'PENDING').length)

const entries = [
  { title: '我要预约', desc: '浏览可用教室并发起预约', icon: 'Calendar', path: '/student/classrooms' },
  { title: '我的预约', desc: '查看预约状态与签到签退', icon: 'Document', path: '/student/reservations' },
  { title: '使用登记', desc: '签到签退与设备状况填报', icon: 'EditPen', path: '/student/usage' }
]

const statusText = (s) => ({ PENDING: '待审批', APPROVED: '已通过', REJECTED: '已驳回', COMPLETED: '已完成', CANCELLED: '已取消' }[s] || s)

const typeText = (t) => ({ MULTIMEDIA: '多媒体', COMPUTER: '机房', LAB: '实验室', NORMAL: '普通' }[t] || t)

const formatTime = (t) => {
  if (!t) return ''
  return t.replace('T', ' ').substring(0, 16)
}

const goReserve = (room) => {
  router.push('/student/classrooms')
}

const loadData = async () => {
  try {
    const [res1, res2] = await Promise.all([
      classroomApi.getList({ page: 1, pageSize: 6, status: 'AVAILABLE' }),
      reservationApi.getMyList({ page: 1, pageSize: 5 })
    ])
    availableRooms.value = res1.data.list || []
    myReservations.value = res2.data.list || []
  } catch (e) {
    // 忽略
  }
}

onMounted(loadData)
</script>

<style lang="scss" scoped>
.student-home {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

// 学生主题色
.student-theme {
  --role-color: #06b6d4;
  --role-color-rgb: 6, 182, 212;
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

// 快捷入口
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

// 区块卡片
.block-card {
  padding: 24px;
  animation: cardIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);

  .block-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h3 { font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 2px; }
    .block-sub { font-size: 11px; color: var(--text-tertiary); }
  }
}

.classroom-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.room-chip {
  padding: 14px 16px;
  border-radius: 10px;
  background: rgba(var(--role-color-rgb), 0.05);
  border: 1px solid rgba(var(--role-color-rgb), 0.15);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    background: rgba(var(--role-color-rgb), 0.1);
    border-color: rgba(var(--role-color-rgb), 0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(var(--role-color-rgb), 0.1);
  }

  .room-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .room-name { font-size: 15px; font-weight: 700; color: var(--text-primary); }
    .room-type {
      padding: 1px 8px;
      background: rgba(var(--role-color-rgb), 0.12);
      color: var(--role-color);
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
    }
  }

  .room-meta {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 12px;
    color: var(--text-secondary);

    span { display: flex; align-items: center; gap: 4px; }
    .el-icon { font-size: 13px; color: var(--text-tertiary); }
  }
}

// 时间轴
.timeline {
  position: relative;
  padding-left: 20px;

  &::before {
    content: '';
    position: absolute;
    left: 5px;
    top: 8px;
    bottom: 8px;
    width: 2px;
    background: rgba(var(--role-color-rgb), 0.25);
  }
}

.timeline-item {
  position: relative;
  padding-bottom: 16px;

  &:last-child { padding-bottom: 0; }

  .time-dot {
    position: absolute;
    left: -20px;
    top: 4px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--card-bg);
    border: 2px solid var(--role-color);
    z-index: 1;

    &.pending { border-color: #f59e0b; }
    &.approved { border-color: #10b981; background: #10b981; }
    &.rejected { border-color: #ef4444; }
    &.completed { border-color: #3b82f6; background: #3b82f6; }
    &.cancelled { border-color: #9ca3af; }
  }

  .time-content {
    padding: 10px 14px;
    background: rgba(var(--role-color-rgb), 0.04);
    border-radius: 8px;
    transition: background 0.3s;

    &:hover { background: rgba(var(--role-color-rgb), 0.08); }

    .time-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 6px;
    }
    .time-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      font-size: 12px;
      color: var(--text-secondary);

      span { display: flex; align-items: center; gap: 4px; }
      .el-icon { font-size: 13px; color: var(--text-tertiary); }
    }
  }
}

// 状态标签和空状态使用 global.scss 中的全局 .status-tag / .empty-state

@media (max-width: 768px) {
  .quick-entry { grid-template-columns: 1fr; }
  .banner-stats { display: none; }
}
</style>
